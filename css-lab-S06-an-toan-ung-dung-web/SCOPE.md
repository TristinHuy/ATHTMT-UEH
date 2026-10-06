# Phạm vi cho phép, bài S6

Văn bản chung của học phần vẫn áp dụng. Trang này nói phần riêng của bài này, và bài này là bài chặt nhất trong tám bài lab.

## Vì sao buổi này chặt hơn các buổi trước

Năm buổi trước bạn cấu hình những thứ chạy trên máy của chính bạn. Buổi này bạn cầm thêm một bộ quét web, tức một công cụ sinh ra để gửi hàng trăm yêu cầu vào một hệ thống rồi đọc lại phản hồi. Một bộ quét trỏ nhầm địa chỉ không phải là một lỗi gõ phím. Nó là một hành vi nhắm vào máy của người khác, và nó để lại dấu vết trong nhật ký của người ta đúng như một cuộc dò tìm thật.

Vì vậy đích của lần quét không nằm trong tay bạn lúc chạy. Nó nằm cố định ở dòng `command` của dịch vụ quét trong `docker-compose.yml`, viết bằng **tên dịch vụ** trong mạng compose, tức một cái tên chỉ phân giải được từ bên trong mạng ấy. Viết như vậy thì một lần gõ nhầm cũng không ra khỏi máy bạn. Bộ chấm đọc lại chính chỗ đó, và nó cũng đọc `Makefile` phòng khi đích bị chuyển sang dòng lệnh cho tiện.

## Bài S6 có đúng ba thao tác chạm tới lỗ hổng

Cả ba đều chạy trên ứng dụng thử nghiệm của chính bạn, ứng dụng do đề phát và do bạn sửa.

Thứ nhất, `make attack` gửi ba yêu cầu: một yêu cầu mang chuỗi thử vào trang tra cứu, một yêu cầu đổi địa chỉ mang gốc hợp lệ mà không mang thẻ, và một yêu cầu đổi địa chỉ mang thẻ thật mà đến từ một gốc lạ. Ba yêu cầu ấy đúng bằng ba yêu cầu bộ chấm gửi, không hơn.

Thứ hai, ở việc 5 bạn mở trình duyệt vào chính ứng dụng ấy trên `127.0.0.1` để thu một báo cáo vi phạm thật. Trình duyệt là một phần của phép đo, vì báo cáo vi phạm chỉ tồn tại khi có một trình duyệt thật áp chính sách.

Thứ ba, `make quet` chạy hai lần quét **nền**. Chế độ nền nghĩa là bộ quét đi qua trang và đọc thứ máy chủ trả về; nó không gửi tải trọng thử.

Không có thao tác thứ tư.

## Bạn được làm

- Tác động lên **các container trong mạng compose của chính bạn**, trên máy của chính bạn.
- Sửa, chạy lại, và phá hỏng ứng dụng thử nghiệm bao nhiêu lần tùy ý trước hạn nộp. Nó dựng ra để hỏng.
- Đọc mã nguồn của ứng dụng huấn luyện, và quét nền nó.

## Bạn không được làm

- **Trỏ bộ quét vào bất cứ địa chỉ nào không phải tên dịch vụ trong mạng compose của bạn.** Không địa chỉ IP, không tên miền, không địa chỉ của trường, không địa chỉ của bạn cùng lớp, kể cả khi bạn chỉ định thử một lần cho biết.
- **Chạy quét chủ động hay fuzzing.** Hai tập lệnh quét chủ động của cùng bộ công cụ gửi tải trọng thử vào ứng dụng, tức đã bước sang phần của học phần Kiểm thử thâm nhập. ADR-0003 cắt chúng khỏi buổi này, và bộ chấm kiểm điều đó.
- **Khai thác ứng dụng huấn luyện.** Nó có hàng chục lỗ hổng và một bảng thành tích mời bạn thử. Buổi này chỉ quét nền nó và xếp loại cảnh báo. Chuỗi khai thác nhiều bước, vượt bộ lọc, và viết tải trọng thuộc học phần Kiểm thử thâm nhập bạn học song song.
- **Lấy thẻ phiên của một tài khoản khác**, kể cả tài khoản do chính bạn tạo trên một hệ thống khác.
- **Mở cổng của hai ứng dụng ra mọi giao diện mạng.** Ứng dụng thử nghiệm neo vào `127.0.0.1` vì nó cố ý để hở; đổi sang `0.0.0.0` là cho cả mạng Wi-Fi bạn đang ngồi truy cập một ứng dụng bạn vừa dựng để hỏng.
- **Đưa dữ liệu cá nhân thật của bất cứ ai vào ứng dụng hay vào bằng chứng nộp lên.** Hồ sơ mẫu trong bài đã có sẵn tên và địa chỉ dựng ra cho việc này.

## Phần phòng thủ đi kèm

Mỗi lần một bài lab cho bạn thấy một cấu hình sai gây ra hậu quả gì, bài đó luôn yêu cầu bạn vá lại và chứng minh đã vá. Ở bài này phần phòng thủ là toàn bộ nội dung, không phải phần phụ, và nó nằm ở bốn chỗ.

Lớp thứ nhất của LH-1 là mã hóa đầu ra tại chỗ ghép, trong mã. Lớp thứ hai là chính sách nội dung, trong cấu hình, dựng với giả định lớp thứ nhất đã vỡ. Nửa thứ nhất của LH-2 là thuộc tính cookie, do trình duyệt áp. Nửa thứ hai là phép đối chiếu phía máy chủ, do bạn áp.

Bốn chỗ ấy đều bị bộ chấm kiểm bằng yêu cầu thật, và chiều dương cũng bị kiểm: một ứng dụng xóa sạch chữ người dùng gõ vào và từ chối mọi yêu cầu ghi thì qua được mọi phép kiểm phòng thủ mà đã hỏng theo một cách khác, cách mà người dùng chịu chứ không phải kẻ tấn công chịu.

Nếu bạn thấy mình đang tìm cách vượt qua chính sách nội dung thay vì dựng nó cho chặt, bạn đã đi lạc sang môn khác. Đó là dấu hiệu để dừng lại, không phải dấu hiệu để tự hào.

## Một chỗ riêng của bài này: bằng chứng mang dấu vết phiên

Báo cáo dạng HTML của một lần quét nhúng nguyên văn phần thân của những phản hồi mà bộ quét nhận được, gồm cả tiêu đề mang cookie phiên và cả chuỗi bạn đã gửi thử. Nó tiện để đọc và không tiện để nộp. Bản JSON đủ cho việc chấm và không mang phần ấy, nên `.gitignore` loại bản HTML khỏi kho và bài chỉ đòi bản JSON.

Nhật ký ứng dụng thì ngược lại, nó phải nộp, vì buổi S7 lấy nó làm một trong sáu nguồn. Trước khi đẩy lên, đọc lướt một lượt và tự hỏi trong đó có gì bạn không muốn người khác đọc hay không. Nhận ra một trường ghi rộng hơn mức cần là một phần của bài chứ không phải một lời thú nhận.

## Trách nhiệm pháp lý, viết ở dạng nguyên tắc

Trang này cố ý **không dẫn số hiệu điều luật nào**. Phán quyết B6 của ADR-0003 gỡ mọi trích dẫn luật khỏi văn bản phạm vi cho tới khi người soạn đọc được trực tiếp văn bản hợp nhất trên nguồn chính thức và ghi được ngày truy cập. Dẫn sai một điều luật trong một văn bản sinh viên phải ký là chuyện không được phép làm cho tiện.

Ba nguyên tắc dưới đây không phụ thuộc vào việc tra cứu đó, và bạn cần nắm ngay từ hôm nay.

**Ranh giới không nằm ở chỗ bạn có gây thiệt hại hay không, mà nằm ở chỗ bạn có được phép hay không.** Một lần quét cho biết vào một hệ thống không phải của bạn đã nằm ngoài ranh giới rồi, kể cả khi không có gì hỏng. Điều này đúng với mọi bộ quét, và đúng nhất với bộ quét web, vì nó là loại công cụ dễ chạy nhất trong tám buổi.

**Một công cụ chạy được không có nghĩa là bạn được chạy nó.** Bộ quét trong bài này không hỏi bạn có quyền với đích hay không, và không công cụ nào hỏi câu ấy. Câu ấy do người dùng công cụ trả lời trước khi bấm phím, và trách nhiệm đi theo câu trả lời đó.

**Thứ bạn học được ở đây dùng để dựng, không dùng để thử người khác.** Cùng một kiến thức về cách một trang bị chèn mã vừa cho phép bạn vá nó vừa cho phép bạn khai thác nó. Học phần này đo phần thứ nhất, và ranh giới giữa hai phần là ranh giới nghề nghiệp chứ không phải ranh giới kỹ thuật.

## Khi bạn không chắc

Hỏi trước, trên Discussions của học phần. Không ai bị trừ điểm vì hỏi một câu về ranh giới. Người ta chỉ mất nhiều thứ vì không hỏi.
