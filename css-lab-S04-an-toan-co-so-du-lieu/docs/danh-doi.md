Trong tình huống đơn vị chỉ có ba nhân sự, để tránh quy trình bị đình trệ, chúng ta buộc phải bỏ phép tách nhiệm vụ nghiêm ngặt giữa người tạo đề nghị chi và người duyệt chi. Nghĩa là, trong một số trường hợp, một cá nhân sẽ được nắm cả hai quyền để tự xử lý luồng công việc.

Để giảm thiểu rủi ro khi gộp quyền, biện pháp bù (compensating control) là áp dụng kiểm toán sau sự kiện (post-event audit) kết hợp cảnh báo tức thời. Mọi giao dịch tự duyệt sẽ tự động gửi email báo cáo cho hai người còn lại, và `pgaudit` ghi lại lịch sử thao tác không thể chối cãi. 

Về con số hòa vốn, giả sử chi phí để thuê thêm nhân sự thứ tư nhằm tách biệt nhiệm vụ là 20.000.000 VNĐ/tháng. Nếu xác suất một nhân viên trục lợi gian lận là 5% mỗi tháng, điểm hòa vốn sẽ là: 20.000.000 / 0.05 = 400.000.000 VNĐ. Nếu hạn mức quỹ rủi ro của công ty thấp hơn 400 triệu đồng, thì việc không thuê thêm người và chấp nhận rủi ro sẽ có lợi hơn.

Dù vậy, biện pháp bù này yếu hơn ở chỗ nó mang tính phát hiện (detective) chứ không phòng ngừa (preventive). Sự cố hoàn toàn có thể xảy ra và tiền đã bị chuyển đi mất trước khi những nhân sự khác kịp đọc báo cáo để can thiệp.