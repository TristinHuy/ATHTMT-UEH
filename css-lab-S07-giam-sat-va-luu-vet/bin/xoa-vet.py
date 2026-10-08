#!/usr/bin/env python3
"""Thí nghiệm một chặng: xóa dấu vết ở nơi nó sinh ra, rồi tìm lại nó ở nơi khác.

    python3 bin/xoa-vet.py

Đây là toàn bộ phần tấn công của bài S7, và nó dừng ở đúng một thao tác: cắt cụt
một tệp nhật ký trong thư mục nhat-ky/S07/ của chính bạn. Không có bước nào chạm
tới máy khác, tới container của người khác, hay tới một tệp nằm ngoài thư mục bài
làm. Kỹ thuật tương ứng trong ATT&CK là T1685.006, và bài này thực hiện nó ở mức
vừa đủ để trả lời một câu, chứ không đi sâu vào nghệ thuật xóa dấu vết. Phần sâu
thuộc học phần Kiểm thử thâm nhập.

Câu phải trả lời: nếu người chiếm được máy xóa được tệp nhật ký, thì chặng chuyển
đi có cứu được dòng chữ hay không, và cứu được trong khoảng thời gian nào?

Tập lệnh gieo một dòng, đợi Loki nhận, cắt cụt tệp nguồn, rồi hỏi lại Loki. Nó
cũng đo bề rộng của khoảng nguy hiểm, tức khoảng thời gian dòng chữ mới chỉ tồn
tại ở một nơi. Trong khoảng ấy, một lệnh xóa là đủ để mất nó vĩnh viễn.
"""
from __future__ import annotations

import json
import os
import time
import uuid
from pathlib import Path

GOC = Path(__file__).resolve().parent.parent
NGUON = GOC / "nhat-ky" / "S07" / "thu-nghiem-xoa-vet.log"
RA = GOC / "evidence" / "S7" / "xoa-vet.txt"

import importlib.util  # noqa: E402

_dac_ta = importlib.util.spec_from_file_location("do_tre", GOC / "bin" / "do-tre.py")
_do_tre = importlib.util.module_from_spec(_dac_ta)
_dac_ta.loader.exec_module(_do_tre)


def main() -> int:
    dau_rieng = "xoa-vet-" + uuid.uuid4().hex[:12]
    NGUON.parent.mkdir(parents=True, exist_ok=True)
    RA.parent.mkdir(parents=True, exist_ok=True)

    dong_ghi: list[str] = []

    def ghi(chu: str) -> None:
        print(chu)
        dong_ghi.append(chu)

    ghi(f"dau rieng          : {dau_rieng}")
    t0 = time.time()
    with NGUON.open("a", encoding="utf-8") as f:
        f.write(json.dumps({
            "thoi_diem": time.strftime("%Y-%m-%dT%H:%M:%S%z"),
            "buoi": "S07", "dich_vu": "thu-nghiem", "nguoi_dung": "van-hanh",
            "hanh_dong": "gieo-dong-se-bi-xoa", "ket_qua": "cho_phep", "ly_do": "",
            "thong_diep": f"dong nay se bi xoa khoi nguon, dau rieng {dau_rieng}",
        }, ensure_ascii=False) + "\n")
        f.flush()
        os.fsync(f.fileno())
    ghi(f"da gieo vao nguon  : {NGUON.relative_to(GOC)}")

    thay = None
    while time.time() - t0 < 120:
        thay = _do_tre.hoi_loki(dau_rieng)
        if thay:
            break
        time.sleep(0.5)
    if not thay:
        ghi("Loki chua nhan duoc dong nay sau 120 giay, khong tiep tuc thi nghiem.")
        ghi("Duong dan dang dut. Sua xong roi chay lai buoc nay.")
        RA.write_text("\n".join(dong_ghi) + "\n", encoding="utf-8")
        return 1
    be_rong = time.time() - t0
    ghi(f"loki da nhan sau   : {be_rong:.3f} giay")

    NGUON.write_text("", encoding="utf-8")
    ghi("da cat cut tep nguon: kich thuoc con 0 byte")

    con_o_loki = _do_tre.hoi_loki(dau_rieng)
    ghi(f"tim lai o loki     : {'CON' if con_o_loki else 'MAT'}")
    ghi("")
    ghi("Doc ket qua nay theo dung mot cach. Dong chu song sot khong phai vi Loki")
    ghi("manh, ma vi no da roi khoi mien tin cay noi no sinh ra truoc luc bi xoa.")
    ghi(f"Truoc moc {be_rong:.3f} giay, cung mot lenh xoa se lam mat han dong chu ay.")
    ghi("Do la be rong cua khoang nguy hiem, va rut ngan no la viec cua chang chuyen.")

    RA.write_text("\n".join(dong_ghi) + "\n", encoding="utf-8")
    print()
    print(f"Da ghi {RA.relative_to(GOC)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
