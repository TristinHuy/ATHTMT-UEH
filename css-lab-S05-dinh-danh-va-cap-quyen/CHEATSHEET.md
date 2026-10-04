# Thẻ tham chiếu, lab S5

Mười hai lệnh, mỗi lệnh một dòng nghĩa và một dòng hậu quả nếu gõ sai. In ra một trang, để cạnh máy.

| Lệnh | Nghĩa | Nếu gõ sai |
|---|---|---|
| `make preflight` | ghi máy, Python, trạng thái Docker vào `evidence/S5/preflight.txt` | không có tệp này thì một phép kiểm đỏ ngay, dù phần còn lại đúng |
| `make up` | dựng vùng định danh và dịch vụ, nạp tệp cấu hình lần đầu | chạy khi container cũ còn sống thì tệp cấu hình mới KHÔNG được nạp |
| `make down` | xóa container, mạng, và dữ liệu vùng định danh | xóa luôn tài khoản và bí mật một lần một mã đã ghi danh, phải ghi danh lại |
| `docker compose logs -f may-danh-tinh` | xem máy chủ danh tính khởi động tới đâu | thiếu bước này thì mọi lỗi cấu hình đều trông giống nhau, đều là "không nối được" |
| `docker compose logs -f dich-vu` | xem dịch vụ nói gì khi từ chối một tấm thẻ | câu trong `TheKhongHopLe` hiện ở đây, viết câu mơ hồ thì tự mình khó gỡ |
| `make attack` | gửi sáu yêu cầu vào dịch vụ đang ở chế độ khởi đầu | chạy sau khi đã viết `kiem_the` thì không còn trạng thái đầu để so |
| `make do-argon2 NHAN=truoc-khi-doi` | đo giá một lần đoán mật khẩu, ghi nối vào tệp đo | quên `NHAN` thì hai lần đo mang cùng một nhãn và không so được |
| `make defend` | dựng lại dịch vụ sau khi bạn sửa `kiem_the.py` | sửa tệp vùng định danh mà chỉ chạy lệnh này thì cấu hình cũ vẫn còn nguyên |
| `make nam-phep-kiem` | sáu lần gọi thật, sinh bằng chứng vào `evidence/S5` | chạy khi vùng định danh chưa sẵn sàng thì phép P1 đỏ và năm phép còn lại vô nghĩa |
| `make verify` | chạy đúng mười sáu phép kiểm mà bộ chấm chạy | bỏ qua bước này rồi nộp là cách phổ biến nhất để mất điểm dễ |
| `make export-evidence` | gom bằng chứng và ghi `SHA256SUMS` | thiếu tệp băm thì người chấm không đối chiếu được bản bạn nộp với bản máy sinh |
| `bash ghim-digest.sh --sua` | thay thẻ ảnh bằng digest thật, chạy trên máy có mạng | chạy trên máy không có mạng thì tập lệnh dừng và không sửa gì, đó là chủ ý |

## Bốn chỗ hay vấp, và câu trả lời ngắn

**Sửa `cau-hinh/vung-dinh-danh.json` xong mà không thấy gì đổi.** Việc nạp chỉ xảy ra lúc vùng định danh được dựng lần đầu. Chạy `make down` rồi `make up`.

**Tấm thẻ thật cũng bị hàm của bạn từ chối.** Đọc trường `aud` trong thẻ trước khi sửa hàm: `python3 -c "import base64,json,sys; p=sys.argv[1].split('.')[1]; print(json.loads(base64.urlsafe_b64decode(p+'==')))" <chuỗi thẻ>`. Nếu không thấy tên dịch vụ trong đó thì bộ ánh xạ tên người nhận đã bị xóa khỏi tệp cấu hình.

**`make nam-phep-kiem` treo rất lâu.** Nó đợi tấm thẻ hết hạn cho phép kiểm N3, và quãng đợi bằng đúng hạn thẻ bạn đặt. Đặt 60 giây trong lúc làm bài, rồi cân nhắc lại con số cuối cùng.

**Không xin được thẻ vì thiếu mã một lần.** Sau khi bật yếu tố thứ hai, luồng cấp trực tiếp cũng đòi mã ấy. Ghi bí mật vào `cau-hinh/totp-bi-mat.txt` và công cụ tự tính; tệp ấy không đi vào kho.
