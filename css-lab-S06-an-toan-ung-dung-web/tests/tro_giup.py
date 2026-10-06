"""Phần dùng chung của bộ kiểm công khai lab S6.

Tệp này không chứa phép kiểm nào. Nó giữ bốn thứ mà năm tệp kiểm đều cần: chỗ
đứng của bài đang chấm, danh mục mã chuẩn được phép dùng, một cái xưởng nhỏ dựng
ứng dụng của bạn lên rồi gọi nó bằng HTTP thật, và vài hàm đọc tệp có thông điệp
lỗi tử tế.

Cái xưởng ấy là chỗ đáng đọc trước khi làm bài, vì nó quyết định bộ chấm đo được
gì. Nó nạp `ung-dung/ung_dung.py` của bạn theo đường dẫn, gắn vào đó chính
`ung-dung/chinh-sach.yaml` của bạn, cho máy chủ nghe trên một cổng tạm của
127.0.0.1, rồi gửi những yêu cầu thật. Nghĩa là bảy phép kiểm nhóm lỗ hổng và
nhóm chính sách nội dung là phép ĐO THẬT, không phải phép đọc lời khai: thứ quyết
định chúng xanh hay đỏ là phản hồi mà mã của bạn trả về. Chúng cũng không cần
Docker, nên bạn tự kiểm được ngay cả khi máy đang hỏng phần container.

Hai gốc đường dẫn, và nhầm chỗ này thì bộ chấm chấm nhầm thứ. `ROOT` là bài đang
chấm, tức thứ sinh viên nộp, và nó đổi được qua biến môi trường LAB_ROOT. `KHUNG`
là bản phát của lab, nơi đặt bộ luật semgrep; bộ luật ấy do đề cung cấp chứ không
do sinh viên viết, nên nó luôn lấy từ KHUNG. Nếu lấy nó từ ROOT thì một bài nộp có
thể thay chính cái thước đang đo mình.

Sinh viên không cần đặt LAB_ROOT và không nên đặt. Nó tồn tại để bộ kiểm nội bộ
của giảng viên chạy được chính bộ kiểm này lên một bản mẫu đạt và một bản mẫu
trượt, vì một bộ chấm chưa bao giờ chạy trên một bài sai thì không ai biết nó có
bắt được lỗi hay không.
"""
from __future__ import annotations

import contextlib
import importlib.util
import json
import os
import socket
import sys
import threading
import urllib.error
import urllib.request
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
MAKEFILE = ROOT / "Makefile"
UNG_DUNG = ROOT / "ung-dung" / "ung_dung.py"
CHINH_SACH = ROOT / "ung-dung" / "chinh-sach.yaml"
XEP_LOAI = ROOT / "docs" / "xep-loai-canh-bao.yaml"
DANH_DOI = ROOT / "docs" / "danh-doi.md"

EVID = ROOT / "evidence" / "S6"
PREFLIGHT = EVID / "preflight.txt"
QUET_TRUOC = EVID / "quet-truoc.json"
QUET_SAU = EVID / "quet-sau.json"
SEMGREP_TRUOC = EVID / "semgrep-truoc.json"
SEMGREP_SAU = EVID / "semgrep-sau.json"
BAO_CAO_CSP = EVID / "bao-cao-csp.jsonl"
NHAT_KY = EVID / "nhat-ky.txt"

# Trần bốn container cho mỗi lab, gồm cả container chấm. Ngưỡng của ADR-0003 mục
# N3, đặt theo cấu hình laptop phổ thông của lớp chứ không theo sở thích.
TRAN_CONTAINER = 4

# Danh mục mã chuẩn. CHÉP từ core/syllabus/mapping/S06-mapping.yaml, khối lab, nơi
# từng mã đã được mở trang riêng và đọc trạng thái ngày 18/08/2026. Không gõ lại
# theo trí nhớ: buổi S07 đã trả giá một lần khi nhánh T1562 bị thu hồi trong
# ATT&CK v19 mà tài liệu vẫn in bản cũ.
# Phiên bản danh mục: ATT&CK content v19.2, CWE List 4.20, OWASP Top 10:2025.
MA_ATTACK_CHO_PHEP = {"T1189", "T1190", "T1195.001", "T1539"}
MA_CWE_CHO_PHEP = {
    "CWE-79", "CWE-209", "CWE-352", "CWE-639",
    "CWE-862", "CWE-918", "CWE-1104", "CWE-1275",
}

# Hai lỗ hổng được chỉ định của bài, và mã đúng của chúng.
#
# Ô OWASP của LH-1 là chỗ dễ gán sai nhất trong cả bài, nên nó được chốt sẵn ở
# đây. Danh sách ánh xạ của A05:2025 Injection là danh sách CHỨA CWE-79, đọc ngày
# 18/08/2026; A01:2025 và A10:2025 thì không. Bảng ánh xạ của buổi ghi rõ điều
# này để bộ chấm không xếp CWE-79 nhầm chỗ, dù thân bài trình bày kịch bản chéo
# trang trong cùng mục với chuyện khác.
MA_DUNG_LH1 = {"ma_cwe": "CWE-79", "hang_owasp": "A05:2025"}
MA_DUNG_LH2 = {"ma_cwe": "CWE-352", "hang_owasp": "A01:2025", "ma_cwe_nua_samesite": "CWE-1275"}

XEP_LOAI_HOP_LE = {"sua_bang_cau_hinh", "sua_bang_ma", "khong_phai_canh_bao_that"}
XEP_LOAI_SUA_DUOC = {"sua_bang_cau_hinh", "sua_bang_ma"}

# Tên dịch vụ trong mạng compose của bài. Bộ quét chỉ được trỏ vào đây, và không
# vào đâu khác. Ràng buộc này là ràng buộc của SCOPE.md, không phải sở thích về
# cách viết cấu hình.
DICH_VU_DUOC_QUET = {"ung-dung", "muc-tieu"}

# Bốn chỉ thị mà chính sách nội dung của bài phải khai, ứng với bốn câu hỏi in
# trong ung-dung/chinh-sach.yaml.
CHI_THI_BAT_BUOC = ("script-src", "object-src", "base-uri", "frame-ancestors")

# Từ khóa lành dùng cho chiều dương. Nó có dấu tiếng Việt và có khoảng trắng, nên
# một bộ lọc danh sách đen viết vội sẽ cắt mất một phần của nó.
TU_KHOA_LANH = "bảng lương quý 3"

TAI_TRONG_THU = (
    "<script>alert(1)</script>",
    '"><img src=x onerror=alert(1)>',
)

GOC_HOP_LE = "http://127.0.0.1:8081"
GOC_LA = "http://trang-cua-ke-tan-cong.example"


# ------------------------------------------------------------ đọc tệp

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


def so_tu(chu: object) -> int:
    return len(str(chu or "").split())


# ------------------------------------------------------------ dựng ứng dụng của bạn

def nap_ung_dung():
    """Nạp ung-dung/ung_dung.py của bài đang chấm, theo đường dẫn chứ theo tên."""
    if not UNG_DUNG.exists():
        pytest.fail(
            f"Không thấy {UNG_DUNG}. Đây là tệp mang chỗ làm việc thứ nhất của bài, "
            "đừng đổi tên và đừng đổi chỗ nó."
        )
    dac_ta = importlib.util.spec_from_file_location("ung_dung_cua_bai", UNG_DUNG)
    mo_dun = importlib.util.module_from_spec(dac_ta)
    sys.modules["ung_dung_cua_bai"] = mo_dun
    try:
        dac_ta.loader.exec_module(mo_dun)
    except Exception as loi:  # noqa: BLE001
        pytest.fail(
            f"Nạp ung_dung.py thất bại: {type(loi).__name__}: {loi}. "
            "Ứng dụng không chạy được thì không phép kiểm nào của bài đo được gì."
        )
    for ten in ("MayChu", "MayChuDaLuong", "html_tim_kiem"):
        if not hasattr(mo_dun, ten):
            pytest.fail(
                f"ung_dung.py thiếu {ten}. Bài chỉ yêu cầu bạn sửa MỘT dòng trong tệp này; "
                "xóa hay đổi tên các phần khác làm bộ chấm không gọi được ứng dụng."
            )
    return mo_dun


@contextlib.contextmanager
def may_chu_cua_ban():
    """Dựng ứng dụng của bạn trên một cổng tạm của 127.0.0.1, trả về địa chỉ gốc.

    Cổng lấy số 0, tức để hệ điều hành tự chọn một cổng còn rỗi, nên bộ kiểm chạy
    được cả khi `make up` đang giữ cổng 8081. Máy chủ tắt hẳn khi khối with kết
    thúc, kể cả khi một phép kiểm ném ngoại lệ giữa chừng.
    """
    mo_dun = nap_ung_dung()
    mo_dun.MayChu.chinh_sach = doc_yaml(
        CHINH_SACH,
        "Đây là tệp mang ba chỗ làm việc còn lại của bài.",
    )
    try:
        may = mo_dun.MayChuDaLuong(("127.0.0.1", 0), mo_dun.MayChu)
    except OSError as loi:
        pytest.fail(f"Không mở được cổng tạm để dựng ứng dụng: {loi}")
    cong = may.socket.getsockname()[1]
    luong = threading.Thread(target=may.serve_forever, daemon=True)
    luong.start()
    try:
        yield f"http://127.0.0.1:{cong}"
    finally:
        may.shutdown()
        may.server_close()
        luong.join(timeout=5)


def _goi(yeu_cau: urllib.request.Request) -> tuple[int, dict[str, list[str]], str]:
    """Gửi một yêu cầu, trả về mã, tiêu đề, thân.

    Mã 4xx của HTTP làm urllib ném ngoại lệ, nhưng ở bài này một câu trả lời 403
    là kết quả đáng mong đợi chứ không phải sự cố, nên nó được bắt lại và trả về
    như mọi câu trả lời khác.
    """
    try:
        with urllib.request.urlopen(yeu_cau, timeout=10) as phan_hoi:
            than = phan_hoi.read().decode("utf-8", "replace")
            return phan_hoi.status, _gom_tieu_de(phan_hoi.headers), than
    except urllib.error.HTTPError as loi:
        than = loi.read().decode("utf-8", "replace")
        return loi.code, _gom_tieu_de(loi.headers), than
    except (urllib.error.URLError, socket.timeout) as loi:
        pytest.fail(
            f"Không gọi được ứng dụng của bạn: {loi}. Ứng dụng phải khởi động được "
            "với chính chinh-sach.yaml bạn nộp; thử `python3 ung-dung/ung_dung.py` "
            "và đọc thông báo lỗi."
        )


def _gom_tieu_de(tieu_de) -> dict[str, list[str]]:
    """Gom tiêu đề phản hồi thành từ điển tên viết thường và danh sách giá trị.

    Phải là danh sách chứ không phải một giá trị, vì Set-Cookie có thể xuất hiện
    nhiều lần trong một phản hồi và lấy mỗi lần đầu là bỏ sót.
    """
    ra: dict[str, list[str]] = {}
    for ten, gia_tri in tieu_de.items():
        ra.setdefault(ten.lower(), []).append(gia_tri)
    return ra


def get(goc: str, duong: str, **tieu_de_them: str):
    yeu_cau = urllib.request.Request(goc + duong, method="GET")
    for ten, gia_tri in tieu_de_them.items():
        yeu_cau.add_header(ten.replace("_", "-"), gia_tri)
    return _goi(yeu_cau)


def post(goc: str, duong: str, du_lieu: str, **tieu_de_them: str):
    yeu_cau = urllib.request.Request(
        goc + duong,
        data=du_lieu.encode("utf-8"),
        method="POST",
    )
    yeu_cau.add_header("Content-Type", "application/x-www-form-urlencoded")
    for ten, gia_tri in tieu_de_them.items():
        yeu_cau.add_header(ten.replace("_", "-"), gia_tri)
    return _goi(yeu_cau)


def lay_the_chong_gia_mao(goc: str) -> str:
    """Lấy thẻ chống giả mạo từ chính trang biểu mẫu, như một trình duyệt thật."""
    _, _, than = get(goc, "/thu/doi-dia-chi")
    dau = than.find('name="the" value="')
    if dau == -1:
        pytest.fail(
            "Trang /thu/doi-dia-chi không còn ô ẩn mang thẻ chống giả mạo. "
            "Thẻ ấy do bản phát sinh sẵn và bài không yêu cầu bạn đổi cách phát nó; "
            "việc của bạn là bật phần KIỂM nó trong chinh-sach.yaml."
        )
    dau += len('name="the" value="')
    return than[dau:than.find('"', dau)]


def gia_tri_csp(tieu_de: dict[str, list[str]]) -> tuple[str, str]:
    """Trả về (tên tiêu đề chính sách nội dung, giá trị), hoặc ("", "") khi không có."""
    for ten in ("content-security-policy", "content-security-policy-report-only"):
        if ten in tieu_de:
            return ten, tieu_de[ten][0]
    return "", ""


def chi_thi_csp(gia_tri: str) -> dict[str, str]:
    """Tách chuỗi chính sách thành từ điển tên chỉ thị và phần giá trị."""
    ra: dict[str, str] = {}
    for phan in gia_tri.split(";"):
        phan = phan.strip()
        if not phan:
            continue
        ten, _, con_lai = phan.partition(" ")
        ra[ten.strip().lower()] = con_lai.strip()
    return ra
