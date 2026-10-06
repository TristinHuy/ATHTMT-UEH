# Ảnh của ứng dụng thử nghiệm, lab S6.
#
# CHUA_GHIM_DIGEST: thẻ python:3.12-slim, chờ ghim-digest.sh thay bằng digest.
# Một thẻ như 3.12-slim trỏ sang một ảnh khác mỗi lần bản vá Debian được phát,
# nên hai lần dựng cách nhau một tuần cho hai ảnh khác nhau. Digest là băm của
# chính ảnh; đổi một byte là đổi digest.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PYTHONHASHSEED=0 \
    TZ=Asia/Ho_Chi_Minh \
    LC_ALL=C.UTF-8

WORKDIR /usr/local/lib/css-s06
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Chạy dưới người dùng không phải root. Buổi S2 đã dạy vì sao, và một bài lab
# dạy an toàn mà tự chạy bằng root thì tự bác bỏ chính nó.
RUN useradd --create-home --uid 10006 css
USER css

COPY --chown=css:css ung_dung.py .

EXPOSE 8081
CMD ["python3", "/usr/local/lib/css-s06/ung_dung.py"]
