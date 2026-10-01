-- Bước quan sát đầu buổi, chạy bằng vai trò khach_tam, tức tài khoản báo cáo cũ
-- không ai nhớ dùng làm gì. Ba câu, và chúng khác nhau ở chỗ quan trọng.
--
-- Câu thứ nhất đọc thẳng bảng lương. Nó chạy được vì một dòng GRANT cho tiện mà
-- người tiền nhiệm đã chạy, và phần việc của bạn hôm nay đóng được nó lại.
--
-- Hai câu sau không đọc bảng nào. Chúng hỏi hai con số thống kê hợp lệ, cả hai
-- đều qua được tấm chắn ngưỡng năm người, rồi trừ cho nhau ở trong đầu bạn.
-- Phần việc của bạn hôm nay KHÔNG đóng được chỗ đó, và mục 4.8 nói vì sao.
SELECT ho_ten, bo_mon, luong FROM nhan_su ORDER BY id;

SELECT * FROM thong_ke_theo_nam('He thong thong tin', 2100);
SELECT * FROM thong_ke_theo_nam('He thong thong tin', 2019);
