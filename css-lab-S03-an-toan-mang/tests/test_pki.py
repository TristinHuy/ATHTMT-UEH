"""Kiểm bộ chứng thư bạn đã dựng, bằng chính openssl.

Sáu phép kiểm dưới đây không đọc lời khai của tệp cấu hình. Chúng mở từng chứng
thư ra, dựng lại chuỗi tin cậy, so tên, so khóa, và đo hạn. Đó là bậc bằng chứng
thứ hai ở §3.5 của giáo trình: quan sát hệ thống đang có, thay vì tin điều người
cấu hình định làm.

Ba mã điểm yếu của §3.3 nằm rải trong sáu phép này. CWE-295 và CWE-296 ở phép
kiểm chuỗi, CWE-297 ở phép so tên, CWE-298 ở phép đo hạn.
"""
from __future__ import annotations

from datetime import datetime, timezone

import pytest

from tro_giup import HAN_TOI_DA_NGAY, PKI, TEN_DICH_VU, doc_ngay, openssl

CAN_CO = [
    "ca/ca.crt", "ca/ca.key",
    "may-chu/may-chu.crt", "may-chu/may-chu.key",
    "khach/khach.crt", "khach/khach.key",
    "ca-ngoai/ca-ngoai.crt", "ca-ngoai/ca-ngoai.key",
    "ca-ngoai/khach-ngoai.crt", "ca-ngoai/khach-ngoai.key",
]


@pytest.fixture(scope="module", autouse=True)
def du_tep_pki():
    """Dừng cả tệp này ngay khi thiếu tệp, thay vì để sáu phép cùng đỏ vì một
    nguyên nhân. Sáu thông báo cho một lỗi làm người đọc mất dấu lỗi thật."""
    thieu = [ten for ten in CAN_CO if not (PKI / ten).exists()]
    if thieu:
        pytest.fail(
            "Thiếu tệp trong pki/:\n  " + "\n  ".join(thieu)
            + "\nĐọc pki/README.md, phần danh sách tệp. Tên tệp là một phần của đề."
        )


def xac_minh(chung_thu: str, ca: str):
    return openssl("verify", "-CAfile", str(PKI / ca), str(PKI / chung_thu))


def khoa_cong_khai_cua_chung_thu(ten: str) -> str:
    return openssl("x509", "-in", str(PKI / ten), "-noout", "-pubkey").stdout.strip()


def khoa_cong_khai_cua_khoa_rieng(ten: str) -> str:
    return openssl("pkey", "-in", str(PKI / ten), "-pubout").stdout.strip()


def test_ca_noi_bo_dung_la_mot_ca():
    """Một chứng thư tự ký chưa phải một tổ chức cấp chứng thư. Thiếu ràng buộc
    cơ bản CA:TRUE thì openssl từ chối dùng nó để bảo lãnh cho chứng thư khác, và
    mọi phép kiểm chuỗi phía sau sụp theo. Đây là CWE-296 ở dạng sớm nhất."""
    rang_buoc = openssl("x509", "-in", str(PKI / "ca/ca.crt"), "-noout", "-ext", "basicConstraints")
    assert "CA:TRUE" in rang_buoc.stdout, (
        "ca/ca.crt không mang basicConstraints CA:TRUE, nên nó không ký được cho ai.\n"
        f"openssl đọc được: {rang_buoc.stdout.strip() or rang_buoc.stderr.strip()!r}\n"
        "Dựng lại CA với addext basicConstraints=critical,CA:TRUE,pathlen:0."
    )
    tu_ky = xac_minh("ca/ca.crt", "ca/ca.crt")
    assert tu_ky.returncode == 0, (
        "ca/ca.crt không tự xác minh được, tức nó không phải một gốc tin cậy hoàn chỉnh.\n"
        f"openssl nói: {tu_ky.stderr.strip()}"
    )


def test_chung_thu_may_chu_do_ca_noi_bo_ky_va_khop_khoa():
    """Hai câu hỏi khác nhau, và cả hai đều phải đúng thì máy chủ mới phục vụ được.
    Chuỗi có dựng ngược về CA của bạn không, và khóa riêng đang nằm cạnh chứng thư
    có đúng là khóa của chứng thư ấy không. Lệch khóa là lỗi hay gặp nhất khi
    người ta cấp lại chứng thư mà quên thay khóa, và nginx sẽ từ chối khởi động."""
    ket_qua = xac_minh("may-chu/may-chu.crt", "ca/ca.crt")
    assert ket_qua.returncode == 0, (
        "may-chu.crt không dựng ngược được về ca/ca.crt.\n"
        f"openssl nói: {ket_qua.stderr.strip() or ket_qua.stdout.strip()}\n"
        "Ký lại chứng thư máy chủ bằng đúng CA nội bộ, không phải bằng CA ngoài."
    )
    assert khoa_cong_khai_cua_chung_thu("may-chu/may-chu.crt") == khoa_cong_khai_cua_khoa_rieng(
        "may-chu/may-chu.key"
    ), (
        "may-chu.key không phải khóa riêng của may-chu.crt. Cấp lại chứng thư từ "
        "đúng yêu cầu ký sinh ra bởi khóa này."
    )


def test_ten_tren_chung_thu_khop_ten_dich_vu():
    """Chỗ phản trực giác nhất của §3.3. Một chứng thư ký hợp lệ vẫn có thể mang
    tên của người khác, nên kiểm chuỗi mà bỏ so tên là để ngỏ đúng cánh cửa mà
    CWE-297 và kỹ thuật T1557 đi qua. Tên phải nằm ở subjectAltName, vì các thư
    viện hiện nay không đọc CN để so tên nữa."""
    ext = openssl("x509", "-in", str(PKI / "may-chu/may-chu.crt"), "-noout", "-ext", "subjectAltName")
    ra = ext.stdout
    assert "subjectAltName" in ra or "DNS:" in ra, (
        "may-chu.crt không có phần subjectAltName nào. Cấp lại với "
        f"addext subjectAltName=DNS:{TEN_DICH_VU}."
    )
    assert f"DNS:{TEN_DICH_VU}" in ra, (
        f"subjectAltName của may-chu.crt không chứa DNS:{TEN_DICH_VU}.\n"
        f"Đang có: {ra.strip()!r}\n"
        f"Máy khách gọi tới bằng tên {TEN_DICH_VU} trong mạng compose, nên tên trên "
        "chứng thư phải đúng tên đó, không phải localhost."
    )


def test_han_chung_thu_may_chu_nam_trong_khoang_cho_phep():
    """Hạn là một quyết định quản trị, không phải một quyết định mật mã. §3.4 tính
    ra rằng hạn ngắn thì công gia hạn dày, hạn dài thì một chứng thư bị lộ sống
    lâu. Học phần chốt trần 400 ngày để bạn phải chạm vào phép tính đó. Phép kiểm
    hạn còn hiệu lực chính là chỗ CWE-298 nói tới."""
    dates = openssl("x509", "-in", str(PKI / "may-chu/may-chu.crt"), "-noout", "-dates").stdout
    moc = dict(
        dong.split("=", 1) for dong in dates.strip().splitlines() if "=" in dong
    )
    bat_dau = doc_ngay(moc["notBefore"])
    ket_thuc = doc_ngay(moc["notAfter"])
    bay_gio = datetime.now(timezone.utc)
    assert ket_thuc > bay_gio, (
        f"may-chu.crt đã hết hạn lúc {moc['notAfter']}. Cấp lại rồi chạy lại bốn phép kiểm."
    )
    song = (ket_thuc - bat_dau).days
    assert song <= HAN_TOI_DA_NGAY, (
        f"may-chu.crt có vòng đời {song} ngày, quá trần {HAN_TOI_DA_NGAY} ngày của học phần.\n"
        "Rút hạn xuống, và nói trong đoạn đánh đổi vì sao bạn chọn con số đó."
    )


def test_chung_thu_khach_do_ca_noi_bo_ky_va_khop_khoa():
    """Chứng thư khách là thứ biến câu hỏi của máy chủ từ ai gọi được tới tôi
    thành ai chứng minh được mình giữ khóa riêng ứng với một chứng thư do tổ chức
    tôi cấp. Nó phải do chính CA nội bộ ký, nếu không phép kiểm K3 sẽ đỏ."""
    ket_qua = xac_minh("khach/khach.crt", "ca/ca.crt")
    assert ket_qua.returncode == 0, (
        "khach.crt không dựng ngược được về ca/ca.crt.\n"
        f"openssl nói: {ket_qua.stderr.strip() or ket_qua.stdout.strip()}"
    )
    assert khoa_cong_khai_cua_chung_thu("khach/khach.crt") == khoa_cong_khai_cua_khoa_rieng(
        "khach/khach.key"
    ), "khach.key không phải khóa riêng của khach.crt."


def test_ca_ngoai_that_su_la_mot_ca_khac():
    """Tổ chức thứ hai phải là một tổ chức thật, và phải thật sự lạ.

    Thật, nghĩa là chứng thư khách của nó dựng ngược được về chính nó: một CA giả
    vờ thì không dạy được gì. Lạ, nghĩa là nó không dựng ngược được về CA nội bộ
    của bạn. Hai điều đó cộng lại cho bạn một chứng thư còn hạn, đúng cú pháp, ký
    hợp lệ, và vô giá trị với máy chủ của bạn. Khoảng cách giữa hợp lệ và được tôi
    tin chính là kho tin cậy ở CWE-295.
    """
    trong_nha = xac_minh("ca-ngoai/khach-ngoai.crt", "ca-ngoai/ca-ngoai.crt")
    assert trong_nha.returncode == 0, (
        "khach-ngoai.crt không dựng ngược được về chính ca-ngoai.crt, nên tổ chức "
        "thứ hai chưa dựng xong.\n"
        f"openssl nói: {trong_nha.stderr.strip() or trong_nha.stdout.strip()}"
    )
    ngoai_nha = xac_minh("ca-ngoai/khach-ngoai.crt", "ca/ca.crt")
    assert ngoai_nha.returncode != 0, (
        "khach-ngoai.crt lại dựng ngược được về CA nội bộ. Hai tổ chức của bạn "
        "đang là một, nên phần thử thách K5 không chứng minh được điều gì."
    )
