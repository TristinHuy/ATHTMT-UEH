"""Phần dùng chung của bộ kiểm công khai.

Tệp này không chứa phép kiểm nào. Nó giữ bốn thứ mà cả ba tệp kiểm đều cần: chỗ
đứng của bài, cách đọc tập lệnh SQL của người học, cách bỏ chú thích khỏi SQL, và
cách đọc một tệp kết quả.

Chỗ đáng nói nhất là phép bỏ chú thích. Ba tệp SQL phát cho người học chứa rất
nhiều dòng giải thích, và trong đó có cả tên những câu lệnh mà đề bài yêu cầu
viết. Một bộ kiểm đọc nguyên văn tệp sẽ thấy chữ `FORCE ROW LEVEL SECURITY` nằm
trong một dòng chú thích rồi báo đạt, tức là chấm điểm cho đề bài chứ không chấm
bài làm. Vì vậy mọi phép kiểm ở đây đọc phần SQL đã bỏ chú thích.

Biến môi trường `LAB_ROOT` cho phép chạy chính những phép kiểm này lên một thư
mục khác. Người học không cần đặt nó, và không nên đặt. Nó tồn tại để bộ kiểm
nội bộ của giảng viên chạy được bộ kiểm này lên một bản mẫu đạt và một bản mẫu
trượt, vì một bộ chấm chưa bao giờ chạy trên một bài sai thì không ai biết nó
bắt được lỗi hay không.
"""
from __future__ import annotations

import os
import re
from pathlib import Path

ROOT = Path(os.environ.get("LAB_ROOT") or Path(__file__).resolve().parent.parent).resolve()

SQL = ROOT / "sql"
EVID = ROOT / "evidence" / "S4"
CAU_HINH_MAY_CHU = ROOT / "csdl" / "pgaudit.conf"

# Tệp dữ liệu phát sẵn. Nó KHÔNG phải bài làm, và nó chứa đúng một dòng cấp
# quyền rộng mà người học phải thu lại, nên nếu gộp nó vào phần đọc bài làm thì
# mọi bài đều bị bắt vì một dòng không do mình viết.
TEP_PHAT_SAN = "00-du-lieu.sql"

BA_VAI_TRO = ("ung_dung", "duyet_chi", "bao_cao")
VAI_TRO_SO_HUU = "chu_luoc_do"
VAI_TRO_DANH_DAU = "kiem_toan"

BANG_NHAY_CAM = "nhan_su"
BANG_MUC_HANG = "de_nghi_chi"


def bo_chu_thich(sql: str) -> str:
    """Bỏ chú thích một dòng và chú thích khối, giữ nguyên phần còn lại."""
    sql = re.sub(r"/\*.*?\*/", " ", sql, flags=re.DOTALL)
    sql = re.sub(r"--[^\n]*", " ", sql)
    return sql


def doc_sql_bai_lam() -> str:
    """Gộp mọi tệp SQL của người học, đã bỏ chú thích, đã chuẩn hóa khoảng trắng.

    Duyệt theo thứ tự đã sắp chứ không theo thứ tự hệ tệp trả về, để hai lần chạy
    trên cùng một bài cho cùng một chuỗi.
    """
    if not SQL.is_dir():
        return ""
    phan = []
    for tep in sorted(SQL.glob("*.sql")):
        if tep.name == TEP_PHAT_SAN:
            continue
        phan.append(bo_chu_thich(tep.read_text(encoding="utf-8")))
    return re.sub(r"\s+", " ", " ".join(phan))


def doc_cau_hinh_may_chu() -> str:
    if not CAU_HINH_MAY_CHU.exists():
        return ""
    dong = []
    for d in CAU_HINH_MAY_CHU.read_text(encoding="utf-8").splitlines():
        d = d.split("#", 1)[0].strip()
        if d:
            dong.append(d)
    return "\n".join(dong)


def co(mau: str, trong: str) -> bool:
    """Tìm một mẫu, không phân biệt hoa thường, coi mọi khoảng trắng như một."""
    return re.search(mau, trong, flags=re.IGNORECASE) is not None


def doc_ket_qua(duong_dan: Path) -> dict[str, str]:
    """Đọc một tệp kết quả dạng khóa và giá trị, mỗi dòng một cặp."""
    ra: dict[str, str] = {}
    for dong in duong_dan.read_text(encoding="utf-8").splitlines():
        if not dong.strip() or ":" not in dong:
            continue
        khoa, gia_tri = dong.split(":", 1)
        ra[khoa.strip()] = gia_tri.strip()
    return ra
