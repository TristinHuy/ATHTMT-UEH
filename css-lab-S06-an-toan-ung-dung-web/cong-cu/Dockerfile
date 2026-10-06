# Ảnh công cụ của lab S6: semgrep, và chỉ semgrep.
#
# Bản dựng đầu của ảnh này còn một tầng lấy tệp nhị phân Trivy. Tầng ấy đã bị gỡ,
# vì ADR-0003 mục 2 dời Trivy khỏi buổi S6 và đặt nó ở buổi S8, nơi câu hỏi về
# chuỗi cung ứng được hỏi trọn vẹn cùng SBOM, chữ ký hiện vật và cổng an toàn.
# Quét ảnh ở đây thì hỏi được nửa câu rồi bỏ dở, và nửa câu ấy chiếm mất thời
# lượng của phần buổi S6 thật sự dạy, tức là vá một lỗ hổng web bằng cấu hình và
# bằng mã rồi chứng minh khai thác đã thất bại.
#
# Vì sao vẫn dựng một ảnh riêng cho một công cụ. Trần bốn container cho mỗi lab
# là ràng buộc thiết kế của học phần, ghi ở ADR-0003 mục N3, và bài này đã dùng
# hết bốn suất: ứng dụng huấn luyện, ứng dụng thử nghiệm, bộ quét nền, và chỗ
# này. Đặt semgrep trong một ảnh của bài thay vì cài lên máy bạn giữ cho hai lần
# chạy cách nhau ba tháng vẫn dùng đúng một phiên bản bộ quy tắc.
#
# Semgrep hỏi đúng một câu, và biết nó KHÔNG hỏi gì cũng là một phần của bài: nó
# hỏi "tôi có tự viết một lỗi đã có tên chưa", chứ không hỏi "thứ tôi mang vào có
# ai báo hỏng chưa". Câu thứ hai là câu của buổi S8.

# CHUA_GHIM_DIGEST: thẻ semgrep/semgrep:1.148.0, chờ ghim-digest.sh thay bằng digest
FROM semgrep/semgrep:1.148.0

ENV TZ=Asia/Ho_Chi_Minh \
    LC_ALL=C.UTF-8 \
    PYTHONHASHSEED=0 \
    SEMGREP_SEND_METRICS=off

WORKDIR /lab
ENTRYPOINT []
CMD ["/bin/sh"]
