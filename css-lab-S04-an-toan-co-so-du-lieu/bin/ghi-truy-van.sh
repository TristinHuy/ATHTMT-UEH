#!/usr/bin/env sh
# Chạy một truy vấn, ghi lại kết quả ở hai dạng.
#
#   bin/ghi-truy-van.sh <mã> <loại> <vai-trò> <mong-đợi> <mô-tả> -- <lệnh...>
#
#   mã        A1 tới A6 cho phép kiểm âm, D1 tới D3 cho phép kiểm dương
#   loại      am hoặc duong
#   vai-trò   tên vai trò cơ sở dữ liệu chạy câu này
#   mong-đợi  CHAY_DUOC, KHONG_DONG, LOI_QUYEN, LOI_CHINH_SACH, LOI_RANG_BUOC
#
# Hai dạng, vì hai người đọc khác nhau. Tệp `evidence/S4/kiem-<mã>.txt` là bản
# tóm tắt máy đọc được. Tệp `evidence/S4/tho/<mã>.log` là nhật ký thô, dành cho
# người chấm đọc khi bản tóm tắt không đủ.
#
# VÌ SAO PHÁN QUYẾT CÓ NĂM GIÁ TRỊ CHỨ KHÔNG PHẢI HAI. Một truy vấn bị chặn có
# thể bị chặn theo ba kiểu rất khác nhau, và gộp chúng lại thành một chữ "trượt"
# là đánh mất đúng phần đáng học. Bị từ chối quyền nghĩa là bạn chưa được cấp
# cái cửa ấy. Trả về không dòng nào nghĩa là cửa mở nhưng chính sách mức hàng đã
# lọc sạch. Vi phạm chính sách khi ghi nghĩa là vế WITH CHECK đã chặn. Vi phạm
# ràng buộc nghĩa là một luật nghiệp vụ trong lược đồ đã chặn. Bốn kiểu ấy nằm
# ở bốn lớp phòng thủ khác nhau, và đề bài chỉ định sẵn mỗi phép kiểm phải bị
# chặn ở lớp nào.
#
# Phán quyết tính từ mã thoát của psql và từ thông điệp của máy chủ, không tính
# từ lời khai. Thông điệp ấy phụ thuộc locale, nên cả Makefile lẫn tệp compose
# đều cố định LC_ALL và LANG; đổi hai thứ đó là làm hỏng phép phân loại này.
#
# Tập lệnh luôn thoát 0, kể cả khi kết quả lệch mong đợi. Việc của nó là ghi lại
# điều đã xảy ra, không phải phán xử; phán xử là việc của `make verify`. Nhờ vậy
# một phép hỏng không chặn tám phép còn lại chạy.

set -u

MA="$1"; LOAI="$2"; VAI_TRO="$3"; MONG_DOI="$4"; MO_TA="$5"
shift 5
[ "${1:-}" = "--" ] && shift

EVID="evidence/S4"
mkdir -p "$EVID/tho"

LENH="$*"
THO="$EVID/tho/$MA.log"

printf 'lenh: %s\n\n' "$LENH" > "$THO"
sh -c "$LENH" >> "$THO" 2>&1
MA_THOAT=$?

if [ "$MA_THOAT" -eq 0 ]; then
  if grep -qE '^\(0 rows\)|^UPDATE 0$|^DELETE 0$' "$THO"; then
    THUC_TE="KHONG_DONG"
  else
    THUC_TE="CHAY_DUOC"
  fi
elif grep -qi 'permission denied' "$THO"; then
  THUC_TE="LOI_QUYEN"
elif grep -qi 'row-level security policy' "$THO"; then
  THUC_TE="LOI_CHINH_SACH"
elif grep -qi 'violates check constraint' "$THO"; then
  THUC_TE="LOI_RANG_BUOC"
elif grep -qiE 'does not exist|role .* is not permitted to log in|authentication failed' "$THO"; then
  THUC_TE="LOI_MOI_TRUONG"
else
  THUC_TE="LOI_KHAC"
fi

{
  echo "ma: $MA"
  echo "loai: $LOAI"
  echo "vai_tro: $VAI_TRO"
  echo "mo_ta: $MO_TA"
  echo "lenh: $LENH"
  echo "mong_doi: $MONG_DOI"
  echo "thuc_te: $THUC_TE"
  echo "ma_thoat: $MA_THOAT"
  echo "nhat_ky_tho: $THO"
  echo "sinh_boi: bin/ghi-truy-van.sh"
} > "$EVID/kiem-$MA.txt"

if [ "$THUC_TE" = "$MONG_DOI" ]; then
  echo "  $MA đúng như mong đợi: $THUC_TE"
elif [ "$THUC_TE" = "LOI_MOI_TRUONG" ]; then
  echo "  $MA CHƯA CHẠY ĐƯỢC: vai trò hoặc đối tượng chưa tồn tại. Chạy lại make defend, rồi đọc $THO."
else
  echo "  $MA LỆCH: mong đợi $MONG_DOI, thực tế $THUC_TE. Đọc $THO trước khi sửa cấu hình."
fi
exit 0
