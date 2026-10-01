-- Bước 1. Thu quyền cấp sẵn, rồi dựng ba vai trò với quyền tối thiểu.
--
-- BẠN VIẾT TỆP NÀY. Bộ kiểm đọc chính nó, sau khi bỏ hết chú thích, nên những
-- dòng giải thích dưới đây không được tính là bài làm.
--
-- Thứ tự có lý do. Thu quyền trước, cấp quyền sau. Làm ngược lại thì có một
-- khoảng thời gian mọi vai trò mới dựng đều thừa hưởng phần cấp sẵn của PUBLIC,
-- và trong khoảng ấy bài kiểm quyền của bạn nói dối.

-- ---------------------------------------------------------------------------
-- 1.1. Thu những gì PUBLIC được cấp sẵn.
--
-- Bốn chỗ, và bỏ sót chỗ nào thì vai trò nào cũng còn đường vòng tới đó.
--   a. quyền trên bảng mà người tiền nhiệm đã cấp cho PUBLIC
--   b. quyền EXECUTE trên hàm, thứ PostgreSQL cấp sẵn cho PUBLIC
--   c. quyền USAGE trên lược đồ public
--   d. quyền CONNECT trên cơ sở dữ liệu
--
-- Chỗ (d) đòi một quyết định chứ không chỉ một câu lệnh: thu CONNECT của PUBLIC
-- rồi thì mọi vai trò cần nối vào đều phải được cấp lại, kể cả ba vai trò bạn
-- sắp dựng. Viết theo thứ tự nào là việc của bạn, miễn là cuối bước 1 chúng nối
-- được vào và khách_tạm thì không.

REVOKE SELECT ON ALL TABLES IN SCHEMA public FROM PUBLIC;
REVOKE EXECUTE ON ALL FUNCTIONS IN SCHEMA public FROM PUBLIC;
REVOKE USAGE ON SCHEMA public FROM PUBLIC;
REVOKE CONNECT ON DATABASE css_s04 FROM PUBLIC;



-- ---------------------------------------------------------------------------
-- 1.2. Ba vai trò.
--
-- | vai trò      | làm gì trong hệ thống                                     |
-- |--------------|-----------------------------------------------------------|
-- | chu_luoc_do  | sở hữu bảng, chạy di trú lược đồ. Ứng dụng KHÔNG nối bằng  |
-- |              | vai trò này, vì chủ sở hữu tự cấp lại được quyền cho mình  |
-- |              | sau khi bị thu, tức là thu không bền.                      |
-- | ung_dung     | vai trò ứng dụng nối vào hằng ngày. Đọc và ghi đề nghị chi |
-- |              | của chính nó, không đọc bảng nhân sự.                      |
-- | duyet_chi    | vai trò duyệt chi. Nhìn được mọi đề nghị, đổi được trạng   |
-- |              | thái, và KHÔNG tạo được đề nghị nào. Đây là phép tách      |
-- |              | nhiệm vụ ở mục 4.5 dịch sang ngôn ngữ cấp quyền.           |
-- | bao_cao      | vai trò báo cáo, chỉ đọc, và chỉ đọc thống kê.            |
--
-- Bảng trên có bốn dòng vì chu_luoc_do là vai trò sở hữu, không nằm trong ba
-- vai trò làm việc. Cả bốn đều cần mật khẩu để nối vào; dùng 'lab2026' cho khớp
-- với Makefile, và nhớ rằng một mật khẩu chung như thế chỉ chấp nhận được trong
-- một mạng ảo dựng ra rồi xóa đi trong cùng một buổi.
--
-- Ba điều bộ kiểm sẽ tìm, nói trước để bạn khỏi mất điểm oan:
--   - không vai trò nào mang SUPERUSER, BYPASSRLS, hay CREATEROLE;
--   - không có GRANT nào cấp cho PUBLIC;
--   - không có GRANT ALL PRIVILEGES trên bảng nhan_su hay de_nghi_chi.
-- Điều thứ nhất đáng dừng lại một nhịp. BYPASSRLS đi xuyên qua mọi chính sách
-- bạn sắp viết ở bước 2, nên một vai trò mang nó biến cả bước ấy thành trang
-- trí.

CREATE ROLE chu_luoc_do LOGIN PASSWORD 'lab2026' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
CREATE ROLE ung_dung LOGIN PASSWORD 'lab2026' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
CREATE ROLE duyet_chi LOGIN PASSWORD 'lab2026' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;
CREATE ROLE bao_cao LOGIN PASSWORD 'lab2026' NOSUPERUSER NOCREATEDB NOCREATEROLE NOBYPASSRLS;

GRANT CONNECT ON DATABASE css_s04 TO chu_luoc_do, ung_dung, duyet_chi, bao_cao;
GRANT USAGE, CREATE ON SCHEMA public TO chu_luoc_do;
GRANT USAGE ON SCHEMA public TO ung_dung, duyet_chi, bao_cao;



-- ---------------------------------------------------------------------------
-- 1.3. Chuyển quyền sở hữu và cấp quyền tối thiểu.
--
-- Hai bảng và hai đối tượng thống kê hiện do vai trò quản trị sở hữu. Chuyển
-- chúng cho chu_luoc_do, rồi cấp cho ba vai trò còn lại đúng phần chúng cần:
-- ung_dung đọc và ghi de_nghi_chi; duyet_chi đọc và sửa de_nghi_chi nhưng không
-- thêm dòng; bao_cao đọc khung nhìn thống kê và gọi được hàm thống kê theo năm.
--
-- Trước khi viết, tự trả lời một câu: vì sao bao_cao không cần một quyền nào
-- trên bảng nhan_su mà vẫn đọc được con số tổng?

ALTER TABLE nhan_su OWNER TO chu_luoc_do;
ALTER TABLE de_nghi_chi OWNER TO chu_luoc_do;
ALTER VIEW thong_ke_bo_mon OWNER TO chu_luoc_do;
ALTER FUNCTION thong_ke_theo_nam(text, integer) OWNER TO chu_luoc_do;

GRANT SELECT, INSERT, UPDATE ON de_nghi_chi TO ung_dung;
GRANT SELECT, UPDATE ON de_nghi_chi TO duyet_chi;
GRANT SELECT ON thong_ke_bo_mon TO bao_cao;
GRANT EXECUTE ON FUNCTION thong_ke_theo_nam(text, integer) TO bao_cao;

