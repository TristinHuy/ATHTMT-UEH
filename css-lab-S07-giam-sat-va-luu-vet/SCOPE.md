# Phạm vi cho phép, bài S7

Văn bản chung của học phần vẫn áp dụng. Trang này nói phần riêng của bài này, và bài này có một chỗ đáng đọc kỹ hơn các buổi trước.

## Bài S7 có đúng một thao tác tấn công

Thao tác ấy là `make attack`. Nó gieo một dòng vào một tệp trong `nhat-ky/S07/` của bạn, đợi kho nhật ký nhận được, rồi **cắt cụt chính tệp ấy**, rồi hỏi lại kho xem dòng chữ còn không.

Ranh giới của nó, viết ra để không ai phải đoán.

- Tệp bị cắt cụt nằm trong thư mục bài làm của bạn, và nó do chính tập lệnh ấy tạo ra ở bước trước đó.
- Không có bước nào chạm tới nhật ký hệ thống của máy thật, tới `journald` của máy bạn, tới container của người khác, hay tới bất cứ tệp nào ngoài thư mục bài làm.
- Kỹ thuật tương ứng trong ATT&CK là T1685.006, xóa nhật ký hệ thống trên Linux. Bài này thực hiện nó ở mức vừa đủ để trả lời một câu hỏi về thiết kế, không đi sâu vào cách xóa cho sạch. Phần sâu thuộc học phần Kiểm thử thâm nhập mà bạn học song song.

Câu hỏi mà thao tác ấy trả lời: chặng chuyển có cứu được dòng chữ không, và cứu được kể từ lúc nào. Con số bạn thu về là bề rộng của khoảng thời gian dòng chữ mới chỉ tồn tại ở một nơi. Trong khoảng ấy, một lệnh xóa duy nhất là đủ để mất nó vĩnh viễn, và không cơ chế nào ở các bước sau cứu lại được.

## Bạn được làm

- Tác động lên **các container trong mạng compose của chính bạn**, trên máy của chính bạn.
- Đọc, chép, xóa các tệp trong thư mục bài làm của chính bạn.
- Thử lại bao nhiêu lần tùy ý trước hạn nộp.

## Bạn không được làm

- Chạy `make attack` hay bất cứ thao tác xóa nào **bên ngoài thư mục bài làm**. Cụ thể với bài này: không chạy nó với quyền quản trị của máy thật, không trỏ nó vào `/var/log`, và không gắn thêm thư mục nào của máy thật vào container.
- Quét, dò, thử đăng nhập, hay gửi lưu lượng bất thường tới **bất cứ hệ thống nào không phải của bạn**, gồm cả hệ thống của trường và của bạn cùng lớp.
- Mở cổng của kho nhật ký ra mọi giao diện mạng. Tệp compose cố ý không mở cổng nào cho nó, và bộ chấm kiểm điều đó.
- Đưa dữ liệu cá nhân thật của bất cứ ai vào nhật ký nộp lên.

## Phần phòng thủ đi kèm

Mỗi lần một bài lab cho bạn thấy một cấu hình sai gây ra hậu quả gì, bài đó luôn yêu cầu bạn vá lại và chứng minh đã vá. Ở bài này phần phòng thủ nằm ở ba chỗ, và cả ba đều bị bộ chấm kiểm.

Thứ nhất, thư mục nguồn gắn vào chặng chuyển ở chế độ chỉ đọc. Chặng đọc nhật ký mà ghi được vào nhật ký thì nó vừa chuyển tin vừa sửa được tin.

Thứ hai, kho giữ đứng sau một ranh giới mạng và không nhìn thấy thư mục nguồn. Việc của nó bắt đầu sau khi dòng chữ đã rời khỏi nơi sinh ra.

Thứ ba, hạn giữ do bạn đặt và bạn phải nói được vì sao chọn con số ấy. Giữ ngắn thì rẻ và mất câu trả lời; giữ dài thì tốn và tăng lượng dữ liệu cá nhân bạn phải chịu trách nhiệm.

Nếu bạn thấy mình đang đi sâu vào việc xóa dấu vết cho khéo thay vì rút ngắn khoảng nguy hiểm, bạn đã đi lạc sang môn khác. Đó là dấu hiệu để dừng lại, không phải dấu hiệu để tự hào.

## Một chỗ riêng của bài này: dữ liệu trong nhật ký

Nhật ký của năm buổi trước có thể chứa tên tài khoản, địa chỉ mạng, và ở buổi bốn còn chứa nguyên văn câu truy vấn kèm giá trị tham số. Đó là dữ liệu về hoạt động của chính bạn, nhưng nó tập thành một hồ sơ, và một hồ sơ thì có chủ.

Ba việc phải làm. Không đưa dữ liệu cá nhân thật của người khác vào nhật ký nộp lên. Không đẩy thư mục `nhat-ky/` lên kho, tệp `.gitignore` đã loại nó sẵn. Và khi viết `docs/duong-di-nhat-ky.md`, nói thẳng nếu bạn thấy một trường nào đó đang ghi rộng hơn mức cần; nhận ra chỗ ấy là một phần của bài chứ không phải một lời thú nhận.

## Trách nhiệm pháp lý, viết ở dạng nguyên tắc

Trang này cố ý **không dẫn số hiệu điều luật nào**. Phán quyết B6 của ADR-0003 gỡ mọi trích dẫn luật khỏi văn bản phạm vi cho tới khi người soạn đọc được trực tiếp văn bản hợp nhất trên nguồn chính thức và ghi được ngày truy cập. Dẫn sai một điều luật trong một văn bản sinh viên phải ký là chuyện không được phép làm cho tiện.

Ba nguyên tắc dưới đây không phụ thuộc vào việc tra cứu đó, và bạn cần nắm ngay từ hôm nay.

**Ranh giới không nằm ở chỗ bạn có gây thiệt hại hay không, mà nằm ở chỗ bạn có được phép hay không.** Một lần quét cho biết vào một hệ thống không phải của bạn đã nằm ngoài ranh giới rồi, kể cả khi không có gì hỏng.

**Xóa hoặc sửa dấu vết trên một hệ thống không phải của bạn là hành vi nặng hơn việc truy cập trái phép, chứ không nhẹ hơn.** Nó phá đúng thứ mà người khác dùng để biết chuyện gì đã xảy ra, nên nó gây thiệt hại cho cả những người không liên quan tới bạn. Bài này cho bạn làm thao tác ấy trên tệp của chính bạn, trong một môi trường dựng ra để hủy, và ngoài phạm vi ấy thì không.

**Nhật ký là dữ liệu về con người, không chỉ là dữ liệu về máy.** Thu, giữ, và chuyển nó đi đều là hành vi có người chịu ảnh hưởng. Nguyên tắc thực dụng: chỉ thu thứ bạn nói được là để trả lời câu hỏi nào, chỉ giữ trong thời gian bạn nói được là vì sao, và chỉ cho ai đọc mà bạn nói được là vì việc gì.

## Khi bạn không chắc

Hỏi trước, trên Discussions của học phần. Không ai bị trừ điểm vì hỏi một câu về ranh giới. Người ta chỉ mất nhiều thứ vì không hỏi.
