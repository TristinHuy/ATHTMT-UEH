# Lab S5. Mục tiêu theo chuẩn chung của học phần.
# Ảnh ghim theo digest sau khi chạy ghim-digest.sh. Múi giờ, locale và hạt giống
# cố định để hai lần chạy cho cùng kết quả.

SHELL := /bin/bash
export TZ := Asia/Ho_Chi_Minh
export LC_ALL := C.UTF-8
export PYTHONHASHSEED := 0

EVID := evidence/S5
CHAY := docker compose --profile cong-cu run --rm -T
CONG_CU := $(CHAY) cong-cu

.PHONY: preflight up attack defend nam-phep-kiem do-argon2 verify export-evidence down help

help:
	@echo "preflight        ghi thông tin máy, kiểm Docker chạy được"
	@echo "up               dựng vùng định danh và dịch vụ theo cấu hình hiện có"
	@echo "attack           chạy sáu phép kiểm khi dịch vụ chưa vá, giữ trạng thái đầu buổi"
	@echo "defend           nạp lại dịch vụ sau khi sửa kiem_the.py hoặc chinh-sach.yaml"
	@echo "do-argon2        đo giá một lần đoán mật khẩu, ghi vào $(EVID)/do-argon2.txt"
	@echo "nam-phep-kiem    chạy P1 và N1 tới N5, ghi bằng chứng vào $(EVID)"
	@echo "verify           chạy bộ kiểm, đây là thứ bộ chấm chạy"
	@echo "export-evidence  gom bằng chứng vào $(EVID), kèm SHA256SUMS"
	@echo "down             dọn môi trường, xóa cả vùng định danh đã nạp"

preflight:
	@mkdir -p $(EVID)
	@{ \
	  echo "kien truc CPU: $$(uname -m)"; \
	  echo "he dieu hanh : $$(uname -s)"; \
	  echo "phien ban Python: $$(python3 --version 2>&1)"; \
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
	docker compose up -d --build may-danh-tinh dich-vu
	@echo "Vùng định danh ở http://127.0.0.1:8080, tài khoản quản trị khai trong docker-compose.yml."
	@echo "Dịch vụ hồ sơ KHÔNG lộ cổng nào ra máy thật; muốn gọi nó thì đứng từ trong mạng compose."
	@echo "Vùng định danh chỉ nạp cau-hinh/vung-dinh-danh.json ở lần dựng đầu. Sửa xong thì make down rồi make up."

attack:
	@echo "Bước này chạy TRƯỚC khi viết phần kiểm thẻ, và chỉ chạy một lần."
	@echo "Nó không phá gì: nó gửi các tấm thẻ thử, gồm cả thẻ hỏng, vào dịch vụ của chính sinh viên."
	@mkdir -p $(EVID)
	-$(CONG_CU) python3 /lab/bin/nam-phep-kiem.py truoc-khi-va 2>&1 | tee $(EVID)/truoc-khi-va.txt
	@echo
	@echo "Đọc cột thực tế. Chỗ nào ghi DUOC_NHAN mà đáng lẽ phải BI_TU_CHOI là một chỗ hỏng có mã riêng."
	@echo "Giữ tệp $(EVID)/truoc-khi-va.txt để so với trạng thái cuối buổi."

defend:
	docker compose up -d --build --force-recreate dich-vu
	@echo "Đã nạp lại dịch vụ. Bốn thứ phải xong trước bước này, tự kiểm lại:"
	@echo "  1. docker-compose.yml có ba tham số hàm băm, và đã đo trước khi chọn số"
	@echo "  2. cau-hinh/vung-dinh-danh.json bật yếu tố thứ hai, giới hạn số lần hỏi, rút hạn thẻ"
	@echo "  3. cau-hinh/chinh-sach.yaml diễn đạt đúng ba mệnh đề của việc 6"
	@echo "  4. dich-vu/kiem_the.py kiểm đủ thuật toán, người nhận, thời hạn"
	@echo "Đổi tệp vùng định danh thì phải make down trước, vì việc nạp chỉ xảy ra một lần."

do-argon2:
	@mkdir -p $(EVID)
	$(CHAY) -e CSS_NHAN_DO=$(or $(NHAN),chua-dat-ten) cong-cu python3 /lab/bin/do-argon2.py
	@echo "Chạy hai lần, một lần trước và một lần sau khi đổi tham số:"
	@echo "  make do-argon2 NHAN=truoc-khi-doi"
	@echo "  make do-argon2 NHAN=sau-khi-doi"

nam-phep-kiem:
	@mkdir -p $(EVID)/tho
	@echo "Sáu lần gọi thật. Phép cuối phải đợi tấm thẻ hết hạn, nên bước này lâu bằng đúng hạn thẻ đã đặt."
	$(CONG_CU) python3 /lab/bin/nam-phep-kiem.py
	@docker compose logs --no-color --no-log-prefix dich-vu 2>/dev/null | grep ' su_kien=kiem_the ' > $(EVID)/nhat-ky-dich-vu.log || true
	@test -s $(EVID)/nhat-ky-dich-vu.log || echo "Cảnh báo: nhật ký dịch vụ rỗng, chạy lại sau make up."
	@echo
	@echo "Bằng chứng ở $(EVID). Sáu tệp kiem-*.txt là bản máy đọc, thư mục tho/ là bản người đọc."

verify:
	python3 -m pytest tests/ -v --tb=short

export-evidence:
	@mkdir -p $(EVID)
	@$(MAKE) --no-print-directory preflight >/dev/null
	@{ find $(EVID) -type f -not -name SHA256SUMS; \
	   echo SCOPE.md; echo docker-compose.yml; \
	   echo cau-hinh/vung-dinh-danh.json; echo cau-hinh/chinh-sach.yaml; \
	   echo dich-vu/kiem_the.py; } \
	  | sort | xargs sha256sum > $(EVID)/SHA256SUMS
	@echo "Bằng chứng ở $(EVID), kèm SHA256SUMS."
	@echo "Băm này cho người chấm đối chiếu tệp nộp với tệp do máy sinh ra."

down:
	-docker compose --profile cong-cu down -v --remove-orphans
	@echo "Đã xóa container, mạng, và cả dữ liệu vùng định danh. Lần up sau nạp lại từ cau-hinh/."
