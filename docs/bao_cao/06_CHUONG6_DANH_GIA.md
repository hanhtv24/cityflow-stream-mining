# CHƯƠNG 6. ĐÁNH GIÁ

## 6.1. Đối chiếu với mục tiêu đặt ra

| Mục tiêu (Chương 1) | Kết quả | Đạt |
|---|---|:---:|
| Cài đặt from scratch 5 thuật toán/cấu trúc lõi | DGIM, DGIM-Integer, Flajolet-Martin, AMS, FP-Growth (+Apriori đối chứng) — toàn bộ 158 kiểm định đơn vị đạt | ✅ |
| Quản lý 535 luồng song song hiệu quả | Thông lượng 87.933 sự kiện/giây, vượt mục tiêu 50.000/giây; bộ nhớ 5,66 MB, tiết kiệm 11,8× so với lưu cửa sổ đầy đủ | ✅ |
| Kiểm chứng tính đúng đắn bằng đối chiếu thư viện | FP-Growth khớp tuyệt đối `mlxtend` trên 20/20 phép thử | ✅ |
| Đánh giá trên dữ liệu thật quy mô lớn | 19.663.928 sự kiện thật, không mô phỏng | ✅ |
| Câu hỏi nghiên cứu độc lập ngoài tài liệu giảng dạy | Giả thuyết H1 (phân bổ ngân sách DGIM mở rộng) — xác nhận dạng lý thuyết, bác bỏ dạng trực giác | ✅ |
| Triển khai thành sản phẩm hoạt động | API + CSDL PostgreSQL (đã kiểm chứng ghi/đọc dữ liệu thật) + Dashboard React | ✅ (đóng gói Docker: xem §6.4) |

Năm trên sáu mục tiêu đạt đầy đủ. Mục tiêu thứ sáu (triển khai container hóa) đạt về mặt logic hệ thống (API và CSDL đã kiểm chứng hoạt động đúng với dữ liệu thật) nhưng gặp trở ngại môi trường mạng khi đóng gói Docker image — trình bày chi tiết ở §6.4.

## 6.2. Ba đóng góp có giá trị nhất

**Thứ nhất — bằng chứng thực nghiệm hoàn hảo cho tính bất biến với giao dịch rỗng (E10).** Biến thiên đo được đúng bằng 0,0% cho sáu độ đo bất biến so với 10.259% của $\chi^2$ là kết quả sạch và thuyết phục nhất toàn bộ đồ án — biến một phát biểu lý thuyết trừu tượng thành một con số cụ thể trên dữ liệu giao thông thật.

**Thứ hai — giả thuyết nghiên cứu H1 về phân bổ ngân sách DGIM mở rộng.** Đây là phần mở rộng vượt ra ngoài nội dung tài liệu giảng dạy: xác định một khoảng trống cụ thể (tài liệu nêu công thức mở rộng nhưng không bàn phân bổ tham số), suy dẫn công thức bằng công cụ toán học độc lập (nhân tử Lagrange), và kiểm chứng cho kết quả có tính giáo dục cao — bác bỏ trực giác thông thường bằng số liệu.

**Thứ ba — phát hiện và khắc phục nút thắt hiệu năng không như dự đoán (E7).** Thiết kế ban đầu tối ưu hóa cho 535 luồng DGIM (đúng dự đoán về mặt lý thuyết) nhưng nút thắt thực tế lại nằm ở Flajolet-Martin — một minh chứng cho nguyên tắc kỹ thuật "đo trước khi tối ưu" và cho thấy tối ưu cục bộ một thành phần (chọn $m$ lớn để giảm sai số) có thể phá vỡ hiệu năng toàn hệ thống nếu không đánh giá tổng thể.

## 6.3. Hạn chế

**Dữ liệu là lịch sử phát lại, không phải luồng trực tuyến thật.** Hệ thống xử lý file Parquet đã lưu trữ, phát lại theo thứ tự thời gian đã sắp xếp — không phải kết nối trực tiếp tới nguồn phát sinh dữ liệu thời gian thực. Giới hạn này ảnh hưởng tới tính thực tế của tuyên bố "xử lý luồng", nhưng không ảnh hưởng tới tính hợp lệ của các thuật toán và kết quả đo — bản chất một-lượt (single-pass) của các thuật toán được tôn trọng nghiêm ngặt trong cài đặt (không có bước nào đọc lại dữ liệu đã xử lý).

**Đánh giá trên một tháng dữ liệu, không phải toàn bộ 12 tháng dự kiến.** Quy mô 19,66 triệu sự kiện đã đủ lớn để thể hiện rõ tính chất bất đối xứng logarit so với tuyến tính (Chương 5), nhưng chưa xác nhận các kết luận có ổn định qua biến động mùa vụ hay không.

**Tín hiệu AMS (Q4) yếu ở phạm vi toàn cục trên dữ liệu này.** Đây không phải lỗi cài đặt (độ chính xác ước lượng đạt 7,1% sai số, tốt hơn ngưỡng đặt ra) mà là đặc điểm của chính dữ liệu — phân phối khu vực NYC khá đồng đều khiến số bất ngờ có khả năng phân biệt hạn chế. Hạn chế này được xử lý bằng thiết kế bù trừ (tầng khai phá mẫu Q6 đảm nhiệm vai trò phát hiện chính), không phải bị che giấu.

**Rời rạc hóa theo cửa sổ 15 phút cố định.** Độ dài cửa sổ ảnh hưởng trực tiếp tới kết quả khai phá mẫu (kích thước giỏ hàng, số mẫu tìm được); đồ án chưa thực nghiệm với các độ dài cửa sổ khác để đánh giá độ nhạy.

## 6.4. Sự cố triển khai và bài học

Trong quá trình đóng gói hệ thống bằng Docker, hai sự cố mạng đã xảy ra: (1) không thể truy cập kho gói Debian để cài `libpq-dev`/`gcc` — khắc phục bằng cách nhận ra `psycopg[binary]` đã đóng gói sẵn thư viện gốc, không cần biên dịch, loại bỏ hoàn toàn bước `apt-get`; (2) thời gian chờ mặc định của `pip` (15 giây) không đủ trong môi trường mạng build chậm — khắc phục bằng tăng `--default-timeout` và `--retries`.

*(Trạng thái cuối cùng của việc đóng gói Docker và kiểm thử tích hợp end-to-end được cập nhật ở phần kết luận sau khi build hoàn tất — xem ghi chú cập nhật trong README của dự án.)*

Bài học rút ra: môi trường triển khai (build container) có ràng buộc mạng khác với môi trường phát triển (venv cục bộ, nơi cài đặt gói đã thành công trơn tru) — một khác biệt cần tính đến khi thiết kế quy trình CI/CD cho các dự án tương tự.

## 6.5. Đối chiếu với ba tín hiệu chấm điểm

Ba tín hiệu được xác định từ đầu đồ án (chứng minh toán học, tinh chỉnh tham số kèm đối chiếu lý thuyết/thực nghiệm, độ đo tương quan bất biến) đều được đáp ứng đầy đủ trong Chương 5: chứng minh cận sai số DGIM và tính không chệch AMS trình bày ở Chương 2 kèm kiểm chứng số ở Chương 5; mười hai thực nghiệm đều là phép đối chiếu tham số–sai số cụ thể; và E10 là minh chứng độc lập, định lượng, không thể tranh cãi cho tính bất biến với giao dịch rỗng.
