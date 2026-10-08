"""Kiểm tệp preflight, tức bằng chứng môi trường của sinh viên thật sự chạy.

Phép kiểm này tồn tại vì rủi ro lớn nhất của học phần không phải là bài khó, mà
là sinh viên không dựng nổi môi trường và phát hiện ra điều đó quá muộn. Riêng ở
buổi bảy, cái giá của việc phát hiện muộn cao hơn mọi buổi khác, vì bài này ăn
đầu vào từ năm buổi trước và không có cách nào làm bù trong một tối.
"""
from __future__ import annotations

import pytest

from tro_giup import PREFLIGHT, ROOT

BAT_BUOC = {
    "kien truc CPU": "kiến trúc CPU",
    "phien ban Python": "phiên bản Python",
    "phien ban Docker": "phiên bản Docker",
    "docker daemon": "trạng thái docker daemon",
}


@pytest.fixture(scope="module")
def noi_dung() -> str:
    if not PREFLIGHT.exists():
        pytest.fail(
            f"Không thấy {PREFLIGHT.relative_to(ROOT)}. Chạy `make preflight` rồi commit tệp đó."
        )
    return PREFLIGHT.read_text(encoding="utf-8")


def test_ghi_du_cac_muc(noi_dung):
    thieu = [ten for khoa, ten in BAT_BUOC.items() if khoa not in noi_dung]
    assert not thieu, "Preflight thiếu: " + ", ".join(thieu) + ". Chạy lại `make preflight`."


def test_docker_co_mat(noi_dung):
    dong = [d for d in noi_dung.splitlines() if d.startswith("phien ban Docker")]
    assert dong, "Preflight không có dòng phiên bản Docker."
    assert "KHONG CO" not in dong[0], (
        "Máy chưa cài Docker, nên chặng chuyển và kho nhật ký của bài này không dựng được. "
        "Báo giảng viên chậm nhất hai ngày trước buổi S8."
    )


def test_docker_daemon_chay(noi_dung):
    dong = [d for d in noi_dung.splitlines() if d.startswith("docker daemon")]
    assert dong, "Preflight không có dòng trạng thái docker daemon."
    assert "KHONG CHAY" not in dong[0], (
        "Docker đã cài nhưng daemon chưa chạy, nên không một phép đo nào của bài này "
        "thực hiện được. Trên Windows và macOS thì mở Docker Desktop và đợi biểu tượng "
        "cá voi chuyển sang trạng thái đang chạy. Trên Linux thì chạy "
        "`sudo systemctl start docker`."
    )
