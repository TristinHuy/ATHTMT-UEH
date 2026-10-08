"""Hiện vật thứ ba: quy tắc phát hiện, phép đo của nó, và giá của việc báo nhầm.

Bốn phép kiểm, và chúng đo bốn thứ khác nhau. Quy tắc có đọc được không. Quy tắc
có nói về hành vi hay chỉ học thuộc tập mẫu. Con số bạn khai có tính lại được từ
chính quy tắc ấy không, và có đạt hai ngưỡng không. Cuối cùng, đoạn văn của bạn
có đứng trên con số vừa đo hay đứng trên một con số nào khác.

Phép cuối là phép yếu nhất trong bốn phép, và điều đó phải nói thẳng. Máy đếm
được số từ và tìm được một con số trong văn bản, nhưng nó không đọc được lập luận.
Một đoạn văn qua được phép kiểm ấy vẫn mất điểm ở thang chấm nếu phép tính phút
công không có căn cứ.
"""
from __future__ import annotations

import re

import pytest

from tro_giup import (
    DO_CHINH_XAC,
    GIA_BAO_NHAM,
    NGUONG_DO_CHINH_XAC,
    NGUONG_DO_PHU,
    QUY_TAC,
    TAP_CO_NHAN,
    TRUONG_CAM_TRONG_QUY_TAC,
    doc_json,
    nap_bo_chay,
)

TOI_DA_TU = 300
TOI_THIEU_TU = 60


@pytest.fixture(scope="module")
def bo_chay():
    return nap_bo_chay()


@pytest.fixture(scope="module")
def quy_tac(bo_chay):
    try:
        return bo_chay.doc_quy_tac(QUY_TAC)
    except bo_chay.QuyTacHong as loi:
        pytest.fail(f"Quy tắc chưa đọc được.\n{loi}")


@pytest.fixture(scope="module")
def ket_do(bo_chay, quy_tac):
    tap = bo_chay.doc_tap_co_nhan(TAP_CO_NHAN)
    return bo_chay.do_tren_tap(quy_tac, tap)


def test_quy_tac_doc_duoc_theo_tap_con_sigma(quy_tac):
    """Phép này chạy trước mọi phép khác vì nó là điều kiện của chúng.

    Nó cũng kiểm hai trường mà người ta hay bỏ trống cho nhanh. Trường
    falsepositives là chỗ người trực lúc nửa đêm đọc để quyết định có gọi điện cho
    ai không, nên bỏ trống nó là đẩy việc phán đoán sang một người đang buồn ngủ.
    Trường level nói quy tắc này đáng dựng ai dậy, và một quy tắc không xếp mức thì
    hoặc là mọi thứ đều khẩn cấp, hoặc là không có gì khẩn cấp cả."""
    assert len(quy_tac.tieu_de.split()) >= 3, (
        f"Tiêu đề {quy_tac.tieu_de!r} quá ngắn. Nó là dòng đầu tiên người trực đọc, "
        "nên nó phải nói được quy tắc bắt hành vi gì."
    )
    assert quy_tac.muc in {"informational", "low", "medium", "high", "critical"}, (
        f"Trường level là {quy_tac.muc!r}. Sigma nhận năm mức: informational, low, "
        "medium, high, critical."
    )
    thuc_chat = [x for x in quy_tac.bao_nham_da_biet if len(x.split()) >= 5]
    assert thuc_chat, (
        "Trường falsepositives còn trống hoặc còn là câu hướng dẫn của bản phát. "
        "Sau khi chạy `make do-chinh-xac`, bạn ĐÃ BIẾT nguồn báo nhầm của mình là gì. "
        "Viết nó ra đây, kèm cách nhận ra nó."
    )


def test_quy_tac_khong_neo_vao_truong_rieng_cua_tap_mau(quy_tac):
    """Một quy tắc khớp đúng những bản ghi đã biết là đáp án chép lại, không phải
    phát hiện. Trên dữ liệu thật, nơi không có trường id và không có nhãn sẵn, nó
    bắt được đúng không bản ghi nào."""
    pham = sorted(quy_tac.truong_da_dung & TRUONG_CAM_TRONG_QUY_TAC)
    assert not pham, (
        f"Quy tắc lọc theo trường {pham}, tức trường chỉ có nghĩa bên trong tập mẫu này.\n"
        "Trường id là số thứ tự bản ghi, trường nhan là đáp án, trường thoi_diem chỉ đúng "
        "cho đúng ngày đã gieo. Viết lại quy tắc theo hành vi: cái gì bị từ chối, vì lý do "
        "gì, và chủ thể nào không phải nguồn báo nhầm đã biết."
    )
    assert len(quy_tac.truong_da_dung) >= 2, (
        f"Quy tắc chỉ nhìn một trường: {sorted(quy_tac.truong_da_dung)}. "
        "Bản thô đi kèm đề cũng chỉ nhìn một trường, và nó có độ chính xác thấp tới mức "
        "người trực sẽ tắt chuông. Chạy `make do-chinh-xac`, đọc danh sách bắt nhầm, "
        "rồi tìm đặc điểm phân biệt."
    )


def test_do_chinh_xac_tinh_lai_duoc_va_dat_nguong(ket_do):
    """Bộ chấm tính lại phép đo từ chính quy tắc bạn nộp, rồi so với tệp bạn khai.

    Bước so lại không phải là nghi ngờ. Nó bảo đảm rằng con số trong bài của bạn
    đúng là con số quy tắc HIỆN TẠI sinh ra, chứ không phải con số của một phiên
    bản bạn đã sửa từ lâu rồi quên chạy lại. Đây cũng là kỷ luật của cả học phần:
    một phép đo không tái lập được thì không phải là phép đo.
    """
    khai = doc_json(DO_CHINH_XAC, "Chạy `make do-chinh-xac` rồi commit tệp sinh ra.")

    lech = []
    for khoa in ("TP", "FP", "FN", "TN", "tong_ban_ghi"):
        if int(khai.get(khoa, -1)) != int(ket_do[khoa]):
            lech.append(f"{khoa}: bạn khai {khai.get(khoa)!r}, tính lại được {ket_do[khoa]}")
    for khoa in ("do_chinh_xac", "do_phu"):
        if abs(float(khai.get(khoa, -1)) - float(ket_do[khoa])) > 0.001:
            lech.append(f"{khoa}: bạn khai {khai.get(khoa)!r}, tính lại được {ket_do[khoa]}")
    assert not lech, (
        "Tệp evidence/S7/do-chinh-xac.json không khớp với quy tắc hiện tại:\n  "
        + "\n  ".join(lech)
        + "\nChạy lại `make do-chinh-xac` sau mỗi lần sửa quy tắc."
    )

    assert ket_do["do_phu"] >= NGUONG_DO_PHU, (
        f"Độ phủ đạt {ket_do['do_phu']}, ngưỡng là {NGUONG_DO_PHU}. "
        f"Quy tắc bỏ sót {ket_do['FN']} sự kiện đáng bắt: {ket_do['bo_sot']}.\n"
        "Đọc các bản ghi ấy trong nhan/tap-co-nhan.jsonl và hỏi điều kiện nào của bạn "
        "đã loại chúng ra. Bỏ sót nguy hiểm hơn báo nhầm, vì người ta sẽ tin vào sự im lặng."
    )
    assert ket_do["do_chinh_xac"] >= NGUONG_DO_CHINH_XAC, (
        f"Độ chính xác đạt {ket_do['do_chinh_xac']}, ngưỡng là {NGUONG_DO_CHINH_XAC}. "
        f"Quy tắc bắt nhầm {ket_do['FP']} bản ghi: {ket_do['bat_nham']}.\n"
        "Mở từng bản ghi ấy ra và tìm điều làm chúng khác với sự kiện thật. Có hai nhóm: "
        "một nhóm bị từ chối vì lý do không liên quan tới chứng thực, và một nhóm lặp lại "
        "theo lịch, tức là nguồn báo nhầm đã biết chứ không phải sự cố."
    )


def test_doan_gia_cua_bao_nham_dung_so_da_do(ket_do):
    """Hai câu hỏi của mục 7.7, và đoạn văn phải trả lời cả hai bằng số của chính bạn."""
    if not GIA_BAO_NHAM.exists():
        pytest.fail(
            f"Không thấy {GIA_BAO_NHAM.name}. Viết một đoạn dưới {TOI_DA_TU} từ trả lời "
            "hai câu: với tỉ lệ báo nhầm vừa đo, người trực mất bao nhiêu phút mỗi ngày "
            "cho riêng quy tắc này, và nếu chỉ giữ nhật ký bảy ngày thay vì chín mươi thì "
            "câu hỏi nào trong bảng năm sự kiện không còn trả lời được."
        )
    chu = GIA_BAO_NHAM.read_text(encoding="utf-8")
    dem = len(chu.split())
    assert TOI_THIEU_TU <= dem <= TOI_DA_TU, (
        f"Đoạn văn dài {dem} từ. Đề đặt trần {TOI_DA_TU} từ và sàn {TOI_THIEU_TU} từ. "
        "Trần có mặt vì hai câu hỏi này trả lời được gọn khi bạn đã đo; sàn có mặt vì "
        "một câu trả lời không kèm phép tính thì không kiểm được."
    )

    fp = int(ket_do["FP"])
    co_so = re.search(rf"(?<!\d){fp}(?!\d)", chu) is not None
    assert co_so, (
        f"Đoạn văn không nhắc tới con số {fp}, tức số lần bắt nhầm mà quy tắc của bạn "
        "sinh ra trên hai mươi tư giờ dữ liệu. Phép tính phút công phải bắt đầu từ con "
        "số ấy, nếu không thì nó nói về một quy tắc khác."
    )
    thap = chu.lower()
    assert "phút" in thap or "phut" in thap, (
        "Đoạn văn không có đơn vị phút. Câu hỏi thứ nhất hỏi công sức của người trực "
        "mỗi ngày, và một câu trả lời không có đơn vị thì không so được với thứ gì."
    )
    co_bay = re.search(r"(?<!\d)7(?!\d)|bảy|bay ngay", chu, re.IGNORECASE) is not None
    co_chin_muoi = re.search(r"(?<!\d)90(?!\d)|chín mươi|chin muoi", chu, re.IGNORECASE) is not None
    assert co_bay and co_chin_muoi, (
        "Đoạn văn chưa trả lời câu hỏi thứ hai. Nó phải đối chiếu hạn giữ bảy ngày với "
        "hạn giữ chín mươi ngày và chỉ ra dòng nào trong bảng năm sự kiện mất câu trả lời."
    )
