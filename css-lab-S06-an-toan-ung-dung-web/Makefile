# Lab S6. Mục tiêu theo chuẩn chung của học phần.
# Ảnh ghim theo digest sau khi chạy ghim-digest.sh. Múi giờ, locale và hạt giống
# cố định để hai lần chạy cho cùng kết quả.
#
# Một điều riêng của buổi này, đọc trước khi gõ lệnh đầu tiên. Địa chỉ đích của bộ
# quét KHÔNG nằm trong tệp này. Nó nằm ở dòng command của dịch vụ quét trong
# docker-compose.yml, viết bằng tên dịch vụ trong mạng compose, và bộ chấm đọc lại
# chính chỗ đó. Đặt đích ở một chỗ cố định là biện pháp, không phải thói quen: một
# đích truyền qua dòng lệnh là một đích gõ nhầm được, và một bộ quét gõ nhầm địa
# chỉ đã ra khỏi phạm vi cho phép rồi.

SHELL := /bin/bash
# Lệnh Python chạy trên máy của sinh viên (không phải trong container). Windows cài từ
# python.org chỉ có `python` và `py`, còn `python3` hoặc không có hoặc là bí danh dẫn tới
# Microsoft Store và báo lỗi; macOS và Linux thường chỉ có `python3`. Chọn cái chạy được
# đầu tiên để cùng một Makefile dùng được trên cả ba hệ điều hành.
PY := $(shell for p in python3 python py; do "$$p" --version >/dev/null 2>&1 && { echo $$p; break; }; done)
ifeq ($(PY),)
PY := python3
endif

export TZ := Asia/Ho_Chi_Minh
export LC_ALL := C.UTF-8
export PYTHONHASHSEED := 0

EVID := evidence/S6
NHAN ?= chua-dat-ten
CONG_CU := docker compose --profile cong-cu run --rm -T cong-cu

.PHONY: preflight up attack defend quet quet-ma thu-bao-cao verify export-evidence down help

help:
	@echo "preflight        ghi thông tin máy, kiểm Docker chạy được, dọn chỗ cho bằng chứng"
	@echo "up               dựng ứng dụng thử nghiệm và ứng dụng huấn luyện"
	@echo "attack           gọi thẳng hai lỗ hổng, ghi $(EVID)/thu-lo-hong-<nhãn>.txt"
	@echo "                 dùng: make attack NHAN=truoc-khi-va   rồi   make attack NHAN=sau-khi-va"
	@echo "defend           nạp lại ứng dụng sau khi bạn sửa chinh-sach.yaml hoặc ung_dung.py"
	@echo "quet             quét nền hai ứng dụng: make quet NHAN=truoc | NHAN=sau"
	@echo "quet-ma          quét mã bằng bộ luật của bài: make quet-ma NHAN=truoc | NHAN=sau"
	@echo "thu-bao-cao      lấy báo cáo vi phạm chính sách nội dung ra khỏi container"
	@echo "verify           chạy bộ kiểm, đây là thứ bộ chấm chạy"
	@echo "export-evidence  gom bằng chứng vào $(EVID), kèm nhật ký ứng dụng và SHA256SUMS"
	@echo "down             dọn môi trường"

preflight:
	@mkdir -p $(EVID)
	@# Bộ quét chạy dưới người dùng zap, mã số 1000, và nó ghi báo cáo vào thư mục
	@# này qua một volume. Trên máy Linux, thư mục do bạn tạo thường không cho người
	@# dùng khác ghi, nên báo cáo sẽ không rơi ra ngoài container và bạn sẽ đi tìm
	@# một lỗi không có thật. Nới quyền ở đây, một lần, và nói ra vì sao.
	-@chmod a+rwX $(EVID) 2>/dev/null
	@{ \
	  echo "kien truc CPU: $$(uname -m)"; \
	  echo "he dieu hanh : $$(uname -s)"; \
	  echo "phien ban Python: $$($(PY) --version 2>&1)"; \
	  if command -v docker >/dev/null 2>&1; then \
	    echo "phien ban Docker: $$(docker --version 2>&1)"; \
	    if docker info >/dev/null 2>&1; then \
	      echo "docker daemon: chay"; \
	    else \
	      echo "docker daemon: KHONG CHAY"; \
	    fi; \
	  else \
	    echo "phien ban Docker: KHONG CO"; \
	    echo "docker daemon: KHONG CHAY"; \
	  fi; \
	} > $(EVID)/preflight.txt
	@cat $(EVID)/preflight.txt
	@echo
	@echo "Đã ghi $(EVID)/preflight.txt"

up:
	docker compose up -d --build ung-dung muc-tieu
	@echo
	@echo "Ứng dụng thử nghiệm ở http://127.0.0.1:8081, và nó chỉ nghe trên máy bạn."
	@echo "Ứng dụng huấn luyện KHÔNG lộ cổng nào ra máy thật; bộ quét gọi nó từ trong mạng compose."
	@echo "Ba chỗ làm việc trong chinh-sach.yaml được gắn ở chế độ chỉ đọc, nên sửa xong"
	@echo "chỉ cần make defend, không phải dựng lại ảnh."

attack:
	@echo "Bước này không phá gì. Nó gửi ba yêu cầu vào ứng dụng của CHÍNH BẠN trên"
	@echo "127.0.0.1 và ghi lại ứng dụng trả lời ra sao. Đọc SCOPE.md trước nếu chưa đọc."
	@mkdir -p $(EVID)
	$(PY) bin/thu-lo-hong.py --nhan "$(NHAN)"
	@echo
	@echo "Chạy hai lần thì con số mới nói được điều gì:"
	@echo "  make attack NHAN=truoc-khi-va    trước khi sửa một dòng nào"
	@echo "  make attack NHAN=sau-khi-va      sau khi đã vá cả hai lỗ hổng"

defend:
	docker compose up -d --force-recreate ung-dung
	@echo "Đã nạp lại ứng dụng. Bốn thứ phải xong trước bước này, tự kiểm lại:"
	@echo "  1. ung-dung/ung_dung.py: chuỗi từ người gửi yêu cầu đã đi qua html.escape"
	@echo "  2. chinh-sach.yaml khối csp: đủ bốn chỉ thị, và che_do đã sang cuong-che"
	@echo "  3. chinh-sach.yaml khối cookie_phien: samesite và httponly đã đặt"
	@echo "  4. chinh-sach.yaml khối chong_gia_mao: kiem_origin và the_chong_gia_mao đã bật"
	@echo "Ứng dụng đọc chính sách một lần lúc khởi động, nên sửa tệp mà không chạy bước"
	@echo "này thì bạn đang đo phiên bản cũ."

quet:
	@test "$(NHAN)" != "chua-dat-ten" || { echo "Thiếu NHAN. Dùng: make quet NHAN=truoc hoặc NHAN=sau"; exit 2; }
	@mkdir -p $(EVID)
	@echo "Quét NỀN. Bộ quét đọc thứ máy chủ trả về, không gửi tải trọng thử."
	@echo "Mã thoát của lần quét không phải phán quyết của bài; phán quyết nằm trong tệp báo cáo."
	-docker compose --profile quet run --rm quet
	@test -f $(EVID)/quet.json || { echo "Không thấy $(EVID)/quet.json. Xem lại quyền ghi của thư mục bằng chứng, chạy make preflight."; exit 1; }
	@mv $(EVID)/quet.json $(EVID)/quet-$(NHAN).json
	@echo "Đã ghi $(EVID)/quet-$(NHAN).json và $(EVID)/quet-muc-tieu.json"
	@echo "Tệp thứ hai là nguồn của bảng xếp loại cảnh báo; nó không đổi giữa hai lần chạy"
	@echo "vì bạn không sửa ứng dụng huấn luyện."

quet-ma:
	@test "$(NHAN)" != "chua-dat-ten" || { echo "Thiếu NHAN. Dùng: make quet-ma NHAN=truoc hoặc NHAN=sau"; exit 2; }
	@mkdir -p $(EVID)
	-$(CONG_CU) semgrep --config /lab/quet/quy-tac-semgrep.yml --json \
	  --output /lab/evidence/semgrep-$(NHAN).json /lab/ung-dung
	@echo "Đã ghi $(EVID)/semgrep-$(NHAN).json"
	@echo "Bộ luật chỉ có một luật, và nó nhắm đúng lỗ hổng LH-1. Im lặng của một công cụ"
	@echo "không phải là bằng chứng về sự vắng mặt của lỗi, và mục 6.5 nói vì sao."

thu-bao-cao:
	@mkdir -p $(EVID)
	docker compose exec -T ung-dung cat /tmp/bao-cao-csp.jsonl > $(EVID)/bao-cao-csp.jsonl
	@echo "Đã ghi $(EVID)/bao-cao-csp.jsonl, $$(wc -l < $(EVID)/bao-cao-csp.jsonl) dòng."
	@echo "Tệp rỗng nghĩa là chưa trình duyệt nào gửi báo cáo nào. Thu bằng chứng này khi"
	@echo "chính sách còn ở chế độ bao-cao VÀ lỗ hổng LH-1 còn hở: sau khi bạn mã hóa đầu"
	@echo "ra thì chuỗi lạ không vào tới trang nữa, nên không còn gì để trình duyệt chặn."

verify:
	$(PY) -m pytest tests/ -v --tb=short

export-evidence:
	@mkdir -p $(EVID)
	@$(MAKE) --no-print-directory preflight >/dev/null
	@# Nhật ký của ứng dụng là hiện vật của buổi này VÀ là một trong sáu nguồn của
	@# buổi S7. Lấy nó ra trước khi make down, vì down xóa container và nhật ký đi
	@# theo container.
	-docker compose logs --no-color --no-log-prefix ung-dung > $(EVID)/nhat-ky.txt 2>/dev/null
	@{ find $(EVID) -type f -not -name SHA256SUMS; \
	   echo SCOPE.md; echo docker-compose.yml; \
	   echo ung-dung/ung_dung.py; echo ung-dung/chinh-sach.yaml; \
	   echo docs/xep-loai-canh-bao.yaml; echo docs/danh-doi.md; } \
	  | sort | xargs sha256sum > $(EVID)/SHA256SUMS
	@echo "Bằng chứng ở $(EVID), kèm SHA256SUMS."
	@echo "Băm này để người chấm biết tệp bạn nộp đúng là tệp máy sinh ra."

down:
	-docker compose --profile quet --profile cong-cu down -v --remove-orphans
	@echo "Đã xóa container và mạng. Thư mục $(EVID) vẫn còn, vì đó là bài của bạn"
	@echo "chứ không phải trạng thái của container."
