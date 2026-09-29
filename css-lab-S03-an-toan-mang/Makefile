# Lab S3. Mục tiêu theo chuẩn chung của học phần.
# Ảnh ghim theo digest sau khi chạy ghim-digest.sh. Múi giờ, locale và hạt giống
# cố định để hai lần chạy cho cùng kết quả.

SHELL := /bin/bash
export TZ := Asia/Ho_Chi_Minh
export LC_ALL := C.UTF-8
export PYTHONHASHSEED := 0

EVID := evidence/S3
KHACH := docker compose run --rm -T may-khach
KHACH_SH := docker compose run --rm -T --entrypoint sh may-khach
GHI := bin/ghi-ket-qua.sh

# Ba tham số lặp lại ở mọi lần nối, gom một chỗ để sửa một lần.
NEO := -connect may-chu:8443 -tls1_3 -CAfile /pki/ca/ca.crt -verify_return_error

.PHONY: preflight up attack defend bon-phep-kiem quan-sat thu-thach verify export-evidence down help

help:
	@echo "preflight        ghi thông tin máy, kiểm Docker và openssl chạy được"
	@echo "up               dựng máy chủ theo cấu hình hiện có trong nginx/"
	@echo "attack           đọc trộm nội dung trên chặng phẳng, khi TLS chưa bật"
	@echo "defend           dựng lại máy chủ với cấu hình và bộ chứng thư bạn vừa viết"
	@echo "bon-phep-kiem    chạy K1 tới K4, ghi bằng chứng vào $(EVID)"
	@echo "quan-sat         chạy testssl.sh như một người quan sát độc lập"
	@echo "thu-thach        phép kiểm K5 tùy chọn, chứng thư khách do CA ngoài ký"
	@echo "verify           chạy bộ kiểm, đây là thứ bộ chấm chạy"
	@echo "export-evidence  gom bằng chứng vào $(EVID), kèm SHA256SUMS"
	@echo "down             dọn môi trường"

preflight:
	@mkdir -p $(EVID)
	@{ \
	  echo "kien truc CPU: $$(uname -m)"; \
	  echo "he dieu hanh : $$(uname -s)"; \
	  echo "phien ban Python: $$(python3 --version 2>&1)"; \
	  if command -v openssl >/dev/null 2>&1; then \
	    echo "phien ban openssl: $$(openssl version 2>&1)"; \
	  else \
	    echo "phien ban openssl: KHONG CO"; \
	  fi; \
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
	docker compose up -d may-chu
	@echo "Máy chủ đang chạy trong mạng css-s03-labnet, không lộ cổng nào ra máy thật."
	@echo "Muốn nhìn thấy nó thì đứng từ trong mạng: make attack, hoặc make bon-phep-kiem."

attack:
	@echo "Bước này chạy TRƯỚC khi bạn bật TLS, và chỉ chạy một lần."
	@echo "Nó không phá gì cả: nó chỉ đọc thứ máy chủ đang phát ra dưới dạng bản rõ."
	@mkdir -p $(EVID)
	-$(KHACH_SH) -c 'wget -q -T 5 -O - http://may-chu:8080/' | tee $(EVID)/truoc-khi-va.txt
	@echo
	@echo "Chuỗi vừa hiện ra là thứ mọi tiến trình khác trong cùng mạng cũng đọc được."
	@echo "Đó là điểm yếu CWE-319, và §3.3 của giáo trình gọi nó là chặng cuối."

defend:
	docker compose up -d --force-recreate may-chu
	@echo "Đã nạp lại cấu hình. Ba thứ phải xong trước bước này, tự kiểm lại:"
	@echo "  1. pki/ đủ chứng thư, do CA nội bộ của bạn cấp"
	@echo "  2. nginx/may-chu.conf chỉ còn khối server có ssl"
	@echo "  3. ssl_verify_client on, và ssl_client_certificate trỏ tới CA nội bộ"

bon-phep-kiem:
	@mkdir -p $(EVID)/tho
	@echo "Bốn phép kiểm, hai lớp, mỗi lớp một chiều dương và một chiều âm."
	@$(GHI) K1 1 THANH_CONG "Verification: OK" \
	  "Lop TLS, chieu duong: chung thu may chu dung nguoc duoc ve CA noi bo va ten khop" \
	  -- '$(KHACH) s_client $(NEO) -verify_hostname may-chu -cert /pki/khach/khach.crt -key /pki/khach/khach.key -brief < /dev/null'
	@$(GHI) K2 1 BI_TU_CHOI "-" \
	  "Lop TLS, chieu am: goi bang mot ten khac phai bi tu choi, phep so ten dang chay" \
	  -- '$(KHACH) s_client $(NEO) -verify_hostname may-chu-gia -cert /pki/khach/khach.crt -key /pki/khach/khach.key -brief < /dev/null'
	@$(GHI) K3 2 THANH_CONG "200 OK" \
	  "Lop mTLS, chieu duong: co trinh chung thu khach thi doc duoc noi dung" \
	  -- '$(KHACH_SH) -c "printf \"GET / HTTP/1.0\r\nHost: may-chu\r\n\r\n\" | openssl s_client $(NEO) -verify_hostname may-chu -cert /pki/khach/khach.crt -key /pki/khach/khach.key -quiet -ign_eof"'
	@$(GHI) K4 2 BI_TU_CHOI "200 OK" \
	  "Lop mTLS, chieu am: khong trinh chung thu khach thi phai bi tu choi" \
	  -- '$(KHACH_SH) -c "printf \"GET / HTTP/1.0\r\nHost: may-chu\r\n\r\n\" | openssl s_client $(NEO) -verify_hostname may-chu -quiet -ign_eof"'
	@echo
	@echo "Bằng chứng ở $(EVID). Bốn tệp kiem-K*.txt là bản máy đọc, thư mục tho/ là bản người đọc."

quan-sat:
	@mkdir -p $(EVID)
	docker compose --profile quan-sat run --rm quan-sat --quiet --color 0 may-chu:8443 | tee $(EVID)/quan-sat-ngoai.txt
	@echo
	@echo "Đầu ra này do một công cụ khác sinh ra, không do cấu hình của bạn khai."
	@echo "Người chấm đọc nó, máy không chấm nó. Lý do ghi ở README, mục máy chấm kiểm những gì."

thu-thach:
	@mkdir -p $(EVID)/tho
	@$(GHI) K5 2 BI_TU_CHOI "200 OK" \
	  "Thu thach: chung thu khach con han, dung cu phap, nhung do CA ngoai ky" \
	  -- '$(KHACH_SH) -c "printf \"GET / HTTP/1.0\r\nHost: may-chu\r\n\r\n\" | openssl s_client $(NEO) -verify_hostname may-chu -cert /pki/ca-ngoai/khach-ngoai.crt -key /pki/ca-ngoai/khach-ngoai.key -quiet -ign_eof"'
	@echo "K5 không nằm trong phần máy chấm. Nó là chỗ để bạn trả lời câu hỏi kho tin cậy rộng tới đâu."

verify:
	python3 -m pytest tests/ -v --tb=short

export-evidence:
	@mkdir -p $(EVID)
	@$(MAKE) --no-print-directory preflight >/dev/null
	@{ find $(EVID) -type f -not -name SHA256SUMS; \
	   echo SCOPE.md; echo docker-compose.yml; echo nginx/may-chu.conf; } \
	  | sort | xargs sha256sum > $(EVID)/SHA256SUMS
	@echo "Bằng chứng ở $(EVID), kèm SHA256SUMS."
	@echo "Băm này để người chấm biết tệp bạn nộp đúng là tệp máy sinh ra."

down:
	-docker compose --profile cong-cu --profile quan-sat down -v --remove-orphans
