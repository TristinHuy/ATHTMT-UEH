# Ảnh của dịch vụ tài nguyên và của chỗ bạn đứng để đo. Một ảnh dùng cho cả hai
# vai, vì hai vai cần đúng một bộ thư viện và vì mỗi ảnh thêm là một lần tải về
# nữa trên máy sinh viên.
#
# CHUA_GHIM_DIGEST: dòng FROM dưới đây ghim theo thẻ, chưa ghim theo digest. Chạy
# ghim-digest.sh trên máy có mạng để thay thẻ bằng digest thật. Không tự gõ một
# chuỗi sha256 vào đây: một chuỗi bịa trông giống hệt một chuỗi thật cho tới ngày
# nó làm hỏng một lần dựng.
FROM python:3.12-slim

# Thư viện ghim theo phiên bản chính xác, không ghim theo dải. Ba tên này đọc và
# ký thẻ, nên một bản khác nhau ở đây là một hành vi kiểm chữ ký khác nhau.
COPY requirements.txt /tmp/requirements.txt
RUN pip install --no-cache-dir -r /tmp/requirements.txt \
 && rm -f /tmp/requirements.txt

# Tiến trình không chạy bằng root. Buổi S2 đã dựng lý do cho dòng này; ở đây nó
# là thói quen đã thành nếp chứ không phải yêu cầu mới của bài.
RUN useradd --system --uid 10005 --create-home --shell /usr/sbin/nologin sv
USER sv

ENV PYTHONPATH=/usr/local/lib/css-s05 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /lab
EXPOSE 8000
CMD ["python3", "/usr/local/lib/css-s05/may-chu.py"]
