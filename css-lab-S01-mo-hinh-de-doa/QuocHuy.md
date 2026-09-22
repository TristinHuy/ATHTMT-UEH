# Báo Cáo Mô Hình Đe Dọa (Threat Model) - Lab S1

## 1. Hệ Thống Được Chọn
Hệ thống được chọn là **Hệ thống Web Bán Hàng Mini**, bao gồm đúng 3 thành phần chính:
1. **Trình duyệt người dùng (Client Browser):** Giao diện tương tác, nơi người dùng gửi thông tin đặt hàng và xem hồ sơ cá nhân.
2. **Máy chủ ứng dụng (Web API Server):** Đóng vai trò xử lý logic phân quyền, tính toán đơn hàng và giao tiếp với cơ sở dữ liệu.
3. **Cơ sở dữ liệu (PostgreSQL Database):** Lưu trữ toàn bộ bảng tài khoản, quyền hạn, dữ liệu sản phẩm và lịch sử giao dịch.

---

## 2. Ba Mối Đe Dọa Được Chọn Để Xử Lý
Dựa trên ma trận rủi ro (Rủi ro = Tác động x Khả năng), 3 mối đe dọa có điểm rủi ro cao nhất được ưu tiên xử lý gồm:

1. **M03 - Lỗ hổng kiểm soát truy cập mức đối tượng (BOLA/IDOR)**
   * Điểm rủi ro: 4 x 5 = 20 (Cao nhất).
   * Phát biểu: *Người dùng thông thường xem được chi tiết đơn hàng của người khác khi thay đổi trực tiếp tham số order_id trên URL do ứng dụng không kiểm tra quyền sở hữu.*
   * Phương án & Chi phí: 8 giờ công để bổ sung middleware xác thực quyền truy cập tài nguyên theo user session.

2. **M01 - Tấn công tiêm lệnh SQL (SQL Injection)**
   * Điểm rủi ro: 5 x 4 = 20.
   * Phát biểu: *Một kẻ tấn công thực hiện trích xuất dữ liệu thẻ thanh toán nếu máy chủ ứng dụng bị tấn công SQL Injection do không lọc đầu vào khi truy vấn.*
   * Phương án & Chi phí: 16 giờ công để chuẩn hóa toàn bộ truy vấn sang dạng Parameterized Queries/Prepared Statements.

3. **M02 - Lưu trữ mã độc phía máy khách (Stored XSS)**
   * Điểm rủi ro: 4 x 4 = 16.
   * Phát biểu: *Kẻ tấn công đánh cắp phiên làm việc của khách hàng khi chèn mã độc Javascript vào phần đánh giá sản phẩm do thiếu cơ chế kiểm duyệt nội dung.*
   * Phương án & Chi phí: 12 giờ công để thiết lập header Content-Security-Policy (CSP) và cơ chế encode/sanitize đầu vào bằng DOMPurify.

---

## 3. Lý Do Lựa Chọn và Biện Luận
* **Vì sao chọn 3 mối này:** 
  * M03 và M01 dẫn đầu danh sách với điểm rủi ro đạt mức tối đa (20/25). Cả hai đều đe dọa trực tiếp đến tính bảo mật dữ liệu nhạy cảm (thông tin thanh toán, đơn hàng) và có khả năng khai thác rất cao trên môi trường web thương mại điện tử.
  * M02 đạt điểm rủi ro 16/25, trực tiếp nhắm vào người dùng cuối và đánh cắp phiên đăng nhập (Session Hijacking).
  * Xét theo Nguyên lý thứ 7 (Cân bằng chi phí và rủi ro), tổng chi phí khắc phục 3 mối này là 36 giờ công—hoàn toàn khả thi, mang lại giá trị bảo vệ lớn nhất cho hệ thống mà không đòi hỏi thay đổi kiến trúc hạ tầng phức tạp.

* **Vì sao không chọn các mối còn lại:**
  * Các mối **M04, M06, M08** có điểm rủi ro trung bình (12 - 15), tần suất khai thác thấp hơn hoặc có thể kiểm soát tạm thời bằng các lớp phòng thủ sẵn có (như Nginx rate limit, certbot SSL tự động).
  * Các mối **M05, M07** có tác động nghiêm trọng (5) nhưng khả năng xảy ra ở giai đoạn đầu thấp (2), đồng thời chi phí triển khai hệ thống backup thảm họa và hạ tầng mã hóa phần cứng tốn kém hơn nhiều so với việc vá các lỗ hổng logic ứng dụng cấp thiết.