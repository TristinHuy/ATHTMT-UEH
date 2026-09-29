"""Phần dùng chung của bộ kiểm công khai.

Tệp này không chứa phép kiểm nào. Nó giữ ba thứ mà cả bốn tệp kiểm đều cần: chỗ
đứng của bài, cách gọi `openssl`, và cách đọc một tệp kết quả.

Biến môi trường `LAB_ROOT` cho phép chạy chính những phép kiểm này lên một thư
mục khác. Sinh viên không cần đặt nó, và không nên đặt. Nó tồn tại để bộ kiểm
nội bộ của giảng viên chạy được bộ kiểm này lên một bản mẫu đạt và một bản mẫu
trượt, vì một bộ chấm chưa bao giờ chạy trên một bài sai thì không ai biết nó
bắt được lỗi hay không.
"""
from __future__ import annotations

import os
import shutil
import subprocess
from pathlib import Path

import pytest

ROOT = Path(os.environ.get("LAB_ROOT") or Path(__file__).resolve().parent.parent).resolve()

PKI = ROOT / "pki"
EVID = ROOT / "evidence" / "S3"

TEN_DICH_VU = "may-chu"
HAN_TOI_DA_NGAY = 400

THANG = {
    "Jan": 1, "Feb": 2, "Mar": 3, "Apr": 4, "May": 5, "Jun": 6,
    "Jul": 7, "Aug": 8, "Sep": 9, "Oct": 10, "Nov": 11, "Dec": 12,
}


def can_openssl() -> None:
    """Dừng sớm và nói rõ, thay vì để năm phép kiểm cùng đỏ vì một nguyên nhân."""
    if shutil.which("openssl") is None:
        pytest.fail(
            "Không có openssl trên máy chạy bộ kiểm. Bộ kiểm này đọc chứng thư của "
            "bạn bằng chính openssl chứ không tin lời khai của tệp cấu hình, nên "
            "thiếu nó thì không kiểm được gì. Cài openssl rồi chạy lại."
        )


def openssl(*args: str) -> subprocess.CompletedProcess:
    can_openssl()
    return subprocess.run(
        ["openssl", *args],
        capture_output=True,
        text=True,
        env={**os.environ, "LC_ALL": "C", "TZ": "UTC"},
    )


def doc_ket_qua(duong_dan: Path) -> dict[str, str]:
    """Đọc một tệp kết quả dạng khóa và giá trị, mỗi dòng một cặp."""
    ra: dict[str, str] = {}
    for dong in duong_dan.read_text(encoding="utf-8").splitlines():
        if not dong.strip() or ":" not in dong:
            continue
        khoa, gia_tri = dong.split(":", 1)
        ra[khoa.strip()] = gia_tri.strip()
    return ra


def doc_ngay(chuoi: str):
    """Đổi 'Aug 18 10:00:00 2026 GMT' thành datetime.

    Không dùng strptime với %b vì tên tháng phụ thuộc locale, và một bài trượt vì
    máy sinh viên đặt locale khác là một cáo buộc sai. Cáo buộc sai tốn kém đúng
    bằng một lỗi bị bỏ sót.
    """
    from datetime import datetime, timezone

    phan = chuoi.replace("GMT", "").split()
    if len(phan) < 4:
        raise ValueError(f"không đọc được ngày: {chuoi!r}")
    thang, ngay, gio, nam = phan[0], int(phan[1]), phan[2], int(phan[3])
    h, m, s = (int(x) for x in gio.split(":"))
    return datetime(nam, THANG[thang], ngay, h, m, s, tzinfo=timezone.utc)
