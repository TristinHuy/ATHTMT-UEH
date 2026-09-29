"""Kiểm bốn bằng chứng nối mạng, và hai hiện vật đi kèm.

Đây là bậc bằng chứng nặng nhất của §3.5: một phép kiểm xanh chỉ có nghĩa khi bạn
biết nó chuyển đỏ trong trường hợp nào. Bài này đòi bốn lần nối chia thành hai
lớp, mỗi lớp một chiều dương và một chiều âm, và hai chiều âm mới là chỗ chứng
minh lớp phòng thủ đang bật chứ không phải đang vắng mặt.

Phần bốn tệp kết quả do `make bon-phep-kiem` sinh ra, và phán quyết trong đó lấy
từ mã thoát cùng dấu hiệu trong đầu ra, không lấy từ lời khai. Sửa tay một tệp
kết quả là gian lận học thuật, không phải mẹo vặt; thang chấm nói rõ mức xử lý.
"""
from __future__ import annotations

import pytest

from tro_giup import EVID, ROOT, doc_ket_qua

MONG_DOI = {
    "K1": ("1", "THANH_CONG", "chứng thư máy chủ dựng ngược về CA nội bộ và tên khớp"),
    "K2": ("1", "BI_TU_CHOI", "gọi bằng một tên khác thì phép so tên phải chặn"),
    "K3": ("2", "THANH_CONG", "có trình chứng thư khách thì đọc được nội dung"),
    "K4": ("2", "BI_TU_CHOI", "không trình chứng thư khách thì phải bị từ chối"),
}

KHOA_BAT_BUOC = ["ma", "lop", "mo_ta", "lenh", "mong_doi", "thuc_te", "ma_thoat", "nhat_ky_tho"]

DANH_DOI = ROOT / "docs" / "danh-doi.md"
IT_NHAT_TU, NHIEU_NHAT_TU = 120, 300


def test_preflight_ghi_du_va_may_chay_duoc():
    """Rủi ro lớn nhất của học phần không phải bài khó, mà là sinh viên không dựng
    nổi môi trường và phát hiện ra điều đó quá muộn. Bài này cần cả Docker lẫn
    openssl, nên preflight hỏi cả hai."""
    tep = EVID / "preflight.txt"
    if not tep.exists():
        pytest.fail("Không thấy evidence/S3/preflight.txt. Chạy `make preflight` rồi commit tệp đó.")
    noi_dung = tep.read_text(encoding="utf-8")
    thieu = [
        ten
        for ten in ("kien truc CPU", "phien ban Python", "phien ban openssl", "phien ban Docker", "docker daemon")
        if ten not in noi_dung
    ]
    assert not thieu, "Preflight thiếu: " + ", ".join(thieu) + ". Chạy lại `make preflight`."
    assert "phien ban openssl: KHONG CO" not in noi_dung, (
        "Máy chưa có openssl. Bộ chứng thư của bài dựng bằng chính công cụ này."
    )
    assert "docker daemon: KHONG CHAY" not in noi_dung, (
        "Docker đã cài nhưng daemon chưa chạy, nên bốn phép kiểm nối mạng không chạy được. "
        "Trên Windows và macOS thì mở Docker Desktop và đợi biểu tượng cá voi chuyển sang "
        "trạng thái đang chạy. Trên Linux thì chạy `sudo systemctl start docker`."
    )


def test_bon_phep_kiem_deu_co_ket_qua_dung_dinh_dang():
    """Thiếu một trong bốn thì bài chưa chứng minh được cả hai lớp, và một tệp kết
    quả không có nhật ký thô đi kèm thì người chấm không đọc lại được lần nối ấy."""
    hong = []
    for ma in MONG_DOI:
        tep = EVID / f"kiem-{ma}.txt"
        if not tep.exists():
            hong.append(f"{ma}: chưa có evidence/S3/kiem-{ma}.txt.")
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
        + "\nChạy `make up`, `make defend`, rồi `make bon-phep-kiem`."
    )


def test_bon_ket_qua_dung_nhu_mong_doi():
    """Phép kiểm nặng nhất của cả bài.

    Hai chiều dương chứng minh hệ thống còn phục vụ được người có quyền. Hai chiều
    âm chứng minh nó từ chối đúng người không có quyền, và đó mới là điều một cấu
    hình an toàn phải nói được. Một bài chỉ có chiều dương thì mới chứng minh được
    rằng hệ thống chưa hỏng theo một kiểu, chưa chứng minh được rằng lớp phòng thủ
    đang bật.
    """
    hong = []
    for ma, (lop, mong_doi, y_nghia) in MONG_DOI.items():
        tep = EVID / f"kiem-{ma}.txt"
        if not tep.exists():
            hong.append(f"{ma}: chưa chạy.")
            continue
        ket_qua = doc_ket_qua(tep)
        if ket_qua.get("lop") != lop:
            hong.append(f"{ma}: ghi lớp {ket_qua.get('lop')!r}, phải là {lop!r}.")
        if ket_qua.get("mong_doi") != mong_doi:
            hong.append(f"{ma}: mong đợi bị đổi thành {ket_qua.get('mong_doi')!r}, phải là {mong_doi!r}.")
        if ket_qua.get("thuc_te") != mong_doi:
            hong.append(
                f"{ma}: thực tế {ket_qua.get('thuc_te')!r}, đáng lẽ {mong_doi!r}, vì {y_nghia}. "
                f"Đọc {ket_qua.get('nhat_ky_tho', 'nhật ký thô')} trước khi sửa."
            )
    assert not hong, "Bốn phép kiểm chưa nói được điều cần nói:\n  " + "\n  ".join(hong)


def test_doan_danh_doi_co_va_dung_do_dai():
    """Phép xấp xỉ, và nói thẳng ra là xấp xỉ.

    Máy đếm được số từ, máy không đọc được một lập luận có sắc hay không. Phép này
    chỉ chặn hai thứ: không nộp, và nộp một đoạn quá ngắn tới mức không thể chứa
    một lựa chọn kèm lý do. Chất lượng lập luận do người chấm đọc theo rubric, và
    một đoạn qua được phép kiểm này vẫn mất điểm nếu nó chỉ kể lại việc đã làm.
    """
    if not DANH_DOI.exists():
        pytest.fail(
            "Không thấy docs/danh-doi.md. Đề yêu cầu một đoạn không quá ba trăm chữ: "
            "nếu phải bỏ bớt một lớp phòng thủ vì chi phí vận hành thì bạn bỏ lớp nào, "
            "và bằng chứng nào cho thấy phần còn lại vẫn đứng."
        )
    chu = [t for t in DANH_DOI.read_text(encoding="utf-8").split() if not t.startswith("#")]
    assert IT_NHAT_TU <= len(chu) <= NHIEU_NHAT_TU, (
        f"docs/danh-doi.md dài {len(chu)} từ, cần từ {IT_NHAT_TU} tới {NHIEU_NHAT_TU} từ."
    )
