# Thang chấm lab S6

Tổng 100 điểm, quy về 3 phần trăm điểm học phần. Máy chấm 60, người chấm 30, phần tái lập 10.

| Tiêu chí | Trọng số | Ai chấm | Tốt, 100% | Khá, 75% | Trung bình, 50% | Kém, 0% |
|---|---|---|---|---|---|---|
| Bộ kiểm tự động | 60 | Máy | Mười sáu phép kiểm xanh | Một tới hai phép đỏ | Ba tới năm phép đỏ | Từ sáu phép đỏ trở lên, hoặc không nộp |
| Bảng xếp loại cảnh báo, phần máy không đo được | 12 | Người | Mỗi dòng xếp đúng nhóm và ghi chú nói được dựa vào đâu; ranh giới giữa sửa bằng cấu hình và sửa bằng mã được rút ra từ chính báo cáo chứ không từ tên gọi của cảnh báo | Phần lớn xếp đúng, một hai dòng xếp theo tên cảnh báo mà chưa mở nội dung ra đọc | Khoảng một nửa số dòng có ghi chú chỉ nhắc lại tên cảnh báo, không nói được vì sao nhóm ấy chứ không phải nhóm kia | Xếp loại hàng loạt cho đủ bảng, hoặc bảng rõ ràng chưa đối chiếu với báo cáo nào |
| Hai lớp cho mỗi lỗ hổng, và lý do cần cả hai | 10 | Người | Nói được lớp nào chặn đường nào, và nói được vì sao một lớp không đủ; chọn mức SameSite kèm đánh đổi thật chứ không kèm một câu chung chung | Dựng đủ hai lớp nhưng lý do cần cả hai còn mượn nguyên câu của tài liệu | Dựng đủ hai lớp mà không phân biệt được lớp nào chặn gì | Chỉ dựng một lớp, hoặc dựng đủ hai lớp bằng cách chép cấu hình mà không đọc |
| Đoạn đánh đổi, và quyết định mức đầu tư | 8 | Người | Phép tính công sức đứng trên số phút đo được của chính mình, và câu trả lời về một giờ mỗi tuần chọn một việc cụ thể kèm lý do nó đáng hơn việc khác | Tính đúng nhưng căn cứ về số phút mỗi cảnh báo còn mơ hồ | Chỉ nhắc lại con số của bảng mà không tính ra hệ quả nào | Không có phép tính, hoặc đoạn văn không đứng trên bảng của chính mình |
| Tái lập được | 10 | Máy | `make verify` chạy xanh trên kho sạch mới nhân bản, không cần thao tác tay nào | Cần đúng một thao tác tay không ghi trong README | Cần nhiều thao tác tay | Không chạy được |

## Hai điều người chấm không trừ điểm

**Tỉ lệ p thấp, hoặc cao.** Con số ấy là con số của lần quét trên máy bạn, và nó thay đổi theo cả phiên bản bộ quét lẫn cách bạn đọc từng cảnh báo. Học phần này đo chất lượng của lập luận về đánh đổi, không đo con số. Một bài có p bằng 0,3 kèm ba ghi chú sắc đứng trên một bài có p bằng 0,8 kèm tám ghi chú chép lại tên cảnh báo.

**Xếp một cảnh báo khác với người chấm.** Ranh giới giữa ba nhóm có chỗ thật sự mờ, nhất là những cảnh báo đúng về một hệ thống chạy thật mà không áp dụng cho một phòng thí nghiệm chạy trên máy cục bộ. Điều được chấm là bạn có mở dòng ấy ra đọc rồi mới quyết hay không. Điều duy nhất bị trừ ở đây là xếp một dòng vào nhóm không phải cảnh báo thật mà không nói được dựa vào đâu.

## Hai điều bị trừ nặng

**Bằng chứng sửa tay.** Chép tệp báo cáo của lần quét trước thành lần quét sau, gõ thẳng một con số vào tệp kết xuất, hay dựng một dòng nhật ký cho khớp phép kiểm, tất cả đều là cùng một việc: làm giả phần mà máy không dựng lại được. Bộ chấm bắt được dạng thô nhất bằng cách so băm hai tệp báo cáo và bằng cách tính lại tỉ lệ p từ chính bảng của bạn, nhưng phần còn lại do người chấm đọc. Chỗ này rơi thẳng xuống mức Kém của cả bốn tiêu chí người chấm, kể cả khi mười sáu phép kiểm đều xanh.

**Vá bằng cách tắt chức năng.** Xóa chuỗi người dùng gõ vào thay vì mã hóa nó, hay từ chối mọi yêu cầu ghi cho chắc, đều đóng được lỗ hổng theo nghĩa hẹp và đều chuyển thiệt hại từ kẻ tấn công sang người dùng. Bộ chấm có một phép kiểm riêng cho chiều dương đúng vì lý do đó. Nếu phép ấy đỏ trong khi ba phép phòng thủ xanh, bài chưa đạt tiêu chí thứ ba dù bảng điểm máy trông gần đủ.

## Một chỗ nằm ngoài thang chấm

Trỏ bộ quét ra ngoài phạm vi cho phép không phải một mức điểm. Nó là vi phạm văn bản `SCOPE.md` mà bạn đã đọc và đã ký nhận, và nó được xử lý theo quy định về liêm chính học thuật của học phần chứ không theo bảng trên. Bộ chấm phát hiện được vì đích quét nằm cố định trong tệp compose và trong `Makefile`, và cả hai đều nằm trong kho bạn nộp.
