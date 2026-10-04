"""Hai phép kiểm gọi thẳng hàm `quyet_dinh` với chính tệp chính sách của bạn.

Chúng đo phần mà §5.5 gọi là bước từ "ai" sang "được làm gì". Một tấm thẻ đã
kiểm xong chỉ trả lời câu thứ nhất; câu thứ hai được tính lại ở MỖI yêu cầu, và
đó là điều mà chữ "phân quyền" trong nhiều tài liệu Việt làm người đọc quên mất.

Phép thứ hai là phép kiểm âm thứ năm của bài, và là phép khó chấp nhận nhất về
mặt trực giác: người xin là người thật, thẻ của họ hoàn hảo, vai của họ đúng, và
hệ thống vẫn phải từ chối. Từ chối một danh tính hợp lệ chính là chỗ đặc quyền
tối thiểu có hiệu lực.
"""
from __future__ import annotations

import pytest

from tro_giup import (
    CHINH_SACH,
    DON_VI_CUA_MINH,
    DON_VI_KHAC,
    doc_yaml,
    khai_mau,
    nap_kiem_the,
)


@pytest.fixture(scope="module")
def bai():
    return nap_kiem_the()


@pytest.fixture(scope="module")
def chinh_sach() -> dict:
    return doc_yaml(CHINH_SACH, "Đây là tệp chính sách sinh viên viết ở việc 6.")


def _hoi(bai, chinh_sach, khai: dict, phuong_thuc: str, don_vi: str) -> bool:
    """Hỏi chính sách một câu, và biến mọi cách hỏng thành một câu người đọc được."""
    yeu_cau = {"duong_dan": "/ho-so", "phuong_thuc": phuong_thuc, "don_vi": don_vi}
    try:
        return bai.quyet_dinh(khai, yeu_cau, chinh_sach)
    except NotImplementedError:
        pytest.fail("quyet_dinh chưa được viết. Xem việc 6 trong README.md.")
    except Exception as loi:  # noqa: BLE001
        pytest.fail(
            f"quyet_dinh ném {type(loi).__name__} với yêu cầu {phuong_thuc} /ho-so: {loi}. "
            "Một yêu cầu không khớp quy tắc nào phải trả về False, không được làm vỡ dịch vụ."
        )


def test_cho_qua_dung_vai_va_chan_dung_thao_tac(bai, chinh_sach):
    """Chính sách phải nói được cả hai chiều trong cùng một tệp.

    Nhân viên đọc được hồ sơ đơn vị mình, và cũng chính nhân viên ấy không xóa
    được. Một chính sách chỉ có chiều cho phép thì không phải chính sách, nó là
    một danh sách tiện ích."""
    nhan_vien = khai_mau()
    truong = khai_mau(realm_access={"roles": ["truong-don-vi"]}, preferred_username="chi-tdv")

    assert _hoi(bai, chinh_sach, nhan_vien, "GET", DON_VI_CUA_MINH) is True, (
        "Nhân viên phải đọc được hồ sơ trong đơn vị của mình. Chính sách đang chặn cả người có quyền."
    )
    assert _hoi(bai, chinh_sach, nhan_vien, "DELETE", DON_VI_CUA_MINH) is False, (
        "Nhân viên KHÔNG được xóa hồ sơ. Quy tắc mẫu trong chinh-sach.yaml cố ý cho cả ba phương thức; "
        "việc 6 yêu cầu sửa quy tắc đó chứ không chồng thêm quy tắc mới lên nó."
    )
    assert _hoi(bai, chinh_sach, truong, "DELETE", DON_VI_CUA_MINH) is True, (
        "Trưởng đơn vị phải xóa được hồ sơ trong đơn vị của mình."
    )


def test_danh_tinh_hop_le_nhung_vuot_pham_vi_don_vi_bi_chan(bai, chinh_sach):
    """Phép kiểm âm thứ năm, CWE-863.

    CWE-863 là "kiểm sai", khác với CWE-862 là "không kiểm". Chỗ này đúng nghĩa
    kiểm sai: hệ thống CÓ nhìn vai và thấy vai hợp lệ, rồi dừng ở đó, trong khi
    quyết định còn phụ thuộc một thuộc tính nữa là đơn vị. §5.5 đếm ra 144 vai
    khi cố diễn đạt chuyện này bằng vai thuần túy, và đó là lý do một thuộc tính
    rẻ hơn một trăm bốn mươi tư dòng bảng."""
    nhan_vien = khai_mau(don_vi=DON_VI_CUA_MINH)
    assert _hoi(bai, chinh_sach, nhan_vien, "GET", DON_VI_KHAC) is False, (
        f"Người của {DON_VI_CUA_MINH} đọc được hồ sơ của {DON_VI_KHAC}. "
        "Danh tính hợp lệ không phải giấy phép vào mọi phòng. Bật chi_trong_don_vi cho quy tắc "
        "tương ứng, và so đơn vị của chủ thể với đơn vị của tài nguyên trong quyet_dinh."
    )
    quan_tri = khai_mau(realm_access={"roles": ["quan-tri"]}, preferred_username="quan-tri")
    assert _hoi(bai, chinh_sach, quan_tri, "GET", DON_VI_KHAC) is True, (
        "Vai quản trị phải đọc được hồ sơ của mọi đơn vị, theo mệnh đề thứ ba của việc 6."
    )
