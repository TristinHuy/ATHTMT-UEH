-- A5, phép kiểm ÂM, chạy bằng vai trò chu_luoc_do, tức CHỦ SỞ HỮU bảng.
-- Đây là bẫy mặc định của mục 4.4. Bật an toàn mức hàng không áp chính sách cho
-- chủ sở hữu, trừ khi bật thêm FORCE. Thiếu một câu lệnh ấy thì mọi chính sách
-- bạn viết vẫn đúng, vẫn chạy, và vẫn vô hiệu với đúng vai trò có nhiều quyền
-- nhất. Mong đợi: KHONG_DONG.
SELECT id, nguoi_tao FROM de_nghi_chi;
