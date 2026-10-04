"""Năm phép kiểm gọi thẳng hàm `kiem_the` của bạn, với thẻ do bộ kiểm tự dựng.

Đây là phần đo THẬT của bài, không phải phép xấp xỉ: bộ kiểm giữ khóa riêng nên
nó dựng được đúng tấm thẻ nó muốn, và phán quyết của hàm bạn viết là thứ duy
nhất quyết định phép kiểm xanh hay đỏ. Không cần Docker cho năm phép này.

Bốn phép âm nói về ba cạm bẫy ở §5.5, và một phép dương đứng cạnh chúng. Phép
dương không phải cho đủ bộ: một hàm từ chối tất cả cũng qua được cả bốn phép âm,
và một dịch vụ từ chối cả người có quyền thì đã hỏng theo cách khác.
"""
from __future__ import annotations

import pytest

from tro_giup import (
    CAU_HINH,
    KHOA_CONG_PEM,
    THAN_KHACH_KHAC,
    nap_kiem_the,
    the_alg_none,
    the_dung_khoa_that,
    the_ky_khoa_khac,
)


@pytest.fixture(scope="module")
def bai():
    return nap_kiem_the()


def _phai_bi_tu_choi(bai, the: str, ten_phep: str, ma_diem_yeu: str) -> None:
    """Đòi đúng lớp ngoại lệ trong hợp đồng, không đòi một ngoại lệ bất kỳ.

    Một hàm chưa viết xong cũng ném ngoại lệ, và nếu bộ chấm nhận ngoại lệ bất kỳ
    thì nó cho điểm một bài chưa làm gì. Lớp `TheKhongHopLe` là chỗ bạn nói rằng
    mình đã kiểm và đã từ chối, khác hẳn với việc chương trình vỡ giữa chừng.
    """
    try:
        ket = bai.kiem_the(the, KHOA_CONG_PEM, CAU_HINH)
    except bai.TheKhongHopLe:
        return
    except NotImplementedError:
        pytest.fail(
            f"{ten_phep}: kiem_the chưa được viết. Xem việc 7 trong README.md."
        )
    except Exception as loi:  # noqa: BLE001
        pytest.fail(
            f"{ten_phep}: hàm ném {type(loi).__name__} thay vì TheKhongHopLe. "
            f"Bắt lấy lỗi của thư viện rồi ném lại đúng lớp trong hợp đồng, kèm câu nói rõ "
            f"phép kiểm nào đã chặn. Chi tiết: {loi}"
        )
    pytest.fail(
        f"{ten_phep}: tấm thẻ này được NHẬN, đáng lẽ phải bị từ chối. "
        f"Đây là điểm yếu {ma_diem_yeu}. Hàm trả về: {ket!r}"
    )


def test_the_hop_le_thi_duoc_nhan(bai):
    """Chiều dương. Thẻ do đúng khóa ký, đúng người nhận, đúng bên phát hành,
    còn hạn, thì phải qua, và tập khai trả về phải là tập khai bên trong thẻ."""
    try:
        khai = bai.kiem_the(the_dung_khoa_that(), KHOA_CONG_PEM, CAU_HINH)
    except NotImplementedError:
        pytest.fail("kiem_the chưa được viết. Xem việc 7 trong README.md.")
    except Exception as loi:  # noqa: BLE001
        pytest.fail(
            f"Thẻ hợp lệ lại bị từ chối bằng {type(loi).__name__}: {loi}. "
            "Ba chỗ hay sai: kiểm sai khóa công khai, đòi một thuật toán mà thẻ không dùng, "
            "hoặc quên biên lệch đồng hồ."
        )
    assert isinstance(khai, dict), f"kiem_the phải trả về dict tập khai, đang trả về {type(khai).__name__}."
    thieu = [k for k in ("sub", "aud", "exp", "realm_access") if k not in khai]
    assert not thieu, (
        "Tập khai trả về thiếu " + ", ".join(thieu)
        + ". Trả về đúng tập khai đã kiểm, đừng dựng một dict mới cho gọn: "
        "hàm quyet_dinh đọc vai và đơn vị từ chính tập khai này."
    )


def test_the_khai_thuat_toan_rong_bi_tu_choi(bai):
    """Cạm bẫy thứ nhất, CWE-347. Tấm thẻ tự khai `alg: none` và bỏ trống chữ ký.

    Nó qua cửa khi và chỉ khi bạn lấy danh sách thuật toán từ chính tấm thẻ. Đây
    là chỗ dễ nhất để hiểu vì sao §5.5 nói không bao giờ tin trường alg: người
    gửi được tự chọn cách mình bị kiểm thì phép kiểm không còn là phép kiểm."""
    _phai_bi_tu_choi(bai, the_alg_none(), "thuật toán rỗng", "CWE-347")


def test_the_ky_bang_khoa_khac_bi_tu_choi(bai):
    """Cũng CWE-347, nhưng ở chiều khác. Chữ ký đúng cú pháp, thuật toán đúng,
    tập khai đẹp; chỉ có điều nó do một khóa riêng khác ký. Phép kiểm này đỏ khi
    bạn tắt phần kiểm chữ ký để bài chạy cho nhanh."""
    _phai_bi_tu_choi(bai, the_ky_khoa_khac(), "ký bằng khóa khác", "CWE-347")


def test_the_qua_han_bi_tu_choi(bai):
    """Cạm bẫy thứ ba, CWE-613. Thẻ do đúng khóa ký, chỉ mỗi hết hạn từ một giờ
    trước. Đây là hiện tượng mở đầu §5.1: cái đồng hồ quyết định phiên còn sống
    hay đã chết, và phía máy chủ phải là nơi đọc cái đồng hồ ấy."""
    import time

    bay_gio = int(time.time())
    _phai_bi_tu_choi(
        bai,
        the_dung_khoa_that(iat=bay_gio - 7200, exp=bay_gio - 3600),
        "thẻ quá hạn",
        "CWE-613",
    )


def test_the_phat_cho_than_khach_khac_bi_tu_choi(bai):
    """Cạm bẫy thứ hai, CWE-863. Thẻ thật, khóa thật, người dùng thật, còn hạn,
    nhưng phát cho một thân khách khác của cùng vùng định danh.

    Đây là phép kiểm hay bị bỏ nhất, vì bỏ nó thì mọi thứ vẫn chạy. Hậu quả chỉ
    lộ ra khi một dịch vụ khác trong tổ chức bị chiếm: thẻ người dùng cấp cho nó
    lập tức dùng được ở dịch vụ của bạn."""
    _phai_bi_tu_choi(
        bai,
        the_dung_khoa_that(aud=THAN_KHACH_KHAC, azp=THAN_KHACH_KHAC),
        "thẻ phát cho thân khách khác",
        "CWE-863",
    )
