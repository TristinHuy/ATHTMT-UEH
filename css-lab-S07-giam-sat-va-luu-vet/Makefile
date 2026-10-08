# Lab S7. Mục tiêu theo chuẩn chung của học phần.
# Ảnh ghim theo digest sau khi chạy ghim-digest.sh. Múi giờ, locale và hạt giống
# cố định để hai lần chạy cho cùng kết quả.

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

EVID := evidence/S7
CHAY := docker compose --profile cong-cu run --rm -T cong-cu

.PHONY: preflight nap-nhat-ky up attack defend do-tre do-chinh-xac hoi verify export-evidence down help

help:
	@echo "preflight        ghi thông tin máy, kiểm Docker chạy được"
	@echo "up               dựng kho nhật ký, chặng chuyển, và container hỏi"
	@echo "nap-nhat-ky      chép bằng chứng của S2 tới S6 vào nhat-ky/ theo tên buổi"
	@echo "attack           gieo một dòng, xóa nó khỏi nguồn, rồi tìm lại ở kho"
	@echo "defend           nạp lại chặng chuyển sau khi bạn sửa cấu hình"
	@echo "do-tre           đo độ trễ riêng từng chặng, ghi $(EVID)/do-tre.csv"
	@echo "do-chinh-xac     chạy quy tắc Sigma lên tập có nhãn, ghi kết quả đo"
	@echo "hoi              hỏi Loki một câu LogQL: make hoi NHAN=S03 Q='{...}'"
	@echo "verify           chạy bộ kiểm, đây là thứ bộ chấm chạy"
	@echo "export-evidence  gom bằng chứng vào $(EVID), kèm SHA256SUMS"
	@echo "down             dọn môi trường, xóa cả kho nhật ký đã nạp"

preflight:
	@mkdir -p $(EVID)
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

# Bước này chép chứ không gắn liên kết, và lý do là nội dung bài học. Thư mục
# bằng chứng của năm buổi trước mang năm cái tên không thống nhất, evidence/S02,
# evidence/S3, evidence/S4, evidence/S5, evidence/S6, vì chúng được dựng ở năm
# thời điểm khác nhau. Chuẩn hóa tên ngay tại cửa vào là việc rẻ nhất bạn làm
# được cho chính mình, và nó cũng đúng là việc mà một chặng thu thập nhật ký
# thật phải làm với năm nguồn viết theo năm quy ước.
nap-nhat-ky:
	@for b in S02 S03 S04 S05 S06; do mkdir -p nhat-ky/$$b; done
	@mkdir -p nhat-ky/S07
	@echo "Chép bằng chứng của bạn vào đúng năm thư mục dưới đây, đặt đuôi .log:"
	@for b in S02 S03 S04 S05 S06; do \
	  n=$$(ls nhat-ky/$$b/*.log 2>/dev/null | wc -l); \
	  echo "  nhat-ky/$$b/   $$n tệp"; \
	done
	@echo
	@echo "Nguồn nằm ở kho lab của chính bạn từ các buổi trước, thư mục evidence/."
	@echo "Mất dữ liệu hoặc đổi máy thì xin bộ dữ liệu thay thế của giảng viên, và"
	@echo "khai nguon_du_lieu: thay_the trong docs/bang-nam-su-kien.yaml."

up:
	docker compose up -d loki promtail
	docker compose --profile cong-cu build cong-cu
	@echo
	@echo "Kho nhật ký đang chạy, và nó KHÔNG mở cổng nào ra máy thật."
	@echo "Muốn hỏi nó thì đứng từ trong mạng compose:  make hoi NHAN=thu Q='{job=\"nhat-ky-lab\"}'"
	@echo "Muốn nhìn bằng đồ thị thì bật thêm:          docker compose --profile xem up -d grafana"

attack:
	@echo "Phần tấn công của bài này gồm đúng một thao tác, và nó chỉ chạm tệp"
	@echo "trong nhat-ky/S07/ của chính bạn. Đọc SCOPE.md trước nếu chưa đọc."
	@mkdir -p $(EVID)
	$(CHAY) python3 bin/xoa-vet.py
	@echo
	@echo "Đọc $(EVID)/xoa-vet.txt. Con số đáng nhớ là bề rộng khoảng nguy hiểm."

defend:
	docker compose up -d --force-recreate promtail
	@echo "Đã nạp lại chặng chuyển. Bốn thứ phải xong trước bước này, tự kiểm lại:"
	@echo "  1. cau-hinh/promtail.yaml có đủ sáu khối nguồn, S02 tới S07"
	@echo "  2. thư mục nhat-ky/ vẫn gắn ở chế độ chỉ đọc trong docker-compose.yml"
	@echo "  3. cau-hinh/loki.yaml đã đặt hạn giữ, và bạn nói được vì sao chọn số ấy"
	@echo "  4. sigma/quy-tac.yml không còn là bản thô đi kèm đề"
	@echo "Promtail nhớ vị trí đã đọc trên một volume riêng, nên nạp lại không đọc"
	@echo "lại từ đầu. Muốn đọc lại từ đầu thì make down rồi make up."

do-tre:
	@mkdir -p $(EVID)
	$(CHAY) python3 bin/do-tre.py
	@echo "Chạy ít nhất ba lần rồi giữ lần chậm nhất."

do-chinh-xac:
	@mkdir -p $(EVID)
	$(PY) bin/do-chinh-xac.py

hoi:
	@test -n "$(Q)" || { echo "Thiếu câu truy vấn. Dùng: make hoi NHAN=S03 Q='{job=\"nhat-ky-lab\", buoi=\"S03\"}'"; exit 2; }
	@test -n "$(NHAN)" || { echo "Thiếu NHAN. Nó thành tên tệp bằng chứng."; exit 2; }
	@mkdir -p $(EVID)
	$(CHAY) python3 bin/hoi-loki.py --nhan "$(NHAN)" "$(Q)"

verify:
	$(PY) -m pytest tests/ -v --tb=short

export-evidence:
	@mkdir -p $(EVID)
	@$(MAKE) --no-print-directory preflight >/dev/null
	@{ find $(EVID) -type f -not -name SHA256SUMS; \
	   echo SCOPE.md; echo docker-compose.yml; \
	   echo cau-hinh/promtail.yaml; echo cau-hinh/loki.yaml; \
	   echo sigma/quy-tac.yml; echo docs/bang-nam-su-kien.yaml; \
	   echo docs/duong-di-nhat-ky.md; echo docs/gia-cua-bao-nham.md; } \
	  | sort | xargs sha256sum > $(EVID)/SHA256SUMS
	@echo "Bằng chứng ở $(EVID), kèm SHA256SUMS."
	@echo "Băm này để người chấm biết tệp bạn nộp đúng là tệp máy sinh ra."

down:
	-docker compose --profile cong-cu --profile xem down -v --remove-orphans
	@echo "Đã xóa container, mạng, và cả kho nhật ký. Thư mục nhat-ky/ vẫn còn,"
	@echo "vì đó là dữ liệu của bạn chứ không phải trạng thái của container."
