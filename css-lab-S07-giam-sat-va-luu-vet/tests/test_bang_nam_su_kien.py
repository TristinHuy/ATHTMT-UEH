"""Hiện vật thứ hai: bảng năm sự kiện. Đây là phần được chấm nặng nhất.

Ba phép kiểm ở đây đo phần máy đo được: đủ năm buổi, mỗi dòng có một câu truy vấn
thật và hai mã chuẩn nằm trong danh mục đã tra, và có ít nhất một dòng thừa nhận
không tìm được kèm lý do thuộc đúng ba loại. Chúng KHÔNG đo được điều quan trọng
nhất, là câu truy vấn của bạn có thật sự tìm ra đúng sự kiện ấy hay không. Máy
không đứng trong hệ thống của bạn nên không kiểm chứng được điều đó; người chấm
đọc phần ấy theo thang chấm.
"""
from __future__ import annotations

import re

import pytest

from tro_giup import (
    BANG,
    BUOI_BAT_BUOC,
    LY_DO_KHONG_TIM_DUOC,
    MA_ATTACK_CHO_PHEP,
    MA_CWE_CHO_PHEP,
    NGUON_DU_LIEU,
    doc_yaml,
    so_tu,
)

CHO_TRONG = re.compile(r"\|\s*\.\.\.\s*$|^\s*Điền\.?\s*$", re.IGNORECASE)
NGUON_CAM = ("bash_history", "zsh_history", ".history", "lịch sử dòng lệnh")


@pytest.fixture(scope="module")
def bang() -> dict:
    return doc_yaml(
        BANG,
        "Chép docs/bang-nam-su-kien.mau.yaml thành docs/bang-nam-su-kien.yaml rồi điền.",
    )


def test_du_nam_su_kien_dung_nam_buoi(bang):
    nguon = str(bang.get("nguon_du_lieu", "")).strip()
    assert nguon in NGUON_DU_LIEU, (
        f"Trường nguon_du_lieu là {nguon!r}, phải là một trong {sorted(NGUON_DU_LIEU)}. "
        "Người chấm cần biết bảng này nói về hệ thống của bạn hay về bộ dữ liệu thay thế."
    )
    if nguon == "thay_the":
        assert so_tu(bang.get("ly_do_dung_du_lieu_thay_the")) >= 6, (
            "Khai dùng dữ liệu thay thế thì phải nói vì sao, ít nhất sáu từ. "
            "Việc này không bị trừ điểm kiến thức, nhưng giấu nó thì có."
        )

    su_kien = bang.get("su_kien") or []
    assert len(su_kien) == 5, (
        f"Bảng có {len(su_kien)} dòng, đề yêu cầu đúng 5, mỗi buổi từ S02 tới S06 một dòng."
    )
    co = [str((s or {}).get("buoi", "")).strip() for s in su_kien]
    thieu = [b for b in BUOI_BAT_BUOC if b not in co]
    trung = sorted({b for b in co if co.count(b) > 1})
    assert not thieu, "Bảng thiếu dòng cho các buổi: " + ", ".join(thieu)
    assert not trung, "Bảng có hai dòng cho cùng một buổi: " + ", ".join(trung)


def test_moi_dong_co_truy_van_that_va_ma_chuan_dung_danh_muc(bang):
    hong = []
    for s in bang.get("su_kien") or []:
        s = s or {}
        buoi = str(s.get("buoi", "?")).strip()
        truy_van = str(s.get("truy_van", "")).strip()

        if not truy_van.startswith("{"):
            hong.append(f"{buoi}: câu truy vấn không mở bằng bộ chọn luồng dạng {{...}}.")
        elif f'buoi="{buoi}"' not in truy_van and "buoi=" not in truy_van:
            hong.append(f"{buoi}: bộ chọn luồng không lọc theo nhãn buoi, nên nó hỏi cả sáu nguồn.")
        if len(truy_van) < 20 or CHO_TRONG.search(truy_van):
            hong.append(f"{buoi}: câu truy vấn còn là chỗ trống của bản mẫu, chưa phải câu bạn đã chạy.")
        for cam in NGUON_CAM:
            if cam in truy_van.lower():
                hong.append(
                    f"{buoi}: câu truy vấn lấy lịch sử dòng lệnh làm nguồn. Đề cấm điều này, "
                    "vì lịch sử dòng lệnh là thứ biến mất đầu tiên trên một máy đã bị chiếm."
                )

        if so_tu(s.get("mo_ta_su_kien")) < 12:
            hong.append(f"{buoi}: mô tả sự kiện dưới 12 từ, chưa đủ để biết bạn tìm lại thứ gì.")

        ma_attack = str(s.get("ma_attack", "")).strip()
        ma_cwe = str(s.get("ma_cwe", "")).strip()
        if ma_attack not in MA_ATTACK_CHO_PHEP:
            hong.append(
                f"{buoi}: mã ATT&CK {ma_attack!r} không nằm trong danh mục của buổi "
                f"{sorted(MA_ATTACK_CHO_PHEP)}. Danh mục lấy từ bảng đối chiếu của buổi, "
                "bản ATT&CK content v19.2."
            )
        if ma_cwe not in MA_CWE_CHO_PHEP:
            hong.append(
                f"{buoi}: mã CWE {ma_cwe!r} không nằm trong danh mục của buổi "
                f"{sorted(MA_CWE_CHO_PHEP)}. Danh mục lấy từ CWE List 4.20."
            )

        tim_duoc = bool(s.get("tim_duoc"))
        try:
            so_dong = int(s.get("so_dong_khop", 0))
        except (TypeError, ValueError):
            so_dong = -1
            hong.append(f"{buoi}: so_dong_khop không phải số nguyên.")
        if tim_duoc and so_dong < 1:
            hong.append(f"{buoi}: khai tìm được nhưng so_dong_khop là {so_dong}.")
        if not tim_duoc and so_dong > 0:
            hong.append(f"{buoi}: khai không tìm được nhưng so_dong_khop là {so_dong}.")

    assert not hong, "Bảng năm sự kiện chưa đạt:\n  " + "\n  ".join(hong)


def test_co_dong_khong_tim_duoc_kem_ly_do_hop_le(bang):
    """Bắt buộc có ít nhất một dòng không tìm được, và đây không phải là bẫy.

    Một hệ thống ghi chép mà mọi câu hỏi đều có câu trả lời là một hệ thống chưa
    ai hỏi nó câu khó. Dòng không tìm được chỉ ra một chỗ im lặng, và ba lý do
    được nhận ứng với ba cách chữa khác nhau: bật thêm nguồn, thêm trường vào
    dòng nhật ký, hoặc kéo dài hạn giữ. Nói đúng loại im lặng là phần đáng giá
    nhất của cả bảng.
    """
    khong = [s for s in (bang.get("su_kien") or []) if not (s or {}).get("tim_duoc")]
    assert khong, (
        "Cả năm dòng đều khai tìm được. Đề bắt buộc ít nhất một dòng không tìm được.\n"
        "Nếu bạn thật sự tìm ra cả năm thì hãy hỏi thêm một câu khó hơn về một trong "
        "năm sự kiện ấy, ví dụ ai đã gây ra nó chứ không phải nó có xảy ra hay không, "
        "và ghi lại chỗ nhật ký im lặng."
    )
    hong = []
    for s in khong:
        buoi = str(s.get("buoi", "?")).strip()
        ly_do = str(s.get("ly_do_khong_tim_duoc", "")).strip()
        if ly_do not in LY_DO_KHONG_TIM_DUOC:
            hong.append(
                f"{buoi}: lý do {ly_do!r} không thuộc ba loại {sorted(LY_DO_KHONG_TIM_DUOC)}."
            )
        if so_tu(s.get("ghi_chu")) < 15:
            hong.append(
                f"{buoi}: ghi chú dưới 15 từ. Nói rõ bạn đã thử câu nào và vì sao bạn "
                "kết luận đây là loại im lặng ấy chứ không phải loại khác."
            )
    assert not hong, "Dòng không tìm được chưa đạt:\n  " + "\n  ".join(hong)
