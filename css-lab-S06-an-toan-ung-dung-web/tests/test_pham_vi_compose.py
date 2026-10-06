"""Kiểm tệp compose của chính bạn, trước khi kiểm bất cứ thứ gì bạn cấu hình.

Bốn phép kiểm ở đây không đo kiến thức về an toàn web. Chúng cưỡng chế văn bản
phạm vi cho phép và trần thiết kế của học phần. Một văn bản phạm vi mà không ai
kiểm thì chỉ là một lời hứa, nên chỗ kiểm nó nằm ngay đây, trong bộ chấm.

Phép thứ tư là phép riêng của buổi sáu, và nó là phép nghiêm khắc nhất trong cả
tám bài lab. Buổi này đặt vào tay bạn một bộ quét web. Một bộ quét trỏ nhầm địa
chỉ không phải là một lỗi gõ phím, nó là một hành vi nhắm vào máy của người khác,
và ranh giới ấy nằm ở chỗ bạn có được phép hay không chứ không ở chỗ có gì hỏng
hay không.
"""
from __future__ import annotations

import re
from urllib.parse import urlparse

import pytest

from tro_giup import COMPOSE, DICH_VU_DUOC_QUET, MAKEFILE, TRAN_CONTAINER, doc_yaml

# Đích của một lần quét luôn đi sau cờ -t. Chỉ đọc đúng chỗ ấy, để câu `make up`
# in ra địa chỉ trình duyệt trong Makefile không bị bắt nhầm thành đích quét.
DICH_CO_LUOC_DO = re.compile(r"-t\s+(http[^\s\"';]+)")
DICH_KHONG_LUOC_DO = re.compile(r"-t\s+([A-Za-z0-9.-]+:\d+)(?:\s|$)")

# Hai tập lệnh quét chủ động của cùng bộ công cụ. Chúng gửi tải trọng thử, tức
# vượt ra ngoài chế độ nền, và ADR-0003 cắt chúng khỏi buổi này.
QUET_CHU_DONG = ("zap-full-scan.py", "zap-api-scan.py")


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
    """Buổi này dựng một ứng dụng cố ý để hở và một ứng dụng đầy lỗ hổng, cùng lúc,
    trên máy bạn đang ngồi. Cổng của chúng neo vào 127.0.0.1 nghĩa là chỉ máy bạn
    gọi được; mở về mọi giao diện nghĩa là bất cứ ai trong cùng mạng Wi-Fi đều gọi
    được, và khi ấy bạn vừa dựng đúng thứ mà bài học cấm."""
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
        for gan in than.get("volumes") or []:
            if "docker.sock" in str(gan):
                hong.append(
                    f"{ten}: gắn ổ cắm của Docker, tức trao quyền dựng container trên máy "
                    "thật cho tiến trình bên trong. Không việc nào của bài cần điều đó."
                )
    assert not hong, (
        "Ra ngoài phạm vi cho phép:\n  " + "\n  ".join(hong)
        + "\nĐọc lại SCOPE.md, rồi sửa docker-compose.yml."
    )


def test_khong_vuot_tran_bon_container(compose):
    """Trần bốn container là ràng buộc thiết kế, không phải gợi ý.

    Nó có mặt vì lớp học dùng laptop cá nhân, không có phòng máy dự phòng, và một
    bài chỉ chạy được trên máy mạnh là một bài đã hỏng với phần lớn lớp. Buổi này
    đã dùng hết bốn suất: ứng dụng huấn luyện, ứng dụng thử nghiệm, bộ quét nền,
    và chỗ đứng để quét mã. Thêm một dịch vụ nữa thì phải bỏ bớt một dịch vụ đang
    có, và ADR-0003 mục 2 đã cắt Trivy khỏi buổi này đúng theo cách ấy."""
    ten = sorted(dich_vu(compose))
    assert len(ten) <= TRAN_CONTAINER, (
        f"Tệp compose khai {len(ten)} dịch vụ, vượt trần {TRAN_CONTAINER} của ADR-0003 mục N3: "
        + ", ".join(ten)
    )


def test_dich_cua_bo_quet_chi_nam_trong_mang_compose():
    """Phép kiểm riêng của buổi này, và là phép cưỡng chế thẳng một dòng của SCOPE.md.

    Địa chỉ đích của bộ quét phải viết bằng TÊN DỊCH VỤ trong mạng compose, tức
    một cái tên chỉ phân giải được từ bên trong mạng ấy. Viết như vậy thì một lần
    gõ nhầm cũng không ra khỏi máy bạn. Viết bằng địa chỉ bên ngoài thì không có
    lớp nào chặn nữa, và hậu quả của một lần quét nhầm không nằm ở chỗ có gì hỏng
    hay không, mà ở chỗ bạn có được phép quét hệ thống ấy hay không.

    Phép này đọc cả tệp compose lẫn Makefile, vì đích có thể bị chuyển sang dòng
    lệnh cho tiện. Nó cũng chặn hai tập lệnh quét chủ động của cùng bộ công cụ:
    chúng gửi tải trọng thử, tức đã bước sang phần của học phần Kiểm thử thâm
    nhập, và ADR-0003 cắt chúng khỏi buổi này.
    """
    nguon = {"docker-compose.yml": COMPOSE.read_text(encoding="utf-8")}
    if MAKEFILE.exists():
        nguon["Makefile"] = MAKEFILE.read_text(encoding="utf-8")

    hong = []
    so_dich = 0
    for ten_tep, chu in nguon.items():
        for cong_cu in QUET_CHU_DONG:
            if cong_cu in chu:
                hong.append(
                    f"{ten_tep}: gọi {cong_cu}, tức quét chủ động. Buổi này chỉ quét NỀN, "
                    "và phần quét chủ động thuộc học phần Kiểm thử thâm nhập."
                )
        for dich in DICH_CO_LUOC_DO.findall(chu):
            so_dich += 1
            may = urlparse(dich).hostname or ""
            if may not in DICH_VU_DUOC_QUET:
                hong.append(
                    f"{ten_tep}: đích quét {dich} trỏ tới {may or 'một địa chỉ không đọc được'}, "
                    f"không phải tên dịch vụ trong mạng compose {sorted(DICH_VU_DUOC_QUET)}."
                )
        for dich in DICH_KHONG_LUOC_DO.findall(chu):
            so_dich += 1
            may = dich.rsplit(":", 1)[0]
            if may not in DICH_VU_DUOC_QUET:
                hong.append(
                    f"{ten_tep}: đích quét {dich} không phải tên dịch vụ trong mạng compose "
                    f"{sorted(DICH_VU_DUOC_QUET)}."
                )

    assert so_dich, (
        "Không tìm thấy đích quét nào trong docker-compose.yml. Dòng command của dịch vụ "
        "quét là chỗ duy nhất hợp lệ để đích ấy nằm, và bộ chấm đọc lại chính chỗ đó. "
        "Xóa nó đi thì `make quet` không sinh được hai tệp báo cáo mà bài đòi nộp."
    )
    assert not hong, "Bộ quét đang được trỏ ra ngoài phạm vi cho phép:\n  " + "\n  ".join(hong)
