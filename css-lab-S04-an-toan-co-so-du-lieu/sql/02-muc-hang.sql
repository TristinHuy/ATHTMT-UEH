-- Bước 2. An toàn mức hàng, và ràng buộc người tạo khác người duyệt.
--
-- BẠN VIẾT TỆP NÀY.
--
-- Bước 1 trả lời câu hỏi ai đọc được bảng này. Bước 2 trả lời câu hỏi hẹp hơn
-- một bậc: ai đọc được dòng nào. Chỗ khác nhau giữa hai câu là lý do mục 4.4
-- tồn tại, và cũng là điểm yếu CWE-1220.

-- ---------------------------------------------------------------------------
-- 2.1. Bật an toàn mức hàng cho de_nghi_chi.
--
-- Hai câu lệnh, không phải một. Câu thứ nhất bật chính sách cho các vai trò
-- thường. Câu thứ hai áp chính sách cho cả CHỦ SỞ HỮU bảng, và thiếu nó thì
-- chu_luoc_do đọc trọn bảng như chưa có chính sách nào. Đây là bẫy mặc định mà
-- mục 4.4 dặn thuộc lòng, và phép kiểm âm A5 hỏi đúng nó.

ALTER TABLE de_nghi_chi ENABLE ROW LEVEL SECURITY;
ALTER TABLE de_nghi_chi FORCE ROW LEVEL SECURITY;



-- ---------------------------------------------------------------------------
-- 2.2. Chính sách cho ung_dung.
--
-- Đủ hai vế, và người mới hay viết thiếu vế sau.
--   USING      quyết định dòng nào HIỆN RA khi đọc
--   WITH CHECK quyết định dòng nào ĐƯỢC GHI vào
-- Thiếu WITH CHECK thì ung_dung không đọc được đề nghị của người khác, nhưng
-- vẫn tạo được một đề nghị mang tên người khác. Phép kiểm âm A3 hỏi đúng nó.
--
-- Điều kiện của cả hai vế là dòng thuộc về chính phiên đang chạy. Hàm
-- current_user cho bạn tên vai trò của phiên ấy.

CREATE POLICY ung_dung_chi_thay_cua_minh
	ON de_nghi_chi
	FOR ALL
	TO ung_dung
	USING (nguoi_tao = current_user)
	WITH CHECK (nguoi_tao = current_user);



-- ---------------------------------------------------------------------------
-- 2.3. Chính sách cho duyet_chi.
--
-- Vai trò duyệt cần nhìn thấy MỌI đề nghị, nếu không thì nó không duyệt được gì.
-- Nhưng dòng nó ghi xuống phải mang chính tên nó ở cột người duyệt, nếu không
-- thì cột ấy nói dối và nhật ký bên dưới cũng nói dối theo.

CREATE POLICY duyet_chi_xem_va_duyet
	ON de_nghi_chi
	FOR ALL
	TO duyet_chi
	USING (true)
	WITH CHECK (nguoi_duyet = current_user);



-- ---------------------------------------------------------------------------
-- 2.4. Ràng buộc người tạo khác người duyệt.
--
-- Mục 4.5 rút ra một luật: đơn vị nguy hiểm không phải một quyền, mà là một cặp
-- quyền nằm trong cùng một vai trò. Bước 1 đã tách cặp ấy ra hai vai trò. Bước
-- này chặn nốt trường hợp cùng một con người ngồi ở cả hai vai, bằng một ràng
-- buộc nằm trong CƠ SỞ DỮ LIỆU chứ không nằm trong ứng dụng.
--
-- Ràng buộc phải cho phép dòng chưa duyệt, tức cột người duyệt còn trống. Dòng
-- số 5 trong dữ liệu phát sẵn là dòng dùng để thử: nó do duyet_chi tạo ra từ
-- thời chưa tách nhiệm vụ. Phép kiểm âm A4 sẽ thử duyệt đúng dòng đó.

ALTER TABLE de_nghi_chi
	ADD CONSTRAINT nguoi_tao_khac_nguoi_duyet
	CHECK (nguoi_duyet IS NULL OR nguoi_tao <> nguoi_duyet);

