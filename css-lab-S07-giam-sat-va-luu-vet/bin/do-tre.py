#!/usr/bin/env python3
"""Đo độ trễ riêng từng chặng trên đường đi của một dòng nhật ký.

    python3 bin/do-tre.py

Bốn chặng, đo bằng bốn mốc thời gian chứ không bằng một phép trừ duy nhất, vì một
con số tổng không nói được chặng nào chậm. Phép đo gieo một dòng mang dấu riêng
vào nguồn, rồi hỏi Loki lặp lại cho tới khi thấy dòng ấy.

Kết quả ghi vào evidence/S7/do-tre.csv. Chạy phép đo ít nhất ba lần rồi lấy lần
chậm nhất, vì con số bạn cần cho phần lập luận là con số xấu nhất người trực phải
chịu, không phải con số đẹp nhất máy đạt được.
"""
from __future__ import annotations

import csv
import json
import os
import sys
import time
import urllib.parse
import urllib.request
import uuid
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
NGUON = GOC / "nhat-ky" / "S07" / "do-tre.log"
RA = GOC / "evidence" / "S7" / "do-tre.csv"
DIA_CHI = os.environ.get("LOKI_URL", "http://loki:3100")
KIEN_NHAN_GIAY = 120

CHANG = [
    ("sinh", "tu luc su kien xay ra toi luc dong chu nam trong tep nhat ky"),
    ("chuyen", "tu tep nhat ky toi luc Promtail doc va gui di"),
    ("giu", "tu luc Loki nhan toi luc ban ghi tra loi duoc truy van"),
    ("hoi", "tu luc gui truy van toi luc thay dong chu"),
]


def hoi_loki(dau_rieng: str) -> dict | None:
    truy_van = '{job="nhat-ky-lab", buoi="S07"} |= "%s"' % dau_rieng
    het = int(time.time() * 1_000_000_000)
    tham_so = urllib.parse.urlencode(
        {"query": truy_van, "start": het - 3600 * 1_000_000_000, "end": het, "limit": 10}
    )
    try:
        with urllib.request.urlopen(  # noqa: S310
            f"{DIA_CHI}/loki/api/v1/query_range?{tham_so}", timeout=10
        ) as tra_loi:
            than = json.loads(tra_loi.read().decode("utf-8"))
    except Exception:  # noqa: BLE001
        return None
    for luong in than.get("data", {}).get("result", []):
        for muc in luong.get("values", []):
            return {"nhan_luc_nano": int(muc[0])}
    return None


def main() -> int:
    dau_rieng = "do-tre-" + uuid.uuid4().hex[:12]
    NGUON.parent.mkdir(parents=True, exist_ok=True)

    t_su_kien = time.time()
    with NGUON.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "thoi_diem": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "buoi": "S07", "dich_vu": "phep-do", "nguoi_dung": "van-hanh",
            "hanh_dong": "gieo-dau-rieng", "ket_qua": "cho_phep", "ly_do": "",
            "thong_diep": f"phep do do tre, dau rieng {dau_rieng}",
        }, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    t_ghi_xong = time.time()

    t_bat_dau_hoi = time.time()
    thay = None
    while time.time() - t_bat_dau_hoi < KIEN_NHAN_GIAY:
        t_gui = time.time()
        thay = hoi_loki(dau_rieng)
        t_nhan = time.time()
        if thay:
            break
        time.sleep(0.5)
    if not thay:
        print(f"Sau {KIEN_NHAN_GIAY} giây Loki vẫn chưa thấy dòng vừa gieo.", file=sys.stderr)
        print("Đây là một kết quả, không phải một lỗi của tập lệnh. Nó nói rằng đường", file=sys.stderr)
        print("dẫn đang đứt ở đâu đó. Xem nhật ký của promtail trước, vì đó là chặng", file=sys.stderr)
        print("duy nhất đọc được cả hai đầu.", file=sys.stderr)
        return 1

    t_loki_nhan = thay["nhan_luc_nano"] / 1_000_000_000
    do = {
        "sinh": t_ghi_xong - t_su_kien,
        "chuyen": max(0.0, t_loki_nhan - t_ghi_xong),
        "giu": max(0.0, t_gui - t_loki_nhan),
        "hoi": t_nhan - t_gui,
    }
    tong = sum(do.values())

    RA.parent.mkdir(parents=True, exist_ok=True)
    with RA.open("w", encoding="utf-8", newline="") as f:
        ghi = csv.writer(f)
        ghi.writerow(["chang", "mo_ta", "giay"])
        for ten, mo_ta in CHANG:
            ghi.writerow([ten, mo_ta, f"{do[ten]:.3f}"])
        ghi.writerow(["tong", "toan duong tu luc su kien xay ra toi luc truy van thay no", f"{tong:.3f}"])

    for ten, mo_ta in CHANG:
        print(f"{ten:8s} {do[ten]:7.3f} giay   {mo_ta}")
    print(f"{'tong':8s} {tong:7.3f} giay")
    print()
    print(f"Đã ghi {RA.relative_to(GOC)}. Chạy lại vài lần và giữ lần chậm nhất.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
