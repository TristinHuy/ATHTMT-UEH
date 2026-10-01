# Lab S4. Vai trò tối thiểu và an toàn mức hàng trong PostgreSQL

**Học phần An toàn hệ thống máy tính · Buổi 4 · Bài cá nhân · 3 phần trăm điểm học phần**

Hạn nộp: 23:59 hôm trước buổi S5; ngày cụ thể ghi ở Master Hub. Nộp trễ dưới 24 giờ nhận 75 phần trăm điểm đã chấm, trễ 24 tới 72 giờ nhận 50 phần trăm, sau 72 giờ nhận 0.

## Mục tiêu

Sinh viên thu hẹp quyền trên một cơ sở dữ liệu đang mở quá rộng, sao cho mỗi vai trò giữ đúng phần nó cần, rồi chứng minh bằng năm truy vấn ÂM rằng mỗi vai trò không làm được việc nó không được phép.

Vế thứ hai là lý do bài này tồn tại. Phần cấp quyền rất dễ được coi là đã xong, vì mọi câu lệnh `GRANT` và `REVOKE` đều chạy mà không báo lỗi, và bảng quyền in ra trông hoàn toàn hợp lệ. Câu hỏi khó nằm ở chiều ngược lại: làm sao biết một chính sách đang thật sự có hiệu lực? Một chính sách viết đúng cú pháp nhưng không áp cho vai trò nào cũng chạy im lặng như một chính sách đang bảo vệ thật. Mục 4.4 của giáo trình đã chỉ ra một trường hợp như vậy: khi thiếu từ khóa `FORCE`, chủ sở hữu bảng đi qua mọi chính sách.

Một lớp phòng thủ chỉ được coi là đang bật khi có một truy vấn thử đi qua nó và bị chặn lại. Vì vậy bài này yêu cầu năm truy vấn bị chặn, mỗi truy vấn ở một lớp khác nhau: lớp cấp quyền, lớp lọc dòng khi đọc, lớp lọc dòng khi ghi, lớp ràng buộc nghiệp vụ, và lớp áp chính sách cho cả chủ sở hữu bảng. Một truy vấn bị chặn ở lớp khác với lớp đề bài chỉ định vẫn là một truy vấn bị chặn, nhưng nó không chứng minh được lớp cần kiểm đang hoạt động.

Đi kèm là ba truy vấn DƯƠNG. Chúng cần thiết vì cách đơn giản nhất để năm phép kiểm âm chuyển xanh là thu sạch quyền của mọi vai trò. Một hệ thống mà không vai trò nào làm được việc của mình cũng vi phạm nguyên lý đặc quyền tối thiểu, vì nguyên lý này đòi mỗi vai trò có đủ quyền cho công việc của nó chứ không đòi ít quyền nhất có thể.

## Việc phải làm

1. Bộ khung của lab này nằm trong thư mục `bai-nop/S4/` của kho cá nhân trên GitHub. Kéo bản mới nhất của kho về máy bằng `git pull`, mở thư mục `bai-nop/S4/` trong VS Code, rồi chạy `make preflight` trong thư mục đó. Lệnh này ghi kiến trúc máy, phiên bản Python và trạng thái Docker vào `evidence/S4/preflight.txt`. Mọi lệnh `make` của bài đều chạy trong `bai-nop/S4/`, vì bộ chấm trên GitHub Actions chạy bộ kiểm của buổi S4 trong đúng thư mục này.

2. Chạy `make up`. Máy chủ khởi động, rồi lược đồ và mười hai dòng nhân sự được nạp. Đây là điểm xuất phát của bài, và chạy lại đúng lệnh này lúc nào cũng đưa cơ sở dữ liệu về trạng thái đó, nên việc làm hỏng cơ sở dữ liệu trong lúc thử không gây mất mát gì.

3. Chạy `make attack`. Lệnh này chạy ba câu truy vấn hợp lệ bằng `khach_tam`, một tài khoản báo cáo cũ mà không ai còn nhớ mục đích sử dụng. Câu thứ nhất đọc thẳng bảng lương. Hai câu sau chỉ hỏi số liệu thống kê và đều vượt qua ngưỡng chặn năm người, nhưng hiệu của hai kết quả chính là lương tháng của đúng một cá nhân. Tệp `evidence/S4/truoc-khi-siet.txt` cần được giữ lại để nộp.

   Hai loại rò rỉ này khác nhau về bản chất, và bài này chỉ đóng được loại thứ nhất. Mục 4.2 gọi loại thứ hai là bài toán kiểm soát suy luận; mục 4.8 giải thích vì sao bài toán này chưa có lời giải trọn vẹn.

4. Viết `sql/01-vai-tro.sql`. Tệp này thu lại bốn quyền mà `PUBLIC` đang giữ: quyền trên bảng do người tiền nhiệm cấp, quyền `EXECUTE` trên hàm, quyền `USAGE` trên lược đồ, và quyền `CONNECT` trên cơ sở dữ liệu. Sau đó tệp dựng bốn vai trò: `chu_luoc_do` sở hữu bảng, `ung_dung` đọc và ghi, `duyet_chi` duyệt nhưng không tạo đề nghị, `bao_cao` chỉ đọc số liệu thống kê. Việc thu quyền phải đứng trước việc cấp quyền, vì nếu làm ngược lại thì trong khoảng thời gian giữa hai bước, mọi vai trò mới dựng đều thừa hưởng phần cấp sẵn của `PUBLIC`.

5. Viết `sql/02-muc-hang.sql`. Tệp này bật an toàn mức hàng cho `de_nghi_chi` bằng hai câu lệnh chứ không phải một, viết các chính sách có đủ vế `USING` và vế `WITH CHECK`, và đặt ràng buộc người tạo khác người duyệt ngay trong lược đồ. Câu lệnh bật thứ hai dùng từ khóa `FORCE`; thiếu câu này thì chủ sở hữu bảng vẫn đọc được toàn bộ bảng như khi chưa có chính sách nào.

6. Viết `sql/03-pgaudit.sql` và hai dòng trong `csdl/pgaudit.conf` để bật lưu vết ở mức đối tượng thay vì mức phiên. Lựa chọn này là một quyết định vận hành: nhật ký ghi mọi câu lệnh của mọi phiên làm chi phí lưu trữ tăng nhanh nên dễ bị tắt khi chi phí được đem ra xem xét, và một nhật ký đã tắt thì không ghi được sự kiện nào.

7. Chạy `make defend`, rồi `make tam-truy-van`. Tám phép kiểm chạy từ container máy khách, mỗi phép ghi ra hai tệp. Tệp `evidence/S4/kiem-*.txt` là bản tóm tắt máy đọc được, thư mục `evidence/S4/tho/` giữ nhật ký thô cho người chấm. Phán quyết được tính từ mã thoát của `psql` và từ thông điệp lỗi của máy chủ, nên sinh viên không tự ghi dòng kết quả vào các tệp này.

| Phép | Vai trò | Chiều | Phải dừng ở lớp nào | Nó chứng minh điều gì |
|---|---|---|---|---|
| A1 | `bao_cao` | âm | cấp quyền | vai trò báo cáo không chạm được vào bảng gốc |
| A2 | `ung_dung` | âm | lọc dòng khi đọc | chính sách mức hàng giấu đề nghị của người khác |
| A3 | `ung_dung` | âm | lọc dòng khi ghi | vế `WITH CHECK` chặn việc ghi một dòng mang tên người khác |
| A4 | `duyet_chi` | âm | ràng buộc nghiệp vụ | người duyệt không tự duyệt được đề nghị do chính mình tạo |
| A5 | `chu_luoc_do` | âm | `FORCE` | chủ sở hữu bảng cũng nằm dưới chính sách |
| D1 | `ung_dung` | dương | không lớp nào | ứng dụng đọc được phần của chính nó |
| D2 | `ung_dung` | dương | không lớp nào | ứng dụng ghi được phần của chính nó |
| D3 | `bao_cao` | dương | không lớp nào | vai trò báo cáo vẫn đọc được thống kê |

8. Chạy `make suy-luan`. Lệnh này chạy lại hai câu hỏi thống kê ở bước 3, lần này bằng vai trò `bao_cao` sau khi đã siết quyền, và hiệu số vẫn ra đúng con số cũ. Tệp kết quả không được máy chấm; người chấm đọc nó theo `rubric.md`.

9. Viết `docs/bang-vai-tro.md`, mỗi dòng một vai trò. Cột cuối ghi thứ vai trò đó **suy ra** được mà không được phép đọc thẳng. Người chấm đọc cột này kỹ nhất, vì tiêu chí bảng vai trò trong `rubric.md` chấm chủ yếu ở đây.

10. Viết `docs/danh-doi.md`, dài từ 120 tới 300 chữ, trả lời câu hỏi sau: nếu đơn vị chỉ có ba người thì bỏ phép tách nhiệm vụ nào, bù lại bằng biện pháp gì, và điểm hòa vốn là bao nhiêu? Phép tính ở mục 4.5 của giáo trình là điểm xuất phát, và bài làm cần áp nó vào trường hợp đơn vị ba người.

11. Chạy `make export-evidence` rồi `make verify`. Sau đó nộp bằng ba lệnh chạy từ thư mục gốc của kho: `git add bai-nop/S4`, `git commit -m "S4: an toàn cơ sở dữ liệu"`, `git push`. Đẩy lên nhánh `main` trước hạn. Bài nộp là trạng thái của nhánh `main` trên GitHub tại thời điểm hạn nộp, nên đẩy lại nhiều lần trước hạn không bị trừ điểm. Lệnh `git push --force` không được dùng, vì lịch sử commit là bằng chứng nộp đúng hạn.

Phần thử thách không tính điểm máy. `make thu-thach` chạy phép kiểm A6, trong đó `duyet_chi` thử tạo một đề nghị chi. A4 và A6 cùng kiểm việc tách nhiệm vụ nhưng ở hai lớp khác nhau; phần giải thích hai lớp đó khác nhau ở đâu được viết trong bảng vai trò ở bước 9.

## Sản phẩm phải nộp

```
sql/01-vai-tro.sql              thu quyền cấp sẵn, dựng bốn vai trò
sql/02-muc-hang.sql             chính sách mức hàng và ràng buộc nghiệp vụ
sql/03-pgaudit.sql              vai trò đánh dấu và phạm vi lưu vết
csdl/pgaudit.conf               hai dòng bật pgaudit ở mức đối tượng
docs/bang-vai-tro.md            bảng vai trò, có cột suy luận
docs/danh-doi.md                đoạn từ 120 tới 300 chữ
evidence/S4/preflight.txt       kết quả make preflight
evidence/S4/truoc-khi-siet.txt  ba câu truy vấn ở bước 3
evidence/S4/kiem-A1..A5.txt     năm phán quyết âm, máy đọc được
evidence/S4/kiem-D1..D3.txt     ba phán quyết dương
evidence/S4/tho/                nhật ký thô của tám lần chạy
evidence/S4/suy-luan.txt        chuỗi suy luận chạy lại sau khi siết
evidence/S4/pgaudit.txt         nhật ký lưu vết đã lọc
evidence/S4/SHA256SUMS          băm của toàn bộ bằng chứng
```

Tệp `sql/00-du-lieu.sql` được phát sẵn và sinh viên không sửa tệp này. Nó mô tả hiện trạng được bàn giao, kể cả dòng cấp quyền rộng ở cuối tệp. Xóa dòng đó cũng làm phép kiểm quyền chuyển xanh, nhưng không siết được quyền nào: trên một hệ thống thật, câu lệnh cấp quyền đã chạy từ trước và quyền vẫn còn đó dù dòng lệnh bị xóa khỏi tệp. Bộ kiểm đọc lại tệp phát sẵn để xác nhận tệp còn nguyên.

Mốc thời gian lấy theo dấu thời gian commit trên GitHub, không lấy theo lời khai.

## Máy chấm kiểm những gì

Chạy `make verify` để tự kiểm trước khi nộp. Bộ chấm chạy đúng mười sáu phép kiểm đó trong GitHub Actions, không thêm phép nào.

| Nhóm | Phép kiểm | Đạt khi |
|---|---|---|
| Phạm vi | ảnh ghim theo phiên bản cụ thể | không ảnh nào dùng thẻ trôi nổi, kể cả dòng `FROM` trong `csdl/Dockerfile` |
| Phạm vi | không mở cổng ra ngoài máy | không có `ports`, hoặc mọi ánh xạ neo vào `127.0.0.1` |
| Phạm vi | không xin đặc quyền | không `privileged`, không `network_mode: host`, không `cap_add` |
| Cấu hình | dữ liệu phát sẵn còn nguyên | `sql/00-du-lieu.sql` giữ đủ dòng cấp quyền rộng, vai trò `khach_tam`, mười hai dòng nhân sự |
| Cấu hình | thu hết phần cấp sẵn cho `PUBLIC` | đủ bốn câu `REVOKE`: bảng, hàm, lược đồ, cơ sở dữ liệu |
| Cấu hình | bốn vai trò, không vai trò nào thừa quyền | không `SUPERUSER`, `BYPASSRLS`, `CREATEROLE`; không cấp lại cho `PUBLIC`; không `GRANT ALL` trên hai bảng; không `INSERT` cho `duyet_chi` |
| Cấu hình | chính sách mức hàng đủ và có `FORCE` | có `ENABLE` và `FORCE`, từ hai chính sách trở lên, có cả `USING` lẫn `WITH CHECK` |
| Cấu hình | ràng buộc người tạo khác người duyệt | một ràng buộc `CHECK` nhắc cả hai cột |
| Cấu hình | pgaudit bật ở mức đối tượng | `shared_preload_libraries` có `pgaudit`, có `pgaudit.role`, không đặt `pgaudit.log` bằng `all`, và vai trò đánh dấu được cấp quyền trên bảng nhân sự |
| Bằng chứng | preflight đủ mục | ghi đủ máy, Python, Docker, và daemon đang chạy |
| Bằng chứng | tám kết quả đủ và đúng dạng | tám tệp kết quả đủ khóa, mỗi tệp có nhật ký thô đi kèm |
| Bằng chứng | năm phép âm bị chặn đúng lớp | mỗi phán quyết khớp đúng lớp đề bài chỉ định |
| Bằng chứng | ba phép dương vẫn chạy được | không phép nào bị chặn |
| Bằng chứng | nhật ký lưu vết có vết thật | có dòng `AUDIT`, và có dòng nhắc tới bảng nhân sự |
| Bằng chứng | bảng vai trò đủ dòng và có cột suy luận | bốn vai trò, và một cột nói về thứ suy ra được |
| Bằng chứng | đoạn đánh đổi có và đủ dài | từ 120 tới 300 từ |

Ba phép kiểm cuối bảng có giới hạn cần nói rõ. Phép đếm dòng của bảng vai trò và phép đếm từ của đoạn đánh đổi chỉ là phép xấp xỉ mà máy làm được, không đo chất lượng lập luận: chúng phát hiện được bài không nộp hoặc bài chỉ có vài câu, nhưng không phân biệt được một lập luận chặt với một đoạn kể lại việc đã làm. Phần này do người chấm đọc theo `rubric.md`. Phép kiểm nhật ký lưu vết chỉ chứng minh phần mở rộng đã được nạp và đã ghi lại ít nhất một câu truy vấn chạm tới bảng nhân sự; nó không cho biết nhật ký đã đủ để điều tra hay chưa, vì `pgaudit` ghi câu truy vấn chứ không ghi kết quả trả về. Kết quả của `make suy-luan` không được máy chấm, vì phần cần đánh giá ở đó là kết luận sinh viên rút ra từ hai con số.

## Tiêu chí đạt

Mười sáu phép kiểm xanh, **và** năm phép kiểm âm bị chặn đúng ở năm lớp mà đề bài chỉ định. Một bài thu sạch quyền của mọi vai trò làm năm phép âm chuyển xanh nhưng cũng làm ba phép dương chuyển đỏ, nên bộ chấm phân biệt được bài siết đúng với bài siết quá tay.

## Trước khi hỏi

Đọc `SCOPE.md` trước khi chạy `make attack`. Bài này có một bước tấn công thật, ở mức chạy ba câu truy vấn hợp lệ bằng một tài khoản cũ trên cơ sở dữ liệu của chính sinh viên, nên phạm vi ghi trong tệp đó là điều kiện bắt buộc của bài.

Bài này dừng trước phần mã hóa dữ liệu khi lưu. Giáo trình mục 4.4 nêu rõ lý do: mã hóa mức đĩa bảo vệ dữ liệu trước người lấy được vật mang dữ liệu, nhưng không chặn được một truy vấn hợp lệ, vì khi truy vấn chạy thì dữ liệu đã ở dạng rõ trong bộ nhớ máy chủ. Lớp mã hóa này cũng nằm ở máy chủ vật lý, tức ngoài container của sinh viên.

Bài cũng dừng trước phần cảnh báo. Các dòng `pgaudit` sinh ra trong bài này là một trong các nguồn dữ liệu mà lab S7 dùng lại, nên tệp `evidence/S4/pgaudit.txt` cần được commit cùng bài nộp. Việc biến một dòng nhật ký thành một cảnh báo có người xử lý thuộc về buổi S7.

Máy không chạy được bài thì sinh viên báo trên Discussions của học phần chậm nhất **24 giờ trước hạn nộp**, kèm tệp `evidence/S4/preflight.txt`. Nếu `make up` báo lỗi kéo ảnh, chạy `bash ghim-digest.sh` trên máy có mạng trước, rồi thử lại. Nếu `make defend` báo máy chủ không khởi động lại được, nguyên nhân thường là một dòng sai trong `csdl/pgaudit.conf`, và lệnh `docker compose logs --tail 30 csdl` chỉ ra dòng đó. Sinh viên chưa quen git hoặc VS Code đọc tài liệu "Làm lab bằng VS Code và git" (bản 2) trong mục `00_Thong-tin-chung` của thư mục học liệu chia sẻ cho lớp.
