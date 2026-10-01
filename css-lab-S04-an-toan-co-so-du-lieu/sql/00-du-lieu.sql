-- Lược đồ và dữ liệu của bài. TỆP NÀY ĐƯỢC PHÁT SẴN, BẠN KHÔNG SỬA.
--
-- `make up` chạy nó bằng vai trò quản trị, và nó chạy lại được bao nhiêu lần
-- tùy ý: mọi thứ đều bị bỏ đi trước khi dựng lại. Nhờ vậy bạn phá hỏng bài của
-- mình bao nhiêu lần cũng được, `make up` đưa cơ sở dữ liệu về đúng điểm xuất
-- phát trong vài giây.
--
-- Dữ liệu trong đây là dữ liệu dựng riêng cho học phần. Không tên thật, không
-- lương thật, không đơn vị thật.

DROP VIEW IF EXISTS thong_ke_bo_mon;
DROP FUNCTION IF EXISTS thong_ke_theo_nam(text, integer);
DROP TABLE IF EXISTS de_nghi_chi;
DROP TABLE IF EXISTS nhan_su;

-- --------------------------------------------------------------- bảng nhân sự
CREATE TABLE nhan_su (
    id       integer PRIMARY KEY,
    ho_ten   text    NOT NULL,
    bo_mon   text    NOT NULL,
    nam_vao  integer NOT NULL,
    luong    integer NOT NULL   -- đơn vị: triệu đồng mỗi tháng
);

INSERT INTO nhan_su (id, ho_ten, bo_mon, nam_vao, luong) VALUES
  (1,  'NV-01', 'He thong thong tin', 2015, 22),
  (2,  'NV-02', 'He thong thong tin', 2016, 24),
  (3,  'NV-03', 'He thong thong tin', 2017, 26),
  (4,  'NV-04', 'He thong thong tin', 2018, 25),
  (5,  'NV-05', 'He thong thong tin', 2019, 27),
  (6,  'NV-06', 'He thong thong tin', 2021, 24),
  (7,  'NV-07', 'Khoa hoc du lieu',   2016, 23),
  (8,  'NV-08', 'Khoa hoc du lieu',   2018, 25),
  (9,  'NV-09', 'Khoa hoc du lieu',   2020, 21),
  (10, 'NV-10', 'Khoa hoc du lieu',   2022, 20),
  (11, 'NV-11', 'An toan thong tin',  2019, 28),
  (12, 'NV-12', 'An toan thong tin',  2023, 19);

-- Khung nhìn thống kê, có tấm chắn ngưỡng năm người. Vai trò báo cáo sống bằng
-- khung nhìn này chứ không bằng bảng gốc.
CREATE VIEW thong_ke_bo_mon AS
  SELECT bo_mon,
         count(*)   AS so_nguoi,
         sum(luong) AS tong_luong
    FROM nhan_su
   GROUP BY bo_mon
  HAVING count(*) >= 5;

-- Cùng tấm chắn ấy, nhưng cho phép hỏi kèm một mốc năm. Mục 4.1 của giáo trình
-- trình bày phần này dưới dạng khung nhìn; ở đây nó là một hàm, vì mệnh đề lọc
-- theo năm phải chạy TRƯỚC phép gộp thì ngưỡng năm người mới có nghĩa. Hàm chạy
-- bằng quyền của người tạo, nên người gọi không cần quyền nào trên bảng gốc.
CREATE FUNCTION thong_ke_theo_nam(p_bo_mon text, p_nam_toi integer)
RETURNS TABLE (so_nguoi bigint, tong_luong bigint)
LANGUAGE sql
SECURITY DEFINER
AS $$
  SELECT count(*), sum(luong)::bigint
    FROM nhan_su
   WHERE bo_mon = p_bo_mon AND nam_vao <= p_nam_toi
  HAVING count(*) >= 5;
$$;

-- --------------------------------------------------- bảng đề nghị chi
-- Cột nguoi_tao và nguoi_duyet giữ THẲNG tên vai trò cơ sở dữ liệu, để bài học
-- gọn trong một tầng. Hệ thống thật giữ một mã người dùng của ứng dụng và ánh
-- xạ sang phiên; câu hỏi ánh xạ ấy đúng đắn tới đâu là chỗ buổi S5 bắt đầu.
CREATE TABLE de_nghi_chi (
    id          integer PRIMARY KEY,
    nguoi_tao   text    NOT NULL,
    so_tien     integer NOT NULL,
    trang_thai  text    NOT NULL DEFAULT 'moi',
    nguoi_duyet text
);

INSERT INTO de_nghi_chi (id, nguoi_tao, so_tien, trang_thai, nguoi_duyet) VALUES
  (1, 'ung_dung',  1200000, 'moi',      NULL),
  (2, 'ung_dung',   850000, 'da_duyet', 'duyet_chi'),
  (3, 'nv_khac',   2400000, 'moi',      NULL),
  (4, 'nv_khac',    600000, 'da_duyet', 'duyet_chi'),
  -- Dòng số 5 là dòng cũ, có từ thời một người làm cả hai việc. Nó ở đây có
  -- chủ đích: ràng buộc bạn sắp cài phải chặn được đúng dòng này.
  (5, 'duyet_chi', 3100000, 'moi',      NULL);

-- ------------------------------------------------ hiện trạng bạn thừa kế
-- Một tài khoản báo cáo do người tiền nhiệm để lại, không ai nhớ nó dùng làm gì.
CREATE ROLE khach_tam LOGIN PASSWORD 'lab2026';

-- Và một dòng cấp quyền cho tiện, cũng do người tiền nhiệm chạy.
--
-- Đọc kỹ chỗ này, vì nó hay bị kể sai. PostgreSQL KHÔNG cấp sẵn quyền đọc bảng
-- cho PUBLIC. Ba thứ nó cấp sẵn là quyền CONNECT và TEMPORARY trên cơ sở dữ
-- liệu, quyền USAGE trên lược đồ public, và quyền EXECUTE trên mọi hàm bạn tạo
-- ra. Dòng dưới đây là việc của một con người, không phải mặc định của phần
-- mềm, và nó là hiện trạng bạn nhận bàn giao.
GRANT SELECT ON ALL TABLES IN SCHEMA public TO PUBLIC;
