#!/usr/bin/env sh
# Chạy một phép kiểm, ghi lại kết quả ở hai dạng.
#
#   bin/ghi-ket-qua.sh <mã> <lớp> <mong-đợi> <dấu-hiệu> <mô-tả> -- <lệnh...>
#
#   mã        K1 tới K4, hoặc K5 cho phần thử thách
#   lớp       1 cho lớp TLS, 2 cho lớp mTLS
#   mong-đợi  THANH_CONG hoặc BI_TU_CHOI
#   dấu-hiệu  chuỗi phải có trong đầu ra thì mới tính là THANH_CONG; dấu trừ
#             nghĩa là chỉ xét mã thoát
#
# Hai dạng, vì hai người đọc khác nhau. Tệp `evidence/S3/kiem-<mã>.txt` là bản
# tóm tắt máy đọc được, gồm điều bạn chờ đợi và điều thật sự xảy ra. Tệp
# `evidence/S3/tho/<mã>.log` là nhật ký thô, dành cho người chấm đọc khi bản tóm
# tắt không đủ.
#
# Vì sao phán quyết cần cả mã thoát lẫn dấu hiệu. Ở TLS 1.3 phía khách coi như
# bắt tay xong trước khi máy chủ kịp xét chứng thư khách, nên một lần nối bị từ
# chối vẫn có thể trả về mã thoát 0 nếu ta dừng ngay sau bắt tay. Đòi thêm một
# dấu hiệu trong đầu ra, chẳng hạn dòng trạng thái 200, làm phán quyết bám vào
# thứ đã thật sự đi qua kênh chứ không bám vào lúc bắt tay.
#
# Tập lệnh này luôn thoát 0, kể cả khi phép kiểm cho kết quả ngoài mong đợi. Việc
# của nó là ghi lại điều đã xảy ra, không phải phán xử; phán xử là việc của
# `make verify`. Nhờ vậy một phép hỏng không chặn ba phép còn lại chạy.

set -u

MA="$1"; LOP="$2"; MONG_DOI="$3"; DAU_HIEU="$4"; MO_TA="$5"
shift 5
[ "${1:-}" = "--" ] && shift

EVID="evidence/S3"
mkdir -p "$EVID/tho"

LENH="$*"
THO="$EVID/tho/$MA.log"

printf 'lenh: %s\n\n' "$LENH" > "$THO"
sh -c "$LENH" >> "$THO" 2>&1
MA_THOAT=$?

THUC_TE="BI_TU_CHOI"
if [ "$MA_THOAT" -eq 0 ]; then
  if [ "$DAU_HIEU" = "-" ]; then
    THUC_TE="THANH_CONG"
  elif grep -q -- "$DAU_HIEU" "$THO"; then
    THUC_TE="THANH_CONG"
  fi
fi

{
  echo "ma: $MA"
  echo "lop: $LOP"
  echo "mo_ta: $MO_TA"
  echo "lenh: $LENH"
  echo "dau_hieu: $DAU_HIEU"
  echo "mong_doi: $MONG_DOI"
  echo "thuc_te: $THUC_TE"
  echo "ma_thoat: $MA_THOAT"
  echo "nhat_ky_tho: $THO"
  echo "sinh_boi: bin/ghi-ket-qua.sh"
} > "$EVID/kiem-$MA.txt"

if [ "$THUC_TE" = "$MONG_DOI" ]; then
  echo "  $MA đúng như mong đợi: $THUC_TE"
else
  echo "  $MA LỆCH: mong đợi $MONG_DOI, thực tế $THUC_TE. Đọc $THO trước khi sửa cấu hình."
fi
exit 0
