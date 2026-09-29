#!/usr/bin/env bash
# Thay từng thẻ ảnh trong docker-compose.yml bằng digest thật.
#
#   bash ghim-digest.sh [đường-dẫn-compose]
#
# Chạy trên một máy CÓ MẠNG và có Docker. Máy soạn bài không kéo được ảnh nên
# không có digest thật để ghi, và một chuỗi sha256 bịa ra thì trông giống hệt một
# chuỗi thật cho tới ngày nó làm hỏng một lần dựng. Vì vậy tệp compose phát cho
# bạn còn ghi thẻ, kèm dòng chú thích CHUA_GHIM_DIGEST, và tập lệnh này là bước
# còn thiếu.
#
# Vì sao phải ghim. Một thẻ là một cái tên trỏ tới một ảnh, và cái tên đó trỏ đi
# đâu là quyền của người phát hành. `nginx:1.29.3-alpine` hôm nay và cùng thẻ ấy
# sau ba tháng có thể là hai ảnh khác nhau. Một digest thì không, vì nó chính là
# băm của ảnh: đổi một byte trong ảnh là đổi digest. Ghim theo digest là cách rẻ
# nhất để hai lần chạy cách nhau ba tháng vẫn nói về cùng một thứ.
#
# Mã thoát: 0 đã ghim xong, 1 có lỗi, 2 sai tham số.

set -uo pipefail

COMPOSE="${1:-docker-compose.yml}"

if [[ ! -f "$COMPOSE" ]]; then
  echo "Không thấy tệp compose: $COMPOSE" >&2
  exit 2
fi
if ! command -v docker >/dev/null 2>&1; then
  echo "Không có docker trên máy này. Tập lệnh này cần Docker và cần mạng." >&2
  exit 1
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker đã cài nhưng daemon chưa chạy. Mở Docker Desktop hoặc chạy: sudo systemctl start docker" >&2
  exit 1
fi

NGAY="$(date +%d/%m/%Y)"
SAO_LUU="${COMPOSE}.truoc-khi-ghim"
cp "$COMPOSE" "$SAO_LUU"

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

loi=0
so_ghim=0

# Duyệt theo thứ tự dòng của tệp, không theo thứ tự hệ tệp trả về, để hai lần
# chạy cho ra cùng một tệp.
while IFS= read -r ref; do
  [[ -n "$ref" ]] || continue
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
  # Thay đúng dòng image ấy, và thay dòng chú thích CHUA_GHIM_DIGEST ngay trên nó
  # bằng dòng ghi lại thẻ gốc, để về sau còn biết digest này sinh từ thẻ nào.
  python3 - "$COMPOSE" "$ref" "$ten@$digest" "$NGAY" <<'PY'
import sys, pathlib
duong_dan, cu, moi, ngay = sys.argv[1:5]
p = pathlib.Path(duong_dan)
dong = p.read_text(encoding="utf-8").splitlines(keepends=True)
ra = []
for d in dong:
    if d.strip().startswith("# CHUA_GHIM_DIGEST") and cu in d:
        thut = d[: len(d) - len(d.lstrip())]
        ra.append(f"{thut}# đã ghim {ngay} từ thẻ {cu}\n")
        continue
    if d.strip().startswith("image:") and d.split("image:", 1)[1].strip().strip("\"'") == cu:
        thut = d[: len(d) - len(d.lstrip())]
        ra.append(f"{thut}image: {moi}\n")
        continue
    ra.append(d)
p.write_text("".join(ra), encoding="utf-8")
PY
  echo "  đã ghim: $ten@$digest"
  so_ghim=$((so_ghim + 1))
done < <(sed -n 's/^[[:space:]]*image:[[:space:]]*//p' "$COMPOSE" | tr -d "\"'")

echo
if (( loi != 0 )); then
  echo "CHƯA XONG: còn chỗ hỏng ở trên. Bản trước khi sửa nằm ở $SAO_LUU." >&2
  exit 1
fi

if grep -q 'CHUA_GHIM_DIGEST' "$COMPOSE"; then
  echo "CHƯA XONG: vẫn còn dòng CHUA_GHIM_DIGEST trong $COMPOSE." >&2
  exit 1
fi

echo "Đã ghim $so_ghim ảnh. Bản trước khi sửa nằm ở $SAO_LUU."
echo "Kiểm lại bằng: docker compose config | grep image"
exit 0
