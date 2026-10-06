"""Ứng dụng thử nghiệm của lab S6, trạng thái khởi đầu.

Nó nhỏ có chủ đích. Cả buổi học đo quyết định cấu hình của bạn chứ không đo sức
đọc mã, nên mọi thứ đáng đọc nằm gọn trong tệp này và trong chinh-sach.yaml
cạnh nó. Đọc hết một lượt mất khoảng mười phút, và mười phút ấy là phần bắt
buộc: bạn không vá được thứ bạn chưa đọc.

Bốn chỗ bạn sửa đều mang nhãn `CHỖ LÀM VIỆC CỦA BẠN`. Một chỗ nằm trong tệp
này, ba chỗ còn lại nằm trong chinh-sach.yaml. Sự chia ấy không ngẫu nhiên, và
nó là một câu của mục 6.7 giáo trình viết thành mã: có lỗ hổng chỉ sửa được
bằng mã, có lỗ hổng chỉ sửa được bằng cấu hình, và nhầm loại thì bạn sẽ sửa
đúng thứ ở sai chỗ.

Ứng dụng dùng thư viện chuẩn của Python cộng PyYAML, không dùng khung web nào.
Lý do là một khung web hiện đại đã tự đặt sẵn phần lớn các tiêu đề mà bài này
bắt bạn đặt tay, và khi ấy bạn học được cách bật một tùy chọn chứ không học
được thứ tùy chọn ấy làm gì.
"""
from __future__ import annotations

import html
import http.server
import json
import os
import secrets
import socketserver
import sys
import urllib.parse
from pathlib import Path

import yaml

CHINH_SACH = Path(os.environ.get("CSS_CHINH_SACH", "/etc/css-s06/chinh-sach.yaml"))
CONG = int(os.environ.get("CSS_CONG", "8081"))

# Cơ sở dữ liệu của ứng dụng, gói trong một từ điển, vì bài này không nói về cơ
# sở dữ liệu. Buổi S4 đã nói phần ấy.
HO_SO = {"ten": "Nguyễn Văn An", "dia_chi": "12 Nguyễn Đình Chiểu, Quận 1"}


def nap_chinh_sach() -> dict:
    if not CHINH_SACH.exists():
        sys.exit(f"Không thấy tệp chính sách {CHINH_SACH}. Xem docker-compose.yml.")
    return yaml.safe_load(CHINH_SACH.read_text(encoding="utf-8")) or {}


TRANG_TIM_KIEM = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Tra cứu</title></head>
<body>
<h1>Kết quả tra cứu</h1>
<p>Bạn đã tìm: {tu_khoa}</p>
<p>Không có bản ghi nào khớp.</p>
</body></html>
"""

TRANG_DOI_DIA_CHI = """<!doctype html>
<html lang="vi"><head><meta charset="utf-8"><title>Đổi địa chỉ</title></head>
<body>
<h1>Địa chỉ nhận hàng</h1>
<p>Hiện tại: {dia_chi}</p>
<form method="post" action="/thu/doi-dia-chi">
  <input type="hidden" name="the" value="{the}">
  <input name="dia_chi" value="">
  <button type="submit">Lưu</button>
</form>
</body></html>
"""


def html_tim_kiem(tu_khoa: str) -> str:
    """Ghép từ khóa vào thân trang.

    Hàm này KHÔNG mã hóa gì cả, và nó cố ý như vậy. Chỗ phải mã hóa là chỗ gọi
    nó, vì chỉ ở chỗ gọi mới biết chuỗi sắp rơi vào ngữ cảnh nào của tài liệu:
    thân HTML, giá trị thuộc tính, và bên trong một khối kịch bản là ba ngữ
    cảnh khác nhau và ba phép mã hóa khác nhau. Một hàm mã hóa đặt quá sớm sẽ
    đúng cho một ngữ cảnh và sai cho hai ngữ cảnh còn lại.
    """
    return TRANG_TIM_KIEM.format(tu_khoa=tu_khoa)


class MayChu(http.server.BaseHTTPRequestHandler):
    server_version = "css-s06"
    sys_version = ""
    chinh_sach: dict = {}

    # ------------------------------------------------------------ tiêu đề

    def _tieu_de_csp(self, nonce: str) -> tuple[str, str] | None:
        """Dựng tiêu đề chính sách an toàn nội dung từ chinh-sach.yaml.

        Trả về None khi chính sách không khai chỉ thị nào, tức trạng thái khởi
        đầu của bài: máy chủ không nói gì với trình duyệt, nên trình duyệt cho
        chạy mọi thứ có trong trang.
        """
        csp = (self.chinh_sach.get("csp") or {})
        chi_thi = csp.get("chi_thi") or {}
        if not chi_thi:
            return None
        phan = []
        for ten, gia_tri in chi_thi.items():
            gia_tri = str(gia_tri).replace("{nonce}", nonce)
            phan.append(f"{ten} {gia_tri}".strip())
        diem_nhan = csp.get("diem_nhan_bao_cao")
        if diem_nhan:
            phan.append(f"report-uri {diem_nhan}")
        ten_tieu_de = (
            "Content-Security-Policy"
            if csp.get("che_do") == "cuong-che"
            else "Content-Security-Policy-Report-Only"
        )
        return ten_tieu_de, "; ".join(phan)

    def _dat_cookie_phien(self) -> str:
        """Đặt cookie phiên theo chinh-sach.yaml, trả về giá trị đã đặt."""
        cau_hinh = self.chinh_sach.get("cookie_phien") or {}
        ten = cau_hinh.get("ten", "css_s06_phien")
        gia_tri = secrets.token_hex(16)
        phan = [f"{ten}={gia_tri}", "Path=/"]
        if cau_hinh.get("httponly"):
            phan.append("HttpOnly")
        if cau_hinh.get("secure"):
            phan.append("Secure")
        if cau_hinh.get("samesite"):
            phan.append(f"SameSite={cau_hinh['samesite']}")
        self.send_header("Set-Cookie", "; ".join(phan))
        return gia_tri

    def _tra_loi(self, ma: int, than: str, kieu: str = "text/html; charset=utf-8") -> None:
        goi = than.encode("utf-8")
        nonce = secrets.token_urlsafe(16)
        self.send_response(ma)
        self.send_header("Content-Type", kieu)
        self.send_header("Content-Length", str(len(goi)))
        csp = self._tieu_de_csp(nonce)
        if csp:
            self.send_header(*csp)
        self._dat_cookie_phien()
        self.end_headers()
        self.wfile.write(goi)

    # ------------------------------------------------------------ chống giả mạo

    def _the_chong_gia_mao(self) -> str:
        """Thẻ chống giả mạo, buộc vào phiên.

        Thẻ này luôn được PHÁT. Việc nó có được KIỂM hay không do chinh-sach.yaml
        quyết, và đó là chỗ làm việc thứ tư của bạn. Phát mà không kiểm là hình
        dạng thường gặp nhất của lỗ hổng này ngoài đời: nhìn vào mã nguồn thấy có
        thẻ, nên ai cũng tưởng đã xong.
        """
        return secrets.token_urlsafe(24)

    def _tu_choi_vi_gia_mao(self, than_yeu_cau: dict) -> str | None:
        """Trả về lý do từ chối, hoặc None khi yêu cầu đi qua được.

        Hai phép kiểm ở đây đọc thẳng chinh-sach.yaml. Cả hai đang TẮT trong bản
        phát cho bạn.
        """
        cau_hinh = self.chinh_sach.get("chong_gia_mao") or {}
        if cau_hinh.get("kiem_origin"):
            goc = self.headers.get("Origin") or self.headers.get("Referer") or ""
            cho_phep = [str(g) for g in (cau_hinh.get("goc_cho_phep") or [])]
            if not any(goc.startswith(g) for g in cho_phep):
                return f"origin-khong-thuoc-danh-sach-cho-phep: {goc or 'khong-co'}"
        if cau_hinh.get("the_chong_gia_mao"):
            if not (than_yeu_cau.get("the") or [""])[0].strip():
                return "thieu-the-chong-gia-mao"
        return None

    # ------------------------------------------------------------ định tuyến

    def do_GET(self) -> None:  # noqa: N802
        duong, _, truy_van = self.path.partition("?")
        tham_so = urllib.parse.parse_qs(truy_van)

        if duong == "/":
            self._tra_loi(200, "<!doctype html><html lang=vi><body><h1>Cổng thử nghiệm S6</h1></body></html>")
            return

        if duong == "/thu/tim-kiem":
            tu_khoa = (tham_so.get("q") or [""])[0]
            # === CHỖ LÀM VIỆC CỦA BẠN, việc 1: lỗ hổng LH-1, CWE-79 ===
            # Chuỗi `tu_khoa` đến thẳng từ người gửi yêu cầu và đang được ghép
            # nguyên văn vào thân HTML. Mã hóa nó theo đúng ngữ cảnh nó rơi vào.
            # Thư viện chuẩn đã có sẵn hàm cần dùng, và tệp này đã nhập nó ở
            # đầu. Một dòng là đủ; nếu bạn thấy mình viết một bộ lọc danh sách
            # đen thì bạn đang đi sai đường, và mục 6.4 giải thích vì sao.
            than = html_tim_kiem(html.escape(tu_khoa))
            # === HẾT CHỖ LÀM VIỆC ===
            self._tra_loi(200, than)
            return

        if duong == "/thu/doi-dia-chi":
            self._tra_loi(
                200,
                TRANG_DOI_DIA_CHI.format(
                    dia_chi=html.escape(HO_SO["dia_chi"]),
                    the=html.escape(self._the_chong_gia_mao()),
                ),
            )
            return

        self._tra_loi(404, "<!doctype html><html lang=vi><body><p>Không có trang này.</p></body></html>")

    def do_POST(self) -> None:  # noqa: N802
        duong, _, _ = self.path.partition("?")
        dai = int(self.headers.get("Content-Length") or 0)
        tho = self.rfile.read(dai).decode("utf-8", "replace") if dai else ""

        if duong == "/thu/bao-cao-csp":
            # Điểm nhận báo cáo vi phạm chính sách. Trình duyệt gửi tới đây một
            # tài liệu JSON mỗi lần nó chặn hoặc lẽ ra đã chặn một thứ. Ở chế độ
            # chỉ báo cáo, đây là toàn bộ thứ bạn có để biết bật cưỡng chế lên
            # thì trang gãy chỗ nào.
            Path("/tmp/bao-cao-csp.jsonl").open("a", encoding="utf-8").write(tho.strip() + "\n")
            self._tra_loi(204, "")
            return

        if duong == "/thu/doi-dia-chi":
            than_yeu_cau = urllib.parse.parse_qs(tho)
            ly_do = self._tu_choi_vi_gia_mao(than_yeu_cau)
            if ly_do:
                self._tra_loi(
                    403,
                    json.dumps({"phan_quyet": "TU_CHOI", "ly_do": ly_do}, ensure_ascii=False),
                    kieu="application/json; charset=utf-8",
                )
                return
            moi = (than_yeu_cau.get("dia_chi") or [""])[0]
            HO_SO["dia_chi"] = moi or HO_SO["dia_chi"]
            self._tra_loi(
                200,
                json.dumps({"phan_quyet": "DA_NHAN", "dia_chi": HO_SO["dia_chi"]}, ensure_ascii=False),
                kieu="application/json; charset=utf-8",
            )
            return

        self._tra_loi(404, "{}", kieu="application/json; charset=utf-8")

    def log_message(self, dinh_dang: str, *tham_so) -> None:  # noqa: A002
        # Ghi ra dòng chuẩn để `docker compose logs` đọc được, một dòng một yêu
        # cầu, không kèm dấu thời gian, vì dấu thời gian làm hai lần chạy khác
        # nhau ở mức byte và mục 7 của đặc tả đòi hai lần chạy cho cùng kết quả.
        sys.stderr.write("%s %s\n" % (self.address_string(), dinh_dang % tham_so))


class MayChuDaLuong(socketserver.ThreadingMixIn, http.server.HTTPServer):
    daemon_threads = True
    allow_reuse_address = True


def main() -> None:
    MayChu.chinh_sach = nap_chinh_sach()
    with MayChuDaLuong(("0.0.0.0", CONG), MayChu) as may_chu:
        sys.stderr.write(f"css-s06 nghe tren cong {CONG}\n")
        may_chu.serve_forever()


if __name__ == "__main__":
    main()
