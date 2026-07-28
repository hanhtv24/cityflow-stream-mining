# CHƯƠNG 3. PHÂN TÍCH BÀI TOÁN

*(Chương này tương ứng hai pha đầu của CRISP-DM: Business Understanding và Data Understanding. Nội dung tổng hợp từ tài liệu Phase 1–5 của nhóm, dẫn nguồn cụ thể ở mỗi mục.)*

## 3.1. Quy trình lựa chọn đề tài

### 3.1.1. Phân tích cạnh tranh với các nhóm cùng lớp

Trước khi chọn đề tài, nhóm đã phân tích toàn bộ 16 đề tài đã đăng ký của các nhóm khác trong lớp (chi tiết: [`01_PHAN_TICH_DE_TAI_CAC_NHOM.md`](../01_PHAN_TICH_DE_TAI_CAC_NHOM.md)). Ba kết luận chính:

**Bốn cặp đề tài trùng lặp đáng kể** đã tồn tại trước khi nhóm 15 đăng ký: hai nhóm cùng làm luật kết hợp trên dữ liệu bán lẻ (trùng gần như hoàn toàn), hai nhóm cùng làm phát hiện gần trùng lặp bằng Shingling/MinHash/LSH, hai nhóm cùng dùng Bloom Filter cho lọc tốc độ cao.

**Sáu lỗi phương pháp luận** được quan sát ở các đề tài khác: ép thuật toán vào bài toán nó không giải được (luật kết hợp dùng cho dự báo dịch bệnh — luật kết hợp mô tả đồng xuất hiện, không có khái niệm độ trễ thời gian); chọn dữ liệu quá nhỏ cho thuật toán xấp xỉ (mất đi lý do tồn tại của xấp xỉ); tên đề tài hứa nhiều hơn khả năng công cụ; đề tài thuần benchmark thiếu bối cảnh nghiệp vụ; bỏ qua nội dung môn học để làm thị giác máy tính thuần túy.

**Khoảng trống khai thác được:** DGIM (chiếm 22% nội dung chương Data Streaming) không nhóm nào sử dụng làm thuật toán lõi; các độ đo tương quan bất biến với giao dịch rỗng (10% nội dung chương Frequent Patterns) không nhóm nào nêu tên; không nhóm nào kết hợp từ hai chương nội dung trở lên thành một hệ thống thống nhất.

### 3.1.2. Tiêu chí lựa chọn và quyết định

Từ phân tích trên, nhóm xây dựng tám tiêu chí đánh giá (chi tiết: [`02_DE_XUAT_DE_TAI.md`](../02_DE_XUAT_DE_TAI.md)) và đề xuất 16 phương án đề tài. Đề tài **CityFlow** được chọn vì đạt điểm cao nhất (15/16) theo các tiêu chí: khai thác khoảng trống DGIM, có ground truth hoàn hảo để đo sai số (giá trị chính xác tính được offline), dữ liệu đủ lớn để phù hợp tinh thần bài toán luồng, và có tiềm năng kết hợp cả hai lớp bài toán (cửa sổ trượt và khai phá mẫu).

## 3.2. Nguồn dữ liệu

**New York City Taxi & Limousine Commission (TLC) Trip Record Data**, phân đoạn *High Volume For-Hire Vehicle* (FHVHV), công bố công khai theo tháng, sử dụng dữ liệu tháng 01/2024.

Lý do chọn nguồn dữ liệu này: (a) quy mô hàng chục triệu bản ghi/tháng, đủ lớn để thể hiện tính chất bất đối xứng $O(\log N)$ so với $O(N)$; (b) có 265 khu vực địa lý được định danh sẵn (`LocationID`), đúng cấu trúc "nhiều luồng đồng thời" mà bài toán yêu cầu, không cần tự thiết kế cách phân vùng không gian; (c) miễn phí, công khai, có thể tái lập kết quả.

## 3.3. Xác minh chất lượng dữ liệu

*(Chi tiết đầy đủ: [`04_DATA_UNDERSTANDING.md`](../04_DATA_UNDERSTANDING.md); phương pháp: DuckDB truy vấn trực tiếp file Parquet, không nạp toàn bộ vào bộ nhớ.)*

### 3.3.1. Quy mô và chất lượng cơ bản

| Chỉ số | Giá trị đo được |
|---|---|
| Số bản ghi | 19.663.930 (tháng 01/2024) |
| Số cột | 24, trong đó 11 cột được đồ án sử dụng |
| Giá trị thiếu | **0** trên toàn bộ 11 cột sử dụng |
| Bản ghi không hợp lệ (thời gian đảo ngược, thời lượng 0) | 4 bản ghi (0,00002%) |
| Số khu vực | 265 (`taxi_zone_lookup.csv`) |

### 3.3.2. Ba phát hiện quan trọng làm thay đổi thiết kế

**Phát hiện 1 — 44,67% bản ghi lệch thứ tự thời gian.** File Parquet gốc **không** được sắp xếp theo thời gian đón khách. Vì DGIM phụ thuộc chặt vào thứ tự sự kiện (bất biến "bucket mới nhỏ hơn bucket cũ hơn"), việc này bắt buộc phải thêm một bước tiền xử lý sắp xếp lại toàn bộ luồng trước khi đưa vào hệ thống — nếu bỏ qua, mọi kết quả ước lượng sẽ sai mà không có dấu hiệu báo lỗi nào.

**Phát hiện 2 — tham số $m$ của DGIM mở rộng.** Phân phối doanh thu thực tế (trung vị 18,76 USD, phân vị 99,9 là 227,42 USD, giá trị lớn nhất 1.961,28 USD) cho thấy $m=8$ bit (phủ 0–255 USD, kẹp trần khoảng 0,06% bản ghi) là đủ, thay vì giả định ban đầu $m=12$.

**Phát hiện 3 — phân phối khu vực đều hơn dự kiến.** Mười khu vực đông nhất chỉ chiếm 13,3% tổng số chuyến — phản bác giả định ban đầu rằng một vài khu vực trung tâm sẽ áp đảo. Phát hiện này có hai hệ quả thiết kế: (a) việc rời rạc hóa "khu vực hoạt động cao" bắt buộc phải dùng ngưỡng phân vị **riêng cho từng khu vực** thay vì ngưỡng tuyệt đối chung; (b) chỉ số bất ngờ AMS ở phạm vi toàn cục có tín hiệu yếu hơn dự kiến (xác nhận định lượng ở Chương 5, thực nghiệm E6).

### 3.3.3. Xác nhận tính phi dừng

Tỷ lệ số chuyến giữa giờ cao điểm (18h, 1.217.661 chuyến) và giờ thấp điểm (4h, 295.770 chuyến) là **4,1 lần** — xác nhận thực nghiệm cho tính chất phi dừng của luồng dữ liệu đã nêu ở Chương 2, và là căn cứ trực tiếp cho việc sử dụng cửa sổ trượt thay vì thống kê tích lũy toàn kỳ.

## 3.4. Phát biểu lại bài toán sau khi hiểu dữ liệu

Sau khi xác minh dữ liệu thật, sáu câu hỏi nghiệp vụ ở Chương 1 được cụ thể hóa với tham số đã hiệu chỉnh theo dữ liệu thật:

- Q1/Q2: cửa sổ vận hành $N=10^6$ sự kiện, doanh thu biểu diễn bằng $m=8$ bit.
- Q3: số tuyến phân biệt có ground truth chính xác 58.911 tuyến (trên tối đa lý thuyết $265^2=70.225$) — cận cứng cho việc đánh giá thuật toán Flajolet-Martin.
- Q4: kỳ vọng tín hiệu yếu ở phạm vi toàn cục, cần kiểm chứng riêng trên cửa sổ ngắn.
- Q6: ngưỡng "khu vực hoạt động cao" phải chuẩn hóa theo phân vị riêng từng khu vực.

Việc phát hiện và điều chỉnh những sai lệch giữa giả định thiết kế ban đầu và dữ liệu thật minh họa nguyên tắc CRISP-DM: pha Data Understanding không phải bước hình thức mà có thể thay đổi thực chất các quyết định kỹ thuật ở các pha sau.
