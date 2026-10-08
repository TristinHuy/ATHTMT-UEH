# Đường đi nhật ký S7

## Nguồn và chặng chuyển

Promtail đọc sáu thư mục `/nhat-ky/S02/` tới `/nhat-ky/S07/`, gắn nhãn thấp cardinality `job=nhat-ky-lab` và `buoi=Sxx`, rồi đẩy tới `http://loki:3100/loki/api/v1/push`. Nhãn chỉ chọn nguồn; nội dung dòng được giữ để LogQL lọc. Dấu thời gian S02 được phân tích từ đầu dòng, S07 từ JSON. S03 được gom theo kết quả K4; S04-S06 giữ định dạng gốc, nên Loki hiện gán thời gian nhận cho các nguồn ấy. Đặc biệt báo cáo CSP/access của S06 không có thời gian sự kiện. Đây là giới hạn cần khắc phục nếu cần đối chiếu chính xác hạn giữ cho các nguồn đó.

Thư mục `./nhat-ky` chỉ được gắn vào Promtail với `:ro`; vị trí đọc của Promtail nằm ở volume riêng. Loki không nhìn thấy thư mục nguồn, lưu dữ liệu trong volume riêng, chỉ tham gia mạng bridge nội bộ và không xuất bản cổng ra máy thật. Container công cụ chỉ được bật theo profile để hỏi Loki và ghi bằng chứng trong thư mục bài làm. Grafana là tùy chọn, cổng chỉ neo `127.0.0.1`.

## Nơi giữ và ranh giới tin cậy

Loki bật compactor/retention với hạn giữ **90 ngày** và cho truy vấn cửa sổ tối đa tương ứng. Cửa sổ nhận đủ rộng để nạp mẫu S02 cũ. Chín mươi ngày giữ được chuỗi hoạt động xuyên suốt các buổi để so sánh trước/sau khi vá. Nếu giảm xuống bảy ngày, truy vấn S02 về lần leo quyền setuid sẽ mất dòng sau khi mốc sự kiện vượt cửa sổ; với các nguồn S03-S06 chưa chuẩn hóa timestamp, hiện chưa thể kết luận tuổi lưu giữ theo thời điểm sự kiện thay vì thời điểm nạp.

Ranh giới tin cậy là: nguồn sinh dữ liệu nằm trong thư mục bài làm; Promtail chỉ đọc và chuyển; Loki giữ bản đã chuyển trong volume; truy vấn chỉ đi qua mạng Compose. Thí nghiệm `make attack` chỉ cắt tệp do chính nó tạo trong `nhat-ky/S07/`, không tác động nhật ký máy thật hay nguồn ngoài phạm vi.

## Độ trễ và dữ liệu cá nhân

`evidence/S7/do-tre.csv` giữ lần chậm nhất trong ba lần chạy: tổng lần lượt là 3,777 giây, 2,093 giây và 2,428 giây. Lần được giữ có sinh 0,067 giây, chuyển 0,000 giây, giữ 3,705 giây và hỏi 0,006 giây, tổng 3,777 giây. Chặng chuyển được chặn ở 0 nếu dấu thời gian Loki sớm hơn mốc ghi xong; vì vậy số 0,000 không chứng minh việc chuyển tức thời. Phần lớn độ trễ đo được nằm ở lúc bản ghi trở thành kết quả truy vấn được. Thí nghiệm xóa dấu vết đo khoảng nguy hiểm 2,049 giây; kết quả được ghi riêng ở `evidence/S7/xoa-vet.txt`.

Các nguồn S03 có thể mang địa chỉ mạng/chứng thư; S05 ghi chủ thể và lý do xác thực; đặc biệt pgaudit S04 giữ nguyên câu SQL, tên bảng/cột và có thể chứa giá trị nhạy cảm trong những bài khác. Đây là mức ghi rộng hơn cần thiết cho phần lớn câu hỏi. Bản lab hiện dùng dữ liệu giả lập, không đưa dữ liệu cá nhân thật vào, nhưng khi vận hành thật nên giảm/che trường truy vấn và định danh trước khi chuyển, giới hạn người đọc, và chỉ giữ trong thời hạn có lý do.
