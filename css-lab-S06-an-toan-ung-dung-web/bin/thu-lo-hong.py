#!/usr/bin/env python3
"""Gọi hai lỗ hổng của bài bằng ba yêu cầu thật, rồi ghi lại ứng dụng trả lời ra sao.

Tập lệnh này chạy trên MÁY BẠN, không trong container, và nó chỉ gọi 127.0.0.1.
Đó là lý do nó chỉ dùng thư viện chuẩn của Python: bạn đã cần Python để chạy bộ
kiểm, nên bước này không thêm thứ gì phải cài.

Nó không khai thác gì. Ba yêu cầu dưới đây là ba yêu cầu mà chính bộ chấm sẽ gửi
khi bạn chạy `make verify`, viết ra ở đây để bạn ĐỌC được câu trả lời của ứng dụng
trước và sau khi vá, thay vì chỉ thấy một dòng đỏ hoặc một dòng xanh. Khoảng cách
giữa hai lần chạy chính là thứ bạn mang vào đoạn văn cuối bài.

    python3 bin/thu-lo-hong.py --nhan truoc-khi-va
    python3 bin/thu-lo-hong.py --nhan sau-khi-va

Mã thoát: 0 khi ba yêu cầu đã gửi và bằng chứng đã ghi, 1 khi không gọi được ứng
dụng, 2 khi sai tham số. Mã thoát KHÔNG phải phán quyết về bài làm của bạn: một
lần chạy trước khi vá vẫn trả 0, vì việc của nó là ghi lại sự thật chứ không phải
chấm điểm.
"""
from __future__ import annotations

import argparse
import socket
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

GOC_MAC_DINH = "http://127.0.0.1:8081"
GOC_LA = "http://trang-cua-ke-tan-cong.example"
TAI_TRONG = "<script>alert(1)</script>"
THU_MUC_BANG_CHUNG = Path(__file__).resolve().parent.parent / "evidence" / "S6"


def goi(url: str, du_lieu: str | None = None, **tieu_de: str):
    yeu_cau = urllib.request.Request(
        url,
        data=du_lieu.encode("utf-8") if du_lieu is not None else None,
        method="POST" if du_lieu is not None else "GET",
    )
    if du_lieu is not None:
        yeu_cau.add_header("Content-Type", "application/x-www-form-urlencoded")
    for ten, gia_tri in tieu_de.items():
        yeu_cau.add_header(ten.replace("_", "-"), gia_tri)
    try:
        with urllib.request.urlopen(yeu_cau, timeout=10) as phan_hoi:
            return phan_hoi.status, dict(phan_hoi.headers), phan_hoi.read().decode("utf-8", "replace")
    except urllib.error.HTTPError as loi:
        return loi.code, dict(loi.headers), loi.read().decode("utf-8", "replace")
    except (urllib.error.URLError, socket.timeout) as loi:
        sys.stderr.write(
            f"Không gọi được {url}: {loi}\n"
            "Ứng dụng chưa chạy hoặc đang nghe ở cổng khác. Chạy `make up` rồi thử lại.\n"
        )
        raise SystemExit(1)


def lay_the(goc: str) -> str:
    _, _, than = goi(goc + "/thu/doi-dia-chi")
    moc = 'name="the" value="'
    dau = than.find(moc)
    if dau == -1:
        return ""
    dau += len(moc)
    return than[dau:than.find('"', dau)]


def main() -> None:
    bo_doc = argparse.ArgumentParser(description=__doc__)
    bo_doc.add_argument("--nhan", required=True, help="tên lần chạy, thành tên tệp bằng chứng")
    bo_doc.add_argument("--dia-chi", default=GOC_MAC_DINH, help=f"mặc định {GOC_MAC_DINH}")
    tham_so = bo_doc.parse_args()
    goc = tham_so.dia_chi.rstrip("/")

    dong: list[str] = [f"nhan: {tham_so.nhan}", f"dia_chi: {goc}"]

    # Yêu cầu 1. Chuỗi do người gửi điều khiển, ghép vào thân trang.
    ma, tieu_de, than = goi(goc + "/thu/tim-kiem?q=" + urllib.parse.quote(TAI_TRONG))
    con_nguyen_van = TAI_TRONG in than
    dong.append(f"lh1_ma_http: {ma}")
    dong.append(f"lh1_chuoi_con_nguyen_van: {'CO' if con_nguyen_van else 'KHONG'}")
    dong.append(f"lh1_dang_da_ma_hoa: {'CO' if '&lt;script&gt;' in than else 'KHONG'}")

    # Yêu cầu 1 cũng cho biết máy chủ đang nói gì với trình duyệt.
    ten_csp = ""
    for ten in ("Content-Security-Policy", "Content-Security-Policy-Report-Only"):
        if ten in tieu_de:
            ten_csp = ten
            break
    dong.append(f"csp_tieu_de: {ten_csp or 'khong-co'}")
    dong.append(f"csp_gia_tri: {tieu_de.get(ten_csp, '') if ten_csp else ''}")

    cookie = tieu_de.get("Set-Cookie", "")
    dong.append(f"cookie: {cookie or 'khong-co'}")
    dong.append(f"cookie_httponly: {'CO' if 'httponly' in cookie.lower() else 'KHONG'}")
    dong.append(f"cookie_samesite: {'CO' if 'samesite' in cookie.lower() else 'KHONG'}")

    # Yêu cầu 2. Gốc hợp lệ, không thẻ. Chỉ phép kiểm thẻ chặn được.
    than_gui = urllib.parse.urlencode({"dia_chi": "99 Đường Thử Nghiệm"})
    ma, _, tra_loi = goi(goc + "/thu/doi-dia-chi", than_gui, Origin=goc)
    dong.append(f"lh2_goc_hop_le_khong_the: {'BI_TU_CHOI' if ma == 403 else 'DUOC_NHAN'} (ma {ma})")

    # Yêu cầu 3. Gốc lạ, thẻ thật. Chỉ phép kiểm gốc chặn được.
    the = lay_the(goc)
    than_gui = urllib.parse.urlencode({"dia_chi": "99 Đường Thử Nghiệm", "the": the})
    ma, _, tra_loi = goi(goc + "/thu/doi-dia-chi", than_gui, Origin=GOC_LA)
    dong.append(f"lh2_goc_la_co_the: {'BI_TU_CHOI' if ma == 403 else 'DUOC_NHAN'} (ma {ma})")
    dong.append(f"lh2_tra_loi_cuoi: {tra_loi.strip()[:200]}")

    THU_MUC_BANG_CHUNG.mkdir(parents=True, exist_ok=True)
    tep = THU_MUC_BANG_CHUNG / f"thu-lo-hong-{tham_so.nhan}.txt"
    tep.write_text("\n".join(dong) + "\n", encoding="utf-8")

    print("\n".join(dong))
    print()
    print(f"Đã ghi {tep.relative_to(Path(__file__).resolve().parent.parent)}")
    print("Đọc theo cặp. CO ở dòng lh1_chuoi_con_nguyen_van nghĩa là trình duyệt vẫn đọc")
    print("chuỗi ấy như một phần của tài liệu. DUOC_NHAN ở hai dòng lh2 nghĩa là một trang")
    print("khác vẫn ra lệnh được nhân danh người đang đăng nhập.")


if __name__ == "__main__":
    main()
