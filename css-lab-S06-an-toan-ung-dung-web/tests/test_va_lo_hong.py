"""Bốn phép kiểm gọi thẳng ứng dụng của bạn bằng HTTP thật.

Đây là phần đo THẬT của bài, không phải phép xấp xỉ. Bộ chấm dựng chính
`ung-dung/ung_dung.py` của bạn lên với chính `ung-dung/chinh-sach.yaml` của bạn,
rồi gửi những yêu cầu mà một trình duyệt và một trang của kẻ tấn công sẽ gửi.
Thứ quyết định xanh hay đỏ là phản hồi mã của bạn trả về, nên không có cách nào
qua được bốn phép này bằng lời khai. Không phép nào trong bốn phép cần Docker.

Ba phép âm ứng với hai lỗ hổng được chỉ định, và một phép dương đứng cạnh chúng.
Phép dương không phải cho đủ bộ. Một ứng dụng xóa sạch mọi thứ người dùng gõ vào
và từ chối mọi yêu cầu ghi cũng qua được cả ba phép âm, mà nó đã hỏng theo một
cách khác, cách mà người dùng chịu chứ không phải kẻ tấn công chịu. Mục 6.4 gọi
đúng tên chuyện này khi nói mã hóa đầu ra khác một bộ lọc danh sách đen: mã hóa
giữ nguyên thứ người dùng gõ và lấy đi quyền lực của nó, còn bộ lọc thì lấy đi cả
hai và vẫn hở ở khuôn nó chưa nghĩ tới.
"""
from __future__ import annotations

import urllib.parse

import pytest

from tro_giup import (
    GOC_HOP_LE,
    GOC_LA,
    TU_KHOA_LANH,
    get,
    lay_the_chong_gia_mao,
    may_chu_cua_ban,
    post,
)

# Mỗi tải trọng thử đi kèm hai câu hỏi. Câu thứ nhất, chuỗi có còn nguyên quyền
# lực của nó trong tài liệu không. Câu thứ hai, chuỗi có còn được hiển thị lại
# cho người dùng không. Một câu trả lời đúng phải là không cho câu đầu và có cho
# câu sau, và đó chính là định nghĩa của mã hóa theo ngữ cảnh.
TAI_TRONG = (
    (
        "<script>alert(1)</script>",
        "<script>",
        "&lt;script&gt;alert(1)&lt;/script&gt;",
    ),
    (
        '"><img src=x onerror=alert(1)>',
        "<img",
        "&gt;&lt;img src=x onerror=alert(1)&gt;",
    ),
)


@pytest.fixture(scope="module")
def goc():
    with may_chu_cua_ban() as dia_chi:
        yield dia_chi


def test_lh1_chuoi_phan_chieu_da_ma_hoa_theo_ngu_canh(goc):
    """Lỗ hổng LH-1, tức CWE-79 trong CWE List 4.20.

    Chỗ phải sửa là chỗ GỌI hàm dựng trang, không phải bên trong hàm ấy, vì chỉ ở
    chỗ gọi mới biết chuỗi sắp rơi vào ngữ cảnh nào của tài liệu. Thư viện chuẩn
    đã có sẵn hàm cần dùng và tệp đã nhập nó ở đầu.
    """
    hong = []
    for tai_trong, cam, phai_co in TAI_TRONG:
        duong = "/thu/tim-kiem?q=" + urllib.parse.quote(tai_trong)
        ma, _, than = get(goc, duong)
        if ma != 200:
            hong.append(f"{tai_trong!r}: ứng dụng trả mã {ma}, đáng lẽ 200.")
            continue
        if cam.lower() in than.lower():
            hong.append(
                f"{tai_trong!r}: chuỗi {cam!r} còn nguyên trong thân trang, nên trình duyệt "
                "vẫn đọc nó như một phần của tài liệu chứ không như một đoạn chữ."
            )
        if phai_co not in than:
            hong.append(
                f"{tai_trong!r}: không thấy dạng đã mã hóa {phai_co!r} trong thân trang. "
                "Nếu bạn đang lọc bỏ hay thay thế ký tự thì hãy dừng lại: bộ lọc danh sách "
                "đen vừa làm mất chữ của người dùng vừa hở ở khuôn nó chưa nghĩ tới."
            )
    assert not hong, (
        "Lỗ hổng LH-1 chưa đóng:\n  " + "\n  ".join(hong)
        + "\nChỗ làm việc mang nhãn `việc 1` trong ung-dung/ung_dung.py, và một dòng là đủ."
    )


def test_lh2_cookie_phien_khong_di_theo_yeu_cau_lien_trang(goc):
    """Nửa thứ nhất của biện pháp cho LH-2, tức CWE-1275 trong CWE List 4.20.

    Hai thuộc tính, hai việc khác nhau. SameSite nói với trình duyệt đừng đính
    cookie này vào yêu cầu do trang khác khởi xướng, tức chặn đúng đường mà CWE-352
    đi qua. HttpOnly nói với trình duyệt đừng cho kịch bản trong trang đọc cookie,
    tức lấy đi phần thưởng của ATT&CK v19.2 T1539 trong trường hợp lớp thứ nhất đã
    vỡ. Đề bắt bật cả hai vì chúng chặn hai đường khác nhau.
    """
    _, tieu_de, _ = get(goc, "/")
    cookie = tieu_de.get("set-cookie") or []
    assert cookie, (
        "Phản hồi không đặt cookie phiên nào, nên phép kiểm này không đo được gì. "
        "Bản phát luôn đặt cookie ấy; nếu nó biến mất thì bạn đã sửa nhầm chỗ trong ung_dung.py."
    )
    chuoi = "; ".join(cookie)
    thap = chuoi.lower()

    hong = []
    if "httponly" not in thap:
        hong.append(
            "thiếu HttpOnly, nên một đoạn kịch bản lọt vào trang đọc được thẻ phiên và "
            "gửi nó đi nơi khác."
        )
    if "samesite" not in thap:
        hong.append(
            "thiếu SameSite, nên trình duyệt vẫn tự đính cookie này vào yêu cầu do trang "
            "của người khác khởi xướng."
        )
    elif "samesite=none" in thap.replace(" ", ""):
        hong.append(
            "đặt SameSite=None, tức mở lại đúng đường mà biện pháp này sinh ra để đóng. "
            "Chọn Strict hoặc Lax, và viết lý do chọn vào docs/danh-doi.md."
        )
    assert not hong, (
        f"Cookie phiên chưa đạt, tiêu đề hiện tại là {chuoi!r}:\n  " + "\n  ".join(hong)
        + "\nChỗ làm việc mang nhãn `việc 4a` trong ung-dung/chinh-sach.yaml."
    )


def test_lh2_ba_dang_yeu_cau_gia_mao_deu_bi_tu_choi(goc):
    """Nửa thứ hai của biện pháp cho LH-2, tức CWE-352 trong CWE List 4.20.

    Ba yêu cầu, và ba yêu cầu ấy đo hai phép kiểm khác nhau. Yêu cầu thứ hai mang
    gốc hợp lệ nhưng không mang thẻ, nên chỉ phép kiểm thẻ chặn được nó. Yêu cầu
    thứ ba mang thẻ thật nhưng đến từ gốc lạ, nên chỉ phép kiểm gốc chặn được nó.
    Bật một nửa thì một trong hai yêu cầu ấy đi lọt, và đó đúng là hình dạng thường
    gặp nhất của lỗ hổng này ngoài đời: nhìn vào mã thấy có thẻ nên ai cũng tưởng
    đã xong, trong khi thẻ được phát mà không được kiểm.

    Mức trừu tượng của CWE-352 là Composite, tức một điểm yếu chỉ thành lỗ hổng
    khi nhiều điều kiện cùng có mặt. Đó là lý do bằng chính ngôn ngữ của danh mục
    cho việc bài đòi hai lớp chứ không một.
    """
    _, _, trang = get(goc, "/thu/doi-dia-chi")
    dia_chi_truoc = trang

    the_that = lay_the_chong_gia_mao(goc)
    dia_chi_gia = "99 Đường Giả Mạo"
    than = urllib.parse.urlencode({"dia_chi": dia_chi_gia})
    than_co_the = urllib.parse.urlencode({"dia_chi": dia_chi_gia, "the": the_that})

    truong_hop = (
        (
            "không gốc, không thẻ",
            post(goc, "/thu/doi-dia-chi", than),
            "Đây là yêu cầu thô nhất, và cả hai phép kiểm đều chặn được nó.",
        ),
        (
            "gốc hợp lệ, không thẻ",
            post(goc, "/thu/doi-dia-chi", than, Origin=GOC_HOP_LE),
            "Chỉ phép kiểm thẻ chặn được yêu cầu này. Bật the_chong_gia_mao trong chinh-sach.yaml.",
        ),
        (
            "gốc lạ, thẻ thật",
            post(goc, "/thu/doi-dia-chi", than_co_the, Origin=GOC_LA),
            "Chỉ phép kiểm gốc chặn được yêu cầu này. Bật kiem_origin trong chinh-sach.yaml.",
        ),
    )

    hong = []
    for ten, (ma, _, than_tra), goi_y in truong_hop:
        if ma != 403:
            hong.append(f"{ten}: ứng dụng trả mã {ma} và thân {than_tra[:120]!r}. {goi_y}")

    _, _, trang_sau = get(goc, "/thu/doi-dia-chi")
    if dia_chi_gia in trang_sau and dia_chi_gia not in dia_chi_truoc:
        hong.append(
            f"địa chỉ trong hồ sơ đã đổi thành {dia_chi_gia!r} sau ba yêu cầu giả mạo, "
            "tức là một trong ba yêu cầu ấy đã ghi được vào dữ liệu thật."
        )

    assert not hong, (
        "Lỗ hổng LH-2 chưa đóng:\n  " + "\n  ".join(hong)
        + "\nChỗ làm việc mang nhãn `việc 4b` trong ung-dung/chinh-sach.yaml."
    )


def test_ung_dung_van_phuc_vu_nguoi_dung_that(goc):
    """Chiều dương, và nó gánh đúng một nửa ý nghĩa của cả nhóm phép kiểm này.

    Một ứng dụng xóa sạch chữ người dùng gõ vào và từ chối mọi yêu cầu ghi thì qua
    được ba phép âm ở trên mà không đóng được lỗ hổng nào; nó chỉ chuyển thiệt hại
    từ kẻ tấn công sang người dùng. Từ khóa lành dưới đây có dấu tiếng Việt và có
    khoảng trắng, nên một bộ lọc viết vội theo danh sách ký tự cho phép sẽ cắt mất
    một phần của nó, và phép kiểm này nói ra điều đó ngay.
    """
    hong = []

    duong = "/thu/tim-kiem?q=" + urllib.parse.quote(TU_KHOA_LANH)
    ma, _, than = get(goc, duong)
    if ma != 200:
        hong.append(f"tra cứu một từ khóa lành trả mã {ma}, đáng lẽ 200.")
    elif TU_KHOA_LANH not in than:
        hong.append(
            f"tra cứu {TU_KHOA_LANH!r} không hiện lại nguyên văn từ khóa ấy. Mã hóa theo "
            "ngữ cảnh không được phép làm mất chữ của người dùng; nếu chữ bị mất thì bạn "
            "đang lọc chứ không đang mã hóa."
        )

    dia_chi_moi = "45 Lý Thường Kiệt, Quận 10"
    the = lay_the_chong_gia_mao(goc)
    ma, _, than = post(
        goc,
        "/thu/doi-dia-chi",
        urllib.parse.urlencode({"dia_chi": dia_chi_moi, "the": the}),
        Origin=GOC_HOP_LE,
    )
    if ma != 200:
        hong.append(
            f"yêu cầu đổi địa chỉ hợp lệ, mang gốc đúng và thẻ thật, bị trả mã {ma} kèm "
            f"{than[:160]!r}. Kiểm lại danh sách goc_cho_phep: đừng thu hẹp nó tới mức "
            "chính ứng dụng của bạn không còn nằm trong đó."
        )
    else:
        _, _, trang = get(goc, "/thu/doi-dia-chi")
        if dia_chi_moi not in trang:
            hong.append("yêu cầu hợp lệ được nhận nhưng địa chỉ trong hồ sơ không đổi.")

    assert not hong, (
        "Ứng dụng đã chặn được kẻ tấn công nhưng chặn nhầm cả người dùng thật:\n  "
        + "\n  ".join(hong)
    )
