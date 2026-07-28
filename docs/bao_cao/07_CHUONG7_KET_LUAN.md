# CHƯƠNG 7. KẾT LUẬN VÀ HƯỚNG PHÁT TRIỂN

## 7.1. Kết luận

Đồ án đã xây dựng thành công CityFlow — một hệ thống giám sát giao thông đô thị kết hợp năm cấu trúc/thuật toán xử lý luồng dữ liệu (DGIM, DGIM mở rộng cho tổng số nguyên, Flajolet-Martin, AMS, Reservoir Sampling) với một tầng khai phá mẫu phổ biến (FP-Growth cùng bộ mười độ đo tương quan), cài đặt hoàn toàn from scratch và kiểm chứng nghiêm ngặt trên dữ liệu chuyến đi thật quy mô 19,66 triệu bản ghi.

Mười hai thực nghiệm (E1–E12) đã xác nhận đầy đủ các cận lý thuyết được giảng dạy — cận sai số 50% và quan hệ $O(1/r)$ của DGIM, độ phức tạp bộ nhớ logarit, tính không chệch của ước lượng AMS, tính đúng đắn tuyệt đối của FP-Growth so với thư viện tham chiếu — đồng thời tạo ra hai đóng góp vượt ra ngoài phạm vi tài liệu giảng dạy: một giả thuyết nghiên cứu độc lập về phân bổ tham số tối ưu (được xác nhận và bác bỏ ở hai chiều khác nhau một cách có ý nghĩa), và một minh chứng thực nghiệm định lượng hoàn hảo cho tính chất bất biến với giao dịch rỗng của các độ đo tương quan.

Quá trình thực hiện đồ án cũng minh họa nhiều bài học kỹ thuật quan trọng nằm ngoài nội dung lý thuyết thuần túy: sự khác biệt giữa dữ liệu thiết kế trên giấy và dữ liệu thật (ngưỡng rời rạc hóa phải điều chỉnh lại), rủi ro của việc tối ưu cục bộ không xét toàn hệ thống (nút thắt hiệu năng Flajolet-Martin), và tầm quan trọng của việc kiểm chứng ngữ nghĩa luồng trong chính công cụ đo đạc (sai lầm harness ở thực nghiệm đầu tiên).

## 7.2. Hướng phát triển

**Mở rộng quy mô dữ liệu:** đánh giá lại toàn bộ ma trận thực nghiệm trên đầy đủ 12 tháng dữ liệu (ước tính 236 triệu sự kiện) để xác nhận các kết luận ổn định qua biến động mùa vụ.

**Kết nối luồng thời gian thực:** thay thế cơ chế phát lại từ file lưu trữ bằng kết nối trực tiếp tới nguồn phát sinh sự kiện thời gian thực (message queue như Kafka), kiểm chứng các thuật toán one-pass hoạt động đúng trong điều kiện luồng bất tận thật sự.

**Thích ứng với tính phi dừng:** hiện tại hệ thống dùng cửa sổ trượt cố định; hướng mở rộng là bổ sung cơ chế phát hiện trôi khái niệm (concept drift detection) để tự động điều chỉnh ngưỡng rời rạc hóa và tham số sketch theo biến động phân phối dữ liệu theo thời gian.

**Mở rộng độ dài cửa sổ khai phá mẫu:** thực nghiệm với nhiều độ dài cửa sổ khác 15 phút, đánh giá độ nhạy của tập luật kết hợp tìm được theo tham số này.

**Kết hợp đặc trưng ngữ cảnh:** bổ sung dữ liệu ngoại sinh (thời tiết, sự kiện lớn, ngày lễ) làm item bổ sung trong giỏ hàng khai phá mẫu, mở rộng khả năng giải thích nguyên nhân của các luật đồng ùn tắc tìm được.

**Kiểm chứng giả thuyết H1 với độ tin cậy thống kê chặt hơn:** tăng số mốc truy vấn và số tháng dữ liệu đánh giá để xác định khoảng tin cậy cho mức cải thiện của chiến lược phân bổ ngân sách tối ưu, hiện mới dừng ở mức xác nhận xu hướng.
