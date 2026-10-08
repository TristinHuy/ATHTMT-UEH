# Container để hỏi. Hai thứ trong đây phục vụ hai mục đích khác nhau.
#
# logcli là thứ bạn gõ tay trong lúc làm bài, vì nó in ra dạng người đọc và thử
# một câu truy vấn bằng nó nhanh hơn mọi cách khác. Python là thứ ghi lại kết quả
# dưới dạng bộ chấm đọc được. Người chấm cần biết câu truy vấn nào cho ra bao
# nhiêu dòng, và một ảnh chụp màn hình không nói được điều đó.

# CHUA_GHIM_DIGEST: thẻ grafana/logcli:3.5.1, chờ ghim-digest.sh thay bằng digest
FROM grafana/logcli:3.5.1 AS logcli

# CHUA_GHIM_DIGEST: thẻ python:3.12-slim, chờ ghim-digest.sh thay bằng digest
FROM python:3.12-slim

# Đường dẫn của tệp nhị phân trong ảnh logcli CHƯA XÁC MINH trên máy soạn bài, vì
# máy ấy không kéo được ảnh. Nếu đường dẫn sai thì lệnh COPY dừng ngay lúc dựng,
# kèm tên tệp không tìm thấy, chứ không sinh ra một ảnh thiếu công cụ mà tới lúc
# chạy mới lộ. Tra đường dẫn thật bằng:
#   docker run --rm --entrypoint sh grafana/logcli:3.5.1 -c 'command -v logcli'
COPY --from=logcli /usr/bin/logcli /usr/local/bin/logcli

# Lệnh này biến một giả định thành một phép kiểm. Ảnh dựng xong mà logcli không
# chạy được thì việc dựng hỏng tại đây, không phải hỏng lúc bạn đang làm bài.
RUN logcli --version

RUN pip install --no-cache-dir "PyYAML==6.0.2"

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    TZ=Asia/Ho_Chi_Minh \
    LC_ALL=C.UTF-8

WORKDIR /lab
CMD ["sleep", "infinity"]
