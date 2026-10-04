"""Dịch vụ tài nguyên. Bạn KHÔNG cần sửa tệp này, nhưng nên đọc nó một lượt.

Nó cố ý mỏng, để thấy rõ toàn bộ phần khó nằm ở hai hàm bạn viết trong
`kiem_the.py`. Ba việc nó làm là lấy khóa công khai một lần lúc khởi động, bóc
tấm thẻ ra khỏi tiêu đề `Authorization`, và dịch phán quyết thành mã trạng thái.

Mã trạng thái phân biệt hai chuyện khác nhau, và sự phân biệt ấy là một phần của
bài. 401 nghĩa là *tôi không tin tấm thẻ này*, tức `kiem_the` đã chặn. 403 nghĩa
là *tôi tin bạn là ai, và chính vì thế tôi biết bạn không được làm việc này*,
tức `quyet_dinh` đã chặn. Trả 403 cho một tấm thẻ hỏng chữ ký là nói với kẻ tấn
công rằng chữ ký của họ đã qua cửa.
"""
from __future__ import annotations

import base64
import datetime
import json
import os
import re
import sys
import textwrap
import time
import urllib.error
import urllib.parse
import urllib.request
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import yaml

from kiem_the import TheKhongHopLe, kiem_the, quyet_dinh

CANH_BAO_KHOI_DAU = (
    "che do khoi dau: kiem_the hoac quyet_dinh chua duoc viet, dich vu dang boc the "
    "ma khong kiem gi ca"
)


def boc_khong_kiem(the: str) -> dict:
    """Chế độ khởi đầu, dùng khi `kiem_the` chưa được viết.

    Nó bóc phần giữa của tấm thẻ ra và tin mọi thứ đọc được trong đó. Nó có mặt
    để `make attack` cho bạn thấy một dịch vụ không kiểm gì trông ra sao, và nó
    biến mất ngay khi bạn viết xong hàm của mình. Đừng chép nó: đây đúng là hình
    dạng của chỗ hỏng mà cả buổi hôm nay nói tới.
    """
    khai = the.split(".")[1]
    khai += "=" * (-len(khai) % 4)
    return json.loads(base64.urlsafe_b64decode(khai))

NGUOI_NHAN = os.environ.get("CSS_NGUOI_NHAN", "dich-vu-ho-so")
BEN_PHAT_HANH = os.environ.get("CSS_BEN_PHAT_HANH", "http://may-danh-tinh:8080/realms/css")
DUONG_CHINH_SACH = os.environ.get("CSS_CHINH_SACH", "/etc/css-s05/chinh-sach.yaml")
CONG = int(os.environ.get("CSS_CONG", "8000"))

CAU_HINH = {
    "thuat_toan_cho_phep": ["RS256"],
    "nguoi_nhan": NGUOI_NHAN,
    "ben_phat_hanh": BEN_PHAT_HANH,
    "do_lech_dong_ho_giay": 5,
}

# Nhật ký kiểm thẻ. Mỗi yêu cầu xin hồ sơ sinh đúng một dòng theo khuôn chung của
# học phần, và lab S7 tìm lại sự kiện "một tấm thẻ quá hạn" trong chính các dòng
# này. Khuôn dòng:
#
#   <thời điểm ISO 8601 có múi giờ> su_kien=kiem_the uid=<số> euid=<số> chi_tiet=<...>
#
# Ví dụ dòng của phép kiểm N3:
#
#   2026-10-04T14:05:09+0700 su_kien=kiem_the uid=10005 euid=10005 chi_tiet=ly_do=qua_han ket_qua=tu_choi ma_http=401 chu_the_tu_khai=an-nv duong_dan=/ho-so thong_bao=thẻ đã quá hạn
#
# Dòng luôn đi ra stderr, tức vào `docker compose logs dich-vu`. Nếu biến môi
# trường CSS_NHAT_KY trỏ tới một tệp thì dòng được ghi nối thêm vào tệp đó.
NHAT_KY = os.environ.get("CSS_NHAT_KY", "")
DO_DAI_THONG_BAO_TOI_DA = 200
_KY_TU_DIEU_KHIEN = re.compile(r"[\x00-\x1f\x7f]")


def _lam_sach(gia_tri: object, giu_khoang_trang: bool = False) -> str:
    """Bỏ ký tự điều khiển khỏi một giá trị trước khi đưa vào nhật ký.

    Tên người dùng, đường dẫn và câu báo lỗi đều có phần do người gửi yêu cầu
    chọn. Một ký tự xuống dòng lọt vào nhật ký sẽ dựng được một dòng giả mang
    đúng khuôn của dòng thật, tức điểm yếu CWE-117, và lab S7 đọc lại chính nhật
    ký này để điều tra. Dấu bằng trong giá trị cũng được thay bằng gạch dưới, để
    một giá trị không giả được một cặp khóa và giá trị đứng cạnh nó.
    """
    van_ban = _KY_TU_DIEU_KHIEN.sub(" ", str(gia_tri)).replace("=", "_")
    if giu_khoang_trang:
        return " ".join(van_ban.split())
    return "_".join(van_ban.split()) or "-"


def dong_nhat_ky(
    su_kien: str,
    truong: dict,
    thong_bao: str = "",
    thoi_diem: datetime.datetime | None = None,
    uid: int | None = None,
    euid: int | None = None,
) -> str:
    """Dựng một dòng nhật ký theo khuôn chung, không ghi gì ra ngoài.

    Các cặp khóa và giá trị trong `truong` đứng trước, `thong_bao` đứng cuối và
    được giữ khoảng trắng, vì trường cuối dòng là trường duy nhất được phép chứa
    khoảng trắng mà không làm lệch các trường đứng trước nó.
    """
    if thoi_diem is None:
        thoi_diem = datetime.datetime.now().astimezone()
    uid = os.getuid() if uid is None else uid
    euid = os.geteuid() if euid is None else euid
    chi_tiet = " ".join(f"{_lam_sach(k)}={_lam_sach(v)}" for k, v in truong.items())
    if thong_bao:
        chi_tiet += " thong_bao=" + _lam_sach(thong_bao, giu_khoang_trang=True)[:DO_DAI_THONG_BAO_TOI_DA]
    return "{} su_kien={} uid={} euid={} chi_tiet={}".format(
        thoi_diem.strftime("%Y-%m-%dT%H:%M:%S%z"), _lam_sach(su_kien), uid, euid, chi_tiet
    )


def ghi_nhat_ky(dong: str) -> None:
    """Đưa một dòng ra stderr, và nối vào tệp CSS_NHAT_KY nếu biến này được đặt."""
    sys.stderr.write(dong + "\n")
    sys.stderr.flush()
    if not NHAT_KY:
        return
    try:
        with open(NHAT_KY, "a", encoding="utf-8") as tep:
            tep.write(dong + "\n")
    except OSError as loi:
        # Không ghi được tệp nhật ký thì phải báo ra stderr, không bỏ qua im lặng.
        sys.stderr.write(f"khong ghi duoc nhat ky vao {NHAT_KY}: {loi.strerror}\n")


def _doc_doan(the: str, vi_tri: int) -> dict:
    doan = the.split(".")[vi_tri]
    doan += "=" * (-len(doan) % 4)
    gia_tri = json.loads(base64.urlsafe_b64decode(doan))
    return gia_tri if isinstance(gia_tri, dict) else {}


def ly_do_tu_choi(the: str, cau_hinh: dict, bay_gio: float | None = None) -> tuple[str, str]:
    """Gọi tên lý do một tấm thẻ đã bị `kiem_the` từ chối, chỉ để ghi nhật ký.

    Trả về cặp (lý do, chủ thể tự khai). Hàm đọc phần đầu và tập khai CHƯA được
    kiểm chữ ký, nên kết quả chỉ được dùng để ghi nhật ký và không bao giờ được
    dùng để quyết định cho qua hay chặn: quyết định đó đã do `kiem_the` đưa ra.
    Các phép thử đi theo thứ tự thuật toán, thời hạn, người nhận, bên phát hành;
    tấm thẻ không rơi vào nhánh nào thì lý do còn lại được ghi là chữ ký hoặc lỗi
    khác, và câu báo lỗi của `kiem_the` ở trường thong_bao cho biết chi tiết.

    Hàm không bao giờ ném lỗi. Tấm thẻ do người gửi chọn, nên phần JSON bên trong
    có thể lồng sâu tới mức bộ phân tích cạn ngăn xếp; khi ấy, hay gặp bất cứ lỗi
    nào khác, lý do được ghi là `khong_xac_dinh` và dịch vụ vẫn trả 401 như thường.
    """
    try:
        return _ly_do_tu_choi(the, cau_hinh, bay_gio)
    except Exception:
        return "khong_xac_dinh", "-"


def _ly_do_tu_choi(the: str, cau_hinh: dict, bay_gio: float | None) -> tuple[str, str]:
    bay_gio = time.time() if bay_gio is None else bay_gio
    try:
        dau, khai = _doc_doan(the, 0), _doc_doan(the, 1)
    except (IndexError, ValueError):
        return "the_hong", "-"
    chu_the = str(khai.get("preferred_username") or khai.get("sub") or "-")
    if dau.get("alg") not in cau_hinh.get("thuat_toan_cho_phep", []):
        return "thuat_toan", chu_the
    het_han = khai.get("exp")
    if isinstance(het_han, (int, float)) and het_han + cau_hinh.get("do_lech_dong_ho_giay", 0) < bay_gio:
        return "qua_han", chu_the
    nguoi_nhan = khai.get("aud")
    nguoi_nhan = nguoi_nhan if isinstance(nguoi_nhan, list) else [nguoi_nhan]
    if cau_hinh.get("nguoi_nhan") not in nguoi_nhan:
        return "nguoi_nhan", chu_the
    if khai.get("iss") != cau_hinh.get("ben_phat_hanh"):
        return "ben_phat_hanh", chu_the
    return "chu_ky_hoac_khac", chu_the


def lay_khoa_cong(dia_chi: str, so_lan: int = 60) -> str:
    """Hỏi vùng định danh lấy khóa công khai, dạng PEM.

    Vùng định danh khởi động chậm hơn dịch vụ này, nên hàm hỏi lại nhiều lần thay
    vì chết ngay. Khóa lấy MỘT lần lúc khởi động: nếu vùng định danh xoay khóa
    giữa chừng thì dịch vụ phải khởi động lại, và đó là một giới hạn thật của bản
    lab.
    """
    for lan in range(so_lan):
        try:
            with urllib.request.urlopen(dia_chi, timeout=3) as tra_loi:
                than = json.loads(tra_loi.read().decode("utf-8"))
            b64 = than["public_key"]
            than_pem = "\n".join(textwrap.wrap(b64, 64))
            return f"-----BEGIN PUBLIC KEY-----\n{than_pem}\n-----END PUBLIC KEY-----\n"
        except (urllib.error.URLError, KeyError, json.JSONDecodeError, TimeoutError):
            if lan == 0:
                print(f"đang đợi vùng định danh ở {dia_chi}", file=sys.stderr)
            time.sleep(2)
    raise SystemExit(f"không lấy được khóa công khai từ {dia_chi} sau {so_lan} lần hỏi")


def doc_chinh_sach(duong_dan: str) -> dict:
    with open(duong_dan, encoding="utf-8") as tep:
        return yaml.safe_load(tep) or {}


class Xu_Ly(BaseHTTPRequestHandler):
    server_version = "css-s05"
    sys_version = ""

    def _tra_loi(self, ma: int, than: dict) -> None:
        goi = json.dumps(than, ensure_ascii=False).encode("utf-8")
        self.send_response(ma)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Content-Length", str(len(goi)))
        self.end_headers()
        self.wfile.write(goi)

    def _phuc_vu(self, phuong_thuc: str) -> None:
        duong, _, truy_van = self.path.partition("?")
        if duong == "/suc-khoe":
            self._tra_loi(200, {"trang_thai": "song"})
            return

        tieu_de = self.headers.get("Authorization", "")
        if not tieu_de.startswith("Bearer "):
            ghi_nhat_ky(dong_nhat_ky("kiem_the", {
                "ly_do": "thieu_the", "ket_qua": "tu_choi", "ma_http": 401, "duong_dan": duong,
            }))
            self._tra_loi(401, {"tu_choi": "thiếu tiêu đề Authorization dạng Bearer"})
            return

        the = tieu_de[len("Bearer "):].strip()
        try:
            khai = kiem_the(the, self.server.khoa_cong, CAU_HINH)
        except TheKhongHopLe as loi:
            ly_do, chu_the = ly_do_tu_choi(the, CAU_HINH)
            ghi_nhat_ky(dong_nhat_ky("kiem_the", {
                "ly_do": ly_do, "ket_qua": "tu_choi", "ma_http": 401,
                "chu_the_tu_khai": chu_the, "duong_dan": duong,
            }, thong_bao=str(loi)))
            self._tra_loi(401, {"tu_choi": f"thẻ không đứng vững: {loi}"})
            return
        except NotImplementedError:
            khai = boc_khong_kiem(the)
            khoi_dau = True
        else:
            khoi_dau = False

        yeu_cau = {
            "duong_dan": duong,
            "phuong_thuc": phuong_thuc,
            "don_vi": urllib.parse.parse_qs(truy_van).get("don_vi", [""])[0],
        }
        try:
            cho_phep = quyet_dinh(khai, yeu_cau, self.server.chinh_sach)
        except NotImplementedError:
            cho_phep = True
            khoi_dau = True

        chu_the = khai.get("preferred_username") or khai.get("sub") or "-"
        if not cho_phep:
            ghi_nhat_ky(dong_nhat_ky("kiem_the", {
                "ly_do": "chinh_sach", "ket_qua": "tu_choi", "ma_http": 403, "chu_the": chu_the,
                "duong_dan": duong, "phuong_thuc": phuong_thuc, "don_vi": yeu_cau["don_vi"] or "-",
            }))
            self._tra_loi(403, {"tu_choi": "chính sách không cho phép yêu cầu này", "yeu_cau": yeu_cau})
            return

        ghi_nhat_ky(dong_nhat_ky("kiem_the", {
            "ly_do": "khong_kiem" if khoi_dau else "hop_le", "ket_qua": "cho_qua", "ma_http": 200,
            "chu_the": chu_the, "duong_dan": duong, "phuong_thuc": phuong_thuc,
            "don_vi": yeu_cau["don_vi"] or "-",
        }))

        tra_loi = {
            "chu_the": khai.get("preferred_username") or khai.get("sub"),
            "don_vi": khai.get("don_vi"),
            "ho_so": [{"ma": "HS-001", "don_vi": yeu_cau["don_vi"], "noi_dung": "dữ liệu giả, dựng để dạy học"}],
        }
        if khoi_dau:
            tra_loi["canh_bao"] = CANH_BAO_KHOI_DAU
        self._tra_loi(200, tra_loi)

    def do_GET(self) -> None:
        self._phuc_vu("GET")

    def do_POST(self) -> None:
        self._phuc_vu("POST")

    def do_DELETE(self) -> None:
        self._phuc_vu("DELETE")

    def log_message(self, dinh_dang: str, *doi_so) -> None:
        # Ghi ra dòng chuẩn để `docker compose logs dich-vu` đọc được. Buổi S7 lấy
        # chính loại nhật ký này làm dữ liệu, nên đừng tắt nó.
        sys.stderr.write("%s - %s\n" % (self.address_string(), dinh_dang % doi_so))


def main() -> None:
    may = ThreadingHTTPServer(("0.0.0.0", CONG), Xu_Ly)
    may.khoa_cong = lay_khoa_cong(BEN_PHAT_HANH)
    may.chinh_sach = doc_chinh_sach(DUONG_CHINH_SACH)
    print(f"dịch vụ nghe cổng {CONG}, người nhận {NGUOI_NHAN}", file=sys.stderr)
    may.serve_forever()


if __name__ == "__main__":
    main()
