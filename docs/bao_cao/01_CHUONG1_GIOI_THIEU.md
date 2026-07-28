# CHƯƠNG 1. GIỚI THIỆU

## 1.1. Bối cảnh và động lực nghiên cứu

Các đô thị lớn hiện đại vận hành hàng chục nghìn phương tiện giao thông công cộng và tư nhân, tạo ra luồng dữ liệu vị trí và giao dịch liên tục ở tốc độ hàng triệu bản ghi mỗi giờ. Trung tâm điều hành giao thông cần trả lời các câu hỏi vận hành theo thời gian gần thực — *"Trong một triệu chuyến gần nhất, khu vực nào đang có mật độ cao bất thường?"*, *"Tổng doanh thu vận chuyển trong giờ qua là bao nhiêu?"*, *"Những khu vực nào có xu hướng ùn tắc đồng thời?"* — trên **hàng trăm khu vực địa lý song song**.

Ràng buộc kỹ thuật cốt lõi của bài toán này được nêu rõ trong tài liệu giảng dạy môn Khai phá dữ liệu, chương *Data Streaming*:

> *"N có thể rất lớn (hàng triệu phần tử). Có thể có nhiều luồng đồng thời — không thể giữ nhiều cửa sổ."*

Với 265 khu vực taxi của thành phố New York — bộ dữ liệu được chọn làm đối tượng nghiên cứu của đồ án — việc duy trì cửa sổ đầy đủ $N=10^6$ sự kiện cho **mỗi** khu vực, nhân với nhiều loại truy vấn cần trả lời đồng thời (số chuyến, doanh thu, số tuyến phân biệt, mức độ tập trung nhu cầu), tạo ra một bài toán bộ nhớ tăng tuyến tính theo tích của ba đại lượng: số luồng × số loại truy vấn × độ rộng cửa sổ. Đây chính là bài toán mà các cấu trúc dữ liệu xấp xỉ xử lý luồng — DGIM, Flajolet-Martin, AMS — được thiết kế để giải quyết, đổi lấy sai số nhỏ có kiểm soát để đạt bộ nhớ dưới tuyến tính.

Song song đó, việc chỉ giám sát trạng thái từng khu vực độc lập bỏ sót một chiều thông tin quan trọng: **mối quan hệ đồng thời giữa các khu vực**. Nếu khu vực A đang ùn tắc, khu vực B có thường ùn tắc cùng lúc hay không? Đây là câu hỏi thuộc phạm trù khai phá mẫu phổ biến (frequent pattern mining) — một nhánh kiến thức riêng biệt nhưng có thể kết hợp trực tiếp với tầng xử lý luồng để tạo ra một hệ thống hoàn chỉnh hơn.

## 1.2. Phát biểu bài toán

Đồ án giải quyết đồng thời hai lớp bài toán trên cùng một luồng dữ liệu chuyến đi:

**Lớp 1 — Truy vấn cửa sổ trượt xấp xỉ (Q1–Q5):** với ngân sách bộ nhớ giới hạn, trả lời các truy vấn thống kê trên $N$ sự kiện gần nhất của từng luồng trong số hàng trăm luồng song song, với sai số nằm trong cận lý thuyết đã được chứng minh.

**Lớp 2 — Khai phá mẫu đồng xuất hiện (Q6):** từ lịch sử luồng đã tích lũy, phát hiện các tổ hợp khu vực có xu hướng cùng ở trạng thái "hoạt động cao" trong cùng khung thời gian, xếp hạng các tổ hợp này bằng một bộ độ đo tương quan đáng tin cậy thay vì chỉ dựa vào tần suất xuất hiện thô.

Sáu câu hỏi nghiệp vụ cụ thể mà hệ thống phải trả lời:

| Mã | Câu hỏi | Thuật toán | Lớp bài toán |
|---|---|---|---|
| Q1 | Trong $N$ chuyến gần nhất, bao nhiêu chuyến xuất phát từ khu vực $z$? | DGIM | Cửa sổ trượt |
| Q2 | Tổng doanh thu của $N$ chuyến gần nhất là bao nhiêu? | DGIM mở rộng số nguyên | Cửa sổ trượt |
| Q3 | Có bao nhiêu tuyến đường (cặp đón–trả) phân biệt đang hoạt động? | Flajolet-Martin | Cửa sổ trượt |
| Q4 | Nhu cầu đang tập trung bất thường vào một số khu vực hay phân bố đều? | AMS (số bất ngờ) | Cửa sổ trượt |
| Q5 | Giữ mẫu đại diện nào để phân tích sâu mà không lưu toàn bộ luồng? | Reservoir Sampling | Cửa sổ trượt |
| Q6 | Những khu vực nào thường xuyên ùn tắc **cùng nhau**? | FP-Growth + độ đo tương quan | Khai phá mẫu |

## 1.3. Mục tiêu nghiên cứu

**Mục tiêu tổng quát:** xây dựng và đánh giá thực nghiệm một hệ thống khai phá dữ liệu luồng hoàn chỉnh, cài đặt từ đầu (from scratch) các thuật toán lõi, kiểm chứng tính đúng đắn bằng đối chiếu thư viện tham chiếu, và xác nhận các cận lý thuyết bằng dữ liệu thật quy mô lớn.

**Mục tiêu cụ thể:**

1. Cài đặt from scratch năm cấu trúc/thuật toán: DGIM, DGIM mở rộng cho tổng số nguyên, Flajolet-Martin, AMS, FP-Growth (kèm Apriori đối chứng), và một bộ mười độ đo tương quan luật kết hợp.
2. Thiết kế kiến trúc quản lý đồng thời 535 luồng song song (265 khu vực đón + 265 khu vực trả + 5 vị từ toàn cục) với một đồng hồ dùng chung, tối ưu hóa để chỉ xử lý các sự kiện thực sự thay đổi trạng thái.
3. Kiểm chứng tính đúng đắn cài đặt bằng (a) tái hiện chính xác mọi ví dụ số trong tài liệu giảng dạy dưới dạng kiểm định đơn vị, và (b) đối chiếu kết quả FP-Growth từ scratch với thư viện `mlxtend` trên nhiều bộ dữ liệu.
4. Đánh giá thực nghiệm trên dữ liệu chuyến đi thật của New York City TLC — không dùng dữ liệu mô phỏng — qua mười hai thực nghiệm đối chiếu sai số đo được với cận lý thuyết.
5. Xây dựng một câu hỏi nghiên cứu độc lập ngoài phạm vi tài liệu giảng dạy: phân bổ ngân sách bộ nhớ tối ưu trong DGIM mở rộng cho tổng số nguyên, suy dẫn bằng công cụ toán học (nhân tử Lagrange) và kiểm chứng thực nghiệm.
6. Triển khai hệ thống thành sản phẩm hoạt động: API dịch vụ web, cơ sở dữ liệu quan hệ, bảng điều khiển trực quan, và đóng gói triển khai bằng container.

## 1.4. Đối tượng và phạm vi

**Đối tượng nghiên cứu:** các thuật toán xử lý luồng dữ liệu một lượt (single-pass streaming algorithms) và thuật toán khai phá mẫu phổ biến (frequent pattern mining), áp dụng trên dữ liệu giao dịch không gian–thời gian.

**Dữ liệu:** *New York City Taxi & Limousine Commission Trip Record Data*, phân đoạn *High Volume For-Hire Vehicle* (FHVHV — bao gồm Uber, Lyft), tháng 01/2024, gồm **19.663.928 bản ghi** đã qua xác minh chất lượng (Chương 3).

**Phạm vi kỹ thuật:**

- Cài đặt from scratch bằng ngôn ngữ Python, đối chiếu thư viện `mlxtend` chỉ với vai trò kiểm định, không phụ thuộc để vận hành.
- Đánh giá thực nghiệm chủ yếu trên một tháng dữ liệu (19,66 triệu sự kiện) — quy mô đủ lớn để thể hiện đặc tính bất đối xứng $O(\log N)$ so với $O(N)$ mà không đòi hỏi hạ tầng tính toán phân tán.
- Dữ liệu là **lịch sử được phát lại có kiểm soát**, không phải luồng trực tuyến thật — giới hạn này được thừa nhận công khai và phân tích tác động ở Chương 6, không che giấu.

**Phạm vi loại trừ** (không thuộc mục tiêu đồ án, tránh phình phạm vi): không xây dựng mô hình dự báo có giám sát, không xử lý dữ liệu thời tiết hay sự kiện ngoại sinh, không tối ưu hóa tuyến đường, không triển khai trên hạ tầng phân tán thật (Spark/Flink).

## 1.5. Ý nghĩa khoa học và thực tiễn

**Ý nghĩa khoa học:** đồ án không dừng ở việc lặp lại các ví dụ minh họa trong tài liệu giảng dạy mà mở rộng theo hai hướng cụ thể — (a) một phần mở rộng thuật toán (DGIM cho tổng số nguyên, được tài liệu giảng dạy nêu tên nhưng không triển khai chi tiết) kèm câu hỏi nghiên cứu về phân bổ tham số chưa được đề cập trong tài liệu, và (b) một thực nghiệm định lượng trên dữ liệu thật cho tính chất lý thuyết (bất biến với giao dịch rỗng) mà tài liệu giảng dạy chỉ minh họa bằng ví dụ giả định.

**Ý nghĩa thực tiễn:** kiến trúc và bài học rút ra — đặc biệt về tối ưu hóa xử lý theo lô cho các cấu trúc có tính kết hợp, và về việc tham số thiết kế trên giấy cần được kiểm chứng lại khi gặp dữ liệu thật — có thể áp dụng cho các bài toán giám sát luồng dữ liệu quy mô lớn khác ngoài phạm vi giao thông đô thị.

## 1.6. Cấu trúc báo cáo

Báo cáo được tổ chức thành bảy chương:

- **Chương 2 — Cơ sở lý thuyết**, hệ thống hóa kiến thức nền về mô hình luồng dữ liệu, các thuật toán DGIM/Flajolet-Martin/AMS, khai phá mẫu phổ biến bằng FP-Growth, và các độ đo tương quan luật kết hợp.
- **Chương 3 — Phân tích bài toán**, trình bày quy trình lựa chọn đề tài, phân tích cạnh tranh với các đề tài cùng lớp, và xác minh chất lượng dữ liệu thật.
- **Chương 4 — Thiết kế hệ thống**, mô tả kiến trúc bảy tầng, các quyết định thiết kế then chốt, và lược đồ cơ sở dữ liệu.
- **Chương 5 — Thực nghiệm**, trình bày chi tiết mười hai thực nghiệm (E1–E12) cùng số liệu đo được.
- **Chương 6 — Đánh giá**, tổng hợp và phân tích phê phán kết quả, đối chiếu với mục tiêu đặt ra, thảo luận hạn chế.
- **Chương 7 — Kết luận và hướng phát triển**, tóm tắt đóng góp và đề xuất mở rộng.

Phụ lục cung cấp mã nguồn tham chiếu, sơ đồ bổ sung và bảng tra cứu tham số.
