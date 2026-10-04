# Phạm vi cho phép, lab S5

Phiên bản 1. Văn bản này viết riêng cho bài S5 và thay cho văn bản phạm vi chung ở những chỗ hai văn bản khác nhau. Sinh viên đọc văn bản này trước khi chạy lệnh đầu tiên, và đọc lại mỗi khi định thử một thao tác mà mình chưa chắc có nằm trong phạm vi hay không.

## 1. Bài này học gì, và vì sao nó cần một văn bản phạm vi

Bài đo bốn chuẩn đầu ra. Phần tách ba câu hỏi mà chữ "đăng nhập" gộp lại đo CLO1.2. Việc cấu hình một vùng định danh và một chính sách cấp quyền đo CLO2.1, còn phần thu bằng chứng, gồm năm phép kiểm âm, đo CLO2.2. CLO3.1 gắn với việc tuân thủ chính văn bản này.

Bài này làm việc với hai loại dữ liệu mà các buổi trước chưa đụng tới: mật khẩu và tấm thẻ của một danh tính. Ngoài lớp học, chỉ một lần dùng nhầm một trong hai loại dữ liệu này cũng có thể làm mất quyền kiểm soát một tài khoản thật. Phạm vi của bài vì thế hẹp hơn bài S3, và có một quy định áp dụng cho chính sinh viên: tài khoản trong lab là tài khoản giả, không được thay bằng tài khoản thật của sinh viên ở bất kỳ dịch vụ nào.

## 2. Tài sản trong phạm vi

| Thứ | Định danh | Ghi chú |
|---|---|---|
| Máy chủ danh tính | container `css-s05-may-danh-tinh`, tên mạng `may-danh-tinh` | mở về `127.0.0.1:8080`, vì cần trình duyệt để ghi danh yếu tố thứ hai |
| Dịch vụ tài nguyên | container `css-s05-dich-vu`, tên mạng `dich-vu` | không lộ cổng nào ra máy thật |
| Chỗ đứng để đo | container `css-s05-cong-cu` | chỉ dựng lên khi một lệnh `make` cần tới, rồi xóa ngay sau lệnh đó |
| Mạng | mạng bridge `css-s05-labnet` | do compose của bài tạo ra và xóa đi |
| Tài khoản thử | `an-nv`, `binh-nv`, `chi-tdv`, và tài khoản quản trị đầu tiên | tài khoản giả, dựng riêng cho lab, không thuộc về ai |
| Bí mật một lần một mã | `cau-hinh/totp-bi-mat.txt` | nằm trên máy của sinh viên, không đi vào kho |

Vùng định danh là dịch vụ duy nhất của cả học phần được mở một cổng ra máy thật, và ngoại lệ ấy chỉ có hiệu lực khi cổng neo vào `127.0.0.1`. Bộ chấm đọc chính tệp compose để cưỡng chế điều đó.

## 3. Sinh viên được làm

- Dựng, sửa, làm hỏng và dựng lại ba container trên, không giới hạn số lần.
- Đăng nhập bằng ba tài khoản giả của bài, đổi mật khẩu của chúng, khóa chúng, mở lại.
- Dựng thẻ giả bằng công cụ của bài rồi gửi vào dịch vụ **của chính sinh viên**: thẻ khai thuật toán rỗng, thẻ ký bằng khóa do sinh viên tự sinh, thẻ đã quá hạn, thẻ phát cho thân khách khác.
- Đọc, giải mã phần thân, và in ra nội dung những tấm thẻ do vùng định danh của bài phát.
- Thử sai mật khẩu không giới hạn số lần trên vùng định danh của bài, kể cả để đo giới hạn số lần hỏi.
- Đọc tài liệu, đọc mã nguồn mở, đọc kho mã công khai được giới thiệu trong học phần.

## 4. Sinh viên không được làm

- Gửi thẻ, gửi yêu cầu đăng nhập, hay gửi bất kỳ gói tin nào tới một hệ thống không do chính sinh viên dựng trong bài. Điều này áp dụng cho cả máy của sinh viên cùng lớp, hạ tầng của UEH, của HCMUT, và mọi dịch vụ trên Internet.
- Lấy tấm thẻ của một dịch vụ thật mà sinh viên có tài khoản rồi đưa vào bài nộp, kể cả thẻ của chính mình. Mục 5.1 của giáo trình chỉ cho phép ĐỌC thẻ của chính mình trên dịch vụ mình có quyền dùng.
- Dùng mật khẩu thật, thư điện tử thật, số điện thoại thật, hay bí mật một lần một mã thật của bất kỳ ai, kể cả của chính sinh viên, làm dữ liệu thử.
- Commit `cau-hinh/totp-bi-mat.txt`, hoặc bất kỳ bí mật nào khác, vào kho.
- Thử bẻ khóa mật khẩu ở quy mô lớn, hoặc chạy bộ thông tin đăng nhập rò rỉ vào bất cứ đâu. Việc này thuộc học phần Kiểm thử thâm nhập; bài này chỉ giải thích vì sao chính sách xoay vòng mật khẩu không chặn được kiểu tấn công đó.
- Gửi dồn dập yêu cầu xác thực tới một người thật để xem họ có bấm chấp nhận nhầm hay không. Kỹ thuật này có mã ATT&CK T1621; bài này chặn nó bằng cấu hình chứ không thực hiện nó.
- Thêm `privileged`, `network_mode: host`, hoặc `cap_add` vào tệp compose. Bộ chấm đọc chính tệp ấy và đánh trượt nếu thấy.
- Đưa mã khai thác lấy từ nguồn công khai vào bài nộp.

## 5. Kỹ thuật bài này chạm tới, và mức chạm

Bốn mã dưới đây lấy từ bản ATT&CK content v19.2, đọc ngày 18/08/2026. Bài chạm tới cả bốn từ phía phòng thủ, và không thực hiện kỹ thuật nào trong số đó.

| Mã | Tên | Bài này làm gì với nó |
|---|---|---|
| T1110.004 | Credential Stuffing | là lý do §5.3 bác chính sách xoay vòng mật khẩu; bài không chạy kỹ thuật này |
| T1621 | Multi-Factor Authentication Request Generation | là thứ mà giới hạn số lần hỏi ở việc 5 nhằm chặn |
| T1552.001 | Credentials In Files | là lý do bí mật một lần một mã không đi vào kho |
| T1550.001 | Application Access Token | là hiện tượng ở §5.1, và là thứ năm phép kiểm âm đo |

Sáu mã điểm yếu của bài, lấy từ CWE List 4.20 đọc cùng ngày: CWE-256 và CWE-257 cho hai cách lưu mật khẩu sai, CWE-916 cho hàm băm nhanh, CWE-347 cho hai phép kiểm âm đầu, CWE-613 cho phép thứ ba, CWE-863 cho hai phép cuối. Hạng mục OWASP tương ứng là A01:2025, A04:2025 và A07:2025, bản Top 10 năm 2025.

Ranh giới của buổi, chép nguyên từ bảng ranh giới của học phần. Học phần này dạy cấu hình định danh, xác thực nhiều yếu tố, và cấp quyền theo vai, ở mức vận hành. Việc tấn công giao thức xác thực, đánh cắp phiên trên hệ thống thật, và bẻ khóa mật khẩu quy mô lớn thuộc học phần Kiểm thử thâm nhập, học song song trong cùng học kì. Việc dựng lại dòng thời gian một vụ chiếm tài khoản từ nhật ký thuộc học phần Phản ứng với sự cố và điều tra số. Cách trình duyệt giữ thẻ thuộc buổi S6.

## 6. Cửa sổ thời gian

Phạm vi này có hiệu lực từ khi sinh viên nhận bộ khung lab tới khi bài được chấm xong. Mốc viết theo buổi, không theo ngày dương lịch. Học liệu và môi trường sẵn sàng từ trước buổi S5 hai ngày; hạn nộp là 23:59 hôm trước buổi S6, ngày cụ thể ghi ở Master Hub.

## 7. Nghĩa vụ khôi phục và phần phòng thủ đi kèm

Bài này không dừng ở việc chỉ ra một chỗ hỏng. Trình tự `attack`, `defend`, `verify` là bắt buộc, và điểm chỉ được tính trên trạng thái sau cùng của trình tự này.

Bước `attack` gửi các yêu cầu thử vào dịch vụ khi chưa có phép kiểm nào, và cho thấy tấm thẻ hỏng được dịch vụ chấp nhận. Bước `defend` đóng bốn đường mà thẻ hỏng đi qua, cộng đường thứ năm ở tầng cấp quyền. Bước `nam-phep-kiem` chứng minh cả năm đường đã đóng, với năm lần gọi phải bị từ chối và một lần gọi phải được phục vụ. Bài không có đường tắt bỏ qua phần vá, vì bộ chấm đọc trạng thái cuối chứ không đọc trạng thái đầu.

Sau khi nộp, sinh viên chạy `make down` để xóa container, mạng và dữ liệu vùng định danh. Máy của sinh viên phải trở về đúng trạng thái trước buổi, trừ các tệp bằng chứng nằm trong kho.

Nếu công việc chuyển từ vá lỗ hổng sang khai thác lỗ hổng, sinh viên đã ra khỏi phạm vi của học phần này và cần dừng lại.

## 8. Khi lỡ vượt phạm vi

Sinh viên báo trong 24 giờ, trên Discussions của học phần, hoặc bằng thư riêng cho giảng viên nếu sự việc nhạy cảm. Nội dung báo gồm lệnh đã chạy, thời điểm chạy và đích đã chạm tới. Theo chính sách của học phần, một trường hợp được báo cáo trung thực không bị xử lý nặng hơn một trường hợp che giấu, còn trường hợp che giấu thì có thể bị xử lý nặng hơn. Nhật ký không được tự ý xóa, vì nhật ký là bằng chứng duy nhất cho biết sinh viên đã dừng ở đâu.

Bài này có một trường hợp riêng: nếu sinh viên lỡ commit một bí mật, xóa tệp ở lần commit sau là chưa đủ, vì bí mật đã vào lịch sử kho thì vẫn còn trong lịch sử đó. Sinh viên báo ngay, coi bí mật đó là đã lộ, rồi ghi danh lại yếu tố thứ hai để có bí mật mới. Buổi S8 dựng lại đúng tình huống này bằng công cụ dò bí mật trong lịch sử kho.

## 9. Hệ quả học vụ

Áp dụng quy chế học vụ hiện hành của UEH và chính sách liêm chính của học phần. Bài này có một trường hợp cần nêu riêng: sửa tay một tệp trong `evidence/` là làm giả bằng chứng. Sáu tệp kết quả do máy sinh và phán quyết trong đó tính từ mã HTTP thật; băm của chúng nằm trong `SHA256SUMS`, và người chấm đối chiếu chúng với nhật ký thô.

## 10. Hệ quả pháp lý

Trạng thái của mục này là **CHƯA XÁC MINH**, và bản dùng tạm dưới đây viết ở dạng nguyên tắc, không dẫn số hiệu điều khoản. Lý do được ghi rõ, vì bản thân nó cũng là một nội dung của học phần: tới ngày soạn tài liệu, người soạn chưa đọc trực tiếp văn bản hợp nhất từ nguồn chính thức, và dẫn sai một điều luật trong một văn bản sinh viên ký là sai sót không thể chấp nhận. Số hiệu sẽ được bổ sung sau khi tra trên nguồn chính thức và ghi ngày truy cập.

Nguyên tắc sau không phụ thuộc vào việc tra cứu đó và có hiệu lực ngay. Truy cập một hệ thống thông tin khi không được phép là hành vi bị pháp luật Việt Nam điều chỉnh, kể cả khi không gây thiệt hại và kể cả khi người truy cập chỉ định thử. **Ranh giới được xác định bởi việc có được phép hay không, không phải bởi việc có gây thiệt hại hay không.**

Bài này có thêm một nguyên tắc thứ hai, vì bài làm việc với danh tính. Dữ liệu định danh của người khác được pháp luật bảo vệ riêng, và mức bảo vệ đó không phụ thuộc vào mục đích sử dụng dữ liệu. Vì vậy bài lab không cho phép đăng nhập vào tài khoản của người khác, kể cả khi người đó đã đưa mật khẩu, và không cho phép giữ lại tấm thẻ của người khác để thử. Trong nghề kiểm thử, người kiểm thử và người vi phạm được phân biệt bằng một văn bản cho phép ký trước khi chạy lệnh đầu tiên, và văn bản phạm vi này đóng vai trò đó trong bài lab.

## 11. Xác nhận của sinh viên

```
Tôi đã đọc và hiểu văn bản phạm vi này, và tôi giữ đúng nó trong suốt bài lab.

Họ tên: ......................................  Mã số: ....................

Ngày: ......../......../2026                   Ký: ........................
```

## 12. Phiên bản và băm

Phiên bản 1, thuộc lab `css-lab-S05-dinh-danh-va-cap-quyen`. Băm sha256 của chính tệp này nằm trong `evidence/S5/SHA256SUMS` sau khi chạy `make export-evidence`, để bản sinh viên ký truy ngược được về đúng một phiên bản văn bản.

## Khi chưa chắc về phạm vi

Sinh viên hỏi trước trên Discussions của học phần. Câu hỏi về ranh giới phạm vi không bị trừ điểm.
