# Thang chấm lab S4

Tổng 100 điểm, quy về 3 phần trăm điểm học phần. Máy chấm 60, người chấm 30, phần tái lập 10.

| Tiêu chí | Trọng số | Ai chấm | Tốt, 100% | Khá, 75% | Trung bình, 50% | Kém, 0% |
|---|---|---|---|---|---|---|
| Bộ kiểm tự động | 60 | Máy | Cả mười sáu phép kiểm xanh | Một phép kiểm đỏ | Hai tới ba phép kiểm đỏ | Từ bốn phép kiểm đỏ trở lên, hoặc không nộp |
| Bảng vai trò, và riêng cột suy luận | 12 | Người | Mỗi vai trò ghi đúng phần nó cần và không hơn, và cột suy luận nêu được một thứ cụ thể vai trò ấy suy ra được mà không đọc thẳng, kèm đường suy ra | Bảng đúng, cột suy luận nêu được thứ suy ra nhưng không nói đường đi tới nó | Bảng chép lại danh sách quyền đã cấp, cột suy luận để trống hoặc viết chung chung | Không có bảng, hoặc bảng không khớp với tập lệnh SQL đã nộp |
| Đoạn đánh đổi ở `docs/danh-doi.md` | 10 | Người | Chọn một phép tách nhiệm vụ để bỏ, tính ra điểm hòa vốn bằng số có đơn vị, nêu biện pháp bù cụ thể, và thừa nhận biện pháp bù ấy yếu hơn ở chỗ nào | Có lựa chọn, có con số, nhưng biện pháp bù nói chung chung hoặc không nói phần yếu đi | Chỉ nêu lựa chọn, lý do dừng ở mức tốn công, không có con số | Không chọn gì, hoặc mô tả lại việc đã làm |
| Đọc lại chuỗi suy luận sau khi đã siết | 8 | Người | Chỉ ra rõ phần nào của `make attack` đã bị đóng và phần nào không, gọi đúng tên hai loại kiểm soát, và nói được vì sao loại thứ hai không đóng bằng cấp quyền | Nhận ra chuỗi suy luận vẫn chạy, giải thích ở mức mô tả | Nộp `suy-luan.txt` mà không bình luận gì | Không chạy |
| Tái lập được | 10 | Máy | `make up`, `make defend`, `make tam-truy-van`, `make verify` chạy xanh trên kho sạch mới nhân bản, không thao tác tay nào | Cần đúng một thao tác tay không ghi trong README | Cần nhiều thao tác tay | Không chạy được |

Bảng sau liệt kê sáu mã mà hai tiêu chí do người chấm đánh giá dùng để đối chiếu. Các mã chép từ `core/syllabus/mapping/S04-mapping.yaml`, lấy theo CWE List 4.20 và ATT&CK content v19.2, đọc ngày 18/08/2026.

| Mã | Chỗ nó nằm trong bài |
|---|---|
| T1213.006 | kỹ thuật cả buổi nhằm chặn; bảng vai trò là bản trả lời trực tiếp cho nó |
| T1078 | `khach_tam` ở bước `make attack`, một tài khoản hợp lệ mang sẵn quyền rộng |
| CWE-732 | quyền cấp sẵn cho `PUBLIC` và vai trò cấp rộng hơn nhu cầu; phép kiểm A1 |
| CWE-1220 | đơn vị cấp quyền quá thô, lý do tồn tại của an toàn mức hàng; phép kiểm A2 |
| CWE-566 | chỗ hỏng của cách lọc ở tầng ứng dụng; phép kiểm A3 |
| CWE-202 | rò rỉ qua chuỗi truy vấn thống kê; `make attack` và `make suy-luan` |

Lưu ý về cách chấm mã, để người chấm không đòi hỏi vượt mức tài liệu gốc cho phép. CWE-732 mang trạng thái ánh xạ ALLOWED-WITH-REVIEW chứ không phải ALLOWED, nên nó **không** phải câu trả lời đúng duy nhất cho ô cấp quyền quá rộng; một bài dẫn CWE-1220 cho cùng chỗ đó, kèm lập luận, vẫn đạt mức Tốt. CWE-269, mã có tên nghe khớp nhất với chuyện quản lý đặc quyền, không được tính là đáp án, vì trang gốc xếp nó vào diện không khuyến khích ánh xạ.

## Hai điều người chấm không trừ điểm

**Số lần sinh viên làm hỏng cơ sở dữ liệu rồi nạp lại.** Các sự cố như thu nhầm quyền tới mức không nối vào được, viết chính sách khóa luôn vai trò của chính mình, hay đặt sai một dòng trong `csdl/pgaudit.conf` khiến máy chủ không khởi động đều thuộc quá trình làm bài và không bị trừ điểm. `make up` đưa cơ sở dữ liệu về điểm xuất phát trong vài giây và được chạy không giới hạn số lần trước hạn nộp. Điểm được chấm trên trạng thái cuối và phần lập luận đi kèm.

**Chọn cách cài ràng buộc đơn giản hơn.** Ràng buộc người tạo khác người duyệt cài bằng một `CHECK` một dòng, và bài dùng `CHECK` không bị coi là làm ít hơn. Lý do là một ràng buộc đọc hiểu trọn vẹn ngay khi nhìn vào thì kiểm tra được trực tiếp, còn một cơ chế dài hơn cần thêm bằng chứng rằng nó đúng. Bộ chấm của phép kiểm A4 chỉ nhận thông báo vi phạm ràng buộc `CHECK`, nên một trigger tự báo lỗi sẽ bị xếp là lỗi khác và phép kiểm A4 đỏ. Phần mã vượt quá yêu cầu không được cộng điểm.

## Một điều bị trừ nặng

**Chữa đề thay vì chữa hệ thống.** Bài này có hai đường tắt cùng một bản chất. Đường thứ nhất là sửa tay một tệp trong `evidence/`, chẳng hạn gõ `thuc_te: LOI_QUYEN` vào một phép kiểm chưa bao giờ chạy. Đường thứ hai là xóa dòng `GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC` khỏi `sql/00-du-lieu.sql`; thao tác này làm phép kiểm quyền chuyển xanh mà không siết quyền nào.

Cả hai đường tắt đều sửa văn bản mô tả hệ thống thay vì sửa hệ thống, trong khi mục tiêu của bài là chứng minh chính sách có hiệu lực bằng một lần chạy thật bị chặn. Người chấm đối chiếu tám tệp kết quả với nhật ký thô và với `SHA256SUMS`, còn bộ chấm đọc lại tệp dữ liệu phát sẵn, nên cả hai đường tắt đều để lại dấu vết kiểm tra được.

Hậu quả: toàn bộ phần máy chấm và phần người chấm của bài về 0, và sự việc được xử lý theo chính sách liêm chính của học phần. Một bài trung thực còn hai phép kiểm đỏ vẫn được chấm bình thường theo thang ở trên, tức vẫn nhận 50 phần trăm của 60 điểm máy chấm.
