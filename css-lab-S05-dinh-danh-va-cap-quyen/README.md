# Lab S5. Đăng nhập một lần và cấp quyền theo chính sách

**Học phần An toàn hệ thống máy tính · Buổi 5 · Bài cá nhân · 3 phần trăm điểm học phần**

Hạn nộp: 23:59 hôm trước buổi S6; ngày cụ thể ghi ở Master Hub. Nộp trễ dưới 24 giờ nhận 75 phần trăm điểm đã chấm, trễ 24 tới 72 giờ nhận 50 phần trăm, sau 72 giờ nhận 0.

## Mục tiêu

Sinh viên dựng một vùng định danh dùng chung cho nhiều dịch vụ, rồi chứng minh rằng dịch vụ của mình từ chối đúng những tấm thẻ mà nó phải từ chối.

Vế thứ hai là lý do bài này tồn tại. Bật đăng nhập một lần bằng Keycloak chỉ mất vài giờ, và phần lớn tài liệu hướng dẫn dừng ở chỗ đăng nhập thành công: tên người dùng hiện ra và dịch vụ trả về dữ liệu. Một lần đăng nhập thành công không cho biết dịch vụ xử lý một tấm thẻ hỏng ra sao, trong khi thẻ hỏng mới là thứ kẻ tấn công gửi tới.

Ba cạm bẫy ở §5.5 của giáo trình có chung một đặc điểm: chúng là lỗi BỎ SÓT, không phải lỗi gõ sai. Khi dịch vụ tin trường `alg` in trong chính tấm thẻ, người gửi được tự chọn cách thẻ của mình bị kiểm. Thiếu bước so tên người nhận thì dịch vụ nhận cả thẻ mà người dùng đã cấp cho một ứng dụng khác. Còn nếu hạn thẻ không được kiểm ở phía máy chủ, tấm thẻ vẫn dùng được sau khi người dùng đăng xuất. Dù thiếu cả ba phép kiểm này, dịch vụ vẫn chạy bình thường trong sử dụng hằng ngày, và hậu quả chỉ lộ ra khi có người gửi thử một tấm thẻ hỏng.

Lỗi bỏ sót chỉ được phát hiện khi có một yêu cầu thử đi qua đúng chỗ bị bỏ sót, nên bài này chấm bằng năm phép kiểm âm và đặt trọng số cao nhất cho chúng.

## Việc phải làm

1. Bộ khung của lab này nằm trong thư mục `bai-nop/S5/` của kho cá nhân trên GitHub. Kéo bản mới nhất của kho về máy bằng `git pull`, mở thư mục `bai-nop/S5/` trong VS Code, rồi chạy hai lệnh trong thư mục đó: `pip install -r tests/yeu-cau.txt` để cài thư viện cho bộ kiểm, và `make preflight` để ghi kiến trúc máy, phiên bản Python và trạng thái Docker vào `evidence/S5/preflight.txt`. Mọi lệnh `make` của bài đều chạy trong `bai-nop/S5/`, vì bộ chấm trên GitHub Actions chạy bộ kiểm của buổi S5 trong đúng thư mục này. Tệp `tests/yeu-cau.txt` ghim bốn thư viện theo phiên bản chính xác, và ba thư viện đọc và ký thẻ trong số đó trùng phiên bản với `dich-vu/requirements.txt`, để hành vi kiểm chữ ký trên máy sinh viên và trong container là một.

2. Chạy `make up`. Vùng định danh khởi động và nạp `cau-hinh/vung-dinh-danh.json` ở trạng thái khởi đầu, tức trạng thái được cố ý cấu hình lỏng. Mở `http://127.0.0.1:8080`, đăng nhập bằng tài khoản quản trị khai trong `docker-compose.yml`, rồi xem chính sách mật khẩu, chính sách một lần một mã và cấu hình thân khách `dich-vu-ho-so`. Các cấu hình này cần được đọc trước khi sửa, vì việc 4 và việc 5 sửa chính chúng.

3. Chạy `make attack` **trước khi** viết bất kỳ dòng nào của phần kiểm thẻ. Lệnh này chạy sáu phép kiểm nhắm vào dịch vụ của chính sinh viên, trong đó có bốn tấm thẻ hỏng theo bốn kiểu khác nhau. Khi hai hàm ở việc 6 và việc 7 chưa được viết, dịch vụ chạy ở chế độ khởi đầu: nó tách tập khai ra khỏi tấm thẻ, tin mọi thứ đọc được trong đó, và gắn một dòng cảnh báo vào mỗi câu trả lời. Đọc cột thực tế và dòng cảnh báo đó, rồi giữ lại `evidence/S5/truoc-khi-va.txt` cùng thư mục `evidence/S5/truoc-khi-va/`, vì đây là bằng chứng duy nhất về trạng thái trước khi vá để so với trạng thái cuối buổi.

   Ở bước này phép N3 báo `CHUA_CHAY`, và đó không phải lỗi: hạn thẻ ở trạng thái khởi đầu là một giờ, dài hơn mức 305 giây mà tập lệnh chờ, nên yêu cầu của phép N3 chưa được gửi. Một tấm thẻ sống lâu tới mức không thể chờ nó hết hạn trong một buổi lab cũng là lý do việc 5 yêu cầu rút hạn thẻ.

4. **Kho mật khẩu.** Đổi hàm băm sang hàm tốn bộ nhớ, đặt ba tham số của nó ở `docker-compose.yml`, và gỡ hai luật mà NIST SP 800-63B §3.1.1.2 cấm. Đo trước khi chọn số: chạy `make do-argon2 NHAN=truoc-khi-doi`, đổi tham số, rồi chạy lại với `NHAN=sau-khi-doi`. RFC 9106 §4 đưa ra hai bộ tham số làm điểm xuất phát. Tốc độ máy của mỗi sinh viên khác với máy dùng khi viết chuẩn, nên con số cuối cùng do sinh viên chọn dựa trên phép đo của mình.

5. **Yếu tố thứ hai.** Bật một lần một mã, đặt nó thành hành động bắt buộc chứ không phải tùy chọn, và bật giới hạn số lần hỏi. Sau đó ghi danh yếu tố thứ hai bằng trình duyệt cho tài khoản `an-nv` và lưu bí mật vào `cau-hinh/totp-bi-mat.txt`. Tệp này nằm trong `.gitignore` và **không** được commit, vì một bí mật chia sẻ nằm trong kho mã chính là lỗi mà §5.5 nêu tên. Cũng trong `cau-hinh/vung-dinh-danh.json`, đặt `accessTokenLifespan` trong khoảng 60 tới 300 giây, và đóng các chỗ để ngỏ của thân khách `dich-vu-ho-so`: ký tự đại diện `*` trong đường chuyển hướng và nguồn gốc web, luồng ngầm đang bật, và PKCE chưa đòi `S256`. Bộ chấm kiểm các điểm này ở dòng *thân khách và hạn thẻ*, và hạn thẻ ngắn cũng là điều kiện để phép N3 chạy xong trong buổi lab.

6. **Vai và chính sách.** Viết `cau-hinh/chinh-sach.yaml` sao cho ba mệnh đề sau đúng, và chỉ ba mệnh đề đó. Nhân viên đọc được hồ sơ trong đơn vị của mình, và chỉ đọc. Trưởng đơn vị đọc và xóa được hồ sơ trong đơn vị của mình. Quản trị đọc được hồ sơ của mọi đơn vị. Tiếp theo, viết hàm `quyet_dinh` trong `dich-vu/kiem_the.py` để thi hành đúng bảng này, với mặc định là từ chối: một yêu cầu không khớp quy tắc nào thì bị chặn.

7. **Kiểm thẻ.** Viết hàm `kiem_the` trong cùng tệp. Ba cạm bẫy nêu ở mục Mục tiêu tương ứng với ba phép kiểm mà hàm phải có, và hợp đồng của hàm được ghi ở đầu tệp. Tên hai hàm và tên lớp ngoại lệ `TheKhongHopLe` phải giữ nguyên, vì dịch vụ trong container và bộ chấm đều gọi đúng ba tên đó.

8. Chạy `make defend` để nạp lại dịch vụ, rồi `make nam-phep-kiem`. Lệnh sau thực hiện sáu lần gọi thật, mỗi lần ghi ra hai tệp: `evidence/S5/kiem-*.txt` là bản tóm tắt máy đọc được, còn `evidence/S5/tho/` giữ nhật ký thô cho người chấm. Phán quyết được tính từ mã HTTP thật, nên sinh viên không tự ghi dòng kết quả vào các tệp này.

| Phép | Chiều | Nó chứng minh điều gì | Mã điểm yếu |
|---|---|---|---|
| P1 | dương | dịch vụ vẫn phục vụ người có quyền, trong đơn vị của họ | |
| N1 | âm | thẻ khai thuật toán rỗng thì bị chặn | CWE-347 |
| N2 | âm | thẻ ký bằng khóa khác thì bị chặn | CWE-347 |
| N3 | âm | thẻ thật nhưng đã quá hạn thì bị chặn | CWE-613 |
| N4 | âm | thẻ thật nhưng phát cho thân khách khác thì bị chặn | CWE-863 |
| N5 | âm | danh tính hợp lệ mà vượt phạm vi đơn vị thì bị chặn | CWE-863 |

Phép N3 phải đợi tấm thẻ hết hạn, nên bước này kéo dài đúng bằng hạn thẻ đã đặt ở việc 5. Quãng đợi này chính là con số mà việc 9 yêu cầu đo.

9. Viết `docs/danh-doi.md`, dài từ 120 tới 300 chữ, trả lời hai câu hỏi. Câu thứ nhất: sau khi quyền của một tài khoản bị thu hồi, tấm thẻ đã phát còn dùng được bao lâu, đo bằng đồng hồ chứ không suy từ tài liệu? Câu thứ hai: muốn rút con số đó xuống một phần mười thì phải trả giá bằng gì, tính bằng số lần gọi thêm mỗi phút giữa hai dịch vụ? Câu thứ hai yêu cầu phát biểu một quyết định an toàn dưới dạng đánh đổi giữa hai đại lượng đo được.

10. Chạy `make export-evidence` rồi `make verify`. Sau đó nộp bằng ba lệnh chạy từ thư mục gốc của kho: `git add bai-nop/S5`, `git commit -m "S5: định danh và cấp quyền"`, `git push`. Trước khi commit, chạy `git status` và kiểm rằng `cau-hinh/totp-bi-mat.txt` không có trong danh sách tệp sẽ commit; `.gitignore` của bài đã loại tệp này, và bước kiểm chỉ để chắc chắn bí mật không lọt vào lịch sử kho. Đẩy lên nhánh `main` trước hạn. Bài nộp là trạng thái của nhánh `main` trên GitHub tại thời điểm hạn nộp, nên đẩy lại nhiều lần trước hạn không bị trừ điểm. Lệnh `git push --force` không được dùng, vì lịch sử commit là bằng chứng nộp đúng hạn.

## Sản phẩm phải nộp

```
docker-compose.yml              ba tham số hàm băm, cổng vẫn neo vào 127.0.0.1
cau-hinh/vung-dinh-danh.json    kho mật khẩu, yếu tố thứ hai, thân khách, hạn thẻ
cau-hinh/chinh-sach.yaml        bảng chính sách cấp quyền
dich-vu/kiem_the.py             hai hàm sinh viên viết
docs/danh-doi.md                đoạn từ 120 tới 300 chữ
evidence/S5/preflight.txt       kết quả make preflight
evidence/S5/kiem-P1.txt         phán quyết chiều dương
evidence/S5/kiem-N1..N5.txt     năm phán quyết chiều âm
evidence/S5/nhat-ky-dich-vu.log nhật ký kiểm thẻ của dịch vụ, lab S7 dùng lại
evidence/S5/tho/                nhật ký thô của sáu lần gọi
evidence/S5/do-argon2.txt       hai lần đo, trước và sau khi đổi tham số
evidence/S5/SHA256SUMS          băm của toàn bộ bằng chứng
```

`cau-hinh/totp-bi-mat.txt` **không** nằm trong danh sách trên, vì bí mật này không được đưa vào kho. Mốc thời gian lấy theo dấu thời gian commit trên GitHub, không lấy theo lời khai.

## Máy chấm kiểm những gì

Chạy `make verify` để tự kiểm trước khi nộp. Bộ chấm chạy đúng mười sáu phép kiểm này trong GitHub Actions và không thêm phép nào.

| Nhóm | Phép kiểm | Đạt khi |
|---|---|---|
| Phạm vi | ảnh ghim theo phiên bản cụ thể | không ảnh nào dùng thẻ trôi nổi |
| Phạm vi | cổng và đặc quyền | mọi cổng neo vào `127.0.0.1`, không `privileged`, không `network_mode: host`, không `cap_add` |
| Phạm vi | trần bốn container | tệp compose khai nhiều nhất bốn dịch vụ |
| Kiểm thẻ | thẻ hợp lệ được nhận | trả về tập khai có đủ `sub`, `aud`, `exp`, vai |
| Kiểm thẻ | thẻ khai thuật toán rỗng bị từ chối | ném `TheKhongHopLe` |
| Kiểm thẻ | thẻ ký bằng khóa khác bị từ chối | ném `TheKhongHopLe` |
| Kiểm thẻ | thẻ quá hạn bị từ chối | ném `TheKhongHopLe` |
| Kiểm thẻ | thẻ phát cho thân khách khác bị từ chối | ném `TheKhongHopLe` |
| Cấp quyền | cho qua đúng vai, chặn đúng thao tác | nhân viên đọc được, nhân viên không xóa được, trưởng đơn vị xóa được |
| Cấp quyền | chặn đúng phạm vi đơn vị | người của đơn vị này không đọc được hồ sơ đơn vị kia, còn quản trị thì được |
| Cấu hình | kho mật khẩu | hàm băm tốn bộ nhớ, ba tham số có mặt, bộ nhớ từ 64 MiB trở lên, không còn luật xoay vòng |
| Cấu hình | yếu tố thứ hai | một lần một mã bật, đặt làm hành động mặc định, và có giới hạn số lần hỏi |
| Cấu hình | thân khách và hạn thẻ | không đường chuyển hướng đại diện, không luồng ngầm, có PKCE, hạn thẻ từ 60 tới 300 giây |
| Bằng chứng | preflight đủ mục | ghi đủ máy, Python, Docker, và daemon đang chạy |
| Bằng chứng | sáu phép kiểm đủ và đúng | sáu tệp kết quả đủ khóa, có nhật ký thô, và phán quyết đúng như bảng ở việc 8 |
| Bằng chứng | hai hiện vật văn bản | `do-argon2.txt` có hai lần đo, `danh-doi.md` dài từ 120 tới 300 từ |

Năm phép kiểm nhóm *Kiểm thẻ* và hai phép nhóm *Cấp quyền* là **phép đo thật**: bộ chấm giữ khóa riêng, tự dựng thẻ, rồi gọi thẳng hàm của sinh viên. Bảy phép này không cần Docker, và không thể đạt bằng cách đoán vì bộ chấm sinh cặp khóa mới ở mỗi lần chạy.

Phép kiểm ở dòng cuối bảng có giới hạn cần nói rõ. Phép đếm từ của `danh-doi.md` chỉ là phép xấp xỉ mà máy làm được: nó phát hiện được bài không nộp hoặc bài chỉ có vài câu, nhưng không phân biệt được một lập luận chặt với một đoạn kể lại việc đã làm. Phép đếm số lần đo trong `do-argon2.txt` cũng chỉ xác nhận có hai dòng đo, không xác nhận sinh viên đã so sánh hai dòng đó. Phần này do người chấm đọc theo `rubric.md`.

Bộ chấm còn một giới hạn khác: nó đọc `cau-hinh/vung-dinh-danh.json` chứ không hỏi máy chủ danh tính đang chạy, nên nó xác nhận cấu hình đúng hình dạng nhưng không xác nhận máy chủ đã khởi động được với cấu hình đó. Phần này do `make up` và `make nam-phep-kiem` kiểm chứng, và đó là lý do bằng chứng của sáu lần gọi vẫn nằm trong bài nộp.

## Tiêu chí đạt

Mười sáu phép kiểm xanh, **và** năm phán quyết chiều âm trong `evidence/S5/` thật sự là `BI_TU_CHOI` chứ không phải chưa chạy. Một bài chỉ có chiều dương cho thấy dịch vụ vẫn phục vụ người có quyền, nhưng chưa cho thấy lớp phòng thủ nào đang bật.

## Trước khi hỏi

Đọc `SCOPE.md` trước khi chạy `make attack`. Bài này có thao tác gửi thẻ giả vào một dịch vụ, nên phạm vi ghi trong tệp đó là điều kiện bắt buộc của bài: dịch vụ nhận thẻ giả phải là dịch vụ của chính sinh viên, chạy trong mạng compose của bài, còn cùng thao tác đó nhắm vào một hệ thống khác là truy cập trái phép.

`CHEATSHEET.md` liệt kê mười hai lệnh hay dùng, mỗi lệnh kèm hậu quả nếu gõ sai.

Có ba chỗ thường làm mất nhiều thời gian. Vùng định danh chỉ nạp `cau-hinh/vung-dinh-danh.json` ở lần dựng đầu, nên sau khi sửa tệp này phải chạy `make down` rồi `make up`; khởi động lại container bằng `restart` không nạp lại cấu hình. Bộ ánh xạ tên người nhận trong tệp cấu hình do đề bài cho sẵn và không được xóa, vì thiếu nó thì thẻ thật cũng không mang tên dịch vụ hồ sơ ở trường `aud`. Lệnh `make nam-phep-kiem` chạy lâu bằng hạn thẻ đã đặt, nên trong lúc làm bài, đặt hạn 60 giây giúp mỗi lần thử chỉ phải đợi khoảng một phút.

Giáo trình §5.5 nói tới một bộ máy chính sách chạy ngoài mã dịch vụ. Bài lab không dựng bộ máy này, theo quy tắc B7 của ADR-0003: thứ gì bộ chấm không kiểm được bằng máy thì không đưa vào bài lab; phần cấp quyền theo thuộc tính được giữ ở mức khái niệm, cộng một bảng chính sách nhỏ chạy thử được. Nguyên lý vẫn giữ nguyên khi đổi công cụ: chính sách nằm ngoài mã nghiệp vụ, trong một tệp chạy thử được, kể cả với những yêu cầu phải bị từ chối. Kho bí mật ở §5.7 cũng không có trong bài này mà chuyển sang buổi S8, cùng phần chuỗi cung ứng, vì bài lab này đã chạm trần bốn container.

Máy không chạy được bài thì sinh viên báo trên Discussions của học phần chậm nhất **24 giờ trước hạn nộp**, kèm tệp `evidence/S5/preflight.txt`. Nếu `make up` báo lỗi kéo ảnh, chạy `bash ghim-digest.sh --sua` trên máy có mạng trước, rồi thử lại. Sinh viên chưa quen git hoặc VS Code đọc tài liệu "Làm lab bằng VS Code và git" (bản 2) trong mục `00_Thong-tin-chung` của thư mục học liệu chia sẻ cho lớp.
