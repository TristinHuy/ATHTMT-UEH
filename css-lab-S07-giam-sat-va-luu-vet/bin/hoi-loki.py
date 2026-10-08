#!/usr/bin/env python3
"""Gửi một câu LogQL tới Loki và ghi lại đúng những gì Loki trả về.

    python3 bin/hoi-loki.py --nhan S03 '{job="nhat-ky-lab", buoi="S03"} |= "chung thu khach"'

Bạn gõ câu truy vấn bằng logcli khi đang làm bài, vì logcli in ra dạng người đọc
và cho phép thử nhanh. Tập lệnh này tồn tại cho bước sau đó: nó gọi cùng một câu
qua giao diện HTTP của Loki rồi ghi kết quả xuống evidence/S7/ dưới dạng máy đọc
được, kèm thời điểm hỏi. Người chấm cần thấy câu truy vấn nào cho ra bao nhiêu
dòng, và một ảnh chụp màn hình không nói được điều đó.

Tập lệnh chạy trong container cong-cu, nơi tên máy loki phân giải được. Chạy nó
trên máy thật thì Loki không có địa chỉ nào để gọi, và đó là ý đồ: kho nhật ký
không mở cổng ra ngoài mạng compose.
"""
from __future__ import annotations

import argparse
import json
import os
import sys
import time
import urllib.parse
import urllib.request
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
DIA_CHI_MAC_DINH = os.environ.get("LOKI_URL", "http://loki:3100")


def hoi(dia_chi: str, truy_van: str, gio: int) -> dict:
    het = int(time.time() * 1_000_000_000)
    dau = het - gio * 3600 * 1_000_000_000
    tham_so = urllib.parse.urlencode(
        {"query": truy_van, "start": dau, "end": het, "limit": 5000, "direction": "forward"}
    )
    url = f"{dia_chi}/loki/api/v1/query_range?{tham_so}"
    with urllib.request.urlopen(url, timeout=30) as tra_loi:  # noqa: S310
        return json.loads(tra_loi.read().decode("utf-8"))


def main() -> int:
    bo = argparse.ArgumentParser(description="Hỏi Loki một câu LogQL.")
    bo.add_argument("truy_van")
    bo.add_argument("--nhan", required=True, help="tên ngắn của phép hỏi, thành tên tệp bằng chứng")
    bo.add_argument(
        "--gio",
        type=int,
        default=2160,
        help="bề rộng cửa sổ thời gian, tính bằng giờ (mặc định 90 ngày)",
    )
    bo.add_argument("--dia-chi", default=DIA_CHI_MAC_DINH)
    tham_so = bo.parse_args()

    try:
        tra_loi = hoi(tham_so.dia_chi, tham_so.truy_van, tham_so.gio)
    except Exception as loi:  # noqa: BLE001
        print(f"Không hỏi được Loki ở {tham_so.dia_chi}: {type(loi).__name__}: {loi}", file=sys.stderr)
        print("Kiểm ba thứ theo thứ tự: make up đã chạy chưa, container loki còn sống không,", file=sys.stderr)
        print("và bạn có đang đứng trong container cong-cu hay không.", file=sys.stderr)
        return 1

    dong = [
        {"thoi_diem_nano": muc[0], "noi_dung": muc[1], "nhan_dong": luong.get("stream", {})}
        for luong in tra_loi.get("data", {}).get("result", [])
        for muc in luong.get("values", [])
    ]
    dong.sort(key=lambda d: d["thoi_diem_nano"])

    ket = {
        "nhan": tham_so.nhan,
        "truy_van": tham_so.truy_van,
        "cua_so_gio": tham_so.gio,
        "hoi_luc": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
        "so_dong_khop": len(dong),
        "dong": dong[:50],
        "ghi_chu": "Chỉ 50 dòng đầu được giữ lại, con số so_dong_khop là con số đầy đủ.",
    }
    ra = GOC / "evidence" / "S7" / f"truy-van-{tham_so.nhan}.json"
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(json.dumps(ket, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    print(f"{len(dong)} dòng khớp. Đã ghi {ra.relative_to(GOC)}")
    for d in dong[:5]:
        print("  " + d["noi_dung"][:140])
    if len(dong) == 0:
        print()
        print("Không dòng nào khớp. Trước khi sửa câu truy vấn, hỏi một câu rộng hơn")
        print("để biết nguồn ấy có được nạp hay không. Không có dòng nào là một kết quả")
        print("hợp lệ của bài này, và bảng năm sự kiện có sẵn chỗ để ghi lại điều đó.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
