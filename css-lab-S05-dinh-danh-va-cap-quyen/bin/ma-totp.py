#!/usr/bin/env python3
"""In mã một lần của thời điểm hiện tại, từ bí mật ghi danh ở việc 5 của README.

    python3 bin/ma-totp.py                     đọc cau-hinh/totp-bi-mat.txt
    python3 bin/ma-totp.py JBSWY3DPEHPK3PXP    đọc bí mật từ tham số

Vì sao tệp này tự tính thay vì gọi một thư viện. RFC 6238 gọn tới mức viết ra
vừa mười dòng, và mười dòng ấy đáng đọc một lần trong đời: mã một lần không có
gì huyền bí, nó là HMAC của số thứ tự bước thời gian, cắt lấy bốn byte. Thấy
được điều đó thì cũng thấy ngay vì sao một trang giả chuyển tiếp mã trong ba
mươi giây là qua cửa, đúng như §5.4 nói. Máy nào đã có `pyotp` thì tệp này dùng
`pyotp`, và hai đường phải cho cùng một con số; đó cũng là một phép tự kiểm.
"""
from __future__ import annotations

import base64
import hashlib
import hmac
import struct
import sys
import time
from pathlib import Path

BUOC_GIAY = 30
SO_CHU_SO = 6
TEP_BI_MAT = Path(__file__).resolve().parent.parent / "cau-hinh" / "totp-bi-mat.txt"


def ma_totp(bi_mat_base32: str, luc: float | None = None) -> str:
    khoa = base64.b32decode(bi_mat_base32.replace(" ", "").upper() + "=" * (-len(bi_mat_base32) % 8))
    buoc = int((luc if luc is not None else time.time()) // BUOC_GIAY)
    bam = hmac.new(khoa, struct.pack(">Q", buoc), hashlib.sha1).digest()
    lech = bam[-1] & 0x0F
    so = struct.unpack(">I", bam[lech:lech + 4])[0] & 0x7FFFFFFF
    return str(so % (10 ** SO_CHU_SO)).zfill(SO_CHU_SO)


def doc_bi_mat() -> str:
    if not TEP_BI_MAT.exists():
        raise SystemExit(
            f"Không thấy {TEP_BI_MAT.name}. Ghi danh yếu tố thứ hai trong trình duyệt, "
            "chọn mục hiện bí mật dạng chữ, rồi lưu chuỗi đó vào cau-hinh/totp-bi-mat.txt. "
            "Tệp ấy nằm trong .gitignore và không được commit."
        )
    return TEP_BI_MAT.read_text(encoding="utf-8").strip()


def main() -> None:
    bi_mat = sys.argv[1] if len(sys.argv) > 1 else doc_bi_mat()
    ma = ma_totp(bi_mat)
    try:
        import pyotp  # noqa: PLC0415
    except ImportError:
        print(ma)
        return
    ma_thu_vien = pyotp.TOTP(bi_mat).now()
    if ma_thu_vien != ma:
        raise SystemExit(
            f"hai cách tính cho hai kết quả khác nhau: {ma} và {ma_thu_vien}. "
            "Đừng dùng con số nào cho tới khi biết vì sao."
        )
    print(ma)


if __name__ == "__main__":
    main()
