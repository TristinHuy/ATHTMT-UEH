-- A4, phép kiểm ÂM, chạy bằng vai trò duyet_chi.
-- Dòng số 5 do chính duyet_chi tạo ra từ thời chưa tách nhiệm vụ. Cấp quyền
-- không chặn được việc này, vì duyet_chi có quyền duyệt thật; chính sách mức
-- hàng cũng không, vì nó nhìn thấy mọi dòng thật. Thứ phải chặn ở đây là một
-- luật nghiệp vụ nằm trong lược đồ: LOI_RANG_BUOC.
BEGIN;
UPDATE de_nghi_chi
   SET trang_thai = 'da_duyet', nguoi_duyet = current_user
 WHERE id = 5;
ROLLBACK;
