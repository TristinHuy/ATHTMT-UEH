# Bộ chứng thư của bài này

Thư mục này bắt đầu rỗng, và phần lớn công của bài nằm ở chỗ làm nó đầy. Bộ kiểm
đọc thẳng các tệp dưới đây, nên tên tệp là một phần của đề, không phải gợi ý.

```
pki/ca/ca.crt              chứng thư của tổ chức cấp chứng thư nội bộ do bạn dựng
pki/ca/ca.key              khóa riêng của nó
pki/may-chu/may-chu.crt    chứng thư máy chủ, tên trên chứng thư phải là may-chu
pki/may-chu/may-chu.key
pki/khach/khach.crt        chứng thư khách, dùng cho phép kiểm K3
pki/khach/khach.key
pki/ca-ngoai/ca-ngoai.crt      một tổ chức cấp chứng thư THỨ HAI, hoàn toàn riêng
pki/ca-ngoai/ca-ngoai.key
pki/ca-ngoai/khach-ngoai.crt   chứng thư khách do tổ chức thứ hai cấp
pki/ca-ngoai/khach-ngoai.key
```

Bốn tệp cuối là chỗ nhiều người hỏi vì sao phải làm. Chúng tồn tại để trả lời một
câu hỏi mà một chứng thư hợp lệ không trả lời được: chữ ký của một tổ chức nào đó
chứng minh điều gì, khi bất kỳ ai cũng dựng được một tổ chức như vậy trong ba mươi
giây? Dựng CA thứ hai xong, bạn cầm trong tay một chứng thư còn hạn, đúng cú pháp,
ký hợp lệ, và hoàn toàn vô giá trị đối với máy chủ của bạn. Khoảng cách giữa "hợp
lệ" và "được tôi tin" chính là chỗ §3.3 gọi là kho tin cậy.

Một lệnh mẫu cho tổ chức nội bộ, để bạn có chỗ bắt đầu. Phần còn lại là việc của
bạn, vì chép xong mười lệnh mà không biết mình vừa ký cái gì thì bài này chưa dạy
được gì.

```bash
mkdir -p pki/ca
openssl req -x509 -noenc -newkey ec -pkeyopt ec_paramgen_curve:P-256 \
  -days 3650 -subj "/CN=CA noi bo lab S03" \
  -addext "basicConstraints=critical,CA:TRUE,pathlen:0" \
  -addext "keyUsage=critical,keyCertSign,cRLSign" \
  -keyout pki/ca/ca.key -out pki/ca/ca.crt
```

Ba điều bộ kiểm sẽ hỏi tới, nên nghĩ trước khi gõ.

Tên trên chứng thư máy chủ phải nằm ở phần `subjectAltName`, dạng `DNS:may-chu`,
vì đó là tên máy khách gọi tới trong mạng compose. Đặt tên ở trường `CN` mà bỏ
`subjectAltName` thì các thư viện hiện nay không so tên nữa, và phép kiểm K1 sẽ
đỏ.

Hạn của chứng thư máy chủ không được quá 400 ngày. Con số này không phải luật tự
nhiên, nó là quy ước của học phần, đặt để buộc bạn chạm vào phép tính ở §3.4: hạn
càng dài thì một chứng thư bị lộ càng sống lâu, hạn càng ngắn thì công gia hạn
càng dày.

Khóa riêng không bao giờ rời khỏi máy bạn theo bất kỳ đường nào khác ngoài thư
mục này. Ở bài học này chúng vô hại vì chẳng bảo vệ gì thật, nhưng thói quen thì
hình thành từ những lần vô hại.
