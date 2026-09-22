# Lab S1. Mục tiêu theo chuẩn chung của học phần.
# Ảnh ghim theo digest. Múi giờ, locale và hạt giống cố định để hai lần chạy cho
# cùng kết quả.

SHELL := /bin/bash
export TZ := Asia/Ho_Chi_Minh
export LC_ALL := C.UTF-8
export PYTHONHASHSEED := 0

EVID := evidence/S1

.PHONY: preflight up attack defend verify export-evidence down help

help:
	@echo "preflight        ghi thông tin máy, kiểm Docker chạy được"
	@echo "up               dựng môi trường lab"
	@echo "attack           bài S1 không có phần tấn công"
	@echo "defend           bài S1 không có phần phòng thủ bằng cấu hình"
	@echo "verify           chạy bộ kiểm, đây là thứ bộ chấm chạy"
	@echo "export-evidence  gom bằng chứng vào $(EVID)"
	@echo "down             dọn môi trường"

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
	docker compose up --abort-on-container-exit

attack:
	@echo "Bài S1 không có phần tấn công. Xem SCOPE.md."

defend:
	@echo "Bài S1 không có phần phòng thủ bằng cấu hình. Sản phẩm của bài là mô hình đe dọa."

verify:
	python3 -m pytest tests/ -v --tb=short

export-evidence:
	@mkdir -p $(EVID)
	@$(MAKE) --no-print-directory preflight >/dev/null
	@cd $(EVID) && sha256sum * > SHA256SUMS 2>/dev/null || true
	@echo "Bằng chứng ở $(EVID), kèm SHA256SUMS."

down:
	-docker compose down -v --remove-orphans
