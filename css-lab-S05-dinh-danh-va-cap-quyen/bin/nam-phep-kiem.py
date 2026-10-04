#!/usr/bin/env python3
"""Sáu lần gọi thật vào dịch vụ của bạn, và sáu tệp bằng chứng.

Chạy trong container `cong-cu`, không chạy trên máy thật, vì nó cần thư viện đọc
thẻ và cần đứng trong mạng compose của bài.

Năm phép kiểm âm N1 tới N5 là hiện vật được chấm nặng nhất của bài, và P1 là
phép kiểm dương đi kèm chúng. Không có P1 thì năm phép kia không nói gì: một
dịch vụ chết cũng từ chối đủ năm lần, và từ chối vì lý do hoàn toàn khác.

Phán quyết trong mỗi tệp kết quả lấy từ mã HTTP thật của lần gọi, không lấy từ
lời khai. Sửa tay một tệp trong evidence/ là làm giả bằng chứng, và rubric.md nói
rõ mức xử lý.
"""
from __future__ import annotations

import base64
import json
import os
import pathlib
import subprocess
import sys
import time
import urllib.error
import urllib.parse
import urllib.request

import jwt
from cryptography.hazmat.primitives.asymmetric import rsa

VUNG = os.environ.get("CSS_BEN_PHAT_HANH", "http://may-danh-tinh:8080/realms/css")
DICH_VU = os.environ.get("CSS_DICH_VU", "http://dich-vu:8000")
NGUOI_DUNG = os.environ.get("CSS_NGUOI_DUNG", "an-nv")
MAT_KHAU = os.environ.get("CSS_MAT_KHAU", "mat-khau-lab-an")
DON_VI_CUA_MINH = os.environ.get("CSS_DON_VI", "khoa-ktkt")
DON_VI_KHAC = os.environ.get("CSS_DON_VI_KHAC", "khoa-ktqt")
THAN_KHACH = "dich-vu-ho-so"
THAN_KHACH_KHAC = "dich-vu-bao-cao"

GOC = pathlib.Path("/lab")
# Tham số thứ nhất, nếu có, là tên thư mục con để ghi kết quả. `make attack` dùng
# nó để giữ trạng thái đầu buổi ở một chỗ riêng, không đè lên bằng chứng cuối.
THU_MUC_CON = sys.argv[1] if len(sys.argv) > 1 else ""
EVID = GOC / "evidence" / "S5" / THU_MUC_CON if THU_MUC_CON else GOC / "evidence" / "S5"
DUONG_TUONG_DOI = f"evidence/S5/{THU_MUC_CON}/" if THU_MUC_CON else "evidence/S5/"
THO = EVID / "tho"

# Quá con số này thì không đợi nữa. Ở trạng thái khởi đầu, hạn thẻ là một giờ,
# và đợi một giờ trong một tiết lab là chuyện không xảy ra. Chính chỗ không đợi
# được ấy là lý do việc 5 bắt rút hạn thẻ xuống.
CHO_LAU_NHAT_GIAY = 305


def lay_the(than_khach: str) -> str:
    """Xin một tấm thẻ thật bằng luồng cấp trực tiếp.

    Luồng này có mặt trong bài vì nó là cách duy nhất lấy được thẻ mà không cần
    một trình duyệt trong container. Luồng bạn cấu hình cho người dùng thật là
    luồng mã ủy quyền, và §5.2 nói vì sao hai luồng không thay thế nhau.
    """
    du_lieu = {
        "grant_type": "password",
        "client_id": than_khach,
        "username": NGUOI_DUNG,
        "password": MAT_KHAU,
    }
    ma_totp = lay_ma_totp()
    if ma_totp:
        du_lieu["totp"] = ma_totp
    yeu_cau = urllib.request.Request(
        f"{VUNG}/protocol/openid-connect/token",
        data=urllib.parse.urlencode(du_lieu).encode(),
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    try:
        with urllib.request.urlopen(yeu_cau, timeout=15) as tra_loi:
            return json.loads(tra_loi.read())["access_token"]
    except urllib.error.HTTPError as loi:
        than = loi.read().decode("utf-8", "replace")
        raise SystemExit(
            f"không xin được thẻ cho thân khách {than_khach}: HTTP {loi.code} {than}\n"
            "Ba chỗ hay sai: vùng định danh chưa nạp lại sau khi sửa tệp cấu hình, "
            "luồng cấp trực tiếp bị tắt cho thân khách này, hoặc mã một lần đã hết hiệu lực."
        ) from loi


def lay_ma_totp() -> str:
    tep = pathlib.Path("/etc/css-s05/totp-bi-mat.txt")
    if not tep.exists():
        return ""
    ket = subprocess.run(
        [sys.executable, "/lab/bin/ma-totp.py", tep.read_text(encoding="utf-8").strip()],
        capture_output=True, text=True, check=False,
    )
    return ket.stdout.strip()


def goi(the: str, don_vi: str, phuong_thuc: str = "GET") -> tuple[int, str]:
    dia_chi = f"{DICH_VU}/ho-so?" + urllib.parse.urlencode({"don_vi": don_vi})
    yeu_cau = urllib.request.Request(dia_chi, method=phuong_thuc)
    if the:
        yeu_cau.add_header("Authorization", f"Bearer {the}")
    try:
        with urllib.request.urlopen(yeu_cau, timeout=15) as tra_loi:
            return tra_loi.status, tra_loi.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as loi:
        return loi.code, loi.read().decode("utf-8", "replace")
    except urllib.error.URLError as loi:
        return 0, f"không nối được tới dịch vụ: {loi}"


def the_alg_none(the_that: str) -> str:
    """Dựng lại tấm thẻ với phần đầu khai thuật toán rỗng và chữ ký rỗng.

    Tập khai giữ nguyên, nên nếu dịch vụ của bạn tin trường `alg` trong chính tấm
    thẻ thì nó sẽ thấy một người dùng hợp lệ với đầy đủ vai.
    """
    khai = the_that.split(".")[1]
    dau = base64.urlsafe_b64encode(b'{"alg":"none","typ":"JWT"}').decode().rstrip("=")
    return f"{dau}.{khai}."


def the_ky_khoa_khac(the_that: str) -> str:
    """Ký lại đúng tập khai ấy bằng một khóa riêng vừa sinh ra ở đây."""
    khai = json.loads(base64.urlsafe_b64decode(the_that.split(".")[1] + "=="))
    khoa = rsa.generate_private_key(public_exponent=65537, key_size=2048)
    return jwt.encode(khai, khoa, algorithm="RS256")


def ghi(ma: str, loai: str, mo_ta: str, mong_doi: str, ma_http: int, than: str) -> str:
    THO.mkdir(parents=True, exist_ok=True)
    tep_tho = THO / f"{ma}.log"
    tep_tho.write_text(f"ma_http: {ma_http}\n{than}\n", encoding="utf-8")
    if ma_http == 200:
        thuc_te = "DUOC_NHAN"
    elif ma_http in (401, 403):
        thuc_te = "BI_TU_CHOI"
    elif ma_http < 0:
        thuc_te = "CHUA_CHAY"
    else:
        thuc_te = f"KHONG_KET_LUAN_DUOC_{ma_http}"
    (EVID / f"kiem-{ma}.txt").write_text(
        f"ma: {ma}\n"
        f"loai: {loai}\n"
        f"mo_ta: {mo_ta}\n"
        f"mong_doi: {mong_doi}\n"
        f"thuc_te: {thuc_te}\n"
        f"ma_http: {ma_http}\n"
        f"nhat_ky_tho: {DUONG_TUONG_DOI}tho/{ma}.log\n",
        encoding="utf-8",
    )
    print(f"{ma}  mong doi {mong_doi:12s}  thuc te {thuc_te:12s}  HTTP {ma_http}  {mo_ta}")
    return thuc_te


def han_the() -> int:
    """Đọc hạn thẻ từ chính tệp vùng định danh, không gõ lại con số."""
    vung = json.loads(pathlib.Path("/etc/css-s05/vung-dinh-danh.json").read_text(encoding="utf-8"))
    return int(vung.get("accessTokenLifespan", 300))


def main() -> None:
    EVID.mkdir(parents=True, exist_ok=True)
    the = lay_the(THAN_KHACH)
    luc_lay_the = time.time()

    ghi("P1", "duong", "the that, dung than khach, dung don vi cua minh",
        "DUOC_NHAN", *goi(the, DON_VI_CUA_MINH))
    ghi("N1", "am", "the khai thuat toan rong, tuc alg none, CWE-347",
        "BI_TU_CHOI", *goi(the_alg_none(the), DON_VI_CUA_MINH))
    ghi("N2", "am", "the ky bang mot khoa khac, CWE-347",
        "BI_TU_CHOI", *goi(the_ky_khoa_khac(the), DON_VI_CUA_MINH))
    ghi("N4", "am", "the that nhung phat cho than khach khac, CWE-863",
        "BI_TU_CHOI", *goi(lay_the(THAN_KHACH_KHAC), DON_VI_CUA_MINH))
    ghi("N5", "am", "danh tinh hop le nhung xin ho so cua don vi khac, CWE-863",
        "BI_TU_CHOI", *goi(the, DON_VI_KHAC))

    han = han_the()
    if han > CHO_LAU_NHAT_GIAY:
        ghi("N3", "am", f"the that nhung da qua han {han} giay, CWE-613",
            "BI_TU_CHOI", -1,
            f"han the dang la {han} giay, vuot muc {CHO_LAU_NHAT_GIAY} giay ma tap lenh chiu doi.\n"
            "Phep kiem nay chua chay. Rut han the xuong roi chay lai.")
        print(f"\nN3 chua chay: hạn thẻ {han} giây quá dài để đợi trong một buổi lab.")
        print("Đó cũng là lý do việc 5 yêu cầu rút hạn thẻ: một hạn thẻ dài tới mức không thể đợi")
        print("để kiểm cũng là quãng thời gian một tấm thẻ sống thêm sau khi bị thu hồi.")
        return

    con_lai = han + 5 - (time.time() - luc_lay_the)
    if con_lai > 0:
        print(f"\nđợi {con_lai:.0f} giây cho tấm thẻ hết hạn. Hạn đọc từ vùng định danh là {han} giây.")
        print("Đây là con số hiện vật thứ ba hỏi tới, và đây là lúc đo nó bằng đồng hồ.")
        time.sleep(con_lai)
    ghi("N3", "am", f"the that nhung da qua han {han} giay, CWE-613",
        "BI_TU_CHOI", *goi(the, DON_VI_CUA_MINH))

    print(f"\nBằng chứng ở {DUONG_TUONG_DOI}. Đọc lại bằng: make verify")


if __name__ == "__main__":
    main()
