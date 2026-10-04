"""Ba phép kiểm đọc bằng chứng bạn nộp, không đọc lời khai của bạn.

Phần này khác hẳn hai tệp kiểm trước. Ở đó bộ chấm tự dựng thẻ nên nó đo được
trực tiếp; ở đây nó chỉ đọc lại dấu vết của những lần gọi thật đã xảy ra trên
máy bạn. Vì vậy nó kiểm được rằng sáu lần gọi ĐÃ chạy và cho đúng phán quyết, và
nó không kiểm được rằng bạn đã suy nghĩ. Phần sau do người chấm đọc theo rubric.
"""
from __future__ import annotations

import pytest

from tro_giup import EVID, ROOT, doc_ket_qua

MONG_DOI = {
    "P1": ("duong", "DUOC_NHAN", "thẻ thật, đúng thân khách, đúng đơn vị, thì phải qua"),
    "N1": ("am", "BI_TU_CHOI", "thẻ khai thuật toán rỗng, CWE-347"),
    "N2": ("am", "BI_TU_CHOI", "thẻ ký bằng khóa khác, CWE-347"),
    "N3": ("am", "BI_TU_CHOI", "thẻ thật nhưng đã quá hạn, CWE-613"),
    "N4": ("am", "BI_TU_CHOI", "thẻ thật nhưng phát cho thân khách khác, CWE-863"),
    "N5": ("am", "BI_TU_CHOI", "danh tính hợp lệ nhưng vượt phạm vi đơn vị, CWE-863"),
}
KHOA_BAT_BUOC = ["ma", "loai", "mo_ta", "mong_doi", "thuc_te", "ma_http", "nhat_ky_tho"]

DANH_DOI = ROOT / "docs" / "danh-doi.md"
IT_NHAT_TU, NHIEU_NHAT_TU = 120, 300


def test_preflight_ghi_du_va_may_chay_duoc():
    """Rủi ro lớn nhất của học phần không phải bài khó, mà là sinh viên không dựng
    nổi môi trường rồi phát hiện ra điều đó quá muộn. Bài này cần Docker cho phần
    bằng chứng, nên preflight hỏi thẳng trạng thái của nó."""
    tep = EVID / "preflight.txt"
    if not tep.exists():
        pytest.fail("Không thấy evidence/S5/preflight.txt. Chạy `make preflight` rồi commit tệp đó.")
    noi_dung = tep.read_text(encoding="utf-8")
    thieu = [
        ten for ten in ("kien truc CPU", "phien ban Python", "phien ban Docker", "docker daemon")
        if ten not in noi_dung
    ]
    assert not thieu, "Preflight thiếu: " + ", ".join(thieu) + ". Chạy lại `make preflight`."
    assert "phien ban Docker: KHONG CO" not in noi_dung, (
        "Máy chưa cài Docker. Vùng định danh, dịch vụ và sáu lần gọi của bài đều chạy trong container."
    )
    assert "docker daemon: KHONG CHAY" not in noi_dung, (
        "Docker đã cài nhưng daemon chưa chạy, nên `make nam-phep-kiem` không sinh được bằng chứng nào. "
        "Trên Windows và macOS thì mở Docker Desktop và đợi biểu tượng cá voi chuyển sang trạng thái "
        "đang chạy. Trên Linux thì chạy `sudo systemctl start docker`."
    )


def test_sau_phep_kiem_du_va_dung_nhu_mong_doi():
    """Phép kiểm nặng nhất của phần bằng chứng.

    Năm chiều âm chứng minh dịch vụ từ chối đúng năm loại thẻ mà nó phải từ chối,
    và chiều dương chứng minh nó vẫn phục vụ người có quyền. Thiếu chiều dương
    thì năm chiều âm không nói gì: một dịch vụ chết cũng từ chối đủ năm lần.

    Phán quyết đọc từ mã HTTP thật do bin/nam-phep-kiem.py ghi lại, kèm nhật ký
    thô để người chấm đọc lại được. Gõ tay một dòng thuc_te là làm giả bằng
    chứng, không phải mẹo vặt, và rubric.md nói rõ mức xử lý."""
    hong = []
    for ma, (loai, mong_doi, y_nghia) in MONG_DOI.items():
        tep = EVID / f"kiem-{ma}.txt"
        if not tep.exists():
            hong.append(f"{ma}: chưa có evidence/S5/kiem-{ma}.txt.")
            continue
        ket_qua = doc_ket_qua(tep)
        thieu = [k for k in KHOA_BAT_BUOC if k not in ket_qua]
        if thieu:
            hong.append(f"{ma}: tệp kết quả thiếu khóa {', '.join(thieu)}.")
            continue
        tho = ROOT / ket_qua["nhat_ky_tho"]
        if not tho.exists() or len(tho.read_bytes()) < 20:
            hong.append(f"{ma}: nhật ký thô {ket_qua['nhat_ky_tho']} không có hoặc rỗng.")
        if ket_qua.get("loai") != loai:
            hong.append(f"{ma}: ghi loại {ket_qua.get('loai')!r}, phải là {loai!r}.")
        if ket_qua.get("mong_doi") != mong_doi:
            hong.append(f"{ma}: mong đợi bị đổi thành {ket_qua.get('mong_doi')!r}, phải là {mong_doi!r}.")
        if ket_qua.get("thuc_te") != mong_doi:
            hong.append(
                f"{ma}: thực tế {ket_qua.get('thuc_te')!r}, đáng lẽ {mong_doi!r}, vì {y_nghia}. "
                f"Đọc {ket_qua.get('nhat_ky_tho', 'nhật ký thô')} trước khi sửa."
            )
    assert not hong, (
        "Sáu phép kiểm chưa nói được điều cần nói:\n  " + "\n  ".join(hong)
        + "\nChạy `make up`, `make defend`, rồi `make nam-phep-kiem`."
    )


def test_hai_hien_vat_van_ban_co_va_du_do_dai():
    """Phép xấp xỉ, và nói thẳng ra là xấp xỉ.

    Máy đếm được số từ và tìm được một con số có đơn vị; máy không đọc được một
    lập luận có sắc hay không. Phép này chặn hai thứ: không nộp, và nộp một đoạn
    ngắn tới mức không thể chứa một lựa chọn kèm lý do. Một đoạn qua được phép
    kiểm này vẫn mất điểm ở rubric nếu nó chỉ kể lại việc đã làm."""
    hong = []

    do_argon2 = EVID / "do-argon2.txt"
    if not do_argon2.exists():
        hong.append(
            "chưa có evidence/S5/do-argon2.txt. Chạy `make do-argon2 NHAN=truoc-khi-doi`, "
            "đổi tham số, rồi chạy lại với NHAN=sau-khi-doi."
        )
    else:
        dong = [d for d in do_argon2.read_text(encoding="utf-8").splitlines() if d.strip()]
        if len(dong) < 2:
            hong.append(
                f"do-argon2.txt mới có {len(dong)} lần đo. Cần hai lần, trước và sau khi đổi tham số, "
                "vì phép đo này chỉ nói được điều gì khi so hai lần với nhau."
            )

    if not DANH_DOI.exists():
        hong.append(
            "chưa có docs/danh-doi.md. Đề yêu cầu một đoạn từ 120 tới 300 chữ trả lời hai câu: "
            "sau khi thu hồi quyền thì thẻ đã phát còn dùng được bao lâu theo đồng hồ, và muốn rút "
            "con số ấy xuống một phần mười thì phải trả giá bằng gì."
        )
    else:
        chu = [t for t in DANH_DOI.read_text(encoding="utf-8").split() if not t.startswith("#")]
        if not IT_NHAT_TU <= len(chu) <= NHIEU_NHAT_TU:
            hong.append(f"docs/danh-doi.md dài {len(chu)} từ, cần từ {IT_NHAT_TU} tới {NHIEU_NHAT_TU} từ.")

    assert not hong, "Hai hiện vật văn bản chưa đạt:\n  " + "\n  ".join(hong)
