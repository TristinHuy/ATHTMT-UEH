"""Kiểm tám bằng chứng truy vấn, và ba hiện vật đi kèm.

Đây là bậc bằng chứng nặng nhất của bài. Năm phép kiểm âm chứng minh mỗi vai trò
KHÔNG làm được việc nó không được phép, và ba phép kiểm dương chứng minh bạn siết
mà hệ thống vẫn dùng được. Thiếu vế thứ hai thì cách đạt điểm rẻ nhất là thu sạch
quyền của mọi vai trò, và khi ấy bài an toàn đúng theo nghĩa nó không còn dùng
được.

Phán quyết trong tám tệp kết quả do `bin/ghi-truy-van.sh` sinh ra, tính từ mã
thoát của psql và từ thông điệp của máy chủ. Sửa tay một tệp kết quả là gian lận
học thuật, không phải mẹo vặt; thang chấm nói rõ mức xử lý.
"""
from __future__ import annotations

import pytest

from tro_giup import BANG_NHAY_CAM, EVID, ROOT, doc_ket_qua

# Mỗi phép kiểm âm phải bị chặn ở ĐÚNG lớp phòng thủ mà nó sinh ra để hỏi. Một
# câu bị chặn nhầm lớp vẫn là một câu bị chặn, nhưng nó chứng minh một điều khác
# với điều đề bài hỏi, nên bảng dưới đây giữ cả lớp lẫn lý do.
AM = {
    "A1": ("LOI_QUYEN", "bao_cao",
           "vai trò báo cáo không có quyền nào trên bảng gốc, nên câu này phải dừng ở lớp cấp quyền"),
    "A2": ("KHONG_DONG", "ung_dung",
           "cửa vào bảng mở, nhưng chính sách mức hàng phải lọc sạch dòng của người khác"),
    "A3": ("LOI_CHINH_SACH", "ung_dung",
           "vế WITH CHECK phải chặn việc ghi một dòng mang tên người khác"),
    "A4": ("LOI_RANG_BUOC", "duyet_chi",
           "ràng buộc người tạo khác người duyệt phải chặn việc tự duyệt dòng mình tạo"),
    "A5": ("KHONG_DONG", "chu_luoc_do",
           "FORCE ROW LEVEL SECURITY phải áp chính sách cho cả chủ sở hữu bảng"),
}

DUONG = {
    "D1": ("ung_dung", "ứng dụng phải đọc được đề nghị chi của chính nó"),
    "D2": ("ung_dung", "ứng dụng phải tạo được đề nghị chi mang tên chính nó"),
    "D3": ("bao_cao", "vai trò báo cáo phải đọc được khung nhìn thống kê"),
}

KHOA_BAT_BUOC = ["ma", "loai", "vai_tro", "mo_ta", "lenh", "mong_doi", "thuc_te", "ma_thoat", "nhat_ky_tho"]

BANG_VAI_TRO = ROOT / "docs" / "bang-vai-tro.md"
DANH_DOI = ROOT / "docs" / "danh-doi.md"
IT_NHAT_TU, NHIEU_NHAT_TU = 120, 300


def test_preflight_ghi_du_va_may_chay_duoc():
    """Rủi ro lớn nhất của học phần không phải bài khó, mà là người học không
    dựng nổi môi trường và phát hiện ra điều đó quá muộn."""
    tep = EVID / "preflight.txt"
    if not tep.exists():
        pytest.fail("Không thấy evidence/S4/preflight.txt. Chạy `make preflight` rồi commit tệp đó.")
    noi_dung = tep.read_text(encoding="utf-8")
    thieu = [
        ten for ten in ("kien truc CPU", "phien ban Python", "phien ban Docker", "docker daemon")
        if ten not in noi_dung
    ]
    assert not thieu, "Preflight thiếu: " + ", ".join(thieu) + ". Chạy lại `make preflight`."
    assert "docker daemon: KHONG CHAY" not in noi_dung, (
        "Docker đã cài nhưng daemon chưa chạy, nên máy chủ cơ sở dữ liệu không lên được và "
        "tám phép kiểm truy vấn không chạy được. Trên Windows và macOS thì mở Docker Desktop "
        "và đợi biểu tượng cá voi chuyển sang trạng thái đang chạy. Trên Linux thì chạy "
        "`sudo systemctl start docker`."
    )


def test_tam_ket_qua_deu_co_va_dung_dinh_dang():
    """Thiếu một trong tám thì bài chưa nói được điều nó tuyên bố, và một tệp kết
    quả không có nhật ký thô đi kèm thì người chấm không đọc lại được lần chạy
    ấy."""
    hong = []
    for ma in (*AM, *DUONG):
        tep = EVID / f"kiem-{ma}.txt"
        if not tep.exists():
            hong.append(f"{ma}: chưa có evidence/S4/kiem-{ma}.txt.")
            continue
        ket_qua = doc_ket_qua(tep)
        thieu = [k for k in KHOA_BAT_BUOC if k not in ket_qua]
        if thieu:
            hong.append(f"{ma}: tệp kết quả thiếu khóa {', '.join(thieu)}.")
            continue
        tho = ROOT / ket_qua["nhat_ky_tho"]
        if not tho.exists() or len(tho.read_bytes()) < 40:
            hong.append(f"{ma}: nhật ký thô {ket_qua['nhat_ky_tho']} không có hoặc rỗng.")
    assert not hong, (
        "Bằng chứng chưa đủ:\n  " + "\n  ".join(hong)
        + "\nChạy `make up`, `make defend`, rồi `make tam-truy-van`."
    )


def test_nam_truy_van_am_bi_chan_dung_lop():
    """Phép kiểm nặng nhất của cả bài.

    Nó không hỏi năm câu ấy có bị chặn hay không, nó hỏi chúng bị chặn Ở ĐÂU. Một
    câu bị từ chối quyền trong khi đề bài chờ nó bị chính sách mức hàng lọc nghĩa
    là bạn siết đúng nhưng siết nhầm lớp, và lớp bạn định thử vẫn chưa được chứng
    minh là đang bật. Đây cũng là chỗ phân biệt một bài hiểu việc với một bài thu
    hết quyền cho xong.
    """
    hong = []
    for ma, (mong_doi, vai_tro, y_nghia) in AM.items():
        tep = EVID / f"kiem-{ma}.txt"
        if not tep.exists():
            hong.append(f"{ma}: chưa chạy.")
            continue
        ket_qua = doc_ket_qua(tep)
        if ket_qua.get("loai") != "am":
            hong.append(f"{ma}: ghi loại {ket_qua.get('loai')!r}, phải là 'am'.")
        if ket_qua.get("vai_tro") != vai_tro:
            hong.append(f"{ma}: chạy bằng vai trò {ket_qua.get('vai_tro')!r}, phải là {vai_tro!r}.")
        if ket_qua.get("mong_doi") != mong_doi:
            hong.append(f"{ma}: mong đợi bị đổi thành {ket_qua.get('mong_doi')!r}, phải là {mong_doi!r}.")
        thuc_te = ket_qua.get("thuc_te")
        if thuc_te != mong_doi:
            hong.append(
                f"{ma}: thực tế {thuc_te!r}, đáng lẽ {mong_doi!r}, vì {y_nghia}. "
                f"Đọc {ket_qua.get('nhat_ky_tho', 'nhật ký thô')} trước khi sửa."
            )
    assert not hong, "Năm phép kiểm âm chưa nói được điều cần nói:\n  " + "\n  ".join(hong)


def test_ba_truy_van_duong_van_chay_duoc():
    """Ba phép này giữ cho bài nằm lại phía đúng của lằn ranh.

    Đặc quyền tối thiểu không phải là ít quyền nhất có thể, mà là đủ quyền để làm
    đúng việc của mình và không hơn. Một hệ thống không ai dùng được cũng vi phạm
    nguyên lý ấy, chỉ là nó vi phạm ở phía ít ai để ý.
    """
    hong = []
    for ma, (vai_tro, y_nghia) in DUONG.items():
        tep = EVID / f"kiem-{ma}.txt"
        if not tep.exists():
            hong.append(f"{ma}: chưa chạy.")
            continue
        ket_qua = doc_ket_qua(tep)
        if ket_qua.get("vai_tro") != vai_tro:
            hong.append(f"{ma}: chạy bằng vai trò {ket_qua.get('vai_tro')!r}, phải là {vai_tro!r}.")
        if ket_qua.get("thuc_te") != "CHAY_DUOC":
            hong.append(
                f"{ma}: thực tế {ket_qua.get('thuc_te')!r}, đáng lẽ 'CHAY_DUOC', vì {y_nghia}. "
                "Bạn đã siết quá tay ở đúng chỗ này."
            )
    assert not hong, "Ba phép kiểm dương cho thấy hệ thống đã siết quá tay:\n  " + "\n  ".join(hong)


def test_nhat_ky_pgaudit_co_vet_cua_bang_nhay_cam():
    """Phần lưu vết chỉ đáng tin khi có người đọc thử nó một lần.

    Phép này đọc nhật ký máy chủ đã lọc, tìm dấu vết của bảng nhạy cảm. Nó KHÔNG
    kiểm được nội dung nhật ký đúng tới đâu, vì pgaudit ghi câu hỏi chứ không ghi
    câu trả lời; nó chỉ chứng minh phần mở rộng đã được nạp thật và đã thấy thật
    một câu chạm tới bảng ấy.
    """
    tep = EVID / "pgaudit.txt"
    if not tep.exists():
        pytest.fail(
            "Không thấy evidence/S4/pgaudit.txt. Chạy `make defend`, rồi `make tam-truy-van` "
            "và `make suy-luan` để sinh ra vài câu truy vấn, rồi `make export-evidence`."
        )
    noi_dung = tep.read_text(encoding="utf-8")
    assert "AUDIT" in noi_dung.upper(), (
        "Tệp nhật ký không có dòng AUDIT nào. Thường là vì pgaudit chưa được nạp lúc khởi "
        "động: kiểm shared_preload_libraries trong csdl/pgaudit.conf, rồi `make defend` để "
        "khởi động lại máy chủ."
    )
    assert BANG_NHAY_CAM in noi_dung, (
        f"Nhật ký có dòng AUDIT nhưng không dòng nào nhắc tới bảng {BANG_NHAY_CAM}. Vai trò "
        "đánh dấu chưa được cấp quyền trên bảng ấy, nên mức đối tượng chưa phủ tới nó."
    )


def test_bang_vai_tro_du_dong_va_co_cot_suy_luan():
    """Bảng vai trò là chỗ bài này bắt bạn viết ra thứ máy không đo được.

    Cột cuối, cột ghi vai trò ấy SUY RA được gì mà nó không được đọc thẳng, là
    cột đắt nhất, vì nó hỏi đúng khoảng lệch giữa kiểm soát truy nhập và kiểm
    soát suy luận ở mục 4.2. Máy chỉ đếm được rằng cột ấy tồn tại và có đủ dòng.
    Nội dung do người chấm đọc.
    """
    if not BANG_VAI_TRO.exists():
        pytest.fail(
            "Không thấy docs/bang-vai-tro.md. Đề yêu cầu một bảng, mỗi dòng một vai trò, "
            "kèm cột ghi vai trò ấy suy ra được gì mà nó không được đọc thẳng."
        )
    noi_dung = BANG_VAI_TRO.read_text(encoding="utf-8")
    thieu_vai = [v for v in ("chu_luoc_do", "ung_dung", "duyet_chi", "bao_cao") if v not in noi_dung]
    assert not thieu_vai, "Bảng vai trò thiếu dòng cho: " + ", ".join(thieu_vai)
    assert "suy ra" in noi_dung.lower(), (
        "Bảng vai trò chưa có cột suy luận. Tiêu đề cột phải nói rõ nó ghi thứ vai trò ấy "
        "SUY RA được mà không được đọc thẳng, vì đó là phần mục 4.2 hỏi tới."
    )
    so_dong = [d for d in noi_dung.splitlines() if d.strip().startswith("|") and d.count("|") >= 3]
    assert len(so_dong) >= 6, (
        f"Bảng mới có {len(so_dong)} dòng kể cả dòng tiêu đề. Cần bốn vai trò, một dòng tiêu "
        "đề và một dòng phân cách, tức tối thiểu sáu dòng."
    )


def test_doan_danh_doi_co_va_dung_do_dai():
    """Phép xấp xỉ, và nói thẳng ra là xấp xỉ.

    Máy đếm được số từ, máy không đọc được một lập luận có sắc hay không. Phép này
    chỉ chặn hai thứ: không nộp, và nộp một đoạn quá ngắn tới mức không thể chứa
    một lựa chọn kèm lý do. Chất lượng lập luận do người chấm đọc theo rubric, và
    một đoạn qua được phép kiểm này vẫn mất điểm nếu nó chỉ kể lại việc đã làm.
    """
    if not DANH_DOI.exists():
        pytest.fail(
            "Không thấy docs/danh-doi.md. Đề yêu cầu một đoạn không quá ba trăm chữ: nếu đơn "
            "vị bạn chỉ có ba người thì bạn bỏ phép tách nhiệm vụ nào, bù bằng gì, và con số "
            "hòa vốn là bao nhiêu."
        )
    chu = [t for t in DANH_DOI.read_text(encoding="utf-8").split() if not t.startswith("#")]
    assert IT_NHAT_TU <= len(chu) <= NHIEU_NHAT_TU, (
        f"docs/danh-doi.md dài {len(chu)} từ, cần từ {IT_NHAT_TU} tới {NHIEU_NHAT_TU} từ."
    )
