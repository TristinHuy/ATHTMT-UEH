"""Bộ đọc và bộ chạy cho tập con Sigma dùng trong lab S7.

Vì sao lab tự mang một bộ chạy thay vì gọi bộ chuyển đổi Sigma chính thức. Bộ
chuyển đổi chính thức sinh ra câu truy vấn cho một kho nhật ký rồi để kho ấy trả
lời, nên muốn đo được quy tắc bạn viết thì phải có Loki đang chạy, có dữ liệu đã
nạp, và có mạng để cài bộ chuyển đổi. Ba thứ ấy hỏng một là cả bước đo hỏng theo,
và khi đó điểm của bạn phụ thuộc vào máy chứ không phụ thuộc vào quy tắc. Bộ chạy
này đọc thẳng quy tắc rồi áp lên từng bản ghi, nên phép đo cho cùng một con số ở
mọi máy, kể cả máy không dựng nổi container nào.

Cái giá phải trả, và bạn cần biết nó. Đây là TẬP CON của Sigma, không phải Sigma
đầy đủ. Nó hiểu phần cú pháp mà bài này cần và từ chối phần còn lại bằng một câu
báo lỗi nói rõ chỗ nào không hiểu, chứ không im lặng bỏ qua. Một quy tắc chạy
được ở đây vẫn là một quy tắc Sigma hợp lệ, nhưng chiều ngược lại không đúng.

Phần cú pháp được hiểu:

    detection:
      ten_khoi:                     một hoặc nhiều điều kiện, nối với nhau bằng VÀ
        truong: giá trị             bằng đúng, không phân biệt hoa thường
        truong|contains: giá trị    chứa chuỗi con
        truong|startswith: giá trị  bắt đầu bằng
        truong|endswith: giá trị    kết thúc bằng
        truong|contains|all: [a, b] chứa tất cả các chuỗi trong danh sách
        truong: [a, b]              bằng a HOẶC bằng b
      condition: ten_khoi
                 ten_khoi and khoi_khac
                 ten_khoi and not khoi_loai_tru
                 ten_khoi or khoi_khac

Không hỗ trợ: biểu thức chính quy, ký tự đại diện, đếm theo cửa sổ thời gian,
ngoặc đơn, và trộn lẫn "and" với "or" trong cùng một câu điều kiện. Chỗ nào cần
những thứ đó thì viết vào phần ghi chú của bài và nói vì sao tập con này không đủ.
"""
from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable

import yaml

BO_SUA_HIEU_DUOC = {"contains", "startswith", "endswith", "all"}
TRUONG_BAT_BUOC = ("title", "logsource", "detection", "level")


class QuyTacHong(Exception):
    """Quy tắc không đọc được. Thông điệp phải nói rõ chỗ hỏng và việc phải làm."""


def _chuoi(gia_tri: Any) -> str:
    if gia_tri is None:
        return ""
    if isinstance(gia_tri, bool):
        return "true" if gia_tri else "false"
    return str(gia_tri)


@dataclass(frozen=True)
class DieuKien:
    truong: str
    bo_sua: tuple[str, ...]
    gia_tri: tuple[str, ...]

    def khop(self, ban_ghi: dict) -> bool:
        that = _chuoi(ban_ghi.get(self.truong)).casefold()
        muc = [g.casefold() for g in self.gia_tri]
        if "all" in self.bo_sua:
            return all(self._mot(that, m) for m in muc)
        return any(self._mot(that, m) for m in muc)

    def _mot(self, that: str, muc: str) -> bool:
        if "contains" in self.bo_sua:
            return muc in that
        if "startswith" in self.bo_sua:
            return that.startswith(muc)
        if "endswith" in self.bo_sua:
            return that.endswith(muc)
        return that == muc


@dataclass(frozen=True)
class QuyTac:
    tieu_de: str
    muc: str
    nguon: dict
    khoi: dict[str, tuple[DieuKien, ...]]
    dieu_kien: str
    bao_nham_da_biet: tuple[str, ...]
    truong_da_dung: frozenset[str]

    def khop(self, ban_ghi: dict) -> bool:
        return _tinh_dieu_kien(self.dieu_kien, self.khoi, ban_ghi)


def _doc_khoi(ten: str, than: Any) -> tuple[DieuKien, ...]:
    if not isinstance(than, dict):
        raise QuyTacHong(
            f"Khối tìm kiếm {ten!r} phải là một ánh xạ trường sang giá trị. "
            "Dạng danh sách các khối con chưa được tập con này hiểu."
        )
    ra: list[DieuKien] = []
    for khoa, gia_tri in than.items():
        phan = str(khoa).split("|")
        truong, bo_sua = phan[0], tuple(p.strip().casefold() for p in phan[1:])
        la = [b for b in bo_sua if b not in BO_SUA_HIEU_DUOC]
        if la:
            raise QuyTacHong(
                f"Khối {ten!r}, trường {truong!r} dùng bộ sửa {la}. "
                f"Tập con này chỉ hiểu {sorted(BO_SUA_HIEU_DUOC)}."
            )
        muc = gia_tri if isinstance(gia_tri, list) else [gia_tri]
        if not muc:
            raise QuyTacHong(f"Khối {ten!r}, trường {truong!r} không có giá trị nào để so.")
        ra.append(DieuKien(truong, bo_sua, tuple(_chuoi(m) for m in muc)))
    if not ra:
        raise QuyTacHong(f"Khối tìm kiếm {ten!r} rỗng, nên nó khớp mọi bản ghi.")
    return tuple(ra)


def _tinh_dieu_kien(cau: str, khoi: dict[str, tuple[DieuKien, ...]], ban_ghi: dict) -> bool:
    tu = cau.split()
    ve: list[bool] = []
    phep: list[str] = []
    dao = False
    for t in tu:
        thap = t.casefold()
        if thap in {"and", "or"}:
            phep.append(thap)
            continue
        if thap == "not":
            dao = True
            continue
        gia_tri = all(dk.khop(ban_ghi) for dk in khoi[t])
        ve.append(not gia_tri if dao else gia_tri)
        dao = False
    ket = ve[0]
    for i, p in enumerate(phep):
        ket = (ket and ve[i + 1]) if p == "and" else (ket or ve[i + 1])
    return ket


def _kiem_cau_dieu_kien(cau: str, ten_khoi: Iterable[str]) -> None:
    co = set(ten_khoi)
    tu = cau.split()
    if not tu:
        raise QuyTacHong("Trường condition rỗng.")
    phep = {t.casefold() for t in tu if t.casefold() in {"and", "or"}}
    if len(phep) > 1:
        raise QuyTacHong(
            "Câu điều kiện trộn lẫn and với or. Tập con này không có ngoặc đơn nên "
            "thứ tự ưu tiên sẽ mơ hồ, và một quy tắc mơ hồ thì không đo được. "
            "Tách thành hai quy tắc, hoặc gộp điều kiện vào cùng một khối."
        )
    cho_ten = True
    dao_truoc = False
    for t in tu:
        thap = t.casefold()
        if thap in {"and", "or"}:
            if cho_ten:
                raise QuyTacHong(f"Câu điều kiện có phép {thap!r} đứng sai chỗ: {cau!r}")
            cho_ten, dao_truoc = True, False
            continue
        if thap == "not":
            if not cho_ten or dao_truoc:
                raise QuyTacHong(f"Từ not đứng sai chỗ trong câu điều kiện: {cau!r}")
            if "or" in phep:
                raise QuyTacHong("Tập con này chỉ cho phép not trong chuỗi nối bằng and.")
            dao_truoc = True
            continue
        if not cho_ten:
            raise QuyTacHong(f"Hai tên khối đứng liền nhau, thiếu and hoặc or: {cau!r}")
        if t not in co:
            raise QuyTacHong(
                f"Câu điều kiện gọi khối {t!r} nhưng detection không khai khối ấy. "
                f"Các khối đang có: {sorted(co)}."
            )
        cho_ten, dao_truoc = False, False
    if cho_ten:
        raise QuyTacHong(f"Câu điều kiện kết thúc giữa chừng: {cau!r}")
    dung = {t for t in tu if t.casefold() not in {"and", "or", "not"}}
    thua = sorted(co - dung)
    if thua:
        raise QuyTacHong(
            f"Khối {thua} được khai trong detection nhưng câu condition không gọi tới. "
            "Một khối không ai gọi thì không ảnh hưởng gì tới kết quả, và để nó lại "
            "làm người đọc tưởng quy tắc chặt hơn thực tế."
        )


def doc_quy_tac(duong_dan: Path) -> QuyTac:
    if not duong_dan.exists():
        raise QuyTacHong(f"Không thấy {duong_dan}. Đây là tệp bạn viết.")
    try:
        than = yaml.safe_load(duong_dan.read_text(encoding="utf-8"))
    except yaml.YAMLError as loi:
        raise QuyTacHong(f"{duong_dan.name} không phân giải được: {loi}") from loi
    if not isinstance(than, dict):
        raise QuyTacHong(f"{duong_dan.name} phải là một ánh xạ ở mức cao nhất.")
    thieu = [t for t in TRUONG_BAT_BUOC if not than.get(t)]
    if thieu:
        raise QuyTacHong(
            f"{duong_dan.name} thiếu trường bắt buộc: {thieu}. "
            "Bốn trường ấy là phần tối thiểu để người trực biết quy tắc này của ai, "
            "chạy trên nguồn nào, và đáng dựng người dậy lúc nửa đêm hay không."
        )
    phat_hien = than["detection"]
    if not isinstance(phat_hien, dict) or "condition" not in phat_hien:
        raise QuyTacHong("Khối detection phải có trường condition.")
    ten_khoi = [k for k in phat_hien if k != "condition"]
    if not ten_khoi:
        raise QuyTacHong("Khối detection không có khối tìm kiếm nào ngoài condition.")
    khoi = {ten: _doc_khoi(ten, phat_hien[ten]) for ten in ten_khoi}
    cau = str(phat_hien["condition"]).strip()
    _kiem_cau_dieu_kien(cau, khoi)
    bao_nham = than.get("falsepositives") or []
    if isinstance(bao_nham, str):
        bao_nham = [bao_nham]
    truong = {dk.truong for dieu in khoi.values() for dk in dieu}
    return QuyTac(
        tieu_de=str(than["title"]).strip(),
        muc=str(than["level"]).strip().casefold(),
        nguon=than["logsource"] if isinstance(than["logsource"], dict) else {},
        khoi=khoi,
        dieu_kien=cau,
        bao_nham_da_biet=tuple(str(x) for x in bao_nham),
        truong_da_dung=frozenset(truong),
    )


def doc_tap_co_nhan(duong_dan: Path) -> list[dict]:
    """Đọc tập sự kiện có nhãn, mỗi dòng một bản ghi JSON."""
    import json

    if not duong_dan.exists():
        raise QuyTacHong(f"Không thấy tập có nhãn ở {duong_dan}.")
    ra: list[dict] = []
    for so, dong in enumerate(duong_dan.read_text(encoding="utf-8").splitlines(), 1):
        dong = dong.strip()
        if not dong:
            continue
        try:
            ban_ghi = json.loads(dong)
        except json.JSONDecodeError as loi:
            raise QuyTacHong(f"{duong_dan.name} dòng {so} không phải JSON hợp lệ: {loi}") from loi
        if ban_ghi.get("nhan") not in {"dung", "sach"}:
            raise QuyTacHong(
                f"{duong_dan.name} dòng {so} thiếu nhãn hợp lệ. "
                "Nhãn chỉ nhận hai giá trị: dung, sach."
            )
        ra.append(ban_ghi)
    if not ra:
        raise QuyTacHong(f"{duong_dan.name} không có bản ghi nào.")
    return ra


def do_tren_tap(quy_tac: QuyTac, tap: list[dict]) -> dict:
    """Đếm bốn ô của bảng nhầm lẫn rồi tính hai tỉ lệ.

    Quy ước đặt tên trong bài, viết ra đây một lần để không ai phải đoán.
    Độ chính xác là phần báo đúng trong số lần báo, tức nó trả lời câu hỏi của
    người trực: mỗi lần chuông reo thì bao nhiêu phần là thật. Độ phủ là phần
    bắt được trong số sự kiện đáng bắt, tức nó trả lời câu hỏi của người thiết kế:
    quy tắc này bỏ sót bao nhiêu. Hai con số kéo ngược nhau, và bài này ràng buộc
    cả hai để bạn không thể đạt cái này bằng cách hy sinh cái kia.
    """
    tp = fp = fn = tn = 0
    bat_nham: list[str] = []
    bo_sot: list[str] = []
    for ban_ghi in tap:
        bat = quy_tac.khop(ban_ghi)
        dung = ban_ghi["nhan"] == "dung"
        if bat and dung:
            tp += 1
        elif bat and not dung:
            fp += 1
            bat_nham.append(str(ban_ghi.get("id", "?")))
        elif not bat and dung:
            fn += 1
            bo_sot.append(str(ban_ghi.get("id", "?")))
        else:
            tn += 1
    do_chinh_xac = tp / (tp + fp) if (tp + fp) else 0.0
    do_phu = tp / (tp + fn) if (tp + fn) else 0.0
    return {
        "tong_ban_ghi": len(tap),
        "TP": tp, "FP": fp, "FN": fn, "TN": tn,
        "do_chinh_xac": round(do_chinh_xac, 4),
        "do_phu": round(do_phu, 4),
        "bat_nham": bat_nham,
        "bo_sot": bo_sot,
    }
