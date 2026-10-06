"""Hai phép kiểm về lớp chặn nằm trong trình duyệt, đo trên tiêu đề thật.

Chính sách an toàn nội dung là lớp THỨ HAI của bài, dựng với giả định lớp thứ
nhất đã vỡ. Nó không ngăn chuỗi lạ vào trang; nó lấy đi phần thưởng của việc đưa
được chuỗi lạ vào. Hai phép kiểm dưới đây đo đúng hai điều làm nên khác biệt giữa
một chính sách có tác dụng và một chính sách chỉ để cho có: chính sách đang cưỡng
chế hay chỉ đang báo cáo, và số dùng một lần có thật sự dùng một lần hay không.
"""
from __future__ import annotations

import re

import pytest

from tro_giup import CHI_THI_BAT_BUOC, chi_thi_csp, get, gia_tri_csp, may_chu_cua_ban

NONCE = re.compile(r"'nonce-([A-Za-z0-9_\-+/=]{8,})'")
DAI_TOI_THIEU_NONCE = 16


@pytest.fixture(scope="module")
def goc():
    with may_chu_cua_ban() as dia_chi:
        yield dia_chi


def test_csp_o_che_do_cuong_che_va_du_bon_chi_thi(goc):
    """Bốn chỉ thị, ứng với bốn câu hỏi in sẵn trong chinh-sach.yaml.

    Nguồn mã nào được chạy, trang có cần đối tượng nhúng không, địa chỉ cơ sở của
    tài liệu có được đổi không, và trang có được nằm trong khung của trang khác
    không. Ba câu sau hay bị bỏ qua vì `script-src` trông như đã đủ, nhưng một
    chính sách chỉ khai nguồn mã vẫn để ngỏ ba đường đi vòng đã có tên.

    Phép kiểm cũng đòi chế độ cưỡng chế, nghĩa là bạn phải đi qua chế độ chỉ báo
    cáo TRƯỚC rồi mới sang đây, chứ không phải bỏ qua nó. Bằng chứng của chặng chỉ
    báo cáo nằm ở evidence/S6/bao-cao-csp.jsonl và được chấm riêng.
    """
    _, tieu_de, _ = get(goc, "/")
    ten, gia_tri = gia_tri_csp(tieu_de)

    assert ten, (
        "Phản hồi không mang tiêu đề chính sách an toàn nội dung nào. Ở trạng thái khởi "
        "đầu khối chi_thi trong ung-dung/chinh-sach.yaml rỗng, nên ứng dụng không gửi gì "
        "và trình duyệt cho chạy mọi đoạn mã có mặt trong trang. Đó là chỗ làm việc mang "
        "nhãn `việc 2`."
    )
    assert ten == "content-security-policy", (
        "Chính sách đang ở chế độ chỉ báo cáo, tức trình duyệt không chặn gì mà chỉ gửi "
        "báo cáo. Chặng ấy là chặng phải đi qua, không phải chặng dừng lại. Sau khi đã "
        "thu được báo cáo và biết trang gãy ở đâu, đổi che_do sang cuong-che."
    )

    chi_thi = chi_thi_csp(gia_tri)
    hong = []

    for ten_chi_thi in CHI_THI_BAT_BUOC:
        if ten_chi_thi not in chi_thi:
            hong.append(f"thiếu chỉ thị {ten_chi_thi}.")

    nguon_ma = chi_thi.get("script-src", "")
    if nguon_ma:
        if not NONCE.search(nguon_ma):
            hong.append(
                "script-src không mang số dùng một lần. Dạng dùng được là gán cho mỗi lần "
                "tải trang một nonce rồi chỉ cho chạy đoạn mã mang đúng số ấy; chuỗi "
                "{nonce} trong giá trị sẽ được ứng dụng thay bằng số của chính lần tải đó."
            )
        if "unsafe-inline" in nguon_ma:
            hong.append(
                "script-src còn 'unsafe-inline', tức cho chạy mọi đoạn mã nằm thẳng trong "
                "trang. Một chuỗi lạ lọt vào trang chính là một đoạn mã như vậy, nên chính "
                "sách này không chặn được thứ nó sinh ra để chặn."
            )
        if "*" in nguon_ma:
            hong.append("script-src có ký tự đại diện, tức nhận mã từ mọi nguồn.")

    doi_tuong = chi_thi.get("object-src", "")
    if doi_tuong and ("*" in doi_tuong or "unsafe" in doi_tuong):
        hong.append(
            f"object-src là {doi_tuong!r}, tức còn để ngỏ. Đọc lại trang này xem nó có nhúng "
            "đối tượng nào không, rồi chọn giá trị nói đúng điều đó: chừa một đường chạy mã "
            "mà bạn không dùng tới là chừa nó cho người khác dùng."
        )

    assert not hong, (
        f"Chính sách hiện tại là {gia_tri!r}, và nó chưa đạt:\n  " + "\n  ".join(hong)
    )


def test_nonce_khac_nhau_o_moi_lan_tai_trang(goc):
    """Một số dùng một lần mà dùng lại được thì không còn là số dùng một lần.

    Chỗ này đáng đo vì cách hỏng của nó im lặng. Một chính sách khai nonce cố định
    vẫn trông đúng trong mọi lần đọc mã, vẫn qua mọi phép kiểm về hình thức, và
    vẫn để kẻ tấn công đoán trước con số cần gắn vào đoạn mã của họ. Trang khi ấy
    có một chính sách, nhưng không có lớp bảo vệ nào.
    """
    _, tieu_de_1, _ = get(goc, "/")
    _, tieu_de_2, _ = get(goc, "/thu/doi-dia-chi")
    _, gia_tri_1 = gia_tri_csp(tieu_de_1)
    _, gia_tri_2 = gia_tri_csp(tieu_de_2)

    mot = NONCE.search(gia_tri_1)
    hai = NONCE.search(gia_tri_2)
    assert mot and hai, (
        "Không đọc được số dùng một lần trong tiêu đề của cả hai lần tải trang. "
        f"Lần thứ nhất: {gia_tri_1!r}. Lần thứ hai: {gia_tri_2!r}. "
        "Khai script-src với chuỗi {nonce} trong ung-dung/chinh-sach.yaml."
    )

    assert len(mot.group(1)) >= DAI_TOI_THIEU_NONCE, (
        f"Số dùng một lần chỉ dài {len(mot.group(1))} ký tự. Bản phát sinh nó bằng bộ sinh "
        "số ngẫu nhiên dùng cho mật mã; một chuỗi ngắn hay một chuỗi bạn tự gõ thì đoán được."
    )
    assert mot.group(1) != hai.group(1), (
        f"Hai lần tải trang dùng chung một số {mot.group(1)!r}, nên nó không phải số dùng "
        "một lần. Nguyên nhân thường gặp là gõ thẳng một chuỗi cố định vào chinh-sach.yaml "
        "thay vì để nguyên chuỗi {nonce} cho ứng dụng thay."
    )
