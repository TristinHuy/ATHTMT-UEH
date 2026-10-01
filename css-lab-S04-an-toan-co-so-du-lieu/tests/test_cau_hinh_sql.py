"""Đọc chính tập lệnh SQL và tệp cấu hình máy chủ của bạn.

Sáu phép kiểm ở đây trả lời một câu duy nhất: bài của bạn có nói đúng thứ nó
tuyên bố hay không. Chúng đọc văn bản, không nối vào máy chủ, nên chúng chạy
được cả khi Docker chưa lên; đổi lại, chúng chỉ thấy được điều bạn viết chứ
không thấy điều máy chủ thật sự làm. Phần sau là việc của tám phép kiểm truy
vấn, và hai phần bổ trợ nhau chứ không thay nhau: một câu lệnh viết đúng mà
chưa bao giờ chạy vẫn là một lời hứa.

Mọi phép kiểm đọc phần SQL ĐÃ BỎ CHÚ THÍCH, và bỏ qua tệp dữ liệu phát sẵn. Lý
do ghi ở `tro_giup.py`.
"""
from __future__ import annotations

import re

import pytest

from tro_giup import (
    BA_VAI_TRO,
    BANG_MUC_HANG,
    BANG_NHAY_CAM,
    SQL,
    TEP_PHAT_SAN,
    VAI_TRO_DANH_DAU,
    VAI_TRO_SO_HUU,
    co,
    doc_cau_hinh_may_chu,
    doc_sql_bai_lam,
)


@pytest.fixture(scope="module")
def bai_lam() -> str:
    noi_dung = doc_sql_bai_lam()
    if not noi_dung.strip():
        pytest.fail(
            "Không thấy câu lệnh SQL nào trong sql/, ngoài tệp phát sẵn. Ba tệp "
            "01-vai-tro.sql, 02-muc-hang.sql và 03-pgaudit.sql là phần bạn viết."
        )
    return noi_dung


@pytest.fixture(scope="module")
def cac_cau(bai_lam: str) -> list[str]:
    """Tách thành từng câu lệnh, để một phép kiểm hỏi được về một câu chứ không
    về cả tệp. Không tách thì `GRANT INSERT ON x TO a; GRANT SELECT ON x TO b;`
    và một câu duy nhất cấp cả hai cho cả hai trông giống hệt nhau."""
    return [c.strip() for c in bai_lam.split(";") if c.strip()]


def test_du_lieu_phat_san_con_nguyen():
    """Tệp 00-du-lieu.sql là hiện trạng bạn nhận bàn giao, không phải bài làm.

    Nó chứa đúng một dòng cấp quyền rộng, và việc đầu tiên của bài là thu dòng ấy
    lại bằng một câu REVOKE. Xóa nó khỏi tệp phát sẵn cũng làm phép kiểm quyền
    chuyển xanh, nhưng nó không siết gì cả: nó chỉ giấu đi cái đáng siết, và trên
    một hệ thống thật thì dòng ấy vẫn nằm đó vì nó đã chạy từ năm ngoái.
    """
    tep = SQL / TEP_PHAT_SAN
    if not tep.exists():
        pytest.fail(f"Không thấy sql/{TEP_PHAT_SAN}. Lấy lại bản gốc từ kho mẫu.")
    noi_dung = tep.read_text(encoding="utf-8")
    thieu = []
    if not co(r"GRANT\s+SELECT\s+ON\s+ALL\s+TABLES\s+IN\s+SCHEMA\s+public\s+TO\s+PUBLIC", noi_dung):
        thieu.append("dòng cấp quyền rộng do người tiền nhiệm để lại")
    if not co(r"CREATE\s+ROLE\s+khach_tam", noi_dung):
        thieu.append("vai trò khach_tam")
    if len(re.findall(r"'NV-\d\d'", noi_dung)) != 12:
        thieu.append("đủ 12 dòng nhân sự")
    assert not thieu, (
        f"sql/{TEP_PHAT_SAN} đã bị sửa, thiếu: " + ", ".join(thieu)
        + ". Tệp này phát sẵn và không phải phần bài làm. Lấy lại bản gốc rồi siết bằng câu lệnh của bạn."
    )


def test_thu_het_quyen_cap_san_cho_public(bai_lam):
    """Bốn chỗ, và bỏ sót chỗ nào thì mọi vai trò vẫn còn đường vòng tới đó.

    Nguyên lý thứ tư nói trạng thái ban đầu phải là trạng thái đóng, còn một hệ
    quản trị cơ sở dữ liệu thì mở sẵn để lệnh CREATE DATABASE xong là dùng được
    ngay. Khoảng lệch giữa hai điều đó chính là phần việc của bước này.
    """
    can = {
        "quyền trên bảng, thứ người tiền nhiệm đã cấp cho PUBLIC":
            r"REVOKE[^;]*\bON\s+ALL\s+TABLES\s+IN\s+SCHEMA[^;]*FROM\s+PUBLIC",
        "quyền EXECUTE trên hàm, thứ PostgreSQL cấp sẵn cho PUBLIC":
            r"REVOKE[^;]*\bON\s+(ALL\s+FUNCTIONS\s+IN\s+SCHEMA|FUNCTION)[^;]*FROM\s+PUBLIC",
        "quyền USAGE trên lược đồ public":
            r"REVOKE[^;]*\bON\s+SCHEMA[^;]*FROM\s+PUBLIC",
        "quyền CONNECT trên cơ sở dữ liệu":
            r"REVOKE[^;]*\bON\s+DATABASE[^;]*FROM\s+PUBLIC",
    }
    thieu = [ten for ten, mau in can.items() if not co(mau, bai_lam)]
    assert not thieu, (
        "Chưa thu hết phần cấp sẵn cho PUBLIC. Còn thiếu:\n  - " + "\n  - ".join(thieu)
        + "\nThu CONNECT của PUBLIC thì nhớ cấp lại cho đúng những vai trò cần nối vào, "
          "kể cả ba vai trò bạn vừa dựng."
    )


def test_ba_vai_tro_du_va_khong_vai_tro_nao_thua_quyen(bai_lam, cac_cau):
    """Ba vai trò làm việc, cộng vai trò sở hữu, và không vai trò nào mang một
    thuộc tính đi xuyên qua phần còn lại của bài.

    BYPASSRLS đáng dừng lại một nhịp: nó đi xuyên mọi chính sách mức hàng, nên
    một vai trò mang nó biến cả bước hai thành trang trí. SUPERUSER thì đi xuyên
    tất cả, kể cả phần lưu vết.
    """
    hong = []
    for vai in (*BA_VAI_TRO, VAI_TRO_SO_HUU):
        if not co(rf"CREATE\s+ROLE\s+{vai}\b", bai_lam):
            hong.append(f"chưa dựng vai trò {vai}.")

    for cau in cac_cau:
        if not co(r"^(CREATE|ALTER)\s+ROLE\b", cau):
            continue
        for thuoc_tinh in ("SUPERUSER", "BYPASSRLS", "CREATEROLE"):
            if co(rf"\b{thuoc_tinh}\b", cau) and not co(rf"\bNO{thuoc_tinh}\b", cau):
                hong.append(f"vai trò mang {thuoc_tinh}: {cau[:70]}...")

    for cau in cac_cau:
        if co(r"\bGRANT\b", cau) and co(r"\bTO\s+PUBLIC\b", cau):
            hong.append(f"cấp quyền lại cho PUBLIC: {cau[:70]}...")
        if co(r"\bGRANT\s+ALL\b", cau) and co(rf"\b({BANG_NHAY_CAM}|{BANG_MUC_HANG})\b", cau):
            hong.append(f"cấp trọn quyền trên một bảng nhạy cảm: {cau[:70]}...")
        if co(r"\bGRANT\b[^;]*\bINSERT\b", cau) and co(r"\bTO\b[^;]*\bduyet_chi\b", cau):
            hong.append(
                "cấp quyền INSERT cho duyet_chi, tức là người duyệt tạo được đề nghị chi. "
                "Đó là chỗ mục 4.5 gọi là một cặp quyền nằm trong cùng một vai trò."
            )
    assert not hong, "Bộ vai trò chưa đạt:\n  " + "\n  ".join(hong)


def test_chinh_sach_muc_hang_du_hai_ve_va_ap_ca_cho_chu_so_huu(bai_lam):
    """An toàn mức hàng đúng thì cần bốn thứ cùng lúc, và ba trong bốn thứ ấy im
    lặng khi thiếu.

    Thiếu FORCE thì chính sách vẫn tạo được, vẫn chạy được, và vô hiệu với đúng
    vai trò có nhiều quyền nhất. Thiếu WITH CHECK thì phần đọc bị lọc mà phần ghi
    thì không, nên bài trông như đã xong trong khi cửa sau còn mở.
    """
    thieu = []
    if not co(rf"ALTER\s+TABLE[^;]*{BANG_MUC_HANG}[^;]*ENABLE\s+ROW\s+LEVEL\s+SECURITY", bai_lam):
        thieu.append(f"chưa bật ENABLE ROW LEVEL SECURITY cho {BANG_MUC_HANG}")
    if not co(rf"ALTER\s+TABLE[^;]*{BANG_MUC_HANG}[^;]*FORCE\s+ROW\s+LEVEL\s+SECURITY", bai_lam):
        thieu.append(
            f"chưa bật FORCE ROW LEVEL SECURITY cho {BANG_MUC_HANG}, nên chủ sở hữu bảng "
            "vẫn đọc trọn bảng; đây là bẫy mặc định ở mục 4.4 và là điều A5 hỏi"
        )
    so_chinh_sach = len(re.findall(r"CREATE\s+POLICY", bai_lam, flags=re.IGNORECASE))
    if so_chinh_sach < 2:
        thieu.append(
            f"mới có {so_chinh_sach} chính sách; cần ít nhất hai, vì vai trò ứng dụng và "
            "vai trò duyệt nhìn thấy hai tập dòng khác nhau"
        )
    if not co(r"CREATE\s+POLICY[^;]*\bUSING\b", bai_lam):
        thieu.append("không chính sách nào có vế USING, tức là chưa lọc phần đọc")
    if not co(r"CREATE\s+POLICY[^;]*\bWITH\s+CHECK\b", bai_lam):
        thieu.append("không chính sách nào có vế WITH CHECK, tức là chưa lọc phần ghi")
    assert not thieu, "Chính sách mức hàng chưa đủ:\n  - " + "\n  - ".join(thieu)


def test_rang_buoc_nguoi_tao_khac_nguoi_duyet(cac_cau):
    """Ràng buộc này phải nằm trong cơ sở dữ liệu, không nằm trong ứng dụng.

    Lý do đúng bằng lý do của an toàn mức hàng ở mục 4.4: còn công cụ báo cáo,
    còn phiên psql của người vận hành, còn tập lệnh di trú. Một luật nghiệp vụ
    chỉ có trong mã ứng dụng là một luật chỉ đúng trên một trong nhiều con đường.
    """
    tim_thay = [
        cau for cau in cac_cau
        if co(r"\bnguoi_tao\b", cau) and co(r"\bnguoi_duyet\b", cau)
        and co(r"\b(CHECK|TRIGGER)\b", cau)
    ]
    assert tim_thay, (
        "Không thấy ràng buộc nào buộc người duyệt khác người tạo. Đề bài đòi một ràng "
        "buộc CHECK (bộ chấm A4 chỉ nhận vi phạm ràng buộc CHECK), đặt trên bảng " + BANG_MUC_HANG + ", và nó phải cho "
        "phép dòng chưa duyệt, tức cột người duyệt còn trống. Phép kiểm âm A4 thử đúng "
        "dòng số 5 trong dữ liệu phát sẵn."
    )


def test_pgaudit_bat_o_muc_doi_tuong(bai_lam):
    """Bật pgaudit là hai việc ở hai tệp, và cả hai đều im lặng khi làm sai.

    Đặt tên phần mở rộng vào shared_preload_libraries là việc lúc khởi động; quên
    nó thì máy chủ vẫn chạy, chỉ là không ghi gì. Chọn mức đối tượng thay vì ghi
    tất cả là một quyết định vận hành, và mục 4.4 nói vì sao: nhật ký ghi tất cả
    sẽ bị tắt vào ngày có người nhìn hóa đơn lưu trữ.
    """
    cau_hinh = doc_cau_hinh_may_chu()
    if not cau_hinh:
        pytest.fail("Không thấy csdl/pgaudit.conf, hoặc tệp rỗng sau khi bỏ chú thích.")

    thieu = []
    if not co(r"shared_preload_libraries\s*=\s*'[^']*pgaudit", cau_hinh):
        thieu.append(
            "shared_preload_libraries chưa có pgaudit, nên phần mở rộng không được nạp "
            "lúc khởi động và không câu truy vấn nào bị ghi"
        )

    khop = re.search(r"pgaudit\.role\s*=\s*'([^']+)'", cau_hinh, flags=re.IGNORECASE)
    if not khop:
        thieu.append(
            "chưa đặt pgaudit.role, tức là chưa chọn mức đối tượng; đề bài đòi mức đối "
            "tượng chứ không đòi ghi tất cả"
        )
    vai_danh_dau = khop.group(1) if khop else VAI_TRO_DANH_DAU

    if co(r"pgaudit\.log\s*=\s*'all'", cau_hinh):
        thieu.append(
            "pgaudit.log đặt bằng 'all', tức ghi mọi câu của mọi phiên; đó là lựa chọn "
            "mục 4.4 cảnh báo, và nó làm pgaudit.role thành thừa"
        )

    if khop:
        if not co(rf"CREATE\s+ROLE\s+{re.escape(vai_danh_dau)}\b", bai_lam):
            thieu.append(f"chưa dựng vai trò đánh dấu {vai_danh_dau} trong SQL")
        if co(rf"CREATE\s+ROLE\s+{re.escape(vai_danh_dau)}\b[^;]*\bLOGIN\b", bai_lam):
            thieu.append(
                f"vai trò đánh dấu {vai_danh_dau} nối vào được; nó chỉ là cái nhãn, và "
                "một tài khoản thừa nào cũng là một đường vào"
            )
        if not co(rf"GRANT[^;]*\b{BANG_NHAY_CAM}\b[^;]*TO[^;]*\b{re.escape(vai_danh_dau)}\b", bai_lam):
            thieu.append(
                f"chưa cấp quyền đọc bảng {BANG_NHAY_CAM} cho {vai_danh_dau}, nên không "
                "câu nào chạm tới bảng ấy bị ghi lại"
            )
    assert not thieu, "Phần lưu vết chưa đạt:\n  - " + "\n  - ".join(thieu)
