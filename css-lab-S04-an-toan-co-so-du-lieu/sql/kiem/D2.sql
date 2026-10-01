-- D2, phép kiểm DƯƠNG, chạy bằng vai trò ung_dung.
-- Ứng dụng phải tạo được đề nghị chi mang tên chính nó. Câu này chạy trong một
-- giao dịch rồi quay lui, nên nó không để lại dòng nào và chạy lại được bao
-- nhiêu lần cũng cho cùng kết quả.
BEGIN;
INSERT INTO de_nghi_chi (id, nguoi_tao, so_tien) VALUES (903, current_user, 1500000);
ROLLBACK;
