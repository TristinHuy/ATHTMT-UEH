-- A6, phần THỬ THÁCH, không tính vào phần máy chấm. Chạy bằng vai trò duyet_chi.
-- Người duyệt không được tạo đề nghị chi. Đây là phép tách nhiệm vụ ở lớp cấp
-- quyền, khác lớp với A4: A4 chặn việc tự duyệt cái mình đã tạo, còn A6 chặn
-- việc tạo. Mong đợi: LOI_QUYEN.
BEGIN;
INSERT INTO de_nghi_chi (id, nguoi_tao, so_tien) VALUES (902, current_user, 500000);
ROLLBACK;
