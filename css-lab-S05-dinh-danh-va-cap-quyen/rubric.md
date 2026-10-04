# Thang chấm lab S5

Tổng 100 điểm, quy về 3 phần trăm điểm học phần. Máy chấm 60, người chấm 30, phần tái lập 10.

| Tiêu chí | Trọng số | Ai chấm | Tốt, 100% | Khá, 75% | Trung bình, 50% | Kém, 0% |
|---|---|---|---|---|---|---|
| Bộ kiểm tự động | 60 | Máy | Cả mười sáu phép kiểm xanh | Một phép kiểm đỏ | Hai tới ba phép kiểm đỏ | Từ bốn phép kiểm đỏ trở lên, hoặc không nộp |
| Lập luận về ba cạm bẫy của tấm thẻ | 12 | Người | Gọi đúng mã điểm yếu cho từng cạm bẫy, chỉ ra dòng nào trong `kiem_the.py` đóng cạm bẫy nào, và nói được vì sao cả ba đều là lỗi bỏ sót chứ không phải lỗi gõ sai | Nói đúng ba cạm bẫy nhưng gắn mã lỏng lẻo, hoặc không nối được về mã mình viết | Nhắc lại được ba cạm bẫy ở mức mô tả, không nối vào bài của mình | Chép lại giáo trình, hoặc không có |
| Tham số hàm băm chọn có căn cứ | 8 | Người | Có hai lần đo trước và sau, đọc được hiệu số, chọn tham số kèm lý do riêng cho máy của mình, và nói rõ phép đo này là xấp xỉ ở chỗ nào | Có hai lần đo và có lý do, nhưng không nói giới hạn của phép đo | Chép nguyên bộ tham số của RFC 9106 mà không đo | Không đo, hoặc để nguyên tham số khởi đầu |
| Đoạn đánh đổi ở `docs/danh-doi.md` | 10 | Người | Có con số đo bằng đồng hồ, tính ra được cái giá của việc rút con số ấy xuống, nêu đơn vị, và thừa nhận phần rủi ro còn lại | Có con số và có giá, nhưng giá nói chung chung hoặc không có đơn vị | Chỉ kể lại việc đã làm, con số suy từ tài liệu chứ không đo | Không có |
| Tái lập được | 10 | Máy | `make preflight`, `make up`, `make defend`, `make nam-phep-kiem`, `make verify` chạy xanh trên kho sạch mới nhân bản, không thao tác tay nào ngoài bước ghi danh yếu tố thứ hai đã ghi trong README | Cần đúng một thao tác tay không ghi trong README | Cần nhiều thao tác tay | Không chạy được |

Bảng sau liệt kê bảy mã mà hai tiêu chí do người chấm đánh giá dùng để đối chiếu. Các mã lấy từ CWE List 4.20 và ATT&CK content v19.2, đọc ngày 18/08/2026.

| Mã | Chỗ nó nằm trong bài |
|---|---|
| CWE-256 | mật khẩu lưu ở dạng rõ; trạng thái khởi đầu không mắc lỗi này, nhưng §5.3 dựng nó thành thang so sánh |
| CWE-916 | hàm băm nhanh trong trạng thái khởi đầu; việc 4 đổi nó đi |
| CWE-347 | tin trường thuật toán trong chính tấm thẻ; hai phép kiểm âm N1 và N2 |
| CWE-613 | thẻ sống lâu hơn quyền của chủ nó; phép kiểm âm N3, và hạn thẻ trong vùng định danh |
| CWE-798 | khóa hay bí mật nằm trong mã nguồn; lý do `totp-bi-mat.txt` không đi vào kho |
| CWE-863 | có kiểm nhưng kiểm sai; hai phép kiểm âm N4 và N5 |
| T1621 | kỹ thuật mà giới hạn số lần hỏi ở việc 5 nhằm chặn |

## Hai điều người chấm không trừ điểm

**Số lần sinh viên dựng lại vùng định danh.** Các sự cố như quên rằng tệp cấu hình chỉ được nạp ở lần dựng đầu, đặt sai tên biến môi trường của hàm băm, hay ghi danh yếu tố thứ hai xong rồi mất bí mật và phải làm lại đều thuộc quá trình làm bài và không bị trừ điểm. Số lần đỏ trong nhật ký thô cũng không bị trừ. Điểm được chấm trên trạng thái cuối và phần lập luận đi kèm.

**Chọn tham số hàm băm thấp hơn mong muốn vì máy yếu, nếu bài nêu rõ lý do.** Một sinh viên chọn 64 MiB vì máy chỉ có bốn nhân, đo được thời gian đăng nhập tăng gấp ba, rồi nói rõ mình dừng ở đâu và vì sao, được điểm cao hơn một sinh viên đặt 2 GiB chỉ vì thấy con số đó trong chuẩn. Tham số hàm băm là một đánh đổi giữa chi phí của kẻ đoán mật khẩu và thời gian chờ của người dùng thật, và một tham số không thể bật trên hệ thống thật thì không bảo vệ được tài khoản nào.

## Một điều bị trừ nặng

**Làm cho bộ kiểm xanh mà không làm cho dịch vụ đúng.** Bài này có một đường tắt như vậy, và nó được nêu rõ ở đây để sinh viên biết trước hậu quả: viết `kiem_the` sao cho hàm ném `TheKhongHopLe` với bốn tấm thẻ mà bộ chấm dựng, nhưng không thật sự kiểm chữ ký, người nhận và thời hạn, chẳng hạn nhận diện tấm thẻ theo độ dài, theo một chuỗi con, hay theo thứ tự gọi.

Đường tắt này bị phát hiện ngay trong bài. Bộ chấm gọi hàm của sinh viên với thẻ do bộ chấm tự ký, còn `make nam-phep-kiem` gọi dịch vụ với thẻ do vùng định danh thật phát ra. Một hàm chỉ đoán sẽ cho hai kết quả lệch nhau, và người chấm đọc cả hai. Hậu quả: toàn bộ phần máy chấm và phần người chấm của bài về 0, và sự việc được xử lý theo chính sách liêm chính của học phần.

Một bài trung thực còn hai phép kiểm đỏ vẫn được chấm bình thường theo thang ở trên, tức vẫn nhận 50 phần trăm của 60 điểm máy chấm.
