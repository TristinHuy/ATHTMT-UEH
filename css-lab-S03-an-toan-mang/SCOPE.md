# Phạm vi cho phép, lab S3

Phiên bản 1. Văn bản này viết riêng cho bài S3 và thay cho bản chung ở những chỗ hai bên khác nhau. Đọc trước khi chạy lệnh đầu tiên, và đọc lại mỗi khi bạn định thử một thứ mà bạn không chắc.

## 1. Bài này học gì, và vì sao nó cần một văn bản phạm vi

Bài đo bốn chuẩn đầu ra. CLO1.2 ở chỗ bạn gọi tên được vì sao một cấu hình đúng thuật toán vẫn là lỗ hổng. CLO2.1 ở chỗ bạn cấu hình được máy chủ. CLO2.2 ở chỗ bạn thu được bằng chứng, gồm cả một phép kiểm âm. CLO3.1 ở chính văn bản này, tức ở việc bạn nhận ra ranh giới và giữ đúng nó.

Khác với bài S1, bài này có một bước tác động thật. `make attack` mở một kết nối và đọc nội dung máy chủ đang phát ra dưới dạng bản rõ. Việc ấy vô hại ở đây vì máy chủ là của bạn, chạy trong mạng ảo của bạn, và phát ra một chuỗi được dựng riêng để dạy học. Chính vì nó vô hại ở đây mà thói quen phải hình thành ở đây: cùng một lệnh, chạy sang một máy chủ không phải của bạn, là một chuyện hoàn toàn khác.

## 2. Tài sản trong phạm vi

| Thứ | Định danh | Ghi chú |
|---|---|---|
| Máy chủ | container `css-s03-may-chu`, tên mạng `may-chu` | phục vụ trên cổng 8443 sau khi bạn bật TLS |
| Máy khách | container `css-s03-may-khach`, tên mạng `may-khach` | chạy theo từng lượt đo, không chạy nền |
| Người quan sát | container `css-s03-quan-sat` | chỉ chạy khi bạn gọi `make quan-sat` |
| Mạng | mạng bridge `css-s03-labnet` | do compose của bài tạo ra và xóa đi |
| Tài khoản thử | không có | bài này không dùng mật khẩu nào |
| Dữ liệu thử | `noi-dung/index.html` | chuỗi trong đó là chuỗi giả, dựng để dạy học |

Không có cổng nào lộ ra máy thật, và đó là chủ ý. Bốn phép kiểm đều đứng từ trong mạng compose.

## 3. Bạn được làm

- Dựng, sửa, phá và dựng lại ba container trên, bao nhiêu lần tùy ý.
- Chạy `make attack`, tức đọc nội dung trên chặng phẳng của chính máy chủ mình.
- Chạy `openssl s_client` với mọi tham số, hướng vào `may-chu:8443` trong mạng của bạn.
- Chạy `testssl.sh` qua `make quan-sat`, hướng vào chính máy chủ ấy.
- Dựng bao nhiêu tổ chức cấp chứng thư tùy thích, kể cả tổ chức dựng ra để bị từ chối.
- Đọc tài liệu, đọc mã nguồn mở, đọc kho mã công khai được giới thiệu trong học phần.

## 4. Bạn không được làm

- Gửi gói tin tới bất kỳ đích nào ngoài `127.0.0.1` và mạng `css-s03-labnet` của chính bạn. Điều này gồm cả máy của bạn cùng lớp, hạ tầng của UEH, của HCMUT, và của GitHub.
- Quét, dò, hoặc thử nối tới một hệ thống không thuộc quyền quản trị của bạn, kể cả một lần, kể cả để cho biết.
- Chạy `nmap` ra ngoài mạng compose của bài. Bước trinh sát ở lớp chỉ quét mạng ấy.
- Tấn công từ chối dịch vụ dưới mọi hình thức.
- Viết, tải, hoặc chạy mã độc, cửa hậu, kênh điều khiển.
- Thêm `privileged`, `network_mode: host`, hoặc `cap_add` vào tệp compose. Bộ chấm đọc chính tệp ấy và đánh trượt nếu thấy.
- Dùng chứng thư, khóa, tên miền, hoặc dữ liệu cá nhân thật của bất kỳ ai làm dữ liệu mẫu.
- Đưa mã khai thác lấy từ nguồn công khai vào bài nộp.

## 5. Kỹ thuật bài này chạm tới, và mức chạm

Ba mã dưới đây lấy từ bản ATT&CK content v19.2, đọc ngày 18/08/2026. Bài chạm tới chúng từ phía phòng thủ.

| Mã | Tên | Bài này làm gì với nó |
|---|---|---|
| T1557 | Adversary-in-the-Middle | đây là thứ phép so tên ở K1 và K2, cùng bước bật mTLS, nhằm chặn |
| T1046 | Network Service Discovery | bước trinh sát mười phút đầu giờ, chỉ trong mạng compose của bạn |
| T1040 | Network Sniffing | `make attack` đọc chặng phẳng của chính bạn, để thấy dữ liệu trần trông ra sao |

Ranh giới của buổi, chép nguyên từ bảng ranh giới của học phần. Học phần này dạy cấu hình TLS, mTLS, lọc gói, và đọc lưu lượng đã bắt sẵn. Việc quét mạng ngoài phạm vi container của mình, việc né tránh phát hiện, và việc khai thác dịch vụ mạng thuộc học phần Kiểm thử thâm nhập, học song song trong cùng học kì.

## 6. Cửa sổ thời gian

Phạm vi này có hiệu lực từ khi bạn nhận kho tới khi bài được chấm xong. Mốc viết theo buổi, không theo ngày dương lịch. Học liệu và môi trường sẵn sàng từ trước buổi S3 hai ngày; hạn nộp là trước giờ buổi S4.

## 7. Nghĩa vụ khôi phục và phần phòng thủ đi kèm

Bài này không cho bạn thấy một chỗ hỏng rồi bỏ đó. Trình tự `attack`, `defend`, `verify` là bắt buộc, và điểm chỉ tồn tại ở đầu bên kia.

Bước `attack` cho bạn thấy dữ liệu đi trần trên chặng phẳng, tức điểm yếu CWE-319 mà §3.3 gọi là chặng cuối. Bước `defend` buộc bạn đóng chặng ấy lại bằng TLS, rồi dựng thêm lớp thứ hai bằng mTLS. Bước `bon-phep-kiem` buộc bạn chứng minh cả hai lớp đang bật, bằng hai lần nối phải thành công và hai lần nối phải bị từ chối. Bài không có đường tắt bỏ qua phần vá, vì bộ chấm đọc trạng thái cuối chứ không đọc trạng thái đầu.

Sau khi nộp, chạy `make down`. Nó xóa container và mạng của bài. Máy bạn phải trở về đúng trạng thái trước buổi, trừ các tệp bằng chứng nằm trong kho.

Nếu bạn thấy mình đang đi sâu vào việc khai thác một lỗ hổng thay vì vá nó, bạn đã đi lạc sang học phần khác. Đó là dấu hiệu để dừng lại, không phải dấu hiệu để tự hào.

## 8. Khi bạn lỡ vượt phạm vi

Báo trong 24 giờ, trên Discussions của học phần hoặc bằng thư riêng cho giảng viên nếu việc nhạy cảm. Ghi lại lệnh đã chạy, thời điểm, và đích đã chạm tới. Báo cáo trung thực không bị xử lý nặng hơn việc che giấu, và điều ngược lại thì có. Đừng tự xóa nhật ký để cho gọn, vì nhật ký là thứ duy nhất chứng minh được rằng bạn dừng ở đâu.

## 9. Hệ quả học vụ

Theo quy chế học vụ hiện hành của UEH, cùng chính sách liêm chính của học phần. Trong bài này có một chỗ riêng cần nói thẳng, vì nó dễ bị coi là mẹo vặt: sửa tay một tệp trong `evidence/` là làm giả bằng chứng, không phải làm đẹp báo cáo. Tệp kết quả do máy sinh, băm của chúng nằm trong `SHA256SUMS`, và người chấm đọc nhật ký thô.

## 10. Hệ quả pháp lý

Trạng thái của mục này là **CHƯA XÁC MINH**, và bản dùng tạm dưới đây viết ở dạng nguyên tắc, không dẫn số hiệu điều khoản. Lý do ghi thẳng ra, vì nó cũng là một bài học của học phần: tới ngày soạn tài liệu, người soạn chưa đọc trực tiếp văn bản hợp nhất từ nguồn chính thức, và dẫn sai một điều luật trong một văn bản sinh viên ký là chuyện không được phép làm cho tiện. Số hiệu sẽ được bổ sung sau khi tra trên nguồn chính thức và ghi ngày truy cập.

Nguyên tắc thì không phụ thuộc vào việc tra cứu đó, và bạn cần nắm ngay từ hôm nay. Truy cập một hệ thống thông tin mà bạn không được phép truy cập là hành vi bị pháp luật Việt Nam điều chỉnh, kể cả khi không gây thiệt hại, kể cả khi bạn chỉ định thử. **Ranh giới không nằm ở chỗ bạn có gây thiệt hại hay không, mà nằm ở chỗ bạn có được phép hay không.** Một lần quét cho biết vào một hệ thống không phải của bạn đã nằm ngoài ranh giới rồi. Trong nghề, thứ tách một người kiểm thử với một người vi phạm không phải là kỹ năng, mà là một văn bản cho phép, ký trước khi gõ lệnh đầu tiên. Bài lab này là bản tập dượt của đúng văn bản ấy.

## 11. Xác nhận của sinh viên

```
Tôi đã đọc và hiểu văn bản phạm vi này, và tôi giữ đúng nó trong suốt bài lab.

Họ tên: Nguyễn Quốc Huy  Mã số: 31241027109

Ngày: 29/09/2026                   Ký: Nguyễn Quốc Huy
```

## 12. Phiên bản và băm

Phiên bản 1, thuộc lab `css-lab-S03-an-toan-mang`. Băm sha256 của chính tệp này nằm trong `evidence/S3/SHA256SUMS` sau khi bạn chạy `make export-evidence`, để bản bạn ký truy ngược được về đúng một phiên bản văn bản.

## Khi bạn không chắc

Hỏi trước, trên Discussions của học phần. Không ai bị trừ điểm vì hỏi một câu về ranh giới. Người ta chỉ mất nhiều thứ vì không hỏi.
