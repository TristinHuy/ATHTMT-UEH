# Phạm vi cho phép, lab S4

Phiên bản 1. Văn bản này viết riêng cho bài S4 và thay cho văn bản phạm vi chung ở những chỗ hai văn bản khác nhau. Sinh viên đọc văn bản này trước khi chạy lệnh đầu tiên, và đọc lại mỗi khi định thử một thao tác mà mình chưa chắc có nằm trong phạm vi hay không.

## 1. Bài này học gì, và vì sao nó cần một văn bản phạm vi

Bài đo năm chuẩn đầu ra. Phần phân biệt kiểm soát truy nhập với kiểm soát suy luận, tức phân biệt thứ bài này đóng được với thứ nó không đóng được, đo CLO1.2. Đoạn tính chi phí tách nhiệm vụ đo CLO1.3. Bộ vai trò và chính sách mà sinh viên dựng đo CLO2.1, còn phần thu bằng chứng, mà riêng ở bài này là năm bằng chứng âm, đo CLO2.2. CLO3.1 gắn với việc tuân thủ chính văn bản này.

Bài này có một bước tác động thật, ở mức nhẹ hơn nhiều so với điều chữ "tấn công" gợi ra. `make attack` chạy ba câu truy vấn **hợp lệ**, bằng một tài khoản **có thật trong cơ sở dữ liệu của sinh viên**, và không khai thác lỗi phần mềm nào. Chính điểm này là nội dung cần học: hai trong ba câu không vi phạm quy tắc nào, nhưng ghép lại vẫn để lộ lương tháng của một cá nhân. Ví dụ này cho thấy rò rỉ trong cơ sở dữ liệu có thể đến từ một chuỗi câu lệnh bình thường được ghép với nhau, không cần tới một câu lệnh bất thường nào.

Vì các câu lệnh ở đây trông vô hại, ranh giới cần được viết thành văn bản. Cùng câu `SELECT` đó, nếu chạy trên một cơ sở dữ liệu không thuộc quyền quản lý của sinh viên, là truy cập khi không được phép, dù câu lệnh không đổi một ký tự nào.

## 2. Tài sản trong phạm vi

| Thứ | Định danh | Ghi chú |
|---|---|---|
| Máy chủ cơ sở dữ liệu | container `css-s04-csdl`, tên mạng `csdl` | PostgreSQL cộng pgaudit, dựng tại chỗ từ `csdl/Dockerfile` |
| Máy khách | container `css-s04-may-khach` | chạy theo từng lượt hỏi, không chạy nền |
| Mạng | mạng bridge `css-s04-labnet` | do compose của bài tạo ra và xóa đi |
| Cơ sở dữ liệu | `css_s04` | dựng lại được bằng `make up` bất cứ lúc nào |
| Tài khoản thử | `postgres`, `khach_tam`, và bốn vai trò sinh viên dựng | mật khẩu lab `lab2026`, ghi trong tệp compose |
| Dữ liệu thử | mười hai dòng nhân sự, năm đề nghị chi | dữ liệu dựng riêng cho học phần, không tên thật, không lương thật |

Không cổng nào của bài lộ ra máy thật, và đó là thiết kế có chủ ý: tám phép kiểm đều chạy từ bên trong mạng compose. Cổng 5432 mở ra mọi giao diện mạng là một cấu hình sai thường gặp trong các sự cố cơ sở dữ liệu bị đọc trộm, nên bài này không dùng cấu hình đó, kể cả khi nó tiện cho việc thử.

Mật khẩu `lab2026` nằm trong tệp compose để bài tái lập được. Ngoài lớp học, một mật khẩu nằm trong kho mã chính là loại lỗi mà buổi S8 dùng `gitleaks` để tìm, và ngoại lệ ở bài này chỉ áp dụng cho mật khẩu lab, không áp dụng cho bất kỳ mật khẩu thật nào.

## 3. Sinh viên được làm

- Dựng, sửa, phá và dựng lại hai container trên, bao nhiêu lần tùy ý.
- Chạy `make attack`, tức chạy ba câu truy vấn hợp lệ bằng `khach_tam` trên cơ sở dữ liệu của chính sinh viên.
- Nối vào `csdl` bằng `psql` với bất kỳ vai trò nào của bài, và chạy bất kỳ câu SQL nào trên cơ sở dữ liệu `css_s04`.
- Dựng thêm vai trò, thêm chính sách, thêm ràng buộc, kể cả những thứ dựng ra để bị từ chối.
- Xóa sạch cơ sở dữ liệu rồi nạp lại bằng `make up`.
- Đọc tài liệu, đọc mã nguồn mở, đọc kho mã công khai được giới thiệu trong học phần.

## 4. Sinh viên không được làm

- Nối tới bất kỳ máy chủ cơ sở dữ liệu nào không do chính sinh viên dựng trong bài, dù chỉ một lần để thử. Điều này áp dụng cho cả máy của sinh viên cùng lớp và hạ tầng của UEH, của HCMUT, của GitHub.
- Gửi gói tin tới bất kỳ đích nào ngoài `127.0.0.1` và mạng `css-s04-labnet` của chính sinh viên.
- Quét cổng, dò tài khoản, hoặc thử mật khẩu trên bất cứ dịch vụ nào ngoài bài lab của mình.
- Dùng dữ liệu nhân sự, lương, hoặc dữ liệu cá nhân thật của bất kỳ ai làm dữ liệu mẫu. Dữ liệu dựng sẵn của bài đủ cho mọi yêu cầu của đề, còn một bảng lương thật đưa vào kho mã lớp học là một sự cố lộ dữ liệu cá nhân.
- Đưa vào bài nộp bất kỳ đoạn khai thác nào lấy từ nguồn công khai.
- Thêm `privileged`, `network_mode: host`, hoặc `cap_add` vào tệp compose. Bộ chấm đọc chính tệp ấy và đánh trượt nếu thấy.
- Tấn công từ chối dịch vụ dưới mọi hình thức, gồm cả việc cố ý làm cạn kết nối hoặc cạn đĩa của máy chủ.

## 5. Kỹ thuật bài này chạm tới, và mức chạm

Bốn mã ATT&CK và sáu mã CWE dưới đây lấy từ `core/syllabus/mapping/S04-mapping.yaml`, nơi chúng đã qua một lượt tra nguồn. Bản ATT&CK là content v19.2, bản CWE là 4.20, cùng đọc ngày 18/08/2026. Bài chạm tới chúng từ phía phòng thủ.

| Mã | Tên | Bài này làm gì với nó |
|---|---|---|
| T1213.006 | Databases | kỹ thuật chính mà cả buổi nhằm chặn; biện pháp giảm nhẹ đầu tiên trên trang gốc là đặc quyền tối thiểu, đúng bước 4 của đề |
| T1078 | Valid Accounts | `khach_tam` ở `make attack` là một tài khoản hợp lệ đã mang sẵn quyền rộng; bước tách vai trò thu hẹp đúng phạm vi đó |
| T1040 | Network Sniffing | tham số `sslmode` mặc định là `prefer`, nên một phiên có thể lặng lẽ chạy trên kênh phẳng; bài chạm ở mức nhắc tên, phần cấu hình kênh đã làm ở buổi S3 |
| T1190 | Exploit Public-Facing Application | chỉ nhắc tên, không thực hiện; nó có mặt để nói vì sao vai trò cấp rộng biến một lỗi ứng dụng thành mất trọn bảng |

| Mã | Tên | Chỗ nó nằm trong bài |
|---|---|---|
| CWE-202 | Exposure of Sensitive Information Through Data Queries | ba câu ở `make attack` và tệp `suy-luan.txt` |
| CWE-1220 | Insufficient Granularity of Access Control | lý do tồn tại của an toàn mức hàng; phép kiểm A2 |
| CWE-566 | Authorization Bypass Through User-Controlled SQL Primary Key | chỗ hỏng của cách lọc ở tầng ứng dụng; phép kiểm A3 |
| CWE-732 | Incorrect Permission Assignment for Critical Resource | quyền cấp sẵn cho `PUBLIC` và vai trò cấp rộng hơn nhu cầu; phép kiểm A1 |
| CWE-778 | Insufficient Logging | phần `pgaudit`, và riêng vế "ghi mà thiếu chi tiết" |
| CWE-319 | Cleartext Transmission of Sensitive Information | tham số `sslmode`, nối về buổi S3 |

Một mã đã được cân nhắc và không được gán cho bài này. CWE-269 Improper Privilege Management nghe rất khớp với chuyện cấp quyền quá rộng, nhưng trang gốc xếp nó vào diện không khuyến khích dùng để ánh xạ, vì mã này hay bị hiểu sai, và khuyến nghị dùng các mã con cụ thể hơn. Bảng đối chiếu của học phần chọn mã theo khuyến nghị ánh xạ của trang gốc chứ không theo độ khớp của tên gọi.

Ranh giới của buổi, chép nguyên từ bảng ranh giới của học phần. Học phần này dạy phân quyền tối thiểu, an toàn mức hàng, và lưu vết truy cập cơ sở dữ liệu. Việc khai thác tiêm câu lệnh SQL ở mức nâng cao và trích xuất dữ liệu quy mô lớn thuộc học phần Kiểm thử thâm nhập. Việc dựng lại dòng thời gian một sự cố từ nhật ký và thu thập chứng cứ dùng được về sau thuộc học phần Phản ứng với sự cố và điều tra số; bài này dừng ở chỗ nhật ký đã thu đúng, đủ, và đọc được.

## 6. Cửa sổ thời gian

Phạm vi này có hiệu lực từ khi sinh viên nhận bộ khung lab tới khi bài được chấm xong. Mốc viết theo buổi, không theo ngày dương lịch. Học liệu và môi trường sẵn sàng từ trước buổi S4 hai ngày; hạn nộp là 23:59 hôm trước buổi S5, ngày cụ thể ghi ở Master Hub.

## 7. Nghĩa vụ khôi phục và phần phòng thủ đi kèm

Bài này không dừng ở việc chỉ ra một chỗ hỏng. Trình tự `attack`, `defend`, `verify` là bắt buộc, và điểm chỉ được tính trên trạng thái sau cùng của trình tự này.

Bước `attack` cho thấy một tài khoản cũ đọc thẳng được bảng lương, tức điểm yếu CWE-732 mà mục 4.3 gọi là mặc định quá rộng. Bước `defend` đóng đường này bằng cách thu quyền của `PUBLIC` và dựng lại bộ vai trò. Bước `tam-truy-van` chứng minh cả năm lớp đang bật, với năm lần chạy phải bị chặn và ba lần chạy phải thành công. Bài không có đường tắt bỏ qua phần vá, vì bộ chấm đọc trạng thái cuối chứ không đọc trạng thái đầu.

Một phần của bước `attack` **không** đóng được bằng các biện pháp của bài, và đề bài nêu rõ điều này. Chuỗi truy vấn thống kê vẫn để lộ đúng con số cũ sau khi siết quyền, và `make suy-luan` chạy lại chuỗi đó để sinh viên đối chiếu. Phân quyền vẫn là biện pháp đúng trong trường hợp này; rủi ro chỉ xuất hiện khi người vận hành cho rằng phân quyền đã chặn được cả rò rỉ qua suy luận.

Sau khi nộp, sinh viên chạy `make down` để xóa container, mạng và ổ đĩa dữ liệu của bài. Máy của sinh viên phải trở về đúng trạng thái trước buổi, trừ các tệp bằng chứng nằm trong kho.

Nếu công việc chuyển từ siết quyền sang trích xuất dữ liệu, sinh viên đã ra khỏi phạm vi của học phần này và cần dừng lại.

## 8. Khi lỡ vượt phạm vi

Sinh viên báo trong 24 giờ, trên Discussions của học phần, hoặc bằng thư riêng cho giảng viên nếu sự việc nhạy cảm. Nội dung báo gồm lệnh đã chạy, thời điểm chạy và đích đã chạm tới. Theo chính sách của học phần, một trường hợp được báo cáo trung thực không bị xử lý nặng hơn một trường hợp che giấu, còn trường hợp che giấu thì có thể bị xử lý nặng hơn. Nhật ký không được tự ý xóa, vì nhật ký là bằng chứng duy nhất cho biết sinh viên đã dừng ở đâu.

## 9. Hệ quả học vụ

Áp dụng quy chế học vụ hiện hành của UEH và chính sách liêm chính của học phần. Bài này có hai trường hợp cần nêu riêng, vì cả hai dễ bị xem là thao tác vô hại. Sửa tay một tệp trong `evidence/` là làm giả bằng chứng. Sửa `sql/00-du-lieu.sql` để bỏ dòng cấp quyền rộng là làm giả hiện trạng được bàn giao, vì hệ thống không thay đổi mà chỉ văn bản mô tả nó thay đổi.

## 10. Hệ quả pháp lý

Trạng thái của mục này là **CHƯA XÁC MINH**, và bản dùng tạm dưới đây viết ở dạng nguyên tắc, không dẫn số hiệu điều khoản. Lý do được ghi rõ, vì bản thân nó cũng là một nội dung của học phần: tới ngày soạn tài liệu, người soạn chưa đọc trực tiếp văn bản hợp nhất từ nguồn chính thức, và dẫn sai một điều luật trong một văn bản sinh viên ký là sai sót không thể chấp nhận. Số hiệu sẽ được bổ sung sau khi tra trên nguồn chính thức và ghi ngày truy cập.

Nguyên tắc sau không phụ thuộc vào việc tra cứu đó và có hiệu lực ngay. Truy cập một hệ thống thông tin khi không được phép là hành vi bị pháp luật Việt Nam điều chỉnh, kể cả khi không gây thiệt hại và kể cả khi người truy cập chỉ định thử. Với dữ liệu cá nhân còn một tầng điều chỉnh riêng: việc thu thập, sao chép và sử dụng thông tin cá nhân của người khác khi không được phép bị điều chỉnh độc lập với phần quy định về truy cập hệ thống.

Điểm cốt lõi của mục này là **ranh giới được xác định bởi việc có được phép hay không, không phải bởi việc câu lệnh có bất thường hay không.** Ba câu truy vấn ở bước 3 đều hợp lệ và đều nằm trong quyền hạn của tài khoản đang chạy, nhưng trên một hệ thống không thuộc quyền quản lý của sinh viên thì việc chạy chúng vẫn nằm ngoài ranh giới. Trong nghề kiểm thử, người kiểm thử và người vi phạm được phân biệt bằng một văn bản cho phép ký trước khi chạy lệnh đầu tiên, và văn bản phạm vi này đóng vai trò đó trong bài lab.

## 11. Xác nhận của sinh viên

```
Tôi đã đọc và hiểu văn bản phạm vi này, và tôi giữ đúng nó trong suốt bài lab.

Họ tên: ......................................  Mã số: ....................

Ngày: ......../......../2026                   Ký: ........................
```

## 12. Phiên bản và băm

Phiên bản 1, thuộc lab `css-lab-S04-an-toan-co-so-du-lieu`. Băm sha256 của chính tệp này nằm trong `evidence/S4/SHA256SUMS` sau khi chạy `make export-evidence`, để bản sinh viên ký truy ngược được về đúng một phiên bản văn bản.

## Khi chưa chắc về phạm vi

Sinh viên hỏi trước trên Discussions của học phần. Câu hỏi về ranh giới phạm vi không bị trừ điểm.
