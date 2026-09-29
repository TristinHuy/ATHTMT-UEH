# Thang chấm lab S3

Tổng 100 điểm, quy về 3 phần trăm điểm học phần. Máy chấm 60, người chấm 30, phần tái lập 10.

| Tiêu chí | Trọng số | Ai chấm | Tốt, 100% | Khá, 75% | Trung bình, 50% | Kém, 0% |
|---|---|---|---|---|---|---|
| Bộ kiểm tự động | 60 | Máy | Cả mười sáu phép kiểm xanh | Một phép kiểm đỏ | Hai tới ba phép kiểm đỏ | Từ bốn phép kiểm đỏ trở lên, hoặc không nộp |
| Lập luận về ba chỗ hỏng của một cấu hình đúng thuật toán | 12 | Người | Nói được vì sao kiểm chuỗi và so tên là hai phép khác nhau, gắn đúng mã điểm yếu cho từng chỗ, và chỉ ra chỗ nào trong cấu hình của mình đóng chỗ hỏng nào | Nói đúng ba chỗ hỏng nhưng gắn mã lỏng lẻo, hoặc không nối được về cấu hình của mình | Nhắc lại được ba chỗ hỏng ở mức mô tả, không nối vào bài của mình | Chép lại giáo trình, hoặc không có |
| Đoạn đánh đổi ở `docs/danh-doi.md` | 10 | Người | Chọn một lớp để bỏ, tính ra chi phí bằng số có đơn vị, nêu đúng bằng chứng nào còn đứng sau khi bỏ, và thừa nhận rủi ro mới phải bù ở đâu | Có lựa chọn và có lý do, nhưng chi phí nói chung chung hoặc không nói phần phải bù | Chỉ nêu lựa chọn, lý do dừng ở mức tốn công | Không chọn gì, hoặc mô tả lại việc đã làm |
| Đọc bằng chứng do người quan sát độc lập sinh ra | 8 | Người | Đọc kết quả `testssl.sh`, chỉ ra ít nhất một điểm nó nói khác hoặc nói thêm so với tệp cấu hình, và giải thích vì sao | Đọc và tóm tắt đúng, không so với cấu hình | Nộp tệp mà không bình luận gì | Không chạy |
| Tái lập được | 10 | Máy | `make preflight`, `make up`, `make defend`, `make bon-phep-kiem`, `make verify` chạy xanh trên kho sạch mới nhân bản, không thao tác tay nào | Cần đúng một thao tác tay không ghi trong README | Cần nhiều thao tác tay | Không chạy được |

Bảy mã dưới đây là bộ mã tiêu chí thứ hai đòi hỏi. Chúng lấy từ CWE List 4.20 và ATT&CK content v19.2, đọc ngày 18/08/2026.

| Mã | Chỗ nó nằm trong bài |
|---|---|
| CWE-295 | kho tin cậy quá rộng, hoặc phép kiểm bị tắt hẳn; đây là điều phần thử thách K5 hỏi tới |
| CWE-296 | chuỗi tin cậy không dựng ngược được về gốc; phép kiểm CA nội bộ và phép kiểm chứng thư máy chủ |
| CWE-297 | chứng thư hợp lệ nhưng không thuộc về cái tên bạn gọi; phép so tên ở K1 và K2 |
| CWE-298 | chứng thư hết hạn hoặc vòng đời quá dài; phép đo hạn |
| CWE-319 | dữ liệu đi trần trên chặng cuối; bước `make attack` và phép kiểm cổng phẳng |
| T1557 | kỹ thuật mà hai lớp phòng thủ của bài nhằm chặn |
| T1040 | kỹ thuật mà bước `make attack` diễn lại ở mức quan sát, trong mạng của chính bạn |

## Hai điều người chấm không trừ điểm

**Số lần bạn làm hỏng rồi dựng lại.** Bộ chứng thư sai tên, nginx không khởi động được vì lệch khóa, quên `-noenc` rồi bị hỏi mật khẩu, tất cả đều nằm trong quá trình học chứ không nằm trong kết quả. Bạn dựng lại bao nhiêu lần cũng được trước hạn nộp, và nhật ký thô có bao nhiêu lần đỏ cũng không bị trừ. Thứ được chấm là trạng thái cuối và lập luận đi kèm.

**Chọn một cấu hình tối giản.** Một khối `server` gọn với đúng những chỉ thị cần thiết được điểm cao hơn một tệp cấu hình dài chép từ nhiều nguồn, kể cả khi tệp dài kia cũng chạy. Trong an toàn hệ thống, mỗi dòng bạn không hiểu là một dòng bạn không bảo vệ được, và người chấm sẽ hỏi về những dòng thừa chứ không cho điểm chúng.

## Một điều bị trừ nặng

**Sửa tay tệp trong `evidence/`.** Bốn tệp `kiem-K*.txt` do `bin/ghi-ket-qua.sh` sinh ra, và phán quyết trong đó tính từ mã thoát cùng dấu hiệu trong đầu ra thật. Gõ `thuc_te: BI_TU_CHOI` vào một phép kiểm chưa bao giờ chạy là làm giả bằng chứng, và bài này tồn tại để dạy đúng điều ngược lại. Người chấm đối chiếu bản tóm tắt với nhật ký thô và với `SHA256SUMS`, nên chuyện này lộ ra chứ không phải không lộ.

Hậu quả: toàn bộ phần máy chấm và phần người chấm của bài về 0, và việc được xử lý theo chính sách liêm chính của học phần. Một bài trung thực với hai phép kiểm còn đỏ vẫn được chấm bình thường và vẫn có thể đạt, nên không có lý do nào đáng để đánh đổi.
