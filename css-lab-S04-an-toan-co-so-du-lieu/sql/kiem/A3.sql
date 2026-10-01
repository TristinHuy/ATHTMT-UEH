-- A3, phép kiểm ÂM, chạy bằng vai trò ung_dung.
-- Vế USING của chính sách đã chặn phần đọc ở A2. Câu này hỏi vế còn lại: ghi
-- một dòng mang tên người khác. Thiếu WITH CHECK thì câu này chạy trót lọt và
-- A2 vẫn xanh, tức là bài trông như đã xong trong khi cửa sau còn mở.
-- Mong đợi: LOI_CHINH_SACH.
BEGIN;
INSERT INTO de_nghi_chi (id, nguoi_tao, so_tien) VALUES (901, 'nv_khac', 990000);
ROLLBACK;
