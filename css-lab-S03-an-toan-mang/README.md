# Lab S3. Cấu hình TLS đúng và chứng minh nó đúng

**Học phần An toàn hệ thống máy tính · Buổi 3 · Bài cá nhân · 3 phần trăm điểm học phần**

Hạn nộp: trước giờ buổi S4. Nộp trễ dưới 24 giờ nhận 75 phần trăm điểm đã chấm, trễ 24 tới 72 giờ nhận 50 phần trăm, sau 72 giờ nhận 0.

## Mục tiêu

Dựng một kênh có TLS và có xác thực hai chiều, rồi chứng minh cả hai lớp đang thật sự có hiệu lực.

Vế thứ hai mới là lý do bài này tồn tại. Bật TLS là việc của mười lăm phút, và phần lớn hướng dẫn trên mạng dừng lại ở đó: nối được, trình duyệt hiện ổ khóa, xong. Nhưng một ổ khóa chỉ nói rằng có mã hóa, nó không nói ai đang ở đầu kia, và §3.3 của giáo trình đã tách ba chỗ một cấu hình đúng thuật toán vẫn hỏng. Ba chỗ ấy đều không lộ ra khi bạn chỉ thử một lần nối thành công.

Cách duy nhất để biết một lớp phòng thủ đang bật là làm nó chuyển đỏ. Vì vậy bài này đòi bốn phép kiểm chia thành hai lớp, mỗi lớp một chiều dương và một chiều âm. Hai chiều âm là phần khó chấp nhận về mặt tâm lý, vì bạn phải cố ý làm hỏng thứ mình vừa dựng, và đó cũng là phần một bài nộp trung bình luôn thiếu.

## Việc phải làm

1. Nhận kho từ mẫu qua GitHub Classroom, rồi chạy `make preflight`. Lệnh này ghi kiến trúc máy, phiên bản Python, phiên bản openssl và trạng thái Docker vào `evidence/S3/preflight.txt`. Bài này cần cả Docker lẫn openssl, nên preflight hỏi cả hai.

2. Chạy `make up` rồi `make attack`. Máy chủ khởi đầu phục vụ trên kênh phẳng, và `make attack` chỉ làm một việc, là đọc thứ nó đang phát ra. Chuỗi hiện lên màn hình cũng là chuỗi mọi tiến trình khác trong cùng mạng đọc được. Giữ lại tệp `evidence/S3/truoc-khi-va.txt` để so với trạng thái cuối buổi.

3. Dựng **hai** tổ chức cấp chứng thư bằng `openssl`, và cấp ba chứng thư. Tổ chức nội bộ cấp chứng thư cho máy chủ và cho khách. Tổ chức thứ hai, gọi là CA ngoài, cấp một chứng thư khách nữa. Danh sách tệp và lý do có tổ chức thứ hai nằm ở `pki/README.md`. Tên tệp là một phần của đề, vì bộ kiểm đọc thẳng chúng.

4. Viết lại `nginx/may-chu.conf` để máy chủ phục vụ trên TLS 1.3, dùng chứng thư ở bước 3. Bỏ hẳn khối phục vụ trên cổng phẳng. Giữ nó lại cho tiện thử là tự tay để lại đúng chỗ hỏng thứ ba của §3.3, và bộ kiểm sẽ tìm nó trong tệp cấu hình chứ không đợi ai gọi tới cổng ấy.

5. Bật xác thực hai chiều, tức là buộc phía khách cũng phải trình chứng thư. Hai chỉ thị, và thiếu một trong hai thì lớp này không tồn tại. Đọc kỹ ba giá trị mà `ssl_verify_client` nhận được trước khi chọn.

6. Chạy `make defend` để nạp lại cấu hình, rồi `make bon-phep-kiem`. Bốn phép kiểm K1 tới K4 chạy từ container máy khách, và mỗi phép ghi ra hai tệp. Tệp `evidence/S3/kiem-K*.txt` là bản tóm tắt máy đọc được, thư mục `evidence/S3/tho/` giữ nhật ký thô cho người chấm. Phán quyết trong bản tóm tắt lấy từ mã thoát và dấu hiệu trong đầu ra, không lấy từ lời khai, nên bạn không tự gõ dòng kết quả.

| Phép | Lớp | Chiều | Nó chứng minh điều gì |
|---|---|---|---|
| K1 | TLS | dương | chứng thư máy chủ dựng ngược được về CA nội bộ, và tên trên chứng thư khớp tên bạn gọi |
| K2 | TLS | âm | gọi cùng máy chủ ấy bằng một tên khác thì bị từ chối, tức phép so tên đang chạy |
| K3 | mTLS | dương | có trình chứng thư khách thì đọc được nội dung |
| K4 | mTLS | âm | không trình chứng thư khách thì không đọc được gì |

7. Chạy `make quan-sat`. Công cụ `testssl.sh` nhìn máy chủ của bạn từ bên ngoài và không biết gì về ý định của bạn, nên nó là bậc bằng chứng thứ hai ở §3.5. Máy không chấm tệp này, người chấm đọc nó.

8. Viết `docs/danh-doi.md`, không quá ba trăm chữ. Nếu phải bỏ bớt một lớp phòng thủ vì chi phí vận hành thì bạn bỏ lớp nào, và bằng chứng nào cho thấy phần còn lại vẫn đứng? Phép tính vòng đời chứng thư ở §3.4 là chỗ bắt đầu, không phải chỗ kết thúc.

9. Chạy `make export-evidence` rồi `make verify`. Đẩy lên nhánh `main` trước hạn.

Phần thử thách, không tính điểm máy. `make thu-thach` chạy phép kiểm K5 với chứng thư khách do CA ngoài cấp: một chứng thư còn hạn, đúng cú pháp, ký hợp lệ. Nếu máy chủ của bạn nhận nó thì kho tin cậy của bạn rộng hơn bạn tưởng, và câu trả lời cho việc vì sao nên nằm trong đoạn ở bước 8.

## Sản phẩm phải nộp

```
nginx/may-chu.conf              cấu hình máy chủ, đã có TLS và mTLS
pki/                            hai tổ chức cấp chứng thư và ba chứng thư
docs/danh-doi.md                đoạn không quá ba trăm chữ
evidence/S3/preflight.txt       kết quả make preflight
evidence/S3/kiem-K1..K4.txt     bốn phán quyết máy đọc được
evidence/S3/tho/                nhật ký thô của bốn lần nối
evidence/S3/quan-sat-ngoai.txt  kết quả testssl.sh
evidence/S3/SHA256SUMS          băm của toàn bộ bằng chứng
```

Khóa riêng trong `pki/` nộp cùng bài, và điều đó chỉ đúng ở đây. Chúng không bảo vệ gì thật, còn người chấm cần dựng lại được chuỗi tin cậy của bạn. Ngoài lớp học thì khóa riêng không bao giờ đi vào một kho mã.

Mốc thời gian lấy theo dấu thời gian commit trên GitHub, không lấy theo lời khai.

## Máy chấm kiểm những gì

Chạy `make verify` để tự kiểm trước khi nộp. Bộ chấm chạy đúng mười sáu phép kiểm đó trong GitHub Actions, không thêm phép nào.

| Nhóm | Phép kiểm | Đạt khi |
|---|---|---|
| Phạm vi | ảnh ghim theo phiên bản cụ thể | không ảnh nào dùng thẻ trôi nổi |
| Phạm vi | không mở cổng ra ngoài máy | không có `ports`, hoặc mọi ánh xạ neo vào `127.0.0.1` |
| Phạm vi | không xin đặc quyền | không `privileged`, không `network_mode: host`, không `cap_add` |
| Chứng thư | CA nội bộ đúng là một CA | `ca.crt` mang `CA:TRUE` và tự xác minh được |
| Chứng thư | chứng thư máy chủ hợp lệ | dựng ngược được về `ca.crt`, và khóa riêng khớp chứng thư |
| Chứng thư | tên khớp tên dịch vụ | `subjectAltName` chứa `DNS:may-chu` |
| Chứng thư | hạn nằm trong khoảng cho phép | còn hiệu lực, và vòng đời không quá 400 ngày |
| Chứng thư | chứng thư khách hợp lệ | dựng ngược được về `ca.crt`, và khóa riêng khớp |
| Chứng thư | CA ngoài là một CA khác thật | chứng thư của nó dựng ngược được về chính nó, và không về `ca.crt` |
| Cấu hình | chỉ còn giao thức hiện hành | `ssl_protocols` có TLSv1.3 và không còn TLSv1, TLSv1.1, SSLv3 |
| Cấu hình | đòi chứng thư khách đúng cách | `ssl_verify_client on`, và `ssl_client_certificate` trỏ tới CA nội bộ |
| Cấu hình | không còn cổng phẳng | mọi `listen` đều có `ssl`, trừ khối chỉ chuyển hướng |
| Bằng chứng | preflight đủ mục | ghi đủ máy, Python, openssl, Docker, và daemon đang chạy |
| Bằng chứng | bốn phép kiểm đủ và đúng dạng | bốn tệp kết quả đủ khóa, mỗi tệp có nhật ký thô đi kèm |
| Bằng chứng | bốn kết quả đúng như mong đợi | hai chiều dương thành công, hai chiều âm bị từ chối |
| Bằng chứng | đoạn đánh đổi có và đủ dài | từ 120 tới 300 từ |

Hai dòng cuối bảng cần nói rõ giới hạn. Phép đếm từ của đoạn đánh đổi là một phép **xấp xỉ máy làm được**, không phải phép đo chất lượng lập luận: nó chặn được việc không nộp và việc nộp ba câu, nó không phân biệt được một lập luận sắc với một đoạn kể lại việc đã làm. Phần đó do người chấm đọc theo `rubric.md`. Kết quả của `make quan-sat` cũng không được máy chấm, vì đầu ra của `testssl.sh` đổi theo phiên bản và một phép kiểm bám vào chuỗi ký tự của công cụ khác sẽ hỏng vào lần công cụ ấy cập nhật.

## Tiêu chí đạt

Mười sáu phép kiểm xanh, **và** hai phép kiểm âm K2 và K4 thật sự bị từ chối chứ không phải chưa chạy. Một bài chỉ có chiều dương chứng minh được rằng hệ thống chưa hỏng theo một kiểu, chưa chứng minh được rằng lớp phòng thủ đang bật.

## Trước khi hỏi

Đọc `SCOPE.md`. Bài này có một bước tấn công thật, ở mức đọc thứ máy chủ đang phát ra trong mạng của chính bạn, nên ranh giới ở đó là ràng buộc chứ không phải lời khuyên.

Giáo trình §3.7 nhắc tới một lớp thứ ba dựng dưới cả TLS lẫn mTLS. Bài lab không dựng lớp ấy, vì nó cần module trong nhân hệ điều hành và quyền quản trị mạng trên máy thật, tức là vượt ra ngoài container của bạn. Câu hỏi mà lớp thứ ba trả lời được thì buổi S8 chạm lại từ phía chuỗi cung ứng.

Bài này dừng trước phần thu hồi chứng thư. Một chứng thư bị lộ trước hạn thì phép kiểm hạn ở trên không thấy gì cả, và chỗ trống ấy có mã riêng là CWE-299. Trả lời nó cần một dịch vụ tra trạng thái luôn sẵn sàng, tức thêm một thứ có thể hỏng, nên nó là một bài toán vận hành chứ không phải một dòng cấu hình. Giáo trình §3.8 để ngỏ đúng chỗ này.

Bước trinh sát bằng `nmap` mười phút đầu giờ làm tại lớp, trên mạng compose của chính bạn, và không chấm riêng. Nó ở đó để bạn thấy khoảng lệch giữa những cổng bạn nghĩ đang mở và những cổng thật sự mở.

Máy không chạy được thì báo **chậm nhất hai ngày trước buổi S4**, đừng đợi tới hạn nộp. Nếu `make bon-phep-kiem` báo lỗi kéo ảnh, chạy `bash ghim-digest.sh` trên máy có mạng trước, rồi thử lại.
