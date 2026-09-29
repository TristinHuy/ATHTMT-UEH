"""Kiểm cấu hình máy chủ, ở bậc bằng chứng thứ nhất.

§3.5 của giáo trình xếp lời khai của cấu hình vào bậc yếu nhất, vì một dòng trong
tệp chỉ chứng minh rằng ai đó đã gõ nó. Ba phép kiểm ở đây vẫn đáng có, và lý do
đáng nói thẳng: bốn phép kiểm nối mạng ở bậc trên chỉ trả lời được câu hỏi hệ
thống có đang từ chối đúng chỗ hay không, chúng không trả lời được câu hỏi trong
tệp còn sót lại thứ gì. Một cổng phẳng nằm im, chưa ai gọi tới, thì không phép
kiểm nối mạng nào của bài này chạm được vào.
"""
from __future__ import annotations

import re

import pytest

from tro_giup import ROOT

CONF = ROOT / "nginx" / "may-chu.conf"

GIAO_THUC_CAM = ["SSLv2", "SSLv3", "TLSv1.1"]


@pytest.fixture(scope="module")
def cau_hinh() -> str:
    if not CONF.exists():
        pytest.fail(f"Không thấy nginx/may-chu.conf ở {ROOT}.")
    # Bỏ chú thích trước khi đọc, để một dòng đã bị vô hiệu hóa không tính là đã làm.
    return "\n".join(dong.split("#", 1)[0] for dong in CONF.read_text(encoding="utf-8").splitlines())


def chi_thi(cau_hinh: str, ten: str) -> list[str]:
    return [m.group(1).strip() for m in re.finditer(rf"^\s*{ten}\s+([^;]+);", cau_hinh, re.M)]


def khoi_server(cau_hinh: str) -> list[str]:
    """Tách từng khối server bằng cách đếm ngoặc, đủ dùng cho cú pháp của bài này."""
    ra, i = [], 0
    while True:
        dau = cau_hinh.find("server", i)
        if dau == -1:
            return ra
        mo = cau_hinh.find("{", dau)
        if mo == -1:
            return ra
        sau, tang = mo + 1, 1
        while sau < len(cau_hinh) and tang:
            tang += {"{": 1, "}": -1}.get(cau_hinh[sau], 0)
            sau += 1
        ra.append(cau_hinh[mo + 1 : sau - 1])
        i = sau


def test_chi_con_giao_thuc_hien_hanh(cau_hinh):
    """Bật TLS mà để ngỏ một phiên bản cũ thì kẻ đứng giữa chỉ cần ép hai đầu thỏa
    thuận xuống phiên bản ấy. Bài này đòi TLS 1.3, vì bốn phép kiểm đều gọi với
    tls1_3 và vì máy chủ không phục vụ ai ngoài chính bạn."""
    dong = chi_thi(cau_hinh, "ssl_protocols")
    assert dong, (
        "Không thấy chỉ thị ssl_protocols. Nginx sẽ dùng mặc định của bản dựng, và "
        "một cấu hình an toàn không nên phụ thuộc vào mặc định của người khác."
    )
    gop = " ".join(dong)
    assert "TLSv1.3" in gop, f"ssl_protocols {gop!r} chưa bật TLSv1.3."
    co_cu = [g for g in GIAO_THUC_CAM if g in gop] + (
        ["TLSv1"] if re.search(r"TLSv1(?![.\d])", gop) else []
    )
    assert not co_cu, (
        f"ssl_protocols còn giữ {', '.join(co_cu)}. Bỏ hết, chỉ để TLSv1.3, "
        "hoặc TLSv1.2 nếu bạn giải thích được vì sao cần."
    )


def test_doi_chung_thu_khach_va_neo_vao_ca_noi_bo(cau_hinh):
    """Hai dòng, và thiếu một dòng thì lớp thứ hai không tồn tại.

    Giá trị optional_no_ca là cái bẫy nổi tiếng của nginx: nó nhận chứng thư mà
    không đòi chứng thư ấy dựng ngược được về ai, tức là chấp nhận mọi chứng thư
    tự ký. Người cấu hình đọc chữ optional thường tưởng mình đang nới lỏng một
    chút, trong khi thực tế lớp phòng thủ đã tắt hẳn.
    """
    doi = chi_thi(cau_hinh, "ssl_verify_client")
    assert doi, "Không thấy ssl_verify_client. Máy chủ chưa đòi chứng thư khách."
    assert doi[-1] == "on", (
        f"ssl_verify_client đang là {doi[-1]!r}, phải là on.\n"
        "Giá trị optional và optional_no_ca đều để lọt một lần nối không có chứng "
        "thư hợp lệ, và phép kiểm K4 sẽ bắt được điều đó."
    )
    ca = chi_thi(cau_hinh, "ssl_client_certificate")
    assert ca, (
        "Thiếu ssl_client_certificate, nên máy chủ không biết lấy gì để xét chứng "
        "thư khách. Trỏ nó tới chứng thư CA nội bộ của bạn."
    )
    assert ca[-1].endswith("ca.crt"), (
        f"ssl_client_certificate trỏ tới {ca[-1]!r}. Nó phải trỏ tới chứng thư của "
        "CA nội bộ, thường là /pki/ca/ca.crt, chứ không phải chứng thư của một máy."
    )


def test_khong_con_cong_phang(cau_hinh):
    """Chặng cuối, CWE-319. Giữ lại một khối phục vụ trên HTTP phẳng cho tiện thử
    thì hai lớp bên trên chỉ còn là trang trí, vì kẻ ở trong cùng mạng chọn đường
    rẻ nhất chứ không chọn đường bạn muốn họ đi. Một khối chỉ chuyển hướng sang
    https thì được, vì nó không phát nội dung nào."""
    hong = []
    for than in khoi_server(cau_hinh):
        chuyen_huong = re.search(r"return\s+30[128]\s+https://", than) is not None
        for nghe in chi_thi(than, "listen"):
            if "ssl" not in nghe.split() and not chuyen_huong:
                hong.append(f"listen {nghe}")
    assert not hong, (
        "Còn khối server phục vụ trên kênh phẳng: " + ", ".join(hong) + ".\n"
        "Bỏ khối đó đi, hoặc rút nó về đúng một dòng return 301 https://."
    )
