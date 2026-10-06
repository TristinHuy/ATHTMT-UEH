# Lab S6. Hai lỗ hổng, hai lớp chặn, và bằng chứng cho từng lớp

**Học phần An toàn hệ thống máy tính · Buổi 6 · Bài cá nhân · 3 phần trăm điểm học phần**

Hạn nộp: 23:59 hôm trước buổi S7; ngày cụ thể ghi ở Master Hub. Nộp trễ dưới 24 giờ nhận 75 phần trăm điểm đã chấm, trễ 24 tới 72 giờ nhận 50 phần trăm, sau 72 giờ nhận 0.

## Mục tiêu, và vì sao bài này hẹp hơn bạn tưởng

Bạn nhận một ứng dụng nhỏ có hai lỗ hổng được chỉ định sẵn, đọc hết trong mười phút. Việc của bạn là đóng cả hai, dựng thêm một lớp chặn thứ hai trong trình duyệt, rồi chứng minh từng lớp đang có hiệu lực bằng thứ đọc được chứ không bằng lời khai.

Chỗ đáng nói là bài không cho bạn đi xa hơn thế. Bên cạnh ứng dụng của bạn có một ứng dụng huấn luyện đầy lỗ hổng do OWASP phát hành, và bạn chỉ được quét nền nó, không được khai thác nó. Ranh giới ấy không phải sự dè dặt. Trục *An toàn ứng dụng web chuyên sâu* của chương trình đặt ở mức hai, mức dùng được ở vận hành, và đây là trục duy nhất nằm ở mức hai trong cả học phần. Kỹ thuật khai thác sâu thuộc học phần Kiểm thử thâm nhập bạn học song song; thiết kế an toàn ứng dụng web đầy đủ và bộ tiêu chí thẩm định theo mức bảo đảm thuộc học phần tự chọn An toàn ứng dụng Web ở học kì 6.

Điều buổi này thật sự dạy nằm ở chỗ khác, và nó khó hơn việc khai thác. Một lỗ hổng đóng được bằng một dòng mã, một lỗ hổng đóng được bằng hai dòng cấu hình, và nhầm loại thì bạn sẽ sửa đúng thứ ở sai chỗ. Bài chia bốn chỗ làm việc thành một chỗ trong mã và ba chỗ trong tệp chính sách đúng vì lý do đó.

## Hai lỗ hổng, và chúng khác nhau ở đâu

**LH-1** nằm ở trang tra cứu. Chuỗi người dùng gõ vào được ghép thẳng vào thân trang mà chưa mã hóa theo ngữ cảnh, nên trình duyệt đọc nó như một phần của tài liệu chứ không như một đoạn chữ. Đây là CWE-79 trong CWE List 4.20.

**LH-2** nằm ở biểu mẫu đổi địa chỉ. Trình duyệt tự đính cookie phiên vào mọi yêu cầu gửi tới ứng dụng, kể cả yêu cầu do trang của người khác khởi xướng, nên một biểu mẫu ẩn trên trang ấy vẫn ra lệnh được nhân danh người đang đăng nhập. Đây là CWE-352, và mức trừu tượng của nó là Composite, tức một điểm yếu chỉ thành lỗ hổng khi nhiều điều kiện cùng có mặt. Chi tiết ấy giải thích bằng chính ngôn ngữ của danh mục vì sao đề bắt bạn dựng hai lớp chặn chứ không một.

## Việc phải làm

Thứ tự dưới đây không phải gợi ý. Việc 5 chỉ thu được bằng chứng khi việc 6 chưa làm, và đảo hai việc ấy là cách hỏng bài phổ biến nhất của buổi này.

1. **Nhận kho, dựng môi trường.** `make preflight`, rồi `make up`. Bước preflight còn nới quyền ghi cho `evidence/S6/`, vì bộ quét chạy dưới một người dùng khác bạn và báo cáo của nó phải rơi được ra ngoài container.

2. **Đọc trước khi sửa.** `ung-dung/ung_dung.py` và `ung-dung/chinh-sach.yaml`, hết một lượt. Bốn chỗ bạn sửa đều mang nhãn `CHỖ LÀM VIỆC CỦA BẠN` và mỗi chỗ có sẵn câu hỏi bạn phải trả lời trước khi gõ. Bạn không vá được thứ bạn chưa đọc.

3. **Đo trạng thái khởi đầu.** `make attack NHAN=truoc-khi-va` gửi ba yêu cầu vào ứng dụng của chính bạn trên `127.0.0.1` và ghi lại câu trả lời. Không yêu cầu nào trong ba yêu cầu ấy phá gì; chúng đúng là ba yêu cầu bộ chấm sẽ gửi khi bạn chạy `make verify`.

4. **Quét nền và quét mã, lần thứ nhất.** `make quet NHAN=truoc` rồi `make quet-ma NHAN=truoc`. Lần quét mã phải ĐỎ ở bước này. Một phép kiểm chưa bao giờ đỏ thì có thể đang kiểm nhầm chỗ, nên bằng chứng của bài gồm cả lần nó đỏ.

5. **Bật chính sách nội dung ở chế độ chỉ báo cáo, rồi thu một vi phạm thật.** Khai bốn chỉ thị ở khối `csp` trong `chinh-sach.yaml`, giữ `che_do: bao-cao`, chạy `make defend`. Mở trình duyệt vào `http://127.0.0.1:8081/thu/tim-kiem?q=<script>alert(1)</script>`, rồi `make thu-bao-cao`.

   Chế độ chỉ báo cáo là chặng phải đi qua chứ không phải chặng dừng lại. Bật thẳng chế độ cưỡng chế lên một trang đang chạy thì trang gãy ngay, và cái gãy ấy rơi vào người dùng chứ không rơi vào bạn. Cần gạt này có hai đầu: thu báo cáo càng lâu thì càng ít gãy mà cửa càng mở lâu.

   Sau khi đã có báo cáo, đổi `che_do` sang `cuong-che` và mở lại đúng địa chỉ ấy. Lần này đoạn mã không chạy nữa, dù chuỗi vẫn nằm trong trang. Đó là toàn bộ ý nghĩa của lớp thứ hai: nó không ngăn chuỗi lạ vào trang, nó lấy đi phần thưởng của việc đưa được chuỗi lạ vào.

6. **Đóng LH-1 trong mã.** Một dòng ở chỗ làm việc `việc 1`. Thư viện chuẩn đã có sẵn hàm cần dùng và tệp đã nhập nó ở đầu. Nếu bạn thấy mình đang viết một bộ lọc danh sách đen thì hãy dừng lại: mã hóa theo ngữ cảnh giữ nguyên chữ người dùng gõ và lấy đi quyền lực của nó, còn bộ lọc lấy đi cả hai và vẫn hở ở khuôn nó chưa nghĩ tới. Bộ chấm kiểm cả hai chiều ấy.

7. **Đóng LH-2 bằng hai nửa.** Nửa thứ nhất là thuộc tính của cookie phiên, do trình duyệt áp. Nửa thứ hai là phép đối chiếu phía máy chủ, do chính bạn áp. Đề bắt làm cả hai vì một mặc định an toàn nằm trong phần mềm mà bạn không phát hành thì chưa phải biện pháp của bạn: bạn không quyết định được phiên bản trình duyệt người dùng chạy, và không được báo khi nhà phát hành đổi ý.

8. **Đo lại.** `make defend`, rồi `make attack NHAN=sau-khi-va`, `make quet NHAN=sau`, `make quet-ma NHAN=sau`. Lần quét mã phải XANH ở bước này.

9. **Xếp loại cảnh báo và tính con số của riêng bạn.** Chép `docs/xep-loai-canh-bao.mau.yaml` thành `docs/xep-loai-canh-bao.yaml`, điền mã chuẩn của hai lỗ hổng, rồi xếp từng cảnh báo của lần quét nền ứng dụng huấn luyện vào ba nhóm: sửa được bằng cấu hình, sửa được bằng mã, và không phải cảnh báo thật.

   Không bỏ dòng nào. Mẫu số của tỉ lệ p là tổng số cảnh báo, nên bỏ bớt những dòng khó xếp làm p đẹp lên một cách giả tạo. Nhóm thứ ba tốn kém nhất khi xếp sai, vì một cảnh báo thật bị đẩy vào đó thì không ai quay lại nhìn nó nữa; mỗi dòng thuộc nhóm ấy phải kèm lý do từ tám từ trở lên.

10. **Viết đoạn đánh đổi.** `docs/danh-doi.md`, từ 60 tới 300 từ, trả lời hai câu. Nhóm cảnh báo nào bạn xếp nhầm nhiều nhất, và bạn biết mình nhầm nhờ đâu? Nếu chỉ có một giờ mỗi tuần cho việc này thì bạn tiêu giờ ấy vào đâu? Đoạn văn phải đứng trên số đo của chính bạn: gọi t là số phút phân loại một cảnh báo, thì công sức cho mỗi thay đổi thật là t chia p phút.

11. `make export-evidence`, rồi `make verify`. Bước xuất bằng chứng lấy nhật ký ứng dụng ra khỏi container, nên chạy nó TRƯỚC `make down`.

## Sản phẩm phải nộp

```
ung-dung/ung_dung.py            việc 6, một dòng
ung-dung/chinh-sach.yaml        việc 5 và việc 7, ba khối
docs/xep-loai-canh-bao.yaml     hiện vật chấm nặng nhất của phần máy
docs/danh-doi.md                hiện vật văn, dưới 300 từ
evidence/S6/preflight.txt       môi trường
evidence/S6/thu-lo-hong-truoc-khi-va.txt   trạng thái khởi đầu
evidence/S6/thu-lo-hong-sau-khi-va.txt     trạng thái cuối
evidence/S6/quet-truoc.json     quét nền, trước
evidence/S6/quet-sau.json       quét nền, sau
evidence/S6/quet-muc-tieu.json  nguồn của bảng xếp loại
evidence/S6/semgrep-truoc.json  quét mã, phải đỏ
evidence/S6/semgrep-sau.json    quét mã, phải xanh
evidence/S6/bao-cao-csp.jsonl   vi phạm thu ở chế độ chỉ báo cáo
evidence/S6/nhat-ky.txt         nhật ký ứng dụng, và là đầu vào của buổi S7
evidence/S6/SHA256SUMS          băm của những tệp trên
```

Nộp bằng cách đẩy lên nhánh `main` của kho cá nhân trước hạn. Mốc thời gian lấy theo dấu thời gian commit trên GitHub, không lấy theo lời khai.

Bản báo cáo dạng HTML của lần quét không nộp, và `.gitignore` đã loại sẵn nó. Nó nhúng nguyên văn phần thân của những phản hồi mà bộ quét nhận được, gồm cả cookie phiên của bạn. Bản JSON đủ cho việc chấm và không mang phần ấy.

## Máy chấm kiểm những gì

Chạy `make verify` để tự kiểm trước khi nộp. Bộ chấm chạy đúng mười sáu phép kiểm này trong GitHub Actions, không thêm phép nào.

| Phép kiểm | Đạt khi |
|---|---|
| `preflight.txt` đủ mục | ghi đủ kiến trúc CPU, Python, Docker, trạng thái daemon |
| Máy dùng được Docker | dòng phiên bản không ghi KHONG CO và dòng trạng thái không ghi KHONG CHAY |
| Ảnh đã ghim | mọi dòng `image` mang digest, hoặc ít nhất một thẻ phiên bản cụ thể |
| Phạm vi và đặc quyền | cổng neo vào 127.0.0.1, không `privileged`, không `cap_add`, không dùng chung không gian tên với máy thật, không gắn ổ cắm của Docker |
| Trần container | tệp compose khai tối đa 4 dịch vụ |
| Đích của bộ quét | mọi đích quét là tên dịch vụ trong mạng compose, và không gọi tập lệnh quét chủ động |
| LH-1 đã đóng | chuỗi thử không còn nguyên văn trong trang, và dạng đã mã hóa của nó có mặt |
| Cookie phiên | có HttpOnly, có SameSite, và SameSite không phải None |
| LH-2 đã đóng | cả ba dạng yêu cầu giả mạo đều nhận 403, và địa chỉ trong hồ sơ không đổi |
| Vẫn phục vụ người dùng thật | từ khóa lành hiện lại nguyên văn, và yêu cầu hợp lệ đúng gốc đúng thẻ được nhận |
| Chính sách nội dung | tiêu đề ở chế độ cưỡng chế, đủ bốn chỉ thị, script-src có nonce và không có `unsafe-inline` |
| Số dùng một lần | nonce dài từ 16 ký tự và khác nhau ở mỗi lần tải trang |
| Hai lần quét | hai báo cáo nền khác nhau, và lần quét mã đỏ ở bản trước, xanh ở bản sau |
| Bảng xếp loại | mã chuẩn của hai lỗ hổng đúng, mọi cảnh báo được xếp loại, và p tính lại được từ chính bảng |
| Bằng chứng lớp thứ hai | có ít nhất một báo cáo vi phạm thật, và nhật ký có dòng tương ứng |
| Đoạn đánh đổi | dài 60 tới 300 từ, dùng đúng hai con số của bảng, và có đơn vị phút |

Phép kiểm cuối trong bảng là **phép xấp xỉ**, không phải phép đo thật, và điều đó nói thẳng ngay trong mã của nó. Máy đếm được từ và tìm được một con số trong văn bản, nhưng nó không đọc được lập luận: nó không biết phép tính công sức của bạn có căn cứ hay không, và không biết nhóm bạn khai là xếp nhầm nhiều nhất có đúng là nhóm ấy hay không. Phép kiểm bảng xếp loại cũng chỉ đo được phần số học và phần mã chuẩn, không đo được chất lượng của từng quyết định xếp loại. Hai phần ấy do người chấm đọc, theo thang chấm ở `rubric.md`.

Bảy phép kiểm ở giữa bảng thì ngược lại, và đó là phần mạnh nhất của bộ chấm bài này: chúng dựng chính ứng dụng của bạn lên trên một cổng tạm của `127.0.0.1` rồi gửi những yêu cầu thật, nên thứ quyết định xanh hay đỏ là phản hồi mã của bạn trả về. Bảy phép ấy không cần Docker, nên máy hỏng phần container vẫn tự kiểm được phần vá.

## Tiêu chí đạt

Máy chấm xanh, **và** bảng xếp loại có ít nhất một dòng thuộc nhóm không phải cảnh báo thật kèm lý do đọc được, **và** `docs/danh-doi.md` tính ra được số phút công cho mỗi thay đổi thật từ chính tỉ lệ p mà bảng của bạn sinh ra.

## Trước khi hỏi

Đọc `SCOPE.md`. Buổi này đặt vào tay bạn một bộ quét web, và phạm vi cho phép của nó chặt hơn mọi buổi trước.

Bốn chỗ mắc kẹt hay gặp, thử theo thứ tự này trước khi hỏi. Sửa `chinh-sach.yaml` mà không thấy gì đổi: ứng dụng đọc chính sách một lần lúc khởi động, nên phải `make defend`. Thư mục bằng chứng trống sau khi quét: bộ quét chạy dưới người dùng khác bạn và không ghi được vào thư mục, chạy lại `make preflight`. Trình duyệt không gửi báo cáo vi phạm nào: kiểm xem `che_do` còn là `bao-cao` không, và kiểm xem LH-1 đã bị vá chưa, vì sau khi vá thì không còn gì để trình duyệt chặn. Bộ kiểm báo không gọi được ứng dụng: chạy thẳng `python3 ung-dung/ung_dung.py` và đọc thông báo lỗi, thường là một lỗi cú pháp trong tệp chính sách.

Máy không chạy được thì báo **chậm nhất 24 giờ trước hạn nộp**, đừng đợi tới hạn nộp. Buổi S7 lấy nhật ký của buổi này làm một trong sáu nguồn, nên một buổi S6 bỏ dở kéo theo một phần buổi S7.

## Chạy trên Windows

Phần lớn lệnh của bài chạy trong container Linux, nên Windows không khác gì. Chỉ các lệnh chạy trực tiếp trên máy bạn (như `make verify`) cần một Python có trên máy. Làm theo thứ tự sau:

1. Mở **Git Bash** (không dùng PowerShell hay CMD), vì Makefile dùng cú pháp của shell Unix. Lý do: PowerShell và CMD không hiểu `$(...)`, `&&` theo cách Makefile cần.
2. Kiểm Python bằng `python --version` hoặc `py --version`. Cài từ python.org và tick ô *Add python.exe to PATH*. Lý do: bản cài từ python.org chỉ có lệnh `python` và `py`, không có `python3`.
3. Không cần tạo lệnh `python3`. Makefile của bài tự thử `python3`, rồi `python`, rồi `py`, và dùng cái đầu tiên chạy được. Lý do: trên Windows `python3` thường là bí danh dẫn tới Microsoft Store và báo "Python was not found", nên Makefile bỏ qua nó.
4. Chạy `make preflight` trước. Dòng `phien ban Python` phải hiện một số phiên bản. Nếu hiện thông báo lỗi thì Python chưa vào PATH, đóng và mở lại Git Bash sau khi cài.
5. Đừng sửa tệp `.sh` hay Makefile bằng Notepad cũ, vì nó có thể đổi kiểu xuống dòng sang CRLF và làm hỏng script trong container. Dùng VS Code và để kiểu xuống dòng là LF.
