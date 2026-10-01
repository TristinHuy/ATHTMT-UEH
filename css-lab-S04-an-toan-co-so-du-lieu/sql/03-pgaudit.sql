-- Bước 3. Lưu vết ở mức đối tượng.
--
-- BẠN VIẾT TỆP NÀY, cộng hai dòng trong csdl/pgaudit.conf.
--
-- Không chính sách nào ở bước 1 và bước 2 trả lời được câu hỏi ai đã thật sự
-- đọc gì, tuần trước. pgaudit sinh ra nhật ký ấy ngay trong máy chủ, và vị trí
-- đó mới là điều đáng nói: máy chủ là điểm duy nhất nhìn thấy mọi con đường tới
-- dữ liệu, kể cả con đường của một phiên psql không đi qua ứng dụng nào.

-- ---------------------------------------------------------------------------
-- 3.1. Vai trò đánh dấu.
--
-- Cách ghi mức đối tượng của pgaudit hoạt động theo một lối vòng đáng nhớ: bạn
-- dựng một vai trò KHÔNG dùng để nối vào, chỉ dùng làm cái nhãn, rồi cấp cho
-- nó quyền trên đúng những đối tượng bạn muốn ghi. Máy chủ ghi lại mọi câu
-- chạm tới các đối tượng ấy, bất kể ai chạy.
--
-- Dựng vai trò đánh dấu, đặt tên là kiem_toan, và KHÔNG cho nó quyền nối vào.
-- Một vai trò dùng làm nhãn mà nối vào được là một tài khoản thừa, và tài khoản
-- thừa nào cũng là một đường vào.

CREATE ROLE kiem_toan NOLOGIN NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;



-- ---------------------------------------------------------------------------
-- 3.2. Chọn cái gì đáng ghi.
--
-- Cấp cho kiem_toan quyền đọc trên bảng nhan_su, và quyền đọc cùng ghi trên
-- bảng de_nghi_chi. Từ đó máy chủ ghi lại mọi câu chạm tới hai bảng ấy.
--
-- Vì sao không ghi tất cả: nhật ký ghi tất cả sẽ bị tắt vào ngày có người nhìn
-- hóa đơn lưu trữ, và một nhật ký đã tắt thì bằng không. Chọn hẹp là cách giữ
-- cho nó còn sống tới lúc cần.
GRANT SELECT ON nhan_su TO kiem_toan;
GRANT SELECT, INSERT, UPDATE ON de_nghi_chi TO kiem_toan;
--
-- Giới hạn phải biết trước khi tin vào nó: pgaudit ghi CÂU HỎI chứ không ghi
-- CÂU TRẢ LỜI. Nó cho bạn biết ai đã hỏi gì, không cho biết họ đã nhận về bao
-- nhiêu dòng. Chuỗi truy vấn suy luận ở mục 4.1 vì thế hiện lên trong nhật ký
-- như hai câu hỏi hợp lệ, và phần còn lại nằm ngoài tầm của công cụ này.



-- ---------------------------------------------------------------------------
-- 3.3. Hai dòng trong csdl/pgaudit.conf.
--
-- Viết chúng ở tệp đó, không viết ở đây. pgaudit nạp lúc máy chủ khởi động, nên
-- sau khi sửa phải khởi động lại máy chủ; `make defend` làm việc ấy cho bạn.
