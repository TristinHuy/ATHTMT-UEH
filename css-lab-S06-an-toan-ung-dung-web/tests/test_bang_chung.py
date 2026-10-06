"""Bốn phép kiểm đọc bằng chứng bạn nộp, không đọc lời khai của bạn.

Phần này khác hẳn hai tệp kiểm trước. Ở đó bộ chấm dựng ứng dụng của bạn lên rồi
tự gọi, nên nó đo trực tiếp. Ở đây nó chỉ đọc lại dấu vết của những lần chạy đã
xảy ra trên máy bạn, nên nó kiểm được rằng các lần chạy ấy ĐÃ xảy ra và để lại
đúng hình dạng bằng chứng, và nó không kiểm được rằng bạn đã suy nghĩ. Phép cuối
trong bốn phép là phép xấp xỉ, và điều đó được nói thẳng ở chỗ nó.
"""
from __future__ import annotations

import hashlib
import json
import re

import pytest

from tro_giup import (
    BAO_CAO_CSP,
    DANH_DOI,
    MA_DUNG_LH1,
    MA_DUNG_LH2,
    NHAT_KY,
    QUET_SAU,
    QUET_TRUOC,
    SEMGREP_SAU,
    SEMGREP_TRUOC,
    XEP_LOAI,
    XEP_LOAI_HOP_LE,
    XEP_LOAI_SUA_DUOC,
    doc_json,
    doc_yaml,
    so_tu,
)

MA_LUAT_SEMGREP = "css-s06-phan-chieu-chua-thoat"
DIEM_NHAN_BAO_CAO = "/thu/bao-cao-csp"

TOI_THIEU_TU, TOI_DA_TU = 60, 300
TOI_THIEU_CANH_BAO = 5


def _ket_qua_semgrep(duong_dan, viec: str) -> int:
    """Đếm số phát hiện của đúng luật semgrep mà bài phát kèm."""
    bao_cao = doc_json(duong_dan, viec)
    ket = bao_cao.get("results")
    if ket is None:
        pytest.fail(
            f"{duong_dan.name} không có khóa results, nên nó không phải kết xuất của lần quét mã. "
            "Chạy `make quet-ma NHAN=truoc` và `make quet-ma NHAN=sau`, đừng tự dựng tệp này."
        )
    return sum(1 for phat_hien in ket if MA_LUAT_SEMGREP in str(phat_hien.get("check_id", "")))


def test_hai_lan_quet_truoc_va_sau_ghi_lai_duoc_thay_doi():
    """Hai bộ quét, hai câu hỏi khác nhau, và bài đòi cả hai chạy hai lần.

    Bộ quét nền hỏi thứ máy chủ trả về có nói đúng những gì nó phải nói không.
    Bộ quét mã hỏi bạn có tự viết một lỗi đã có tên chưa. Cả hai đều mù ở chỗ
    chúng không biết, đúng như mục 6.5 mô tả, nên không cái nào thay được cái kia.

    Phép kiểm đòi lần quét mã ĐỎ ở bản trước và XANH ở bản sau. Đây là hiện vật
    thứ hai của mục 6.7 viết thành một dòng cụ thể: một phép kiểm chưa bao giờ đỏ
    thì có thể đang kiểm nhầm chỗ, nên bằng chứng phải gồm cả lần nó đỏ.
    """
    hong = []

    ban_truoc = doc_json(QUET_TRUOC, "Chạy `make quet NHAN=truoc` trước khi sửa bất cứ thứ gì.")
    ban_sau = doc_json(QUET_SAU, "Chạy `make quet NHAN=sau` sau khi đã vá cả hai lỗ hổng.")
    if not ban_truoc or not ban_sau:
        hong.append("một trong hai tệp báo cáo quét nền rỗng.")
    bam_truoc = hashlib.sha256(QUET_TRUOC.read_bytes()).hexdigest()
    bam_sau = hashlib.sha256(QUET_SAU.read_bytes()).hexdigest()
    if bam_truoc == bam_sau:
        hong.append(
            "hai tệp báo cáo quét nền giống nhau tới từng byte, nên chúng là hai bản sao "
            "của một lần chạy. Lần quét sau phải chạy lại sau khi bạn đã vá, và nó phải "
            "khác lần trước ít nhất ở những cảnh báo bạn vừa đóng."
        )

    so_truoc = _ket_qua_semgrep(SEMGREP_TRUOC, "Chạy `make quet-ma NHAN=truoc` trước khi sửa mã.")
    so_sau = _ket_qua_semgrep(SEMGREP_SAU, "Chạy `make quet-ma NHAN=sau` sau khi đã sửa mã.")
    if so_truoc < 1:
        hong.append(
            f"lần quét mã trước khi vá không có phát hiện nào của luật {MA_LUAT_SEMGREP}. "
            "Luật ấy nhắm đúng lỗ hổng LH-1 ở trạng thái khởi đầu, nên nó phải đỏ ở bản "
            "trước; nếu nó im lặng thì bạn đã sửa mã rồi mới chạy lần quét đầu tiên."
        )
    if so_sau != 0:
        hong.append(
            f"lần quét mã sau khi vá còn {so_sau} phát hiện của luật {MA_LUAT_SEMGREP}. "
            "Đọc lại chỗ làm việc `việc 1`: chuỗi phải đi qua html.escape ngay tại chỗ ghép."
        )

    assert not hong, "Bằng chứng hai lần quét chưa đạt:\n  " + "\n  ".join(hong)


def test_bang_xep_loai_gan_dung_ma_chuan_va_ty_le_p_tinh_lai_duoc():
    """Hiện vật chấm nặng nhất của phần máy, và nó đo hai thứ tách nhau.

    Thứ nhất là mã chuẩn của hai lỗ hổng. Ô dễ sai nhất là hạng OWASP của LH-1:
    danh sách ánh xạ của A05:2025 là danh sách chứa CWE-79, còn A01:2025 và
    A10:2025 thì không, dù thân bài trình bày kịch bản chéo trang trong cùng mục
    với chuyện khác. Gọi đúng mã là một chuẩn đầu ra của buổi, không phải thủ tục.

    Thứ hai là con số p ở mục 6.5, tức tỉ lệ cảnh báo dẫn tới một thay đổi thật.
    Bộ chấm tính lại nó từ chính bảng bạn điền. Bước tính lại không phải là nghi
    ngờ: nó bảo đảm con số trong bài của bạn đúng là con số bảng của bạn sinh ra,
    chứ không phải con số của một lần xếp loại bạn đã sửa rồi quên cộng lại.
    """
    bang = doc_yaml(
        XEP_LOAI,
        "Chép docs/xep-loai-canh-bao.mau.yaml thành docs/xep-loai-canh-bao.yaml rồi điền.",
    )
    hong = []

    lo_hong = {str((m or {}).get("ma", "")).strip(): (m or {}) for m in bang.get("hai_lo_hong") or []}
    for ten, dung in (("LH-1", MA_DUNG_LH1), ("LH-2", MA_DUNG_LH2)):
        co = lo_hong.get(ten)
        if not co:
            hong.append(f"bảng thiếu khối mã chuẩn cho {ten}.")
            continue
        for khoa, gia_tri_dung in dung.items():
            khai = str(co.get(khoa, "")).strip()
            if khai != gia_tri_dung:
                hong.append(
                    f"{ten}: trường {khoa} khai {khai!r}, mã đúng theo bảng đối chiếu của "
                    f"buổi là {gia_tri_dung!r}."
                )

    canh_bao = bang.get("canh_bao") or []
    if len(canh_bao) < TOI_THIEU_CANH_BAO:
        hong.append(
            f"bảng mới có {len(canh_bao)} cảnh báo. Một lần quét nền ứng dụng huấn luyện "
            f"sinh ra nhiều hơn thế; dưới {TOI_THIEU_CANH_BAO} dòng nghĩa là bạn đang xếp "
            "loại một phần của báo cáo chứ không phải cả báo cáo."
        )
    tong_khai = bang.get("tong_canh_bao")
    if tong_khai != len(canh_bao):
        hong.append(
            f"trường tong_canh_bao ghi {tong_khai!r} nhưng bảng có {len(canh_bao)} dòng. "
            "Hai số này phải khớp, vì mẫu số của p lấy từ đây."
        )

    dem = {loai: 0 for loai in XEP_LOAI_HOP_LE}
    for muc in canh_bao:
        muc = muc or {}
        ma = str(muc.get("ma", "")).strip() or "(không mã)"
        loai = str(muc.get("xep_loai", "")).strip()
        if not str(muc.get("ten", "")).strip():
            hong.append(f"{ma}: thiếu tên cảnh báo, nên người chấm không biết dòng này nói về gì.")
        if loai not in XEP_LOAI_HOP_LE:
            hong.append(f"{ma}: xep_loai là {loai!r}, phải là một trong {sorted(XEP_LOAI_HOP_LE)}.")
            continue
        dem[loai] += 1
        if loai == "khong_phai_canh_bao_that" and so_tu(muc.get("ghi_chu")) < 8:
            hong.append(
                f"{ma}: xếp là không phải cảnh báo thật mà ghi chú dưới 8 từ. Đây là nhóm "
                "tốn kém nhất khi xếp sai, vì một cảnh báo thật bị đẩy vào đây thì không ai "
                "quay lại nhìn nó nữa; nói rõ bạn dựa vào đâu để loại nó."
            )

    sua_duoc = sum(dem[loai] for loai in XEP_LOAI_SUA_DUOC)
    if canh_bao and sua_duoc == 0:
        hong.append(
            "không cảnh báo nào được xếp vào hai nhóm sửa được, nên p bằng 0 và cả đoạn "
            "văn về mức đầu tư mất căn cứ. Xem lại: một báo cáo mà không dòng nào đáng "
            "sửa thường là dấu hiệu của việc xếp loại quá tay, không phải của một ứng "
            "dụng lành."
        )
    if canh_bao:
        p_tinh_lai = round(sua_duoc / len(canh_bao), 4)
        try:
            p_khai = float(bang.get("ty_le_p"))
        except (TypeError, ValueError):
            hong.append(f"trường ty_le_p là {bang.get('ty_le_p')!r}, không đọc được thành số.")
        else:
            if abs(p_khai - p_tinh_lai) > 0.005:
                hong.append(
                    f"ty_le_p khai {p_khai}, tính lại từ chính bảng của bạn được {p_tinh_lai} "
                    f"({sua_duoc} dòng sửa được trên {len(canh_bao)} dòng)."
                )

    assert not hong, "Bảng xếp loại cảnh báo chưa đạt:\n  " + "\n  ".join(hong)


def test_bao_cao_vi_pham_va_nhat_ky_chung_minh_chang_chi_bao_cao_da_chay():
    """Bằng chứng của chặng chỉ báo cáo, và là đầu vào của buổi S7.

    Chặng này chỉ thu được bằng chứng khi lớp thứ nhất còn hở, vì sau khi bạn mã
    hóa đầu ra thì chuỗi lạ không vào tới trang nữa và không còn gì để trình duyệt
    chặn. Thứ tự làm việc trong README có lý do là chỗ đó, và nó cũng chính là
    điều bạn đang chứng minh: hai lớp chặn hai đường khác nhau.

    Dòng nhật ký tương ứng không chỉ phục vụ bài này. Buổi S7 sẽ bắt bạn tìm lại
    chính nó từ kho nhật ký, khi không ai nhắc bạn nó đã xảy ra lúc nào.
    """
    hong = []

    if not BAO_CAO_CSP.exists():
        hong.append(
            "chưa có evidence/S6/bao-cao-csp.jsonl. Đặt che_do về bao-cao, mở trình duyệt "
            "vào trang tra cứu với một tải trọng thử, rồi chạy `make thu-bao-cao`."
        )
    else:
        dong_hop_le = 0
        for dong in BAO_CAO_CSP.read_text(encoding="utf-8").splitlines():
            dong = dong.strip()
            if not dong:
                continue
            try:
                bao_cao = json.loads(dong)
            except json.JSONDecodeError:
                continue
            if "directive" in json.dumps(bao_cao).lower() or "csp-report" in dong.lower():
                dong_hop_le += 1
        if dong_hop_le < 1:
            hong.append(
                "evidence/S6/bao-cao-csp.jsonl không có dòng nào là báo cáo vi phạm thật. "
                "Trình duyệt gửi một tài liệu JSON mỗi lần nó chặn hoặc lẽ ra đã chặn một "
                "thứ; tệp này phải chứa ít nhất một tài liệu như vậy."
            )

    if not NHAT_KY.exists():
        hong.append(
            "chưa có evidence/S6/nhat-ky.txt. Chạy `make export-evidence`, bước ấy lấy nhật "
            "ký của ứng dụng ra khỏi container. Buổi S7 lấy tệp này làm một trong sáu nguồn."
        )
    else:
        co_dong = any(
            DIEM_NHAN_BAO_CAO in dong
            for dong in NHAT_KY.read_text(encoding="utf-8").splitlines()
        )
        if not co_dong:
            hong.append(
                f"evidence/S6/nhat-ky.txt không có dòng nào ghi lại một lần gọi tới "
                f"{DIEM_NHAN_BAO_CAO}. Nhật ký được lấy ra sau khi container đã bị xóa thì "
                "rỗng; chạy `make export-evidence` trước `make down`."
            )

    assert not hong, "Bằng chứng lớp thứ hai chưa đủ:\n  " + "\n  ".join(hong)


def test_doan_danh_doi_dung_so_da_do():
    """Phép xấp xỉ, và nói thẳng ra là xấp xỉ.

    Máy đếm được từ và tìm được một con số trong văn bản; máy không đọc được lập
    luận. Phép này chặn hai thứ: không nộp, và nộp một đoạn viết mà không nhìn vào
    số đo của chính mình. Một đoạn qua được phép kiểm này vẫn mất điểm ở thang chấm
    nếu phép tính công sức của nó không có căn cứ, hoặc nếu nó chỉ kể lại việc đã
    làm thay vì nói ra một lựa chọn.
    """
    bang = doc_yaml(XEP_LOAI, "Đoạn văn này đứng trên con số của bảng xếp loại.")
    canh_bao = bang.get("canh_bao") or []
    tong = len(canh_bao)
    khong_that = sum(
        1 for m in canh_bao
        if str((m or {}).get("xep_loai", "")).strip() == "khong_phai_canh_bao_that"
    )

    if not DANH_DOI.exists():
        pytest.fail(
            f"Không thấy {DANH_DOI.name}. Viết một đoạn dưới {TOI_DA_TU} từ trả lời hai câu: "
            "nhóm cảnh báo nào bạn xếp nhầm nhiều nhất và bạn biết mình nhầm nhờ đâu, và nếu "
            "chỉ có một giờ mỗi tuần cho việc này thì bạn tiêu giờ ấy vào đâu."
        )
    chu = DANH_DOI.read_text(encoding="utf-8")
    dem = len(chu.split())
    hong = []
    if not TOI_THIEU_TU <= dem <= TOI_DA_TU:
        hong.append(
            f"đoạn văn dài {dem} từ. Đề đặt trần {TOI_DA_TU} từ và sàn {TOI_THIEU_TU} từ. "
            "Trần có mặt vì hai câu hỏi này trả lời được gọn khi bạn đã đo; sàn có mặt vì "
            "một câu trả lời không kèm phép tính thì không kiểm được."
        )

    for so, y_nghia in ((tong, "tổng số cảnh báo bạn đã xếp loại"),
                        (khong_that, "số cảnh báo bạn xếp là không phải cảnh báo thật")):
        if not re.search(rf"(?<!\d){so}(?!\d)", chu):
            hong.append(
                f"đoạn văn không nhắc tới con số {so}, tức {y_nghia}. Phép tính công sức "
                "phải bắt đầu từ số đo của chính bạn, nếu không nó nói về một lần quét khác."
            )

    thap = chu.lower()
    if "phút" not in thap and "phut" not in thap:
        hong.append(
            "đoạn văn không có đơn vị phút. Mục 6.5 đo công sức cho mỗi thay đổi thật bằng "
            "t chia p phút, và một câu trả lời không có đơn vị thì không so được với thứ gì."
        )

    assert not hong, "Đoạn đánh đổi chưa đạt:\n  " + "\n  ".join(hong)
