#!/usr/bin/env bash
# Thay thẻ phiên bản bằng digest thật, cho lab S5.
#
# Vì sao có tệp này. Một thẻ như quay.io/keycloak/keycloak:26.4.0 là một cái tên
# trỏ tới một ảnh, và cái tên đó trỏ đi đâu là quyền của người phát hành. Thẻ hôm
# nay và cùng thẻ ấy sau ba tháng có thể là hai ảnh khác nhau, nên bài bạn chạy
# hôm nay và bài bộ chấm chạy tuần sau đứng trên hai máy chủ danh tính khác nhau
# mà không ai biết. Digest là băm của chính ảnh, đổi một byte là đổi digest.
#
# Máy soạn bài không kéo được ảnh nên không lấy được digest thật, và một chuỗi
# sha256 gõ tay là một chuỗi bịa: nó trông giống hệt một chuỗi thật cho tới ngày
# nó làm hỏng một lần dựng. Tập lệnh này chạy trên máy CÓ MẠNG, hỏi sổ đăng ký,
# rồi sửa thẳng vào tệp. Nó không bao giờ tự sinh ra một digest.
#
#   bash ghim-digest.sh          xem trước, không sửa gì
#   bash ghim-digest.sh --sua    sửa thật, giữ bản sao .truoc-khi-ghim
#
# Hai tệp bị đụng tới: docker-compose.yml và dich-vu/Dockerfile. Ảnh dựng tại chỗ
# từ ./dich-vu không nằm trong sổ đăng ký nào nên không có digest để hỏi, và bỏ
# qua chúng là đúng chứ không phải là nhân nhượng; thứ cần ghim của chúng là dòng
# FROM trong Dockerfile.
#
# Mã thoát: 0 xong, 1 có dòng không giải được, 2 sai tham số hoặc thiếu docker.

set -uo pipefail

GOC="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
TEP=("$GOC/docker-compose.yml" "$GOC/dich-vu/Dockerfile")
ANH_DUNG_TAI_CHO='^css-s05-'

SUA=0
case "${1:-}" in
  "")    SUA=0 ;;
  --sua) SUA=1 ;;
  *)     echo "Dùng: bash ghim-digest.sh [--sua]" >&2; exit 2 ;;
esac

if ! command -v docker >/dev/null 2>&1; then
  echo "Không có docker trên máy này. Chạy tập lệnh trên máy có mạng và có docker." >&2
  exit 2
fi
if ! docker info >/dev/null 2>&1; then
  echo "Docker đã cài nhưng daemon chưa chạy. Mở Docker Desktop, hoặc chạy: sudo systemctl start docker" >&2
  exit 2
fi

NGAY="$(date +%d/%m/%Y)"

# Ưu tiên imagetools vì nó hỏi thẳng sổ đăng ký và không phải kéo cả ảnh về; máy
# không có buildx thì lùi về pull rồi inspect.
lay_digest() {
  local ref="$1" d=""
  if docker buildx imagetools inspect "$ref" >/dev/null 2>&1; then
    d=$(docker buildx imagetools inspect "$ref" 2>/dev/null | sed -n 's/^Digest:[[:space:]]*//p' | head -n 1)
  fi
  if [[ -z "$d" ]]; then
    docker pull "$ref" >/dev/null 2>&1 || return 1
    d=$(docker inspect --format '{{index .RepoDigests 0}}' "$ref" 2>/dev/null | sed -n 's/.*@//p')
  fi
  [[ -n "$d" ]] || return 1
  printf '%s\n' "$d"
}

loi=0
so_ghim=0

for tep in "${TEP[@]}"; do
  [[ -f "$tep" ]] || { echo "Không thấy $tep" >&2; loi=1; continue; }
  echo "== $tep"

  # Duyệt theo thứ tự dòng của tệp, không theo thứ tự hệ tệp trả về, để hai lần
  # chạy cho ra cùng một tệp.
  while IFS= read -r ref; do
    [[ -n "$ref" ]] || continue
    if [[ "$ref" == *"@sha256:"* ]]; then
      echo "  đã ghim rồi, bỏ qua: $ref"
      continue
    fi
    if [[ "$ref" =~ $ANH_DUNG_TAI_CHO ]]; then
      echo "  ảnh dựng tại chỗ, không có trong sổ đăng ký: $ref"
      continue
    fi
    if [[ "$ref" != *:* || "$ref" == *:latest ]]; then
      echo "  TỪ CHỐI: $ref không có thẻ phiên bản cụ thể. Ghim một thẻ trôi nổi là ghim vào cát." >&2
      loi=1
      continue
    fi

    echo "  đang hỏi sổ đăng ký: $ref"
    if ! digest=$(lay_digest "$ref"); then
      echo "  THẤT BẠI: không lấy được digest của $ref. Thẻ này có thể không tồn tại, hoặc máy không ra được mạng." >&2
      loi=1
      continue
    fi
    ten="${ref%:*}"
    echo "  digest: $ten@$digest"
    so_ghim=$((so_ghim + 1))

    if (( SUA )); then
      [[ -f "$tep.truoc-khi-ghim" ]] || cp "$tep" "$tep.truoc-khi-ghim"
      python3 - "$tep" "$ref" "$ten@$digest" "$NGAY" <<'PY'
import pathlib, sys
duong_dan, cu, moi, ngay = sys.argv[1:5]
p = pathlib.Path(duong_dan)
ra = []
for d in p.read_text(encoding="utf-8").splitlines(keepends=True):
    goi = d.strip()
    thut = d[: len(d) - len(d.lstrip())]
    if goi.startswith("# CHUA_GHIM_DIGEST") and cu in goi:
        ra.append(f"{thut}# đã ghim {ngay} từ thẻ {cu}\n")
        continue
    if goi.startswith("image:") and goi.split("image:", 1)[1].strip().strip("\"'") == cu:
        ra.append(f"{thut}image: {moi}\n")
        continue
    if goi.startswith("FROM ") and goi.split(None, 1)[1].strip() == cu:
        ra.append(f"{thut}FROM {moi}\n")
        continue
    ra.append(d)
p.write_text("".join(ra), encoding="utf-8")
PY
    fi
  done < <(grep -Eo '^[[:space:]]*(FROM|image:)[[:space:]]+[^[:space:]]+' "$tep" \
           | sed -E 's/^[[:space:]]*(FROM|image:)[[:space:]]+//' | tr -d "\"'")
done

echo
if (( loi != 0 )); then
  echo "CHƯA XONG: còn chỗ hỏng ở trên." >&2
  exit 1
fi
if (( ! SUA )); then
  echo "Xem trước xong, $so_ghim ảnh giải được digest. Chạy lại với --sua để sửa thật."
  exit 0
fi
for tep in "${TEP[@]}"; do
  if grep -q 'CHUA_GHIM_DIGEST' "$tep"; then
    echo "CHƯA XONG: vẫn còn dòng CHUA_GHIM_DIGEST trong $tep." >&2
    exit 1
  fi
done
echo "Đã ghim $so_ghim ảnh. Bản trước khi sửa nằm cạnh mỗi tệp, đuôi .truoc-khi-ghim."
echo "Kiểm lại bằng: docker compose config | grep image"
exit 0
