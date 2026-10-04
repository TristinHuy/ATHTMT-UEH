"""Kiểm tệp compose của chính bạn, trước khi kiểm bất cứ thứ gì bạn cấu hình.

Ba phép kiểm ở đây không đo kiến thức về định danh. Chúng cưỡng chế văn bản phạm
vi cho phép và trần thiết kế của học phần: một bài lab chỉ được tác động trong
mạng compose của chính người làm, chỉ được dùng những quyền đã liệt kê trong đề,
và không được vượt trần bốn container. Một văn bản phạm vi mà không ai kiểm thì
chỉ là một lời hứa, nên chỗ kiểm nó nằm ngay đây, trong bộ chấm.
"""
from __future__ import annotations

import pytest
import yaml

from tro_giup import COMPOSE, ROOT, TRAN_CONTAINER


@pytest.fixture(scope="module")
def compose() -> dict:
    if not COMPOSE.exists():
        pytest.fail(f"Không thấy {COMPOSE.name} ở {ROOT}. Bài lab phải có tệp này.")
    try:
        return yaml.safe_load(COMPOSE.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as loi:
        pytest.fail(f"{COMPOSE.name} không phân giải được: {loi}")


def dich_vu(compose: dict) -> dict:
    return compose.get("services") or {}


def test_moi_anh_ghim_theo_phien_ban_cu_the(compose):
    """Một thẻ trôi nổi làm hai lần chạy cách nhau vài tuần đứng trên hai ảnh
    khác nhau mà không ai biết. Digest là mức ghim đúng; một thẻ phiên bản cụ thể
    là mức chấp nhận được khi máy chưa kéo được ảnh để lấy digest."""
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
    """Vùng định danh cần một cổng vì bạn phải mở trình duyệt để ghi danh yếu tố
    thứ hai, và đó là ngoại lệ DUY NHẤT của bài. Ngoại lệ ấy chỉ được neo vào
    127.0.0.1: mở về mọi giao diện nghĩa là máy chủ danh tính của bạn nghe cả
    trên mạng Wi-Fi bạn đang ngồi. Dịch vụ hồ sơ thì không cần cổng nào, vì mọi
    phép kiểm của bài đều đứng từ trong mạng compose."""
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
        + "\nĐọc lại SCOPE.md mục 4, rồi sửa docker-compose.yml."
    )


def test_khong_vuot_tran_bon_container(compose):
    """Trần bốn container là ràng buộc thiết kế, không phải gợi ý.

    Nó có mặt vì lớp học dùng laptop cá nhân, không có phòng máy dự phòng, và
    một bài chỉ chạy được trên máy mạnh là một bài đã hỏng với phần lớn lớp.
    Bản phát đi kèm ba dịch vụ. Nếu bạn thấy mình cần dịch vụ thứ năm thì gần
    như chắc chắn có một việc đang làm sai chỗ, và đó là lúc hỏi trên Discussions
    chứ không phải lúc thêm khối cấu hình."""
    ten = sorted(dich_vu(compose))
    assert len(ten) <= TRAN_CONTAINER, (
        f"Tệp compose khai {len(ten)} dịch vụ, vượt trần {TRAN_CONTAINER} của ADR-0003 mục N3: "
        + ", ".join(ten)
    )
