from __future__ import annotations
import jwt

class TheKhongHopLe(Exception):
    pass

def kiem_the(the: str, khoa_cong_pem: str, cau_hinh: dict) -> dict:
    try:
        return jwt.decode(
            the,
            khoa_cong_pem,
            algorithms=cau_hinh["thuat_toan_cho_phep"],
            audience=cau_hinh["nguoi_nhan"],
            issuer=cau_hinh["ben_phat_hanh"],
            leeway=cau_hinh["do_lech_dong_ho_giay"],
            options={"require": ["exp", "aud", "sub"]}
        )
    except jwt.ExpiredSignatureError as e:
        raise TheKhongHopLe(f"qua_han: {e}")
    except jwt.InvalidAudienceError as e:
        raise TheKhongHopLe(f"nguoi_nhan sai: {e}")
    except jwt.InvalidAlgorithmError as e:
        raise TheKhongHopLe(f"thuat_toan_khong_hop_le (CWE-347): {e}")
    except jwt.InvalidTokenError as e:
        raise TheKhongHopLe(f"the_hong_hoac_chu_ky_sai (CWE-347): {e}")
    except Exception as e:
        raise TheKhongHopLe(f"loi_khac: {e}")

def quyet_dinh(khai: dict, yeu_cau: dict, chinh_sach: dict) -> bool:
    vai_chu_the = khai.get("realm_access", {}).get("roles", [])
    dv = khai.get("don_vi", [])
    don_vi_chu_the = dv[0] if isinstance(dv, list) and len(dv) > 0 else dv

    for qt in chinh_sach.get("quy_tac", []):
        if qt["vai"] in vai_chu_the:
            if yeu_cau["duong_dan"] == qt["duong_dan"]:
                if yeu_cau["phuong_thuc"] in qt["phuong_thuc"]:
                    if qt.get("chi_trong_don_vi"):
                        if don_vi_chu_the == yeu_cau["don_vi"]:
                            return True
                    else:
                        return True
    return False
