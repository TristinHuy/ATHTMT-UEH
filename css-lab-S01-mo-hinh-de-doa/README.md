# Lab S1. Mô hình đe dọa và kho bằng chứng

**Học phần An toàn hệ thống máy tính · Buổi 1 · Bài cá nhân · 3 phần trăm điểm học phần**

Hạn nộp: trước giờ buổi S2. Nộp trễ dưới 24 giờ nhận 75 phần trăm điểm đã chấm, trễ 24 tới 72 giờ nhận 50 phần trăm, sau 72 giờ nhận 0.

## Mục tiêu

Dựng hạ tầng làm việc cá nhân cho cả học phần, và tập diễn đạt một mối đe dọa thành phát biểu **kiểm được**.

Mục tiêu thứ hai khó hơn vẻ ngoài, và nó là lý do bài này tồn tại. Câu "kẻ tấn công có thể đọc cơ sở dữ liệu" nghe như một mối đe dọa nhưng không kiểm được, vì bạn không biết phải thử gì để xác nhận nó đúng hay sai. Câu "một người dùng đã đăng nhập với vai trò khách hàng đọc được bảng đơn hàng của khách hàng khác nếu ứng dụng không lọc theo mã người dùng" thì kiểm được, vì nó tự nói ra cách kiểm.

## Việc phải làm

1. Nhận kho từ mẫu qua GitHub Classroom.
2. Chạy `make preflight`. Lệnh này ghi kiến trúc CPU, phiên bản Docker và phiên bản Python của máy bạn vào `evidence/S1/preflight.txt`. Đây cũng là phép thử xem môi trường bạn cài ở tài liệu hướng dẫn có thật sự chạy hay không.
3. Chọn **một** hệ thống nhỏ có đúng ba thành phần. Gợi ý: một trang bán hàng gồm trình duyệt, máy chủ ứng dụng, cơ sở dữ liệu; một hệ thống điểm danh; một kho tài liệu nội bộ. Không chọn hệ thống thật của một tổ chức thật.
4. Vẽ sơ đồ luồng dữ liệu, rồi ghi mô hình ra `docs/threat-model.json` theo lược đồ `schema/threat-model.schema.json`. Lược đồ mới là hợp đồng, công cụ thì không: Threat Dragon xuất được tệp này và là lựa chọn tiện nhất nếu bạn muốn một công cụ đồ họa, nhưng vẽ trên giấy rồi tự gõ tệp JSON cũng đạt như nhau. ADR-0003 hạ Threat Dragon xuống mức tùy chọn vì bản web và bản cài của nó xuất ra hai dạng JSON hơi lệch nhau, và vì mục tiêu thật của bài này không nằm ở việc cài thêm một phần mềm.
5. Liệt kê **tối thiểu tám mối đe dọa**. Mỗi mối phải có:
   - một câu phát biểu **kiểm được**, tức đọc xong biết phải thử gì;
   - một trong **bảy nguyên lý cột sống** mà nó chạm tới, ghi bằng số từ 1 tới 7;
   - một **mã kỹ thuật MITRE ATT&CK**, dạng `T1234` hoặc `T1234.001`;
   - hai số từ 1 tới 5 cho **tác động** và **khả năng**.
6. Xếp hạng theo tích tác động nhân khả năng, chọn **ba mối** để xử lý, và với mỗi mối ghi một **ước lượng chi phí xử lý** theo nguyên lý thứ bảy. Ước lượng thô cũng được, nhưng phải có đơn vị và phải nói rõ bạn ước lượng dựa trên cái gì.
7. Viết `README.md` một trang trong kho của bạn: hệ thống bạn chọn, ba mối bạn xử lý, và vì sao chọn ba mối đó chứ không phải ba mối khác.

## Sản phẩm phải nộp

```
docs/threat-model.json      sơ đồ và danh sách mối đe dọa
README.md                   một trang
evidence/S1/preflight.txt   kết quả make preflight
```

Nộp bằng cách đẩy lên nhánh `main` của kho cá nhân trước hạn. Mốc thời gian lấy theo dấu thời gian commit trên GitHub, không lấy theo lời khai.

## Máy chấm kiểm những gì

Chạy `make verify` để tự kiểm trước khi nộp. Bộ chấm chạy đúng những phép kiểm đó trong GitHub Actions.

| Phép kiểm | Đạt khi |
|---|---|
| Tệp JSON hợp lệ theo lược đồ `schema/threat-model.schema.json` | phân giải được và đủ trường bắt buộc |
| Số mối đe dọa | ít nhất 8 |
| Trường nguyên lý | mỗi mối có một số nguyên từ 1 tới 7 |
| Mã ATT&CK | mỗi mối khớp mẫu `T\d{4}(\.\d{3})?` |
| Ba mối được chọn | đúng 3, và đều nằm trong danh sách 8 mối |
| Ước lượng chi phí | cả ba mối được chọn đều có, và có đơn vị |
| Phát biểu kiểm được | mỗi câu dài ít nhất 12 từ và chứa một điều kiện, tức có một trong các chữ nếu, khi, trong trường hợp |
| `preflight.txt` | ghi đủ kiến trúc CPU, phiên bản Docker, phiên bản Python |

Phép kiểm cuối trong bảng là một phép **xấp xỉ máy làm được**, không phải phép đo thật về chất lượng câu văn. Nó chặn được câu quá ngắn và câu không có điều kiện, nhưng nó không phân biệt được một câu hay với một câu vừa đủ dài. Phần đó do người chấm đọc, theo thang chấm ở `rubric.md`.

## Tiêu chí đạt

Máy chấm xanh, **và** ba mối được chọn đều có ước lượng chi phí theo nguyên lý thứ bảy.

## Trước khi hỏi

Đọc `SCOPE.md` để biết ranh giới việc được phép làm. Bài này không có phần tấn công, nhưng ranh giới vẫn áp dụng từ buổi đầu.

Máy không chạy được thì báo **chậm nhất hai ngày trước buổi S2**, đừng đợi tới hạn nộp.
