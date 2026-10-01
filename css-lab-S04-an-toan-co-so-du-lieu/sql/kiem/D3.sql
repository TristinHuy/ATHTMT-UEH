-- D3, phép kiểm DƯƠNG, chạy bằng vai trò bao_cao.
-- Vai trò báo cáo không có quyền nào trên bảng nhan_su, và vẫn phải đọc được
-- con số tổng. Nếu câu này đỏ thì bạn đã siết nhầm chỗ: khung nhìn chạy bằng
-- quyền của người tạo ra nó, nên thứ bao_cao cần là quyền trên khung nhìn.
SELECT bo_mon, so_nguoi, tong_luong FROM thong_ke_bo_mon ORDER BY bo_mon;
