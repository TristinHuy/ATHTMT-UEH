Nếu phải bỏ một lớp phòng thủ để giảm chi phí, em bỏ **mTLS và giữ TLS**.   

Duy trì mTLS cho 5.000 thiết bị đòi hỏi phát hành 5.000 chứng thư khách. Nếu 5% thiết bị thay đổi mỗi tháng, hệ thống tốn hàng chục giờ công định kỳ để cập nhật danh sách thu hồi (CRL/OCSP) cho 250 chứng thư. Chi phí này tốn kém hơn hẳn việc chỉ bảo trì 1 chứng thư máy chủ có hạn tối đa 400 ngày.   

Khi bỏ mTLS, hệ thống vẫn chặn được nghe lén (T1557) và dữ liệu đi trần (CWE-319). Bằng chứng K1 và K2 cho thấy hai lỗ hổng thuật toán độc lập đã bị đóng:   
    - **K1 (chiều dương)** chứng minh "kiểm chuỗi" thành công khi chứng thư dựng ngược được về CA nội bộ (chặn CWE-296).   
    - **K2 (chiều âm)** chứng minh "so tên" thành công khi Nginx từ chối request gọi sai tên (chặn CWE-297).

Hai cơ chế khác biệt này được kích hoạt thông qua chỉ thị ssl_certificate và server_name trong tệp may-chu.conf.   

Rủi ro khi gỡ bỏ chỉ thị ssl_verify_client on là CWE-295 (kho tin cậy mở rộng). Để bù đắp, em sẽ dời việc xác thực lên tầng ứng dụng (như JWT/OAuth2).   

Đồng thời, công cụ độc lập testssl.sh báo lỗi "Chain of trust: NOT ok (chain incomplete)" và hạ máy chủ xuống hạng B. Điều này phản ánh đúng thực tế cấu hình: tệp may-chu.conf chỉ trả về 1 chứng thư máy chủ duy nhất thay vì toàn bộ chuỗi chứng thư hợp lệ. Công cụ cũng chỉ ra sự thiếu hụt của cơ chế kiểm tra trạng thái thu hồi (không có OCSP URI hay CRL). 