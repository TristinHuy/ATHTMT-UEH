#!/usr/bin/env bash
# Thay từng thẻ ảnh bằng digest thật, trong docker-compose.yml VÀ trong
# csdl/Dockerfile.
#
#   bash ghim-digest.sh [đường-dẫn-compose] [đường-dẫn-dockerfile]
#
# Chạy trên một máy CÓ MẠNG và có Docker. Máy soạn bài không kéo được ảnh nên
# không có digest thật để ghi, và một chuỗi sha256 bịa ra thì trông giống hệt
# một chuỗi thật cho tới ngày nó làm hỏng một lần dựng. Vì vậy hai tệp phát cho
# bạn còn ghi thẻ, kèm dòng chú thích CHUA_GHIM_DIGEST, và tập lệnh này là bước
# còn thiếu.
#
# Vì sao phải ghim. Một thẻ là một cái tên trỏ tới một ảnh, và cái tên đó trỏ đi
# đâu là quyền của người phát hành. `postgres:17.6-bookworm` hôm nay và cùng thẻ
# ấy sau ba tháng có thể là hai ảnh khác nhau. Một digest thì không, vì nó chính
# là băm của ảnh: đổi một byte trong ảnh là đổi digest.
#
# Vì sao bài này phải ghim ở HAI chỗ. Dịch vụ csdl dựng ảnh tại chỗ, vì bản
# chính thức không kèm pgaudit. Ghim ảnh dựng ra thì vô nghĩa, vì nó sinh lại
# mỗi lần dựng; thứ quyết định nó là gì nằm ở dòng FROM trong Dockerfile.
#
# Mã thoát: 0 đã ghim xong, 1 có lỗi, 2 sai tham số.

set -uo pipefail

COMPOSE="${1:-docker-compose.yml}"
DOCKERFILE="${2:-csdl/Dockerfile}"

# Ảnh dựng tại chỗ, không hỏi registry.
BO_QUA_RE='^css-s04-'

for tep in "$COMPOSE" "$DOCKERFILE"; do
  if [[ ! -f "$tep" ]]; then
    echo "Không thấy tệp: $tep" >&2
    exit 2
  fi
done
if ! command -v docker >/dev/null 2>&1; then
  echo "Không có docker trên máy này. Tập lệnh này cần Docker và cần mạng." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker đã cài nhưng daemon chưa chạy. Mở Docker Desktop hoặc chạy: sudo systemctl start docker" >&2
  exit 1
fi

NGAY="$(date +%d/%m/%Y)"
loi=0
so_ghim=0

# Sao lưu trước khi sửa, để một lần chạy hỏng giữa chừng không mất bản gốc.
cp "$COMPOSE" "${COMPOSE}.truoc-khi-ghim"
cp "$DOCKERFILE" "${DOCKERFILE}.truoc-khi-ghim"

# Lấy digest của một tham chiếu ảnh. Ưu tiên imagetools vì nó hỏi thẳng registry
# và không phải kéo cả ảnh về; nếu máy không có buildx thì lùi về pull rồi inspect.
lay_digest() {
  local ref="$1" out=""
  if docker buildx imagetools inspect "$ref" >/dev/null 2>&1; then
    out=$(docker buildx imagetools inspect "$ref" 2>/dev/null \
          | sed -n 's/^Digest:[[:space:]]*//p' | head -n 1)
  fi
  if [[ -z "$out" ]]; then
    docker pull "$ref" >/dev/null 2>&1 || return 1
    out=$(docker inspect --format '{{index .RepoDigests 0}}' "$ref" 2>/dev/null \
          | sed -n 's/.*@//p')
  fi
  [[ -n "$out" ]] || return 1
  printf '%s\n' "$out"
}

# Thay một tham chiếu trong một tệp, kèm dòng chú thích ngay trên nó.
thay_trong_tep() {
  python3 - "$1" "$2" "$3" "$4" "$5" <<'PY'
import sys, pathlib
duong_dan, cu, moi, ngay, tu_khoa = sys.argv[1:6]
p = pathlib.Path(duong_dan)
ra = []
for d in p.read_text(encoding="utf-8").splitlines(keepends=True):
    gon = d.strip()
    if gon.startswith("# CHUA_GHIM_DIGEST") and cu in d:
        thut = d[: len(d) - len(d.lstrip())]
        ra.append(f"{thut}# đã ghim {ngay} từ thẻ {cu}\n")
        continue
    if gon.startswith(tu_khoa):
        phan = gon[len(tu_khoa):].split()
        if phan and phan[0].strip("\"'") == cu:
            thut = d[: len(d) - len(d.lstrip())]
            con_lai = " ".join(phan[1:])
            ra.append(f"{thut}{tu_khoa}{moi}{(' ' + con_lai) if con_lai else ''}\n")
            continue
    ra.append(d)
p.write_text("".join(ra), encoding="utf-8")
PY
}

ghim_mot_tep() {   # <tệp> <biểu-thức-trích-ref> <từ-khóa>
  local tep="$1" trich="$2" tu_khoa="$3" ref digest ten
  while IFS= read -r ref; do
    [[ -n "$ref" ]] || continue
    if [[ "$ref" =~ $BO_QUA_RE ]]; then
      echo "ảnh dựng tại chỗ, bỏ qua: $ref"
      continue
    fi
    if [[ "$ref" == *"@sha256:"* ]]; then
      echo "đã ghim rồi, bỏ qua: $ref"
      continue
    fi
    if [[ "$ref" != *:* || "$ref" == *:latest ]]; then
      echo "TỪ CHỐI: $ref không có thẻ phiên bản cụ thể. Ghim một thẻ trôi nổi là ghim vào cát." >&2
      loi=1
      continue
    fi
    echo "đang hỏi registry: $ref"
    if ! digest=$(lay_digest "$ref"); then
      echo "THẤT BẠI: không lấy được digest của $ref. Thẻ này có thể không tồn tại, hoặc máy không ra được mạng." >&2
      loi=1
      continue
    fi
    ten="${ref%:*}"
    thay_trong_tep "$tep" "$ref" "$ten@$digest" "$NGAY" "$tu_khoa"
    echo "  đã ghim: $ten@$digest"
    so_ghim=$((so_ghim + 1))
  done < <(eval "$trich" | tr -d "\"'")
}

# Duyệt theo thứ tự dòng của tệp, không theo thứ tự hệ tệp trả về, để hai lần
# chạy cho ra cùng một tệp.
ghim_mot_tep "$COMPOSE"    "sed -n 's/^[[:space:]]*image:[[:space:]]*//p' '$COMPOSE'" "image: "
ghim_mot_tep "$DOCKERFILE" "sed -n 's/^FROM[[:space:]]\+//p' '$DOCKERFILE' | awk '{print \$1}'" "FROM "

echo
if (( loi != 0 )); then
  echo "CHƯA XONG: còn chỗ hỏng ở trên. Bản trước khi sửa nằm cạnh mỗi tệp, đuôi .truoc-khi-ghim." >&2
  exit 1
fi

for tep in "$COMPOSE" "$DOCKERFILE"; do
  if grep -q 'CHUA_GHIM_DIGEST' "$tep"; then
    echo "CHƯA XONG: vẫn còn dòng CHUA_GHIM_DIGEST trong $tep." >&2
    exit 1
  fi
done

echo "Đã ghim $so_ghim tham chiếu ảnh. Bản trước khi sửa nằm cạnh mỗi tệp, đuôi .truoc-khi-ghim."
echo "Kiểm lại bằng: docker compose config | grep image, và: grep FROM $DOCKERFILE"
exit 0
