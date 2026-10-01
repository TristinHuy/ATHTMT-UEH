-- A2, phép kiểm ÂM, chạy bằng vai trò ung_dung.
-- Cửa vào bảng thì mở, vì ung_dung phải làm việc trên chính bảng này. Thứ phải
-- chặn ở đây là các DÒNG không thuộc về nó, và chính sách mức hàng chặn bằng
-- cách không trả về dòng nào: KHONG_DONG.
SELECT id, nguoi_tao FROM de_nghi_chi WHERE nguoi_tao <> current_user;
