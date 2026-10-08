"""Phần dùng chung của bộ kiểm công khai lab S7.

Tệp này không chứa phép kiểm nào. Nó giữ bốn thứ mà năm tệp kiểm đều cần: chỗ
đứng của bài đang chấm, danh mục mã chuẩn được phép dùng, hai ngưỡng đo, và vài
hàm đọc tệp có thông điệp lỗi tử tế.

Một chỗ cần phân biệt rõ, vì nhầm chỗ này thì bộ chấm chấm nhầm thứ. Có HAI gốc
đường dẫn. `ROOT` là bài đang chấm, tức thứ sinh viên nộp, và nó đổi được qua
biến môi trường LAB_ROOT. `KHUNG` là bản phát của lab, nơi đặt bộ chạy quy tắc
và tập sự kiện có nhãn; hai thứ ấy do đề cung cấp chứ không do sinh viên viết,
nên chúng luôn lấy từ KHUNG. Nếu lấy chúng từ ROOT thì một bài nộp có thể thay
chính cái thước đang đo mình.

Sinh viên không cần đặt LAB_ROOT và không nên đặt. Nó tồn tại để bộ kiểm nội bộ
của giảng viên chạy được chính bộ kiểm này lên một bản mẫu đạt và một bản mẫu
trượt, vì một bộ chấm chưa bao giờ chạy trên một bài sai thì không ai biết nó có
bắt được lỗi hay không.
"""
from __future__ import annotations

import csv
import importlib.util
import json
import os
import sys
from pathlib import Path

import pytest

try:
    import yaml
except ImportError as loi:  # pragma: no cover
    raise RuntimeError(
        "Bộ kiểm cần PyYAML. Cài bằng: pip install -r tests/yeu-cau.txt"
    ) from loi

KHUNG = Path(__file__).resolve().parent.parent
ROOT = Path(os.environ.get("LAB_ROOT") or KHUNG).resolve()

COMPOSE = ROOT / "docker-compose.yml"
PROMTAIL = ROOT / "cau-hinh" / "promtail.yaml"
LOKI_CAU_HINH = ROOT / "cau-hinh" / "loki.yaml"
BANG = ROOT / "docs" / "bang-nam-su-kien.yaml"
GIA_BAO_NHAM = ROOT / "docs" / "gia-cua-bao-nham.md"
QUY_TAC = ROOT / "sigma" / "quy-tac.yml"
EVID = ROOT / "evidence" / "S7"
PREFLIGHT = EVID / "preflight.txt"
DO_TRE = EVID / "do-tre.csv"
DO_CHINH_XAC = EVID / "do-chinh-xac.json"

TAP_CO_NHAN = KHUNG / "nhan" / "tap-co-nhan.jsonl"
BO_CHAY = KHUNG / "bin" / "quy_tac.py"

# Trần bốn container cho mỗi lab, gồm cả container chấm. Ngưỡng của ADR-0003 mục
# N3, đặt theo cấu hình laptop phổ thông của lớp chứ không theo sở thích.
TRAN_CONTAINER = 4

# Danh mục mã chuẩn. CHÉP từ core/syllabus/mapping/S07-mapping.yaml, khối lab, nơi
# từng mã đã được mở trang riêng và đọc trạng thái ngày 18/08/2026. Không gõ lại
# theo trí nhớ: buổi này đã một lần trả giá vì tin trí nhớ, khi nhánh T1562 bị
# thu hồi trong ATT&CK v19 mà tài liệu vẫn in bản cũ.
# Phiên bản danh mục: ATT&CK content v19.2, CWE List 4.20, OWASP Top 10:2025.
MA_ATTACK_CHO_PHEP = {"T1685", "T1685.006", "T1685.004", "T1070.003"}
MA_CWE_CHO_PHEP = {"CWE-778", "CWE-223", "CWE-532", "CWE-779", "CWE-117"}

BUOI_BAT_BUOC = ("S02", "S03", "S04", "S05", "S06")
BUOI_THU_THAP = BUOI_BAT_BUOC + ("S07",)

LY_DO_KHONG_TIM_DUOC = {"khong_he_ghi", "thieu_truong_de_loc", "het_han_giu"}
NGUON_DU_LIEU = {"cua_minh", "thay_the"}

CHANG_BAT_BUOC = ("sinh", "chuyen", "giu", "hoi")

# Hai ngưỡng, và chúng kéo ngược nhau nên phải đặt cùng lúc.
#
# Độ phủ đòi tuyệt đối vì quy tắc này chỉ có một việc: không bỏ sót lần chứng
# thực thất bại nào của một chủ thể thật. Một quy tắc bỏ sót thì phần còn lại của
# phép đo không còn ý nghĩa, vì người ta sẽ tin vào sự im lặng của nó.
#
# Độ chính xác đặt ở 0,80 chứ không ở 1,0, và đó là lựa chọn có lý do. Đòi tuyệt
# đối sẽ ép sinh viên loại trừ từng nguồn báo nhầm cho tới khi quy tắc chỉ còn
# khớp đúng tập mẫu này, tức dạy đúng thói quen mà bài đang muốn chống. Ngưỡng
# 0,80 để lại chỗ cho một vài lần báo nhầm có thật, và chính vài lần ấy là dữ
# liệu cho đoạn văn về giá của báo nhầm.
NGUONG_DO_CHINH_XAC = 0.80
NGUONG_DO_PHU = 1.0

# Trường chỉ có nghĩa bên trong tập mẫu này. Neo quy tắc vào chúng là chép đáp án
# chứ không phải phát hiện, và một quy tắc như vậy vô dụng trên dữ liệu thật.
TRUONG_CAM_TRONG_QUY_TAC = {"id", "nhan", "thoi_diem"}


def doc_yaml(duong_dan: Path, viec: str) -> dict:
    if not duong_dan.exists():
        pytest.fail(f"Không thấy {duong_dan.name} ở {duong_dan.parent}. {viec}")
    try:
        return yaml.safe_load(duong_dan.read_text(encoding="utf-8")) or {}
    except yaml.YAMLError as loi:
        pytest.fail(f"{duong_dan.name} không phân giải được: {loi}")


def doc_json(duong_dan: Path, viec: str) -> dict:
    if not duong_dan.exists():
        pytest.fail(f"Không thấy {duong_dan.name} ở {duong_dan.parent}. {viec}")
    try:
        return json.loads(duong_dan.read_text(encoding="utf-8"))
    except json.JSONDecodeError as loi:
        pytest.fail(f"{duong_dan.name} không phân giải được: {loi}")


def doc_csv(duong_dan: Path, viec: str) -> list[dict]:
    if not duong_dan.exists():
        pytest.fail(f"Không thấy {duong_dan.name} ở {duong_dan.parent}. {viec}")
    with duong_dan.open(encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def nap_bo_chay():
    """Nạp bin/quy_tac.py của BẢN PHÁT, không của bài nộp."""
    if not BO_CHAY.exists():
        pytest.fail(f"Không thấy {BO_CHAY}. Bản phát của lab thiếu bộ chạy quy tắc.")
    dac_ta = importlib.util.spec_from_file_location("quy_tac_ban_phat", BO_CHAY)
    mo_dun = importlib.util.module_from_spec(dac_ta)
    sys.modules["quy_tac_ban_phat"] = mo_dun
    dac_ta.loader.exec_module(mo_dun)
    return mo_dun


def so_tu(chu: object) -> int:
    return len(str(chu or "").split())
