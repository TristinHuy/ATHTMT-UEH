"""Kiểm tệp compose của chính bạn, trước khi kiểm bất cứ thứ gì bạn cấu hình.

Bốn phép kiểm ở đây không đo kiến thức về giám sát. Chúng cưỡng chế văn bản phạm
vi cho phép và trần thiết kế của học phần. Một văn bản phạm vi mà không ai kiểm
thì chỉ là một lời hứa, nên chỗ kiểm nó nằm ngay đây, trong bộ chấm.

Phép thứ tư là phép riêng của buổi bảy, và nó đo đúng bài học của mục 7.3.
"""
from __future__ import annotations

import pytest

from tro_giup import COMPOSE, ROOT, TRAN_CONTAINER, doc_yaml


@pytest.fixture(scope="module")
def compose() -> dict:
    return doc_yaml(COMPOSE, "Bài lab phải có tệp này.")


def dich_vu(compose: dict) -> dict:
    return compose.get("services") or {}


def test_moi_anh_ghim_theo_phien_ban_cu_the(compose):
    """Một thẻ trôi nổi làm hai lần chạy cách nhau vài tuần đứng trên hai ảnh khác
    nhau mà không ai biết. Digest là mức ghim đúng; một thẻ phiên bản cụ thể là
    mức chấp nhận được khi máy chưa kéo được ảnh để lấy digest."""
    hong = []
    for ten, than in dich_vu(compose).items():
        anh = (than or {}).get("image")
        if not anh:
            if (than or {}).get("build"):
                continue
            hong.append(f"{ten}: không khai báo image.")
            continue
        if "@sha256:" in anh:
            continue
        if ":" not in anh:
            hong.append(f"{ten}: {anh} không có thẻ, tức là ngầm dùng latest.")
        elif anh.rsplit(":", 1)[1] in {"latest", "stable", "main", "nightly", ""}:
            hong.append(f"{ten}: {anh} dùng thẻ trôi nổi.")
    assert not hong, (
        "Ảnh chưa ghim đúng mức:\n  " + "\n  ".join(hong)
        + "\nChạy `bash ghim-digest.sh --sua` trên máy có mạng để thay thẻ bằng digest."
    )


def test_khong_mo_cong_qua_rong_va_khong_xin_dac_quyen(compose):
    """Kho nhật ký là thứ người chiếm được máy tìm tới sớm nhất, nên bài này không
    mở cổng nào cho nó. Ngoại lệ duy nhất là Grafana, vì nó cần trình duyệt, và
    ngoại lệ ấy chỉ được neo vào 127.0.0.1: mở về mọi giao diện nghĩa là bảng
    điều khiển nhật ký của bạn nghe cả trên mạng Wi-Fi bạn đang ngồi."""
    hong = []
    for ten, than in dich_vu(compose).items():
        than = than or {}
        for cong in than.get("ports") or []:
            mo_ta = cong if isinstance(cong, str) else str(cong)
            if isinstance(cong, dict):
                dia_chi = cong.get("host_ip", "")
            else:
                phan = mo_ta.split(":")
                dia_chi = phan[0] if len(phan) >= 3 else ""
            if dia_chi != "127.0.0.1":
                hong.append(f"{ten}: cổng {mo_ta} không neo vào 127.0.0.1.")
        if than.get("privileged"):
            hong.append(f"{ten}: privileged: true.")
        if str(than.get("network_mode", "")).strip() == "host":
            hong.append(f"{ten}: network_mode: host, tức đứng thẳng vào mạng máy thật.")
        for quyen in than.get("cap_add") or []:
            hong.append(f"{ten}: cap_add {quyen}, đề bài không cấp quyền nào.")
        if than.get("pid") == "host" or than.get("ipc") == "host":
            hong.append(f"{ten}: dùng chung không gian tên với máy thật.")
    assert not hong, (
        "Ra ngoài phạm vi cho phép:\n  " + "\n  ".join(hong)
        + "\nĐọc lại SCOPE.md, rồi sửa docker-compose.yml."
    )


def test_khong_vuot_tran_bon_container(compose):
    """Trần bốn container là ràng buộc thiết kế, không phải gợi ý.

    Nó có mặt vì lớp học dùng laptop cá nhân, không có phòng máy dự phòng, và một
    bài chỉ chạy được trên máy mạnh là một bài đã hỏng với phần lớn lớp. Buổi bảy
    là buổi dễ vượt trần nhất, vì mọi công cụ giám sát đều mời bạn thêm một tầng.
    ADR-0003 đã cắt Wazuh, Falco và osquery đúng vì lý do đó, và mục 7.2 của giáo
    trình nói thẳng rằng cài xong mà chưa biết mình muốn hỏi gì thì bạn chỉ có
    một cỗ máy bận rộn."""
    ten = sorted(dich_vu(compose))
    assert len(ten) <= TRAN_CONTAINER, (
        f"Tệp compose khai {len(ten)} dịch vụ, vượt trần {TRAN_CONTAINER} của ADR-0003 mục N3: "
        + ", ".join(ten)
    )


def test_nguon_nhat_ky_gan_o_che_do_chi_doc(compose):
    """Chặng đọc nhật ký không được quyền sửa nhật ký.

    Đây là phép kiểm riêng của buổi bảy, và nó đo đúng hình ảnh ở mục 7.3: người
    bị đo mà cầm luôn cái thước. Promtail phải đọc được thư mục nguồn và không
    được ghi vào đó. Kho giữ thì không cần thấy thư mục nguồn chút nào, vì việc
    của nó bắt đầu sau khi dòng chữ đã rời khỏi nơi sinh ra."""
    dv = dich_vu(compose)
    hong = []

    def gan(ten: str) -> list[str]:
        return [str(g) for g in (dv.get(ten) or {}).get("volumes") or []]

    doc_nguon = [g for g in gan("promtail") if "./nhat-ky" in g]
    if not doc_nguon:
        hong.append("promtail không gắn thư mục ./nhat-ky, nên nó không có gì để đọc.")
    for g in doc_nguon:
        if not g.rstrip().endswith(":ro"):
            hong.append(
                f"promtail gắn {g} mà không có :ro. Chặng chuyển ghi được vào nguồn "
                "nghĩa là nó vừa chuyển tin vừa sửa được tin."
            )
    for g in gan("loki"):
        if "./nhat-ky" in g:
            hong.append(
                f"loki gắn {g}. Kho giữ không cần thấy thư mục nguồn, và cho nó thấy "
                "là xóa mất ranh giới giữa nơi sinh và nơi giữ."
            )
    assert not hong, "Ranh giới tin cậy chưa đúng:\n  " + "\n  ".join(hong)
