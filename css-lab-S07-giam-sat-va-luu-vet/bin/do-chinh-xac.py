#!/usr/bin/env python3
"""Chạy quy tắc Sigma của bạn lên tập sự kiện có nhãn, ghi kết quả đo.

    python3 bin/do-chinh-xac.py [--tap <đường-dẫn>] [--quy-tac <đường-dẫn>]

Tệp sinh ra là evidence/S7/do-chinh-xac.json. Bộ chấm tính lại chính phép đo này
từ quy tắc của bạn rồi so với tệp ấy, nên sửa tay con số trong tệp là cách chắc
chắn nhất để bị bắt. Lý do có bước so lại không phải là nghi ngờ: nó bảo đảm rằng
con số bạn dùng trong đoạn văn về giá của báo nhầm đúng là con số quy tắc hiện
tại sinh ra, chứ không phải con số của một phiên bản quy tắc bạn đã sửa từ lâu.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(GOC / "bin"))

from quy_tac import QuyTacHong, do_tren_tap, doc_quy_tac, doc_tap_co_nhan  # noqa: E402


def main() -> int:
    bo = argparse.ArgumentParser(description="Đo quy tắc Sigma trên tập có nhãn.")
    bo.add_argument("--quy-tac", default=str(GOC / "sigma" / "quy-tac.yml"))
    bo.add_argument("--tap", default=str(GOC / "nhan" / "tap-co-nhan.jsonl"))
    bo.add_argument("--ra", default=str(GOC / "evidence" / "S7" / "do-chinh-xac.json"))
    tham_so = bo.parse_args()

    try:
        quy_tac = doc_quy_tac(Path(tham_so.quy_tac))
        tap = doc_tap_co_nhan(Path(tham_so.tap))
    except QuyTacHong as loi:
        print("Quy tắc hoặc tập có nhãn chưa đọc được.", file=sys.stderr)
        print(str(loi), file=sys.stderr)
        return 1

    def goi_ngan(duong_dan: Path) -> str:
        """Tên hiển thị. Đường dẫn nằm ngoài thư mục lab vẫn in được nguyên dạng,
        vì bộ chấm của giảng viên gọi tập lệnh này trên các bản mẫu ở nơi khác."""
        try:
            return str(duong_dan.resolve().relative_to(GOC))
        except ValueError:
            return str(duong_dan)

    ket = do_tren_tap(quy_tac, tap)
    ket["tieu_de_quy_tac"] = quy_tac.tieu_de
    ket["dieu_kien"] = quy_tac.dieu_kien
    ket["tep_quy_tac"] = goi_ngan(Path(tham_so.quy_tac))
    ket["tap_co_nhan"] = goi_ngan(Path(tham_so.tap))
    ket["sinh_boi"] = "bin/do-chinh-xac.py"

    ra = Path(tham_so.ra)
    ra.parent.mkdir(parents=True, exist_ok=True)
    ra.write_text(json.dumps(ket, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")

    print(f"Quy tắc      : {quy_tac.tieu_de}")
    print(f"Điều kiện    : {quy_tac.dieu_kien}")
    print(f"Bản ghi      : {ket['tong_ban_ghi']}")
    print(f"Bắt đúng     : {ket['TP']}")
    print(f"Bắt nhầm     : {ket['FP']}  {ket['bat_nham']}")
    print(f"Bỏ sót       : {ket['FN']}  {ket['bo_sot']}")
    print(f"Độ chính xác : {ket['do_chinh_xac']}")
    print(f"Độ phủ       : {ket['do_phu']}")
    print()
    print(f"Đã ghi {goi_ngan(ra)}")
    print("Tập có nhãn trải đúng 24 giờ, nên số lần bắt nhầm ở trên cũng là số lần")
    print("bắt nhầm mỗi ngày. Đó là con số đi vào docs/gia-cua-bao-nham.md.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
