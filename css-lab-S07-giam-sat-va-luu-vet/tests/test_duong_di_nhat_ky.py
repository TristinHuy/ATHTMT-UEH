"""Hiện vật thứ nhất: cấu hình cả đường dẫn, và số giây từng chặng.

Hai phép kiểm. Phép thứ nhất hỏi đường dẫn có đủ nguồn hay không, vì một chặng
thu thập bỏ sót một nguồn thì mọi câu hỏi về nguồn ấy sẽ nhận được sự im lặng,
và sự im lặng ấy trông giống hệt câu trả lời "không có gì xảy ra". Phép thứ hai
hỏi bạn có đo riêng từng chặng hay không, vì một con số tổng không nói được
chặng nào chậm, và mục 7.2 tồn tại chính để tách bốn việc ấy ra.
"""
from __future__ import annotations

import pytest

from tro_giup import BUOI_THU_THAP, CHANG_BAT_BUOC, DO_TRE, PROMTAIL, ROOT, doc_csv, doc_yaml, so_tu


def test_chang_chuyen_thu_du_sau_nguon():
    cau_hinh = doc_yaml(PROMTAIL, "Đây là tệp bạn sửa ở việc 2.")

    khach = cau_hinh.get("clients") or []
    dia_chi = " ".join(str((k or {}).get("url", "")) for k in khach)
    assert "loki" in dia_chi, (
        "Promtail chưa trỏ về kho nhật ký. Trường clients[].url phải là địa chỉ đẩy "
        "của Loki trong mạng compose, dạng http://loki:3100/loki/api/v1/push."
    )

    khoi = cau_hinh.get("scrape_configs") or []
    thay: dict[str, str] = {}
    thieu_duong_dan = []
    for k in khoi:
        for muc in (k or {}).get("static_configs") or []:
            nhan = (muc or {}).get("labels") or {}
            buoi = str(nhan.get("buoi", "")).strip()
            duong = str(nhan.get("__path__", "")).strip()
            if not buoi:
                continue
            thay[buoi] = duong
            if not duong:
                thieu_duong_dan.append(buoi)

    thieu = [b for b in BUOI_THU_THAP if b not in thay]
    assert not thieu, (
        "Chặng chuyển chưa thu các nguồn sau: " + ", ".join(thieu) + ".\n"
        "Mỗi buổi cần một khối trong scrape_configs, mang nhãn buoi và một __path__.\n"
        "Nguồn S07 cũng bắt buộc, vì hai phép đo của bài gieo dòng vào nhat-ky/S07/."
    )
    assert not thieu_duong_dan, (
        "Các nguồn sau có nhãn buoi nhưng không có __path__, nên Promtail không đọc gì: "
        + ", ".join(thieu_duong_dan)
    )

    sai_cho = {b: d for b, d in thay.items() if not d.startswith("/nhat-ky/")}
    assert not sai_cho, (
        "Các nguồn sau trỏ ra ngoài thư mục đã gắn vào container:\n  "
        + "\n  ".join(f"{b}: {d}" for b, d in sorted(sai_cho.items()))
        + "\nThư mục ./nhat-ky của máy bạn xuất hiện trong container ở /nhat-ky."
    )


def test_do_tre_do_rieng_tung_chang():
    dong = doc_csv(DO_TRE, "Chạy `make do-tre` sau khi đường dẫn đã thông.")
    if not dong:
        pytest.fail(f"{DO_TRE.name} không có dòng dữ liệu nào.")

    cot = set(dong[0])
    thieu_cot = {"chang", "mo_ta", "giay"} - cot
    assert not thieu_cot, (
        f"{DO_TRE.name} thiếu cột: {sorted(thieu_cot)}. Tệp này do bin/do-tre.py sinh ra; "
        "nếu bạn sửa tay thì giữ đúng ba cột ấy."
    )

    bang = {d["chang"].strip(): d for d in dong}
    thieu = [c for c in CHANG_BAT_BUOC if c not in bang]
    assert not thieu, (
        "Chưa đo các chặng: " + ", ".join(thieu) + ".\n"
        "Bốn chặng ứng với bốn việc ở mục 7.2, và tách chúng ra chính là nội dung "
        "của hiện vật này."
    )
    assert "tong" in bang, f"{DO_TRE.name} thiếu dòng tong."

    def giay(ten: str) -> float:
        try:
            return float(bang[ten]["giay"])
        except (TypeError, ValueError):
            pytest.fail(f"Chặng {ten} có giá trị giây không đọc được: {bang[ten]['giay']!r}")

    am = [c for c in CHANG_BAT_BUOC if giay(c) < 0]
    assert not am, f"Các chặng sau có độ trễ âm, tức phép đo hỏng: {am}"

    tong_khai = giay("tong")
    tong_cong = sum(giay(c) for c in CHANG_BAT_BUOC)
    assert abs(tong_khai - tong_cong) <= 0.05, (
        f"Dòng tong ghi {tong_khai:.3f} giây nhưng bốn chặng cộng lại là {tong_cong:.3f} giây. "
        "Hai số này phải khớp, vì bốn chặng là toàn bộ đường đi chứ không phải một phần của nó."
    )

    so_sai = [c for c in CHANG_BAT_BUOC if so_tu(bang[c].get("mo_ta")) < 4]
    assert not so_sai, (
        "Các chặng sau có mô tả quá ngắn để người chấm biết bạn đo từ mốc nào tới mốc nào: "
        + ", ".join(so_sai)
    )
