"""Ba phép kiểm đọc chính hai tệp bạn cấu hình: vùng định danh và tệp compose.

Chúng không gọi máy chủ danh tính. Chúng đọc thứ bạn khai, vì thứ bạn khai là
thứ máy chủ nạp lúc dựng, và vì một phép kiểm đọc cấu hình chạy được trên máy
người chấm mà không cần dựng gì. Giới hạn đi kèm phải nói thẳng: các phép này
xác nhận cấu hình ĐÚNG HÌNH DẠNG, không xác nhận vùng định danh đã khởi động
được với cấu hình ấy. Việc sau do `make up` và `make nam-phep-kiem` trả lời.
"""
from __future__ import annotations

import re

import pytest
import yaml

from tro_giup import (
    BO_NHO_TOI_THIEU_KIB,
    COMPOSE,
    HAN_THE_LON_NHAT,
    HAN_THE_NHO_NHAT,
    NGUOI_NHAN,
    VUNG,
    doc_json,
)


@pytest.fixture(scope="module")
def vung() -> dict:
    return doc_json(VUNG, "Đây là tệp vùng định danh sinh viên sửa ở việc 4 và việc 5.")


@pytest.fixture(scope="module")
def moi_truong() -> dict:
    """Ba tham số hàm băm nằm ở biến môi trường của máy chủ, không nằm trong vùng."""
    than = yaml.safe_load(COMPOSE.read_text(encoding="utf-8")) or {}
    dich_vu = (than.get("services") or {}).get("may-danh-tinh") or {}
    moi = dich_vu.get("environment") or {}
    if isinstance(moi, list):
        moi = dict(m.split("=", 1) for m in moi if "=" in m)
    return {str(k).upper(): str(v) for k, v in moi.items()}


def _so(chuoi: str) -> int | None:
    chuoi = chuoi.strip().strip("\"'")
    return int(chuoi) if chuoi.lstrip("-").isdigit() else None


def test_kho_mat_khau_dung_ham_bam_ton_bo_nho_va_bo_luat_xoay_vong(vung, moi_truong):
    """Hai nửa của §5.3 trong một phép kiểm, vì chúng là một quyết định.

    Nửa thứ nhất là chỗ nên tiêu tiền: hàm băm phải tốn bộ nhớ, và ba tham số của
    nó phải do bạn đặt sau khi đo trên máy thật. Ngưỡng 64 MiB lấy từ RFC 9106 §4,
    bộ tham số dành cho máy eo hẹp bộ nhớ, tức cận DƯỚI chứ không phải đích đến.

    Nửa thứ hai là chỗ không nên tiêu: NIST SP 800-63B bản 31/07/2025, §3.1.1.2,
    cấm ép đổi mật khẩu định kỳ và cấm luật ép trộn ký tự, cả hai ở mức SHALL NOT.
    Trạng thái khởi đầu của bài mang đủ ba luật ấy, và việc của bạn là gỡ chúng
    rồi nói được vì sao gỡ."""
    luat = str(vung.get("passwordPolicy", ""))
    hong = []

    if "argon2" not in luat.lower():
        hong.append(
            f"passwordPolicy đang là {luat!r}, chưa nêu hàm băm tốn bộ nhớ. "
            "Băm bằng hàm nhanh là CWE-916."
        )
    for cam, vi_sao in (
        ("forceExpiredPasswordChange", "ép đổi mật khẩu định kỳ, SP 800-63B §3.1.1.2 cấm"),
        ("specialChars", "luật ép ký tự đặc biệt, cùng mục ấy cấm"),
        ("upperCase", "luật ép chữ hoa, cùng mục ấy cấm"),
    ):
        if cam.lower() in luat.lower():
            hong.append(f"passwordPolicy còn {cam}: {vi_sao}.")

    bo_nho = next((_so(v) for k, v in moi_truong.items() if "ARGON2" in k and "MEMORY" in k), None)
    vong_lap = next((_so(v) for k, v in moi_truong.items() if "ARGON2" in k and "ITERATIONS" in k), None)
    song_song = next((_so(v) for k, v in moi_truong.items() if "ARGON2" in k and "PARALLELISM" in k), None)
    if bo_nho is None or vong_lap is None or song_song is None:
        hong.append(
            "docker-compose.yml chưa đặt đủ ba tham số bộ nhớ, số vòng lặp và mức song song "
            "cho hàm băm ở dịch vụ may-danh-tinh. Tên biến tra trong tài liệu máy chủ danh tính."
        )
    elif bo_nho < BO_NHO_TOI_THIEU_KIB:
        hong.append(
            f"tham số bộ nhớ đang là {bo_nho} KiB, dưới mức {BO_NHO_TOI_THIEU_KIB} KiB tức 64 MiB "
            "của RFC 9106 §4. Đo lại bằng `make do-argon2` rồi chọn con số có thể lập luận để bảo vệ."
        )

    assert not hong, "Kho mật khẩu chưa đạt:\n  " + "\n  ".join(hong)


def test_yeu_to_thu_hai_bat_va_co_gioi_han_so_lan_hoi(vung):
    """Yếu tố thứ hai và giá của nó, §5.4, cũng là một quyết định chứ không phải hai.

    Bật mã một lần mà không giới hạn số lần hỏi là để nguyên đường tấn công
    T1621: hỏi mãi cho tới khi người dùng bấm bừa lúc nửa đêm. Trang kỹ thuật ấy
    ghi biện pháp M1032 bằng đúng chữ giới hạn tần suất yêu cầu, nên hai nửa
    dưới đây phải cùng có mặt."""
    hong = []

    if str(vung.get("otpPolicyType", "")).lower() != "totp":
        hong.append("otpPolicyType phải là totp.")
    if int(vung.get("otpPolicyDigits", 0) or 0) < 6:
        hong.append("otpPolicyDigits dưới 6 chữ số.")

    hanh_dong = {h.get("alias"): h for h in vung.get("requiredActions") or []}
    totp = hanh_dong.get("CONFIGURE_TOTP")
    if not totp:
        hong.append("requiredActions không có mục CONFIGURE_TOTP.")
    else:
        if not totp.get("enabled"):
            hong.append("CONFIGURE_TOTP còn tắt, nên không ai ghi danh được yếu tố thứ hai.")
        if not totp.get("defaultAction"):
            hong.append(
                "CONFIGURE_TOTP chưa đặt làm hành động mặc định, nên nó chỉ là tùy chọn. "
                "Một yếu tố thứ hai mà người dùng phải tự đi tìm thì trên thực tế không tồn tại."
            )

    if not vung.get("bruteForceProtected"):
        hong.append("bruteForceProtected còn tắt, tức không có giới hạn số lần hỏi, tức T1621 để ngỏ.")
    else:
        so_lan = int(vung.get("failureFactor", 0) or 0)
        if not 1 <= so_lan <= 10:
            hong.append(f"failureFactor đang là {so_lan}, hãy đặt trong khoảng 1 tới 10 và nói được vì sao.")

    assert not hong, "Yếu tố thứ hai chưa đứng vững:\n  " + "\n  ".join(hong)


def test_than_khach_khong_de_ngo_va_han_the_du_ngan(vung):
    """Ba chỗ để ngỏ trong trạng thái khởi đầu, và cả ba đều thuộc A01:2025.

    Đường chuyển hướng dạng ký tự đại diện cho phép đẩy mã ủy quyền tới bất cứ
    đâu. Luồng ngầm trả thẻ thẳng trong địa chỉ, nên tấm thẻ nằm lại trong nhật
    ký và trong lịch sử trình duyệt. Hạn thẻ một giờ là khoảng thời gian tấm thẻ
    sống thêm sau khi bạn thu hồi quyền, đúng câu hỏi mà hiện vật thứ ba bắt bạn
    đo bằng đồng hồ."""
    hong = []
    than_khach = {t.get("clientId"): t for t in vung.get("clients") or []}
    chinh = than_khach.get(NGUOI_NHAN)
    if chinh is None:
        hong.append(f"vùng định danh không còn thân khách {NGUOI_NHAN}.")
    else:
        for duong in chinh.get("redirectUris") or []:
            if duong.strip() in {"*", "/*"} or duong.strip().endswith("://*"):
                hong.append(f"redirectUris còn {duong!r}, tức nhận chuyển hướng tới bất cứ đâu.")
        for goc in chinh.get("webOrigins") or []:
            if goc.strip() == "*":
                hong.append("webOrigins còn ký tự đại diện.")
        if chinh.get("implicitFlowEnabled"):
            hong.append("luồng ngầm còn bật, nên thẻ đi trong địa chỉ và nằm lại trong nhật ký.")
        if chinh.get("publicClient") and (chinh.get("attributes") or {}).get("pkce.code.challenge.method") != "S256":
            hong.append(
                "thân khách công khai mà chưa đòi PKCE với S256. Không có nó thì mã ủy quyền "
                "bị chặn giữa đường là dùng lại được."
            )

    han = int(vung.get("accessTokenLifespan", 0) or 0)
    if not HAN_THE_NHO_NHAT <= han <= HAN_THE_LON_NHAT:
        hong.append(
            f"accessTokenLifespan đang là {han} giây, đề yêu cầu trong khoảng "
            f"{HAN_THE_NHO_NHAT} tới {HAN_THE_LON_NHAT}. Cận dưới để bài còn chạy trong một tiết, "
            "cận trên vì đó là quãng thời gian một tấm thẻ sống thêm sau khi quyền đã bị thu hồi."
        )

    assert not hong, "Thân khách và hạn thẻ chưa đạt:\n  " + "\n  ".join(hong)
