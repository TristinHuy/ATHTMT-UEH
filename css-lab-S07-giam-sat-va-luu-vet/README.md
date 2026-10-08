# Lab S7. Phát hiện lại chính cấu hình sai của mình từ nhật ký

Học phần An toàn hệ thống máy tính · Buổi 7 · Bài cá nhân · 3 phần trăm điểm học phần

Hạn nộp: 23:59 hôm trước buổi S8; ngày cụ thể ghi ở Master Hub. Nộp trễ dưới 24 giờ nhận 75 phần trăm điểm đã chấm, trễ 24 tới 72 giờ nhận 50 phần trăm, sau 72 giờ nhận 0.

## Mục tiêu, và vì sao bài này đứng ở buổi bảy chứ không sớm hơn

Sáu buổi vừa qua bạn đã tự tay tạo ra một loạt cấu hình sai rồi tự tay vá chúng. Bạn biết chúng đã xảy ra vì bạn là người gõ lệnh. Bài này lấy đi chỗ dựa ấy và hỏi một câu khác hẳn. Chỉ nhìn vào nhật ký, không được mở lịch sử dòng lệnh, bạn có tìm lại được chúng không?

Đây là câu hỏi mà người vận hành phải trả lời mỗi lần có sự cố, và họ trả lời nó ở tư thế bất lợi hơn bạn nhiều: họ không phải người đã gây ra chuyện, và người đã gây ra chuyện thường không muốn họ tìm thấy. Bài này cho bạn làm thử ở tư thế thuận lợi nhất có thể, khi bạn biết trước mình đang tìm gì, để bạn đo được khoảng cách giữa "hệ thống có ghi lại" và "tôi tìm ra được".

Bài không dừng ở đó. Tìm được một sự kiện đã biết là việc dễ. Việc khó là viết một quy tắc bắt được loại sự kiện ấy khi chưa ai biết nó sắp xảy ra, và biết quy tắc ấy tốn của người trực bao nhiêu. Phần thứ ba của bài đo đúng chuyện đó.

Ranh giới của học phần vẫn giữ nguyên. Bạn học thu nhật ký, hỏi nhật ký, và viết quy tắc phát hiện ở mức vận hành. Dựng dòng thời gian một sự cố, bảo toàn chứng cứ, và điều tra số thuộc học phần Phản ứng với sự cố và điều tra số.

## Việc phải làm

1. Nhận kho từ mẫu qua GitHub Classroom, rồi chạy `make preflight`.

2. **Gom nhật ký của chính bạn.** Chạy `make nap-nhat-ky` để tạo khung thư mục, rồi chép bằng chứng của năm buổi trước vào `nhat-ky/S02/` tới `nhat-ky/S06/`, đặt đuôi `.log`. Nguồn nằm trong thư mục `evidence/` của kho lab từng buổi. Năm thư mục ấy mang năm cái tên không thống nhất vì chúng được dựng ở năm thời điểm khác nhau, nên bước này là bước chuẩn hóa tên, đúng việc mà một chặng thu thập thật phải làm với năm nguồn viết theo năm quy ước.

   Mất dữ liệu hoặc đổi máy giữa các buổi thì xin bộ dữ liệu thay thế của giảng viên. Việc này không bị trừ điểm kiến thức, nhưng bạn phải khai `nguon_du_lieu: thay_the` trong bảng, vì người chấm cần biết bảng nói về hệ thống của bạn hay của người khác.

3. **Dựng đường dẫn.** Điền `cau-hinh/promtail.yaml` cho đủ sáu nguồn, S02 tới S07. Đặt hạn giữ trong `cau-hinh/loki.yaml`. Chạy `make up`, rồi `make hoi` một câu rộng để xác nhận dữ liệu đã vào tới kho.

4. **Chạy một thí nghiệm về việc xóa dấu vết.** `make attack` gieo một dòng vào nguồn của chính bạn, đợi kho nhận được, cắt cụt tệp nguồn, rồi tìm lại dòng ấy ở kho. Nó ghi ra bề rộng của khoảng thời gian mà dòng chữ mới chỉ tồn tại ở một nơi. Toàn bộ phần tấn công của bài gồm đúng thao tác này, và nó chỉ chạm tệp trong `nhat-ky/S07/` của bạn.

5. **Đo độ trễ từng chặng.** `make do-tre`, ít nhất ba lần, giữ lần chậm nhất. Con số bạn cần là con số xấu nhất người trực phải chịu, không phải con số đẹp nhất máy đạt được.

6. **Tìm lại năm sự kiện.** Chép `docs/bang-nam-su-kien.mau.yaml` thành `docs/bang-nam-su-kien.yaml` và điền năm dòng, mỗi buổi một dòng:

   | Buổi | Sự kiện phải tìm lại |
   | --- | --- |
   | S02 | một tiến trình giành thêm quyền qua tệp setuid |
   | S03 | một lần nối bị từ chối vì thiếu chứng thư khách |
   | S04 | một truy vấn chạm bảng lương |
   | S05 | một tấm thẻ quá hạn |
   | S06 | một yêu cầu web bị chính sách nội dung chặn |

   Mỗi sự kiện tìm bằng **đúng một** câu truy vấn LogQL, ghi nguyên văn câu ấy vào bảng. Không được mở lịch sử dòng lệnh. Ràng buộc này nghe như mẹo chống gian lận nhưng không phải: lịch sử dòng lệnh là thứ biến mất đầu tiên trên một máy đã bị chiếm, nên người vận hành không được phép coi nó là nguồn.

   **Bắt buộc có ít nhất một dòng không tìm được**, kèm lý do thuộc đúng một trong ba loại: nguồn ấy không hề ghi, có ghi mà thiếu trường để lọc, hoặc đã hết hạn giữ. Ba loại im lặng ấy chữa bằng ba cách khác nhau, nên gọi đúng tên là phần đáng giá nhất của cả bảng. Giấu dòng không tìm được đi là tự bỏ phần điểm cao nhất.

7. **Viết một quy tắc phát hiện và đo nó.** Sửa `sigma/quy-tac.yml`, rồi chạy `make do-chinh-xac` để chạy quy tắc ấy lên `nhan/tap-co-nhan.jsonl`, một tập sáu mươi sự kiện đã gắn nhãn trải đúng hai mươi tư giờ.

   Bản phát đi kèm một quy tắc **chạy được nhưng chưa đạt**, và đó là chủ ý. Đo nó trước khi sửa một chữ nào: nó bắt hết mọi sự kiện đáng bắt, và cũng bắt hết mọi thứ khác bị từ chối. Việc của bạn là kéo độ chính xác lên trên ngưỡng mà không đánh rơi độ phủ.

   Quy tắc phải nói về hành vi, không nói về bản ghi cụ thể. Nó còn được chạy lại trên một tập có nhãn thứ hai mà bạn không thấy, nên một quy tắc học thuộc tập này sẽ lộ ra ở đó.

8. **Viết hai đoạn văn.** `docs/duong-di-nhat-ky.md` mô tả cấu hình cả đường dẫn, giải thích ranh giới tin cậy giữa nơi sinh, chặng chuyển và nơi giữ, và dẫn số đo độ trễ. `docs/gia-cua-bao-nham.md`, dưới ba trăm từ, trả lời hai câu: với tỉ lệ báo nhầm vừa đo, người trực mất bao nhiêu phút mỗi ngày cho riêng quy tắc này, và nếu chỉ giữ nhật ký bảy ngày thay vì chín mươi thì câu hỏi nào trong bảng năm sự kiện không còn trả lời được.

9. Chạy `make export-evidence`, rồi `make verify`.

## Sản phẩm phải nộp

```text
cau-hinh/promtail.yaml          chặng chuyển, sáu nguồn
cau-hinh/loki.yaml              nơi giữ, có hạn giữ bạn chọn
docs/duong-di-nhat-ky.md        hiện vật 1, phần văn
evidence/S7/do-tre.csv          hiện vật 1, phần số
evidence/S7/xoa-vet.txt         bề rộng khoảng nguy hiểm
docs/bang-nam-su-kien.yaml      hiện vật 2, chấm nặng nhất
sigma/quy-tac.yml               hiện vật 3, quy tắc
evidence/S7/do-chinh-xac.json   hiện vật 3, phép đo
docs/gia-cua-bao-nham.md        hiện vật 3, dưới 300 từ
evidence/S7/preflight.txt       môi trường
evidence/S7/SHA256SUMS          băm của những tệp trên
```

Nộp bằng cách đẩy lên nhánh `main` của kho cá nhân trước hạn. Mốc thời gian lấy theo dấu thời gian commit trên GitHub, không lấy theo lời khai.

Thư mục `nhat-ky/` **không** nộp. Nó chứa nhật ký thô của năm buổi và có thể mang dữ liệu bạn không muốn đẩy lên, đúng cái cân nhắc mà mục 7.5 của giáo trình bàn tới. Tệp `.gitignore` của kho đã loại nó sẵn.

## Máy chấm kiểm những gì

Chạy `make verify` để tự kiểm trước khi nộp. Bộ chấm chạy đúng mười sáu phép kiểm này trong GitHub Actions, không thêm phép nào.

| Phép kiểm | Đạt khi |
| --- | --- |
| `preflight.txt` đủ mục | ghi đủ kiến trúc CPU, Python, Docker, trạng thái daemon |
| Docker có mặt | dòng phiên bản Docker không ghi KHONG CO |
| Docker daemon chạy | dòng trạng thái không ghi KHONG CHAY |
| Ảnh đã ghim | mọi dòng `image` mang digest, hoặc ít nhất một thẻ phiên bản cụ thể |
| Phạm vi và đặc quyền | cổng neo vào 127.0.0.1, không `privileged`, không `cap_add`, không dùng chung không gian tên với máy thật |
| Trần container | tệp compose khai tối đa 4 dịch vụ |
| Nguồn gắn chỉ đọc | `promtail` gắn `./nhat-ky` kèm `:ro`, và `loki` không gắn thư mục ấy |
| Chặng chuyển đủ nguồn | `promtail.yaml` trỏ về Loki và khai đủ sáu nhãn `buoi`, mỗi nhãn có `__path__` dưới `/nhat-ky/` |
| Độ trễ đo từng chặng | `do-tre.csv` có đủ bốn chặng cộng dòng tổng, không có số âm, và tổng bằng đúng bốn chặng cộng lại |
| Bảng đủ năm dòng | đúng 5 sự kiện, đủ năm buổi S02 tới S06, không trùng, `nguon_du_lieu` hợp lệ |
| Truy vấn và mã chuẩn | mỗi câu mở bằng bộ chọn luồng có nhãn `buoi`, không lấy lịch sử dòng lệnh làm nguồn, mã ATT&CK và CWE nằm trong danh mục của buổi |
| Dòng không tìm được | có ít nhất một, lý do thuộc ba loại đã định, ghi chú từ 15 từ trở lên |
| Quy tắc đọc được | đủ `title`, `logsource`, `detection`, `level`, và `falsepositives` đã điền thực chất |
| Quy tắc nói về hành vi | không lọc theo `id`, `nhan`, `thoi_diem`, và nhìn ít nhất hai trường |
| Phép đo tái lập | bộ chấm tính lại từ quy tắc của bạn và ra đúng con số bạn khai, độ phủ đạt 1,0 và độ chính xác từ 0,80 trở lên |
| Đoạn văn về giá | dài 60 tới 300 từ, dùng đúng số lần bắt nhầm đã đo, có đơn vị phút, và đối chiếu hạn giữ bảy ngày với chín mươi ngày |

Ba phép kiểm cuối trong bảng là **phép xấp xỉ**, không phải phép đo thật. Máy đếm được từ và tìm được một con số trong văn bản, nhưng nó không đọc được lập luận: nó không biết phép tính phút công của bạn có căn cứ hay không, và không biết bạn đã chọn đúng dòng nào trong bảng để nói về hạn giữ. Máy cũng **không** kiểm được điều quan trọng nhất của cả bài, là năm câu truy vấn của bạn có thật sự tìm ra đúng năm sự kiện ấy trong hệ thống của bạn hay không, vì nó không đứng trong hệ thống ấy. Phần đó do người chấm đọc, theo thang chấm ở `rubric.md`.

## Tiêu chí đạt

Máy chấm xanh, **và** bảng năm sự kiện có ít nhất một dòng không tìm được kèm lý do đúng loại, **và** `docs/gia-cua-bao-nham.md` tính ra được số phút mỗi ngày từ chính số lần bắt nhầm mà quy tắc của bạn sinh ra.

## Trước khi hỏi

Đọc `SCOPE.md`. Bài này có một thao tác tấn công, và ranh giới của nó hẹp hơn bạn tưởng.

Ba chỗ mắc kẹt hay gặp, thử theo thứ tự này trước khi hỏi. Truy vấn không ra dòng nào: hỏi một câu rộng chỉ có bộ chọn luồng, để biết nguồn ấy có được nạp hay không; nếu rỗng thì lỗi ở chặng chuyển chứ không ở câu truy vấn. Chặng chuyển báo đã gửi mà kho vẫn trống: xem cửa sổ nhận của kho, vì nhật ký năm buổi trước mang dấu thời gian cũ. Kho không trả lời: bạn đang gọi nó từ máy thật, mà nó cố ý không mở cổng nào ra ngoài mạng compose.

Máy không chạy được thì báo **chậm nhất 24 giờ trước hạn nộp**, đừng đợi tới hạn nộp. Buổi này ăn đầu vào từ năm buổi trước, nên nó là buổi ít có khả năng làm bù trong một tối nhất.

## Chạy trên Windows

Phần lớn lệnh của bài chạy trong container Linux, nên Windows không khác gì. Chỉ các lệnh chạy trực tiếp trên máy bạn (như `make verify`) cần một Python có trên máy. Làm theo thứ tự sau:

1. Mở **Git Bash** (không dùng PowerShell hay CMD), vì Makefile dùng cú pháp của shell Unix. Lý do: PowerShell và CMD không hiểu `$(...)`, `&&` theo cách Makefile cần.
2. Kiểm Python bằng `python --version` hoặc `py --version`. Cài từ python.org và tick ô *Add python.exe to PATH*. Lý do: bản cài từ python.org chỉ có lệnh `python` và `py`, không có `python3`.
3. Không cần tạo lệnh `python3`. Makefile của bài tự thử `python3`, rồi `python`, rồi `py`, và dùng cái đầu tiên chạy được. Lý do: trên Windows `python3` thường là bí danh dẫn tới Microsoft Store và báo "Python was not found", nên Makefile bỏ qua nó.
4. Chạy `make preflight` trước. Dòng `phien ban Python` phải hiện một số phiên bản. Nếu hiện thông báo lỗi thì Python chưa vào PATH, đóng và mở lại Git Bash sau khi cài.
5. Đừng sửa tệp `.sh` hay Makefile bằng Notepad cũ, vì nó có thể đổi kiểu xuống dòng sang CRLF và làm hỏng script trong container. Dùng VS Code và để kiểu xuống dòng là LF.
