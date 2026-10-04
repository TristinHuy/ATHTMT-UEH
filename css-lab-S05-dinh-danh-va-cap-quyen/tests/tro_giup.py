"""Phần dùng chung của bộ kiểm công khai lab S5.

Tệp này không chứa phép kiểm nào. Nó giữ bốn thứ mà năm tệp kiểm đều cần: chỗ
đứng của bài, cách nạp hai hàm bạn viết, cách đọc ba tệp cấu hình, và một xưởng
nhỏ để dựng thẻ.

Xưởng dựng thẻ là chỗ đáng nói. Bộ kiểm tự sinh một cặp khóa RSA rồi tự ký thẻ,
nên nó đo được phần kiểm thẻ của bạn mà không cần dựng container nào. Cùng năm
tình huống ấy còn được chạy lại qua HTTP ở `make nam-phep-kiem`, và hai đường
phải cho cùng một phán quyết. Nếu chúng lệch nhau thì thứ chạy trong container
không phải thứ bạn vừa sửa.

Biến môi trường `LAB_ROOT` cho phép chạy chính những phép kiểm này lên một thư
mục khác. Sinh viên không cần đặt nó, và không nên đặt. Nó tồn tại để bộ kiểm
nội bộ của giảng viên chạy được bộ kiểm này lên một bản mẫu đạt và một bản mẫu
trượt, vì một bộ chấm chưa bao giờ chạy trên một bài sai thì không ai biết nó
bắt được lỗi hay không.
"""
from __future__ import annotations

import importlib.util
import json
import os
import time
from pathlib import Path

import pytest

try:
    import jwt
    from cryptography.hazmat.primitives import serialization
    from cryptography.hazmat.primitives.asymmetric import rsa
except ImportError as loi:  # pragma: no cover
    raise RuntimeError(
        "Bộ kiểm cần PyJWT và cryptography. Cài bằng: pip install -r tests/yeu-cau.txt"
    ) from loi

try:
    import yaml
except ImportError as loi:  # pragma: no cover
    raise RuntimeError(
        "Bộ kiểm cần PyYAML. Cài bằng: pip install -r tests/yeu-cau.txt"
    ) from loi

ROOT = Path(os.environ.get("LAB_ROOT") or Path(__file__).resolve().parent.parent).resolve()

COMPOSE = ROOT / "docker-compose.yml"
VUNG = ROOT / "cau-hinh" / "vung-dinh-danh.json"
CHINH_SACH = ROOT / "cau-hinh" / "chinh-sach.yaml"
KIEM_THE = ROOT / "dich-vu" / "kiem_the.py"
EVID = ROOT / "evidence" / "S5"

NGUOI_NHAN = "dich-vu-ho-so"
THAN_KHACH_KHAC = "dich-vu-bao-cao"
BEN_PHAT_HANH = "http://may-danh-tinh:8080/realms/css"
DON_VI_CUA_MINH = "khoa-ktkt"
DON_VI_KHAC = "khoa-ktqt"

CAU_HINH = {
    "thuat_toan_cho_phep": ["RS256"],
    "nguoi_nhan": NGUOI_NHAN,
    "ben_phat_hanh": BEN_PHAT_HANH,
    "do_lech_dong_ho_giay": 5,
}

# Trần bốn container cho mỗi lab, gồm cả container chấm. Ngưỡng này của ADR-0003
# mục N3, đặt theo cấu hình laptop phổ thông của lớp chứ không theo sở thích.
TRAN_CONTAINER = 4

# Hạn thẻ tính bằng giây. Cận dưới để bài còn chạy được trong một tiết; cận trên
# lấy từ chính câu hỏi của hiện vật thứ ba, tức khoảng thời gian một tấm thẻ sống
# thêm sau khi quyền đã bị thu hồi.
HAN_THE_NHO_NHAT, HAN_THE_LON_NHAT = 60, 300

# Bộ nhớ tối thiểu cho hàm băm, tính theo KiB. Con số lấy từ RFC 9106 §4, bộ tham
# số thứ hai dành cho máy eo hẹp bộ nhớ: 64 MiB, 3 vòng lặp, 4 luồng.
BO_NHO_TOI_THIEU_KIB = 65536


# ------------------------------------------------------------ nạp bài của bạn

def nap_kiem_the():
    """Nạp dich-vu/kiem_the.py của bài đang chấm, theo đường dẫn chứ theo tên."""
    if not KIEM_THE.exists():
        pytest.fail(
            f"Không thấy {KIEM_THE.relative_to(ROOT)}. Đây là tệp sinh viên viết, không được chuyển nó sang chỗ khác."
        )
    dac_ta = importlib.util.spec_from_file_location("kiem_the_cua_bai", KIEM_THE)
    mo_dun = importlib.util.module_from_spec(dac_ta)
    try:
        dac_ta.loader.exec_module(mo_dun)
    except Exception as loi:  # noqa: BLE001
        pytest.fail(f"Nạp kiem_the.py thất bại: {type(loi).__name__}: {loi}")
    for ten in ("kiem_the", "quyet_dinh", "TheKhongHopLe"):
        if not hasattr(mo_dun, ten):
            pytest.fail(
                f"kiem_the.py thiếu {ten}. Hợp đồng ba tên này ghi ở đầu chính tệp ấy, "
                "và dịch vụ trong container gọi đúng ba tên đó."
            )
    return mo_dun


def doc_json(duong_dan: Path, ten_viec: str) -> dict:
    if not duong_dan.exists():
        pytest.fail(f"Không thấy {duong_dan.name}. {ten_viec}")
    try:
        return json.loads(duong_dan.read_text(encoding="utf-8"))
    except json.JSONDecodeError as loi:
        pytest.fail(f"{duong_dan.name} không phân giải được: {loi}")


def doc_yaml(duong_dan: Path, ten_viec: str) -> dict:
    if not duong_dan.exists():
        pytest.fail(f"Không thấy {duong_dan.name}. {ten_viec}")
    try:
        return yaml.safe_load(duong_dan.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as loi:
        pytest.fail(f"{duong_dan.name} không phân giải được: {loi}")


def doc_ket_qua(duong_dan: Path) -> dict[str, str]:
    """Đọc một tệp kết quả dạng khóa và giá trị, mỗi dòng một cặp."""
    ra: dict[str, str] = {}
    for dong in duong_dan.read_text(encoding="utf-8").splitlines():
        if not dong.strip() or ":" not in dong:
            continue
        khoa, gia_tri = dong.split(":", 1)
        ra[khoa.strip()] = gia_tri.strip()
    return ra


# ------------------------------------------------------------ xưởng dựng thẻ

_KHOA = rsa.generate_private_key(public_exponent=65537, key_size=2048)
_KHOA_KHAC = rsa.generate_private_key(public_exponent=65537, key_size=2048)


def _pem_cong(khoa) -> str:
    return khoa.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo,
    ).decode()


KHOA_CONG_PEM = _pem_cong(_KHOA)


def khai_mau(**doi) -> dict:
    bay_gio = int(time.time())
    khai = {
        "iss": BEN_PHAT_HANH,
        "aud": NGUOI_NHAN,
        "azp": NGUOI_NHAN,
        "sub": "8f14e45f-ea1b-4a6d-9b3c-000000000001",
        "preferred_username": "an-nv",
        "don_vi": DON_VI_CUA_MINH,
        "realm_access": {"roles": ["nhan-vien"]},
        "iat": bay_gio - 10,
        "exp": bay_gio + 300,
    }
    khai.update(doi)
    return khai


def the_dung_khoa_that(**doi) -> str:
    """Tấm thẻ mà một máy chủ danh tính đúng đắn sẽ phát ra."""
    return jwt.encode(khai_mau(**doi), _KHOA, algorithm="RS256")


def the_ky_khoa_khac(**doi) -> str:
    """Cùng tập khai, ký bằng một khóa riêng khác. Chữ ký đúng cú pháp, sai nguồn."""
    return jwt.encode(khai_mau(**doi), _KHOA_KHAC, algorithm="RS256")


def the_alg_none(**doi) -> str:
    """Thẻ tự khai thuật toán rỗng, chữ ký bỏ trống.

    Dựng bằng tay chứ không bằng thư viện, vì thư viện đã chặn sẵn đường này.
    Đó cũng là điều đáng nhớ: nhiều thư viện chặn giúp bạn, nhưng chỉ khi bạn
    không tự tay tắt phần chặn ấy đi.
    """
    import base64

    def doan(du_lieu: dict) -> str:
        goi = json.dumps(du_lieu, separators=(",", ":")).encode()
        return base64.urlsafe_b64encode(goi).decode().rstrip("=")

    return f"{doan({'alg': 'none', 'typ': 'JWT'})}.{doan(khai_mau(**doi))}."
