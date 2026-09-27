# Bảng làm cứng, lab S2

Tên: Nguyễn Quốc Huy · Mã số sinh viên: 31241027109 · Ngày nộp: 09/22/2026

Mỗi dòng là một thay đổi bạn đã làm, không phải một thay đổi bạn định làm. Cần ít
nhất bốn dòng, và trong đó ít nhất một dòng dẫn về kỹ thuật T1548.001 của ATT&CK
v19.2 và ít nhất một dòng dẫn về một mã trong CWE 4.20.

Ba cột nặng nhẹ khác nhau. Cột thứ nhất dễ nhất, vì nó chỉ đòi bạn đọc tài liệu.
Cột thứ hai đòi bạn nghĩ như người phải trực hệ thống ấy sáu tháng nữa. Cột thứ ba
đòi bạn nghĩ như người tấn công vẫn còn đường vào sau khi bạn đã vá, và nó là cột
hay bị bỏ trống nhất.

| Thay đổi đã làm | Chặn được điều gì, dẫn ATT&CK v19.2 hoặc CWE 4.20 | Làm hỏng điều gì, tính bằng thao tác thủ công mỗi tuần | Thứ vẫn còn qua được sau khi đã sửa |
|---|---|---|---|
| **Gỡ bỏ bit setuid và cấm tiến trình con nâng quyền**<br>• `chmod 0755 /usr/local/bin/doc-bimat`<br>• `security_opt: no-new-privileges:true` | **ATT&CK v19.2 T1548.001** (Abuse Elevation Control Mechanism: Setuid and Setgid).<br>Triệt tiêu hoàn toàn khả năng người dùng không đặc quyền mượn danh nghĩa root qua cờ setuid để đọc tệp bí mật. | **1–2 lần/tuần**.<br>Quản trị viên buộc phải dùng lệnh ngoài (`docker exec -u 0`) nếu cần chạy công cụ chẩn đoán đặc quyền để kiểm tra dữ liệu nội bộ. | Kẻ tấn công nếu khai thác được lỗi thực thi mã tùy ý (RCE) trong tiến trình dịch vụ vẫn đọc được dữ liệu do tiến trình đó sở hữu trong RAM. |
| **Thu hẹp quyền tệp cấu hình**<br>• Chuyển từ `0666` về `0644` trong `Dockerfile` | **CWE-732** (Incorrect Permission Assignment for Critical Resource).<br>Khóa quyền ghi đối với mọi người dùng khác; chỉ tài khoản root mới có thể sửa tệp cấu hình. | **1 lần/tuần**.<br>Mỗi lần cập nhật tham số phải cấp quyền root hoặc build lại image thay vì mở tệp sửa nóng trực tiếp bằng user thường. | Tiến trình chạy bằng root thật sự hoặc người có quyền truy cập trực tiếp host vẫn can thiệp được nếu hệ tệp cho phép ghi. |
| **Hạ quyền tiến trình dịch vụ**<br>• Khai báo `user: "10001"` trong `docker-compose.yml` | **CWE-250** (Execution with Unnecessary Privileges).<br>Hạn chế tối đa bán kính thiệt hại nếu dịch vụ bị chiếm quyền điều khiển nhờ chạy bằng tài khoản thường (`sv`). | **0 thao tác định kỳ**.<br>Chỉ tốn thêm khoảng 30 phút trong lần dựng môi trường ban đầu để gán đúng quyền sở hữu (`chown`) tài nguyên cho UID 10001. | Lỗ hổng thoát vùng chứa (container breakout) ở cấp độ nhân Linux (kernel 0-day) nếu nhân của máy chủ chủ quản chưa được vá. |
| **Khóa hệ tệp và tước toàn bộ Capabilities**<br>• `read_only: true`<br>• `cap_drop: [ALL]`<br>• `cap_add: [NET_BIND_SERVICE]` | Chặn việc tải mã độc, sửa nhị phân và lạm dụng đặc quyền hạt nhân theo **ATT&CK v19.2 T1059**.<br>Chỉ giữ lại năng lực tối thiểu để lắng nghe cổng mạng 80. | **2–3 lần/tuần**.<br>Gây khó khăn khi debug do không tạo được tệp tạm (`/tmp`) hay chỉnh sửa tệp trực tiếp; buộc phải thao tác qua cờ override. | Thư mục gắn ngoài `/var/log/css-s02` vẫn được phép ghi; kẻ tấn công có thể ghi tràn dữ liệu làm cạn đĩa hoặc làm giả nhật ký hệ thống. |

## Một câu về thứ bạn quyết định không làm

Em đã cân nhắc việc đổi cổng lắng nghe của dịch vụ từ cổng đặc quyền 80 sang cổng không đặc quyền (như 8080) để tước bỏ luôn năng lực `NET_BIND_SERVICE`, nhưng quyết định bỏ qua vì việc đổi cổng sẽ phá vỡ tính tương thích với hạ tầng reverse proxy hiện có, buộc toàn bộ đội vận hành phải cấu hình lại đường định tuyến mạng tốn kém nhiều giờ thao tác mỗi tuần, trong khi rủi ro còn lại của năng lực `NET_BIND_SERVICE` khi đã chạy bằng non-root user là rất thấp.
