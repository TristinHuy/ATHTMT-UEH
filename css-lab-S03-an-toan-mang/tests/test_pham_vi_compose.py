"""Kiểm tệp compose của chính bạn, trước khi kiểm bất cứ thứ gì bạn cấu hình.

Ba phép kiểm ở đây không đo kiến thức về TLS. Chúng cưỡng chế văn bản phạm vi cho
phép: một bài lab của học phần này chỉ được tác động trong mạng compose của chính
người làm, và chỉ được dùng những quyền đã liệt kê trong đề. Văn bản phạm vi mà
không có ai kiểm thì chỉ là một lời hứa, nên chỗ kiểm nó nằm ngay đây, trong bộ
chấm, chứ không nằm ở lòng tin.
"""
from __future__ import annotations

import pytest

from tro_giup import ROOT

try:
    import yaml
except ImportError:  # pragma: no cover
    pytest.skip("Thiếu PyYAML, cài bằng: pip install pyyaml", allow_module_level=True)

COMPOSE = ROOT / "docker-compose.yml"


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
    """Một thẻ trôi nổi làm hai lần chạy cách nhau vài tuần nói về hai ảnh khác
    nhau mà không ai biết. Digest là mức ghim đúng; một thẻ phiên bản cụ thể là
    mức chấp nhận được khi máy chưa kéo được ảnh để lấy digest."""
    hong = []
    for ten, than in dich_vu(compose).items():
        anh = (than or {}).get("image")
        if not anh:
            hong.append(f"{ten}: không khai báo image.")
            continue
        if "@sha256:" in anh:
            continue
        if ":" not in anh:
            hong.append(f"{ten}: {anh} không có thẻ, tức là ngầm dùng latest.")
        elif anh.rsplit(":", 1)[1] in {"latest", "stable", "main", ""}:
            hong.append(f"{ten}: {anh} dùng thẻ trôi nổi.")
    assert not hong, (
        "Ảnh chưa ghim đúng mức:\n  " + "\n  ".join(hong)
        + "\nChạy `bash ghim-digest.sh` trên máy có mạng để thay thẻ bằng digest."
    )


def test_khong_mo_cong_ra_ngoai_may(compose):
    """Bốn phép kiểm của bài đều chạy từ trong mạng compose, nên không dịch vụ nào
    cần lộ ra máy thật. Mở một cổng chỉ để cho tiện là đúng loại cấu hình mà
    nguyên lý thứ tư nói tới, và nó cũng đưa dịch vụ ra ngoài phạm vi cho phép."""
    hong = []
    for ten, than in dich_vu(compose).items():
        for cong in (than or {}).get("ports") or []:
            mo_ta = cong if isinstance(cong, str) else str(cong)
            if isinstance(cong, dict):
                dia_chi = cong.get("host_ip", "")
            else:
                phan = mo_ta.split(":")
                dia_chi = phan[0] if len(phan) >= 3 else ""
            if dia_chi != "127.0.0.1":
                hong.append(f"{ten}: {mo_ta} không neo vào 127.0.0.1.")
    assert not hong, (
        "Cổng mở quá rộng:\n  " + "\n  ".join(hong)
        + "\nBỏ hẳn dòng ports, hoặc viết dạng 127.0.0.1:<cổng>:<cổng>."
    )


def test_khong_xin_dac_quyen(compose):
    """Đề bài không cho phép một quyền nào ngoài mặc định. Nếu bạn thấy mình phải
    thêm quyền để bài chạy được thì gần như chắc chắn bạn đang sửa sai chỗ, và đó
    là lúc hỏi trên Discussions chứ không phải lúc thêm cờ."""
    hong = []
    for ten, than in dich_vu(compose).items():
        than = than or {}
        if than.get("privileged"):
            hong.append(f"{ten}: privileged: true.")
        if str(than.get("network_mode", "")).strip() == "host":
            hong.append(f"{ten}: network_mode: host, tức là đứng thẳng vào mạng máy thật.")
        for quyen in than.get("cap_add") or []:
            hong.append(f"{ten}: cap_add {quyen}, đề bài không cấp quyền nào.")
        if than.get("pid") == "host" or than.get("ipc") == "host":
            hong.append(f"{ten}: dùng chung không gian tên với máy thật.")
    assert not hong, (
        "Xin quyền ngoài phạm vi cho phép:\n  " + "\n  ".join(hong)
        + "\nĐọc lại SCOPE.md, mục ràng buộc kỹ thuật."
    )
