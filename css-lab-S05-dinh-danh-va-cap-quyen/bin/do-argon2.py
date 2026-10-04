#!/usr/bin/env python3
"""Đo giá của một lần đoán mật khẩu trên MÁY CỦA BẠN.

Chạy trong container `cong-cu`. Nó đăng nhập bằng luồng cấp trực tiếp vài lần,
lấy trung vị thời gian tường, rồi ghi kết quả vào evidence/S5/do-argon2.txt.

ĐÂY LÀ MỘT PHÉP XẤP XỈ, và nói thẳng ra như vậy. Thời gian đo được gồm cả thời
gian đi lại trong mạng compose, thời gian dựng và ký thẻ, chứ không phải riêng
thời gian băm. Cái nó đo đúng là ĐỘ CHÊNH giữa trước và sau khi bạn đổi tham số,
vì mọi phần khác giữ nguyên. Vì vậy hãy chạy nó HAI lần: một lần với tham số
khởi đầu, một lần sau khi đổi, rồi nói về hiệu số chứ không nói về con số tuyệt
đối. RFC 9106 §4 đưa hai bộ tham số khuyến nghị làm điểm khởi hành, và §5.3 của
giáo trình nói vì sao chúng là điểm khởi hành chứ không phải đáp số: máy của bạn
nhanh chậm khác máy của người viết chuẩn.
"""
from __future__ import annotations

import json
import os
import pathlib
import statistics
import time
import urllib.error
import urllib.parse
import urllib.request

VUNG = os.environ.get("CSS_BEN_PHAT_HANH", "http://may-danh-tinh:8080/realms/css")
NGUOI_DUNG = os.environ.get("CSS_NGUOI_DUNG", "an-nv")
MAT_KHAU = os.environ.get("CSS_MAT_KHAU", "mat-khau-lab-an")
SO_LAN = int(os.environ.get("CSS_SO_LAN", "7"))
NHAN = os.environ.get("CSS_NHAN_DO", "chua-dat-ten")

EVID = pathlib.Path("/lab/evidence/S5")


def mot_lan() -> float:
    """Một lần đăng nhập SAI mật khẩu, cố ý.

    Đo bằng mật khẩu sai chứ không bằng mật khẩu đúng, vì đó mới là việc kẻ tấn
    công làm hàng triệu lần. Máy chủ vẫn phải băm rồi mới biết là sai, nên chi
    phí một lần đoán chính là con số này.
    """
    du_lieu = urllib.parse.urlencode({
        "grant_type": "password",
        "client_id": "dich-vu-ho-so",
        "username": NGUOI_DUNG,
        "password": MAT_KHAU + "-sai",
    }).encode()
    yeu_cau = urllib.request.Request(
        f"{VUNG}/protocol/openid-connect/token",
        data=du_lieu,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    bat_dau = time.perf_counter()
    try:
        urllib.request.urlopen(yeu_cau, timeout=30).read()
    except urllib.error.HTTPError as loi:
        loi.read()
    return (time.perf_counter() - bat_dau) * 1000


def main() -> None:
    EVID.mkdir(parents=True, exist_ok=True)
    do = [mot_lan() for _ in range(SO_LAN)]
    trung_vi = statistics.median(do)
    ket = {
        "nhan": NHAN,
        "so_lan_do": SO_LAN,
        "trung_vi_mili_giay": round(trung_vi, 1),
        "nho_nhat_mili_giay": round(min(do), 1),
        "lon_nhat_mili_giay": round(max(do), 1),
        "phep_do": "thoi gian tuong cua mot lan dang nhap sai mat khau, do tu trong mang compose",
        "gioi_han": "xap xi: gom ca thoi gian di lai va thoi gian dung the, khong rieng thoi gian bam",
    }
    duong = EVID / "do-argon2.txt"
    cu = duong.read_text(encoding="utf-8") if duong.exists() else ""
    duong.write_text(cu + json.dumps(ket, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(ket, ensure_ascii=False, indent=2))
    print(f"\nĐã nối thêm một dòng vào {duong}. Chạy lại sau khi đổi tham số, với CSS_NHAN_DO khác.")


if __name__ == "__main__":
    main()
