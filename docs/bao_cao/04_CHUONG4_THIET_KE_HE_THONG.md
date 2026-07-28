# CHƯƠNG 4. THIẾT KẾ HỆ THỐNG

*(Chương này tương ứng pha Modeling của CRISP-DM về mặt kiến trúc; chi tiết thiết kế đầy đủ tại [`03_THIET_KE_KIEN_TRUC.md`](../03_THIET_KE_KIEN_TRUC.md).)*

## 4.1. Kiến trúc tổng thể

Hệ thống CityFlow tổ chức theo bảy tầng, từ nguồn dữ liệu thô tới giao diện người dùng:

```
L0  Ingestion & Replay      — nạp và phát lại luồng sự kiện (đã sắp xếp thời gian)
L1  Streaming Sketch Layer  — DGIM, DGIM-Integer, Flajolet-Martin, AMS, Reservoir
L2  State Store             — quản lý trạng thái sketch trong bộ nhớ
L3  Mining Layer            — FP-Growth, tính độ đo tương quan, sinh luật
L4  API Layer               — FastAPI, các endpoint REST
L5  Web Dashboard           — React, bốn màn hình trực quan
L6  Benchmark Harness       — đối chiếu ước lượng với oracle chính xác
```

Nguyên tắc thiết kế xuyên suốt:

- **P1 (một lượt):** tầng sketch chỉ được thấy mỗi sự kiện đúng một lần, không lưu lại.
- **P2 (bộ nhớ đo thật):** mọi cấu trúc sketch có phương thức `memory_bytes()` đo bộ nhớ thực tế đang chiếm dụng, không ước lượng bằng công thức lý thuyết — cho phép đối chiếu trực tiếp lý thuyết với cài đặt thật.
- **P3 (oracle tách biệt):** giá trị chính xác dùng để đối chiếu được tính bằng một đường mã hoàn toàn độc lập với sketch (tổng tiền tố trên mảng đầy đủ), loại trừ khả năng "so sánh với chính mình".
- **P4 (from scratch trước, thư viện sau):** mọi thuật toán lõi tự cài đặt; thư viện tham chiếu (`mlxtend`) chỉ dùng để kiểm định, không phải thành phần vận hành.
- **P5 (tham số là biến thực nghiệm):** mọi tham số thuật toán ($N, r, m, g, k$, ngưỡng hỗ trợ tối thiểu) đều cấu hình được, phục vụ trực tiếp cho ma trận thực nghiệm ở Chương 5.

## 4.2. Ánh xạ sự kiện thành 535 luồng song song

Quyết định thiết kế quan trọng nhất của hệ thống: mỗi sự kiện chuyến đi sinh một bit cho **mỗi** trong số 535 luồng — 265 luồng theo khu vực đón, 265 luồng theo khu vực trả, và 5 luồng theo vị từ toàn cục (sân bay, chuyến dài, có phụ phí ùn tắc, đi chung, giá cao).

Với mỗi sự kiện, tuyệt đại đa số (534/535) luồng nhận bit 0. Theo nguyên lý DGIM — bit 0 không làm thay đổi trạng thái cấu trúc — hệ thống chỉ cần chạm vào các luồng thực sự nhận bit 1, dùng một **đồng hồ toàn cục dùng chung** thay vì mỗi luồng tự đếm riêng, và trì hoãn việc loại bucket hết hạn tới thời điểm truy vấn (lazy expiration) thay vì thực hiện ở mỗi lần cập nhật.

## 4.3. Tầng khai phá mẫu — thành phần bắt buộc

Các câu hỏi Q1–Q5 (tầng sketch) trả lời "bao nhiêu", nhưng không trả lời "ở đâu, cùng với ai". Tầng khai phá mẫu (Q6) là thành phần **bắt buộc**, không phải bổ sung tùy chọn: nó chuyển đổi lịch sử luồng đã sắp xếp thành các **giỏ hàng** (mỗi giỏ = một cửa sổ 15 phút), trong đó item là khu vực đang ở trạng thái "hoạt động cao" trong cửa sổ đó, rồi áp dụng FP-Growth để tìm các tổ hợp khu vực đồng xuất hiện.

**Rời rạc hóa theo phân vị riêng từng khu vực** (không dùng ngưỡng tuyệt đối chung): nếu dùng ngưỡng tuyệt đối, các khu vực có quy mô hoạt động lớn sẽ luôn được đánh dấu "hoạt động cao" bất kể biến động thực tế, khiến luật khai phá được trở thành phát biểu tầm thường ("khu vực trung tâm luôn bận"). Chuẩn hóa theo phân vị của chính từng khu vực đảm bảo luật tìm được phản ánh độ lệch so với hành vi thông thường của khu vực đó, không phải quy mô tuyệt đối.

## 4.4. Thiết kế cơ sở dữ liệu

CSDL PostgreSQL lưu trữ kết quả đã được xử lý — không lưu trạng thái sketch đang chạy (bản chất sketch là cấu trúc trong bộ nhớ tiến trình) — theo bảy bảng:

| Bảng | Vai trò |
|---|---|
| `zones` | Danh mục 265 khu vực, kèm hình học GeoJSON cho bản đồ |
| `sketch_snapshots` | Ảnh chụp định kỳ trạng thái sketch (phục vụ khôi phục) |
| `window_aggregates` | Tổng hợp theo cửa sổ 15 phút — đầu vào tầng khai phá |
| `mining_runs` | Metadata mỗi lần chạy khai phá mẫu |
| `frequent_itemsets` | Tập mục thường xuyên tìm được, đánh dấu đóng/cực đại |
| `association_rules` | Luật kết hợp kèm đầy đủ mười độ đo tương quan |
| `benchmark_results` | Kết quả các thực nghiệm E1–E12 |

## 4.5. Thiết kế API và giao diện

**API (FastAPI):** mỗi endpoint ước lượng trả về kèm tham số cấu hình và cận sai số lý thuyết liên quan, biến chính API thành công cụ minh chứng chứ không chỉ phục vụ dữ liệu. Ví dụ, endpoint `/api/window/count` trả về ước lượng cùng với `theoretical_bound` và bộ tham số $(N, r)$ đã dùng.

**Giao diện (React + Leaflet + Recharts):** bốn màn hình tương ứng bốn nhu cầu sử dụng khác nhau:

- **Live Monitor:** bản đồ nhiệt 265 khu vực (tọa độ trung tâm suy từ shapefile TLC, chuyển hệ tọa độ NAD83 State Plane sang WGS84), thanh trượt điều chỉnh độ rộng cửa sổ $N$ trực tiếp.
- **Accuracy Lab:** bảng đối chiếu sai số ước lượng theo khu vực/tham số với cận lý thuyết.
- **Pattern Explorer:** bảng luật kết hợp, cho phép đổi độ đo xếp hạng và quan sát trực tiếp sự đảo lộn thứ hạng.
- **Benchmark Dashboard:** biểu đồ tổng hợp toàn bộ thực nghiệm E1–E11.

**Triển khai:** đóng gói bằng Docker Compose ba dịch vụ (`db`, `api`, `web`), khởi động bằng một lệnh duy nhất.

## 4.6. Ma trận thực nghiệm

Mười hai thực nghiệm (E1–E12) được thiết kế để mỗi cận lý thuyết ở Chương 2 đều có một phép đo thực nghiệm tương ứng đối chiếu trực tiếp — trình bày chi tiết ở Chương 5.
