-- D1, phép kiểm DƯƠNG, chạy bằng vai trò ung_dung.
-- Ba phép kiểm dương tồn tại vì một lý do rất cụ thể. Cách dễ nhất để làm năm
-- phép kiểm âm xanh là thu sạch quyền của mọi vai trò, và khi đó hệ thống an
-- toàn đúng theo nghĩa nó không còn dùng được. Ba phép dương giữ cho bài nằm
-- lại phía đúng của lằn ranh ấy.
SELECT id, so_tien FROM de_nghi_chi WHERE nguoi_tao = current_user;
