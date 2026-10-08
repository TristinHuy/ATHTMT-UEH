# Thang chấm lab S7

Tổng 100 điểm, quy về 3 phần trăm điểm học phần. Máy chấm 60, người chấm 30, phần tái lập 10.

| Tiêu chí | Trọng số | Ai chấm | Tốt, 100% | Khá, 75% | Trung bình, 50% | Kém, 0% |
| --- | --- | --- | --- | --- | --- | --- |
| Bộ kiểm tự động | 60 | Máy | Mười sáu phép kiểm xanh | Một tới hai phép đỏ | Ba tới năm phép đỏ | Từ sáu phép đỏ trở lên, hoặc không nộp |
| Bảng năm sự kiện, phần máy không đo được | 14 | Người | Năm câu truy vấn đều thật sự khoanh đúng sự kiện, đọc câu là biết nó lọc theo dấu hiệu nào và vì sao dấu hiệu ấy phân biệt được sự kiện với nền | Bốn câu chắc chắn, một câu rộng tới mức nó khoanh trúng nhiều thứ khác cùng lúc | Khoảng một nửa số câu chỉ lọc theo một chuỗi con dễ trùng, không neo vào trường nào | Câu truy vấn chép từ bản mẫu, hoặc rõ ràng chưa từng được chạy |
| Dòng không tìm được, và cách gọi tên loại im lặng | 8 | Người | Nói rõ đã thử tới đâu, phân biệt được ba loại im lặng bằng bằng chứng chứ không bằng phỏng đoán, và nêu việc phải làm để lần sau tìm được | Gọi đúng loại nhưng lập luận dựa vào cảm nhận, không dẫn được câu truy vấn đã thử | Gọi tên một loại mà không giải thích vì sao không phải hai loại kia | Điền cho có, hoặc khai không tìm được ở một dòng mà thực ra chưa thử |
| Quy tắc phát hiện, và đoạn văn về giá của báo nhầm | 8 | Người | Điều kiện của quy tắc phản ánh một hiểu biết về hành vi, mục `falsepositives` mô tả đúng nguồn báo nhầm đã đo, và phép tính phút công có căn cứ đo được chứ không phải con số đoán | Quy tắc hợp lý, đoạn văn tính đúng nhưng căn cứ về thời gian mỗi lần xử lý còn mơ hồ | Quy tắc vừa đủ qua ngưỡng bằng cách loại trừ từng trường hợp, đoạn văn chỉ nhắc lại con số mà không tính ra hệ quả | Không có quy tắc của riêng mình, hoặc đoạn văn không đứng trên số đã đo |
| Tái lập được | 10 | Máy | `make verify` chạy xanh trên kho sạch mới nhân bản, không cần thao tác tay nào | Cần đúng một thao tác tay không ghi trong README | Cần nhiều thao tác tay | Không chạy được |

## Hai điều người chấm không trừ điểm

**Một dòng không tìm được, hoặc hai, hoặc ba.** Bài này bắt buộc có ít nhất một, và không đặt trần. Ba dòng không tìm được kèm ba lời giải thích sắc có giá trị hơn năm dòng tìm được kèm năm câu truy vấn rộng tới mức khoanh trúng mọi thứ. Điều duy nhất bị trừ ở đây là khai không tìm được cho một sự kiện mà bạn chưa thử tìm.

**Độ trễ lớn và hạn giữ ngắn.** Con số đo được trên laptop của bạn là con số của laptop bạn, và một chặng chuyển chậm hai giây không phải là một bài làm kém. Hạn giữ bảy ngày cũng là một lựa chọn hợp lệ nếu bạn nói được nó đánh đổi cái gì lấy cái gì. Học phần này đo chất lượng của lập luận về đánh đổi, không đo con số.

## Một điều bị trừ nặng

**Quy tắc Sigma neo vào những bản ghi đã biết thay vì neo vào hành vi.** Liệt kê thẳng các mã bản ghi, ghép một chuỗi chỉ xuất hiện đúng trong tập mẫu, hay loại trừ từng trường hợp một cho tới khi con số đẹp, tất cả đều là cùng một việc: học thuộc tập kiểm thay vì viết một quy tắc phát hiện. Bộ chấm chặn được dạng thô nhất của nó bằng cách cấm ba trường riêng của tập mẫu, và quy tắc của bạn còn được chạy lại trên một tập có nhãn thứ hai mà bạn không thấy.

Chỗ này rơi thẳng xuống mức Kém của tiêu chí thứ tư, kể cả khi mười sáu phép kiểm đều xanh. Lý do không phải là kỷ luật thi cử. Một quy tắc như vậy đạt điểm tuyệt đối trên tập kiểm và bắt được đúng không sự kiện nào trên hệ thống thật, tức là nó tệ hơn không có quy tắc: nó tạo ra cảm giác đang được canh chừng.
