-- A1, phép kiểm ÂM, chạy bằng vai trò bao_cao.
-- Vai trò báo cáo sống bằng khung nhìn thống kê. Nó không có việc gì với bảng
-- gốc, nên câu này phải dừng ở lớp cấp quyền: LOI_QUYEN.
SELECT ho_ten, luong FROM nhan_su LIMIT 5;
