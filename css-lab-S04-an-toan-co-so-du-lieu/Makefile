# Lab S4. Mục tiêu theo chuẩn chung của học phần.
# Ảnh ghim theo digest sau khi chạy ghim-digest.sh. Múi giờ, locale và hạt giống
# cố định để hai lần chạy cho cùng kết quả. Locale ở đây không chỉ để cho đẹp:
# bộ ghi kết quả phân loại phán quyết theo thông điệp lỗi của máy chủ, nên đổi
# LC_ALL là đổi phán quyết.

SHELL := /bin/bash
export TZ := Asia/Ho_Chi_Minh
export LC_ALL := C.UTF-8
export PYTHONHASHSEED := 0

EVID := evidence/S4
GHI  := bin/ghi-truy-van.sh

# Một phiên psql, chạy bằng vai trò ghi ở cuối dòng. Mật khẩu lab nằm trong tệp
# compose, xem ghi chú ở đó.
NHU := docker compose run --rm -T -e PGPASSWORD=lab2026 may-khach \
       psql -h csdl -d css_s04 -v ON_ERROR_STOP=1 -U
QUAN_TRI := docker compose run --rm -T -e PGPASSWORD=lab2026 may-khach \
            psql -h csdl -d css_s04 -v ON_ERROR_STOP=1 -U postgres

.PHONY: preflight up attack defend tam-truy-van suy-luan thu-thach verify export-evidence down help

help:
	@echo "preflight        ghi thông tin máy, kiểm Docker chạy được"
	@echo "up               dựng máy chủ và nạp lược đồ cùng dữ liệu phát sẵn"
	@echo "attack           đọc bảng lương bằng tài khoản cũ, và thử chuỗi truy vấn suy luận"
	@echo "defend           nạp ba tệp SQL của bạn, rồi khởi động lại máy chủ để pgaudit có hiệu lực"
	@echo "tam-truy-van     chạy A1 tới A5 và D1 tới D3, ghi bằng chứng vào $(EVID)"
	@echo "suy-luan         chạy lại chuỗi suy luận SAU khi đã siết, để thấy phần không đóng được"
	@echo "thu-thach        phép kiểm A6 tùy chọn, người duyệt thử tạo đề nghị chi"
	@echo "verify           chạy bộ kiểm, đây là thứ bộ chấm chạy"
	@echo "export-evidence  gom bằng chứng và nhật ký pgaudit vào $(EVID), kèm SHA256SUMS"
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
	docker compose up -d --build csdl
	@echo "Đợi máy chủ nhận kết nối."
	@for i in $$(seq 1 30); do \
	  if docker compose exec -T csdl pg_isready -U postgres -d css_s04 >/dev/null 2>&1; then break; fi; \
	  sleep 2; \
	done
	@docker compose exec -T csdl pg_isready -U postgres -d css_s04 \
	  || { echo "Máy chủ chưa lên. Đọc lỗi bằng: docker compose logs csdl"; exit 1; }
	$(QUAN_TRI) -f /sql/00-du-lieu.sql
	@echo
	@echo "Lược đồ và dữ liệu đã nạp. Đây là điểm xuất phát, chạy lại make up bất cứ lúc nào."
	@echo "Máy chủ không lộ cổng nào ra máy thật; muốn nhìn thấy nó thì đứng từ trong mạng."

attack:
	@echo "Bước này chạy TRƯỚC khi bạn siết quyền."
	@echo "Nó không phá gì cả: nó chỉ chạy ba câu truy vấn hợp lệ bằng một tài khoản cũ."
	@mkdir -p $(EVID)
	-$(NHU) khach_tam -f /sql/kiem/tan-cong.sql | tee $(EVID)/truoc-khi-siet.txt
	@echo
	@echo "Câu thứ nhất đọc thẳng bảng lương, và phần việc hôm nay đóng được nó lại."
	@echo "Hai câu sau chỉ hỏi thống kê. Hiệu của chúng là lương của đúng một người,"
	@echo "và phần việc hôm nay KHÔNG đóng được chỗ đó. Mục 4.8 nói vì sao."

defend:
	$(QUAN_TRI) -f /sql/01-vai-tro.sql
	$(QUAN_TRI) -f /sql/02-muc-hang.sql
	$(QUAN_TRI) -f /sql/03-pgaudit.sql
	@echo "Khởi động lại máy chủ, vì pgaudit nạp lúc khởi động chứ không nạp lúc chạy."
	docker compose restart csdl
	@for i in $$(seq 1 30); do \
	  if docker compose exec -T csdl pg_isready -U postgres -d css_s04 >/dev/null 2>&1; then break; fi; \
	  sleep 2; \
	done
	@docker compose exec -T csdl pg_isready -U postgres -d css_s04 \
	  || { echo "Máy chủ không lên lại được. Gần như luôn là một dòng sai trong csdl/pgaudit.conf."; \
	       echo "Đọc dòng lỗi bằng: docker compose logs --tail 30 csdl"; exit 1; }
	@echo "Đã nạp ba tệp SQL và khởi động lại máy chủ."

tam-truy-van:
	@mkdir -p $(EVID)/tho
	@echo "Năm phép kiểm âm, mỗi phép hỏi một vai trò một việc nó KHÔNG được phép làm."
	@$(GHI) A1 am bao_cao     LOI_QUYEN      "Vai tro bao cao doc thang bang nhan su" \
	  -- '$(NHU) bao_cao -f /sql/kiem/A1.sql'
	@$(GHI) A2 am ung_dung    KHONG_DONG     "Vai tro ung dung doc de nghi chi cua nguoi khac" \
	  -- '$(NHU) ung_dung -f /sql/kiem/A2.sql'
	@$(GHI) A3 am ung_dung    LOI_CHINH_SACH "Vai tro ung dung ghi mot dong mang ten nguoi khac" \
	  -- '$(NHU) ung_dung -f /sql/kiem/A3.sql'
	@$(GHI) A4 am duyet_chi   LOI_RANG_BUOC  "Nguoi duyet tu duyet de nghi do chinh minh tao" \
	  -- '$(NHU) duyet_chi -f /sql/kiem/A4.sql'
	@$(GHI) A5 am chu_luoc_do KHONG_DONG     "Chu so huu bang doc de nghi chi khi da bat FORCE" \
	  -- '$(NHU) chu_luoc_do -f /sql/kiem/A5.sql'
	@echo
	@echo "Ba phép kiểm dương, để chắc rằng bạn siết mà hệ thống vẫn dùng được."
	@$(GHI) D1 duong ung_dung CHAY_DUOC      "Vai tro ung dung doc de nghi chi cua chinh no" \
	  -- '$(NHU) ung_dung -f /sql/kiem/D1.sql'
	@$(GHI) D2 duong ung_dung CHAY_DUOC      "Vai tro ung dung tao de nghi chi mang ten chinh no" \
	  -- '$(NHU) ung_dung -f /sql/kiem/D2.sql'
	@$(GHI) D3 duong bao_cao  CHAY_DUOC      "Vai tro bao cao doc khung nhin thong ke" \
	  -- '$(NHU) bao_cao -f /sql/kiem/D3.sql'
	@echo
	@echo "Bằng chứng ở $(EVID). Tám tệp kiem-*.txt là bản máy đọc, thư mục tho/ là bản người đọc."

suy-luan:
	@mkdir -p $(EVID)
	-$(NHU) bao_cao -f /sql/kiem/suy-luan.sql | tee $(EVID)/suy-luan.txt
	@echo
	@echo "Máy không chấm tệp này, người chấm đọc nó. Lý do ở README, mục máy chấm kiểm những gì."

thu-thach:
	@mkdir -p $(EVID)/tho
	@$(GHI) A6 am duyet_chi LOI_QUYEN "Thu thach: nguoi duyet thu tao mot de nghi chi" \
	  -- '$(NHU) duyet_chi -f /sql/kiem/A6.sql'
	@echo "A6 không nằm trong phần máy chấm. Nó là chỗ để bạn chỉ ra hai lớp khác nhau của tách nhiệm vụ."

verify:
	python3 -m pytest tests/ -v --tb=short

export-evidence:
	@mkdir -p $(EVID)
	@$(MAKE) --no-print-directory preflight >/dev/null
	@docker compose logs --no-color --no-log-prefix csdl 2>/dev/null \
	  | grep -i 'AUDIT' > $(EVID)/pgaudit.txt || true
	@echo "Nhật ký pgaudit: $$(wc -l < $(EVID)/pgaudit.txt) dòng trong $(EVID)/pgaudit.txt"
	@{ find $(EVID) -type f -not -name SHA256SUMS; \
	   echo SCOPE.md; echo docker-compose.yml; echo csdl/pgaudit.conf; \
	   ls sql/*.sql; } \
	  | sort | xargs sha256sum > $(EVID)/SHA256SUMS
	@echo "Bằng chứng ở $(EVID), kèm SHA256SUMS."
	@echo "Băm này để người chấm biết tệp bạn nộp đúng là tệp máy sinh ra."

down:
	-docker compose --profile cong-cu down -v --remove-orphans
