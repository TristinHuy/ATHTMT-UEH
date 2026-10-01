# Máy chủ PostgreSQL của bài, cộng đúng một phần mở rộng.
#
# Vì sao phải dựng ảnh chứ không dùng thẳng ảnh chính thức: ảnh postgres chính
# thức không kèm pgaudit, và §4.4 của giáo trình đặt pgaudit vào giữa bài, vì nó
# là thứ duy nhất trả lời được câu hỏi ai đã đọc gì tuần trước. Gói pgaudit lấy
# từ kho apt của chính dự án PostgreSQL, kho đã được khai báo sẵn trong ảnh
# chính thức.
#
# CHUA_GHIM_DIGEST: thẻ postgres:17.6-bookworm, chờ ghim-digest.sh thay bằng digest
FROM postgres:17.6-bookworm

# Ghim theo phiên bản gói, không lấy bản mới nhất, để hai lần dựng cách nhau vài
# tuần cho cùng một ảnh. Số hiệu gói CHƯA ĐỐI CHIẾU với kho apt vì máy soạn bài
# không ra được mạng; lần chạy CI đầu tiên trên máy có mạng phải xác nhận nó,
# và nếu phiên bản không còn thì sửa đúng một dòng này.
ARG PGAUDIT_PKG=postgresql-17-pgaudit

RUN set -eux; \
    apt-get update; \
    apt-get install -y --no-install-recommends "$PGAUDIT_PKG"; \
    rm -rf /var/lib/apt/lists/*
