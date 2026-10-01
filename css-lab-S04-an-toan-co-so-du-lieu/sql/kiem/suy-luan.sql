-- Chạy SAU khi đã siết xong, bằng vai trò bao_cao.
-- Cùng hai câu hỏi thống kê, cùng tấm chắn, và cùng một hiệu số. Đây là bằng
-- chứng cho một câu khó chịu của buổi học: cấp quyền và lọc dòng trả lời câu
-- hỏi ai chạm được vào vật chứa nào, còn thứ rò ra ở đây là một mệnh đề, mà
-- mệnh đề thì không nằm gọn trong vật chứa nào.
SELECT * FROM thong_ke_theo_nam('He thong thong tin', 2100);
SELECT * FROM thong_ke_theo_nam('He thong thong tin', 2019);
