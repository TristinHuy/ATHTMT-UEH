"""Kiểm tệp preflight, tức bằng chứng rằng máy của bạn dựng nổi môi trường.

Hai phép kiểm, và cả hai tồn tại vì cùng một rủi ro: sinh viên không dựng được
môi trường rồi phát hiện ra điều đó vào đúng hôm nộp bài. Buổi này cần Docker cho
bốn thứ không thay thế được bằng cách khác, gồm ứng dụng huấn luyện, hai lần quét
nền, và lần quét mã. Bảy phép kiểm nhóm lỗ hổng thì chạy được không cần Docker,
nên máy hỏng phần container vẫn tự kiểm được phần vá, và đó là chủ ý của thiết kế
chứ không phải sự may mắn.
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
            f"Không thấy {PREFLIGHT.relative_to(ROOT)}. Chạy `make preflight` rồi commit tệp đó. "
            "Tệp này nói về máy bạn dùng thật, nên bản phát của lab cố ý không mang sẵn nó."
        )
    return PREFLIGHT.read_text(encoding="utf-8")


def test_ghi_du_cac_muc(noi_dung):
    """Bốn dòng, và mỗi dòng trả lời một câu hỏi khác nhau của người chấm.

    Kiến trúc CPU có mặt vì ảnh của ứng dụng huấn luyện và ảnh của bộ quét không
    phải lúc nào cũng có bản cho mọi kiến trúc; một lần chạy chậm bất thường trên
    máy dùng chip ARM thường là do lớp mô phỏng chứ không do bài.
    """
    thieu = [ten for khoa, ten in BAT_BUOC.items() if khoa not in noi_dung]
    assert not thieu, "Preflight thiếu: " + ", ".join(thieu) + ". Chạy lại `make preflight`."


def test_may_dung_duoc_docker(noi_dung):
    """Hai hỏng khác nhau, hai cách chữa khác nhau, nên thông điệp nói cả hai.

    Chưa cài thì phải cài; cài rồi mà daemon chưa chạy thì chỉ cần bật lên. Gộp
    hai tình huống vào một phép kiểm là chủ ý: cả hai đều dẫn tới cùng một hệ quả,
    là không lần quét nào của bài chạy được, và sinh viên cần biết điều đó sớm chứ
    không cần biết nó dưới dạng hai dòng đỏ.
    """
    if "phien ban Docker: KHONG CO" in noi_dung:
        pytest.fail(
            "Máy chưa cài Docker. Ứng dụng huấn luyện, hai lần quét nền và lần quét mã "
            "của bài đều chạy trong container, nên không có Docker thì bốn hiện vật bằng "
            "chứng không sinh ra được. Báo giảng viên chậm nhất hai ngày trước buổi S7, "
            "vì buổi S7 lấy nhật ký của buổi này làm đầu vào."
        )
    assert "docker daemon: KHONG CHAY" not in noi_dung, (
        "Docker đã cài nhưng daemon chưa chạy. Trên Windows và macOS thì mở Docker Desktop "
        "và đợi biểu tượng cá voi chuyển sang trạng thái đang chạy. Trên Linux thì chạy "
        "`sudo systemctl start docker`. Chạy lại `make preflight` sau đó, vì tệp preflight "
        "ghi trạng thái tại thời điểm nó được sinh ra."
    )
