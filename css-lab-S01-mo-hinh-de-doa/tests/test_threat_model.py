"""Bộ kiểm công khai của lab S1.

Sinh viên chạy bộ này bằng `make verify` trước khi nộp. Bộ chấm trong GitHub
Actions chạy đúng những phép kiểm này, không thêm phép nào. Bộ kiểm ẩn nằm ở kho
riêng và chỉ chấm phần lập luận, không chấm lại phần máy đã chấm ở đây.

Nguyên tắc viết bộ kiểm này: mỗi phép kiểm phải nói được vì sao nó tồn tại. Một
phép kiểm mà sinh viên không hiểu vì sao mình trượt là một phép kiểm tồi.
"""
from __future__ import annotations

import json
import re
from pathlib import Path

import pytest

try:
    from jsonschema import Draft202012Validator
except ImportError:  # pragma: no cover
    pytest.skip("Thiếu jsonschema, cài bằng: pip install jsonschema", allow_module_level=True)

ROOT = Path(__file__).resolve().parent.parent
MODEL = ROOT / "docs" / "threat-model.json"
SCHEMA = ROOT / "schema" / "threat-model.schema.json"

ATTACK_RE = re.compile(r"^T\d{4}(\.\d{3})?$")
DIEU_KIEN = ("nếu", "khi", "trong trường hợp", "miễn là", "một khi")
TOI_THIEU_TU = 12


@pytest.fixture(scope="module")
def model():
    if not MODEL.exists():
        pytest.fail(
            f"Không thấy {MODEL.relative_to(ROOT)}.\n"
            "Ghi mô hình đe dọa ra đúng đường dẫn đó, theo lược đồ "
            "schema/threat-model.schema.json. Dùng công cụ nào là việc của bạn."
        )
    try:
        return json.loads(MODEL.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        pytest.fail(f"Tệp JSON không phân giải được: {exc}")


def test_json_hop_le_theo_luoc_do(model):
    """Lược đồ là hợp đồng về hình dạng dữ liệu. Sai hình dạng thì mọi phép kiểm
    sau đều vô nghĩa, nên phép này chạy trước."""
    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    loi = sorted(Draft202012Validator(schema).iter_errors(model), key=lambda e: list(e.path))
    if loi:
        chi_tiet = "\n".join(f"  tại {list(e.path) or 'gốc'}: {e.message}" for e in loi[:8])
        pytest.fail(f"{len(loi)} chỗ không khớp lược đồ:\n{chi_tiet}")


def test_du_tam_moi_de_doa(model):
    n = len(model["moi_de_doa"])
    assert n >= 8, f"Mới có {n} mối đe dọa, đề yêu cầu tối thiểu 8."


def test_ma_moi_de_doa_khong_trung(model):
    ma = [m["ma"] for m in model["moi_de_doa"]]
    trung = {x for x in ma if ma.count(x) > 1}
    assert not trung, f"Mã bị trùng: {sorted(trung)}. Mỗi mối một mã riêng."


def test_nguyen_ly_hop_le(model):
    """Mỗi mối phải gắn vào một trong bảy nguyên lý cột sống. Đây là chỗ bài này
    nối vào phần còn lại của học phần, không phải một trường cho có."""
    for m in model["moi_de_doa"]:
        assert 1 <= m["nguyen_ly"] <= 7, (
            f"{m['ma']}: nguyên lý {m['nguyen_ly']} nằm ngoài dải 1 tới 7."
        )


def test_ma_attack_dung_dang(model):
    for m in model["moi_de_doa"]:
        assert ATTACK_RE.match(m["attack"]), (
            f"{m['ma']}: mã ATT&CK {m['attack']!r} sai dạng. "
            "Đúng dạng là T1234 hoặc T1234.001."
        )


def test_phat_bieu_kiem_duoc(model):
    """Phép xấp xỉ, không phải phép đo thật.

    Máy không đọc được một câu có kiểm được hay không. Nó chỉ chặn được hai dấu
    hiệu của câu chưa kiểm được: câu quá ngắn, và câu không nêu điều kiện nào.
    Phần còn lại do người chấm đọc, theo rubric. Sinh viên qua được phép kiểm này
    mà câu vẫn chung chung thì vẫn mất điểm ở tiêu chí thứ hai của thang chấm.
    """
    hong = []
    for m in model["moi_de_doa"]:
        cau = m["phat_bieu"]
        so_tu = len(cau.split())
        co_dieu_kien = any(k in cau.lower() for k in DIEU_KIEN)
        if so_tu < TOI_THIEU_TU:
            hong.append(f"{m['ma']}: mới {so_tu} từ, cần ít nhất {TOI_THIEU_TU}.")
        elif not co_dieu_kien:
            hong.append(
                f"{m['ma']}: câu không nêu điều kiện nào. Một mối đe dọa kiểm được "
                "thường có dạng ai đó làm được gì NẾU điều kiện nào đó đúng."
            )
    assert not hong, "Phát biểu chưa đạt:\n  " + "\n  ".join(hong)


def test_chon_dung_ba_moi(model):
    assert len(model["chon_xu_ly"]) == 3, (
        f"Chọn {len(model['chon_xu_ly'])} mối, đề yêu cầu đúng 3."
    )


def test_moi_duoc_chon_nam_trong_danh_sach(model):
    co = {m["ma"] for m in model["moi_de_doa"]}
    for c in model["chon_xu_ly"]:
        assert c["ma"] in co, (
            f"Mối {c['ma']} được chọn xử lý nhưng không có trong danh sách mối đe dọa."
        )


def test_moi_duoc_chon_co_uoc_luong_chi_phi(model):
    """Nguyên lý thứ bảy: an toàn là bài toán kinh tế. Một biện pháp không có
    ước lượng chi phí là một biện pháp chưa được cân nhắc, chỉ mới được nghĩ ra."""
    for c in model["chon_xu_ly"]:
        assert c["chi_phi"] >= 0, f"{c['ma']}: chi phí âm."
        assert c["don_vi"].strip(), f"{c['ma']}: thiếu đơn vị của chi phí."
        assert len(c["can_cu"].split()) >= 4, (
            f"{c['ma']}: căn cứ ước lượng quá ngắn. Nói rõ bạn ước lượng dựa trên cái gì."
        )


def test_ba_moi_duoc_chon_nam_trong_nhom_uu_tien(model):
    """Chọn ba mối có tích tác động nhân khả năng thấp nhất là một lựa chọn hợp lệ
    nếu giải thích được, nên phép kiểm này chỉ cảnh báo khi cả ba đều nằm ở nửa
    dưới của bảng xếp hạng. Người chấm đọc phần giải thích trong README."""
    diem = {m["ma"]: m["tac_dong"] * m["kha_nang"] for m in model["moi_de_doa"]}
    xep = sorted(diem, key=lambda k: -diem[k])
    nua_tren = set(xep[: max(1, len(xep) // 2)])
    chon = {c["ma"] for c in model["chon_xu_ly"]}
    assert chon & nua_tren, (
        "Cả ba mối được chọn đều nằm ở nửa dưới bảng xếp hạng. Điều này không sai, "
        "nhưng README phải giải thích vì sao, nếu không người chấm sẽ trừ điểm ở "
        "tiêu chí lập luận."
    )
