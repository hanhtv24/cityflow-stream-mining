# SCRIPT DEMO — CITYFLOW

Kịch bản trình bày trực tiếp trước hội đồng, ước lượng 8–10 phút, đồng bộ với [`CityFlow_Slide_Bao_Ve.pptx`](../slides/CityFlow_Slide_Bao_Ve.pptx).

---

## Chuẩn bị trước buổi bảo vệ (làm trước, không demo trực tiếp)

```bash
docker compose up -d
python scripts/08_load_zones.py     # nạp danh mục khu vực (chạy 1 lần)
```

Đợi 3 dịch vụ `Up (healthy)`:
```bash
docker compose ps
```

Mở sẵn ba tab trình duyệt: `http://localhost:3000` (dashboard), `http://localhost:8000/docs` (Swagger API), terminal chạy `pytest`.

---

## Bước 1 — Khởi động một lệnh (30 giây)

> *"Toàn bộ hệ thống — cơ sở dữ liệu, API, và giao diện — khởi động bằng đúng một lệnh."*

```bash
docker compose ps
```

Chỉ vào 3 container đang chạy: `db`, `api`, `web`. Không cần giải thích thêm — đây là bằng chứng cho yêu cầu "Docker để chạy một lệnh".

## Bước 2 — Live Monitor: bản đồ nhiệt thời gian thực (2 phút)

Mở `http://localhost:3000`.

> *"Đây là bản đồ nhiệt 265 khu vực taxi New York, cập nhật từ dữ liệu thật đang được nạp vào hệ thống."*

- Chỉ vào góc trên bên phải: chỉ số tiến độ nạp dữ liệu (%, thông lượng sự kiện/giây).
- Kéo thanh trượt **N** từ nhỏ sang lớn — quan sát các điểm trên bản đồ đổi màu/kích thước theo thời gian gần thực.
- Chỉ vào bốn ô thống kê bên phải: *"Đây là bốn trong sáu câu hỏi nghiệp vụ — mỗi con số là một ước lượng DGIM hoặc Flajolet-Martin, không phải số đếm chính xác, và mỗi con số đều kèm sai số đã đo được."*

## Bước 3 — Pattern Explorer: đảo thứ hạng luật trực tiếp (2 phút) — ⭐ phần ấn tượng nhất

Chuyển sang tab **Pattern Explorer**.

> *"Đây là kết quả khai phá mẫu — các khu vực có xu hướng ùn tắc cùng nhau."*

- Với độ đo mặc định **Kulczynski**, chỉ vào luật đầu: *"Midtown Center và Midtown East — hai khu vực liền kề thật ở trung tâm Manhattan."*
- **Bấm sang độ đo Lift.** Bảng đổi thứ tự ngay trước mắt hội đồng.
- Kéo xuống phần tương quan Spearman, chỉ vào con số **Support vs Kulczynski = 0,124**: *"Gần như không tương quan — luật phổ biến nhất và luật có quan hệ chặt nhất là hai câu hỏi khác nhau."*

## Bước 4 — Benchmark Dashboard: minh chứng bằng số (2 phút)

Chuyển sang tab **Benchmark**.

> *"Đây không phải giao diện trang trí — mọi biểu đồ đọc trực tiếp từ file kết quả thực nghiệm đã chạy trên 19,66 triệu sự kiện thật."*

- Chỉ vào biểu đồ **E2**: *"Đường nét đứt màu hồng gần như phẳng — xác nhận quan hệ sai số tỷ lệ nghịch với r mà lý thuyết dự đoán."*
- Chỉ vào bảng **E9**: *"FP-Growth nhanh hơn Apriori tới 91 lần, và hai thuật toán cho kết quả giống hệt nhau ở mọi mức — đây là bằng chứng tự kiểm chứng ngay trong mã nguồn."*

## Bước 5 — Chạy kiểm định trực tiếp (1–2 phút, tùy chọn nếu còn thời gian)

Chuyển sang terminal:

```bash
PYTHONIOENCODING=utf-8 pytest tests/ -q
```

> *"158 kiểm định, phần lớn tái hiện trực tiếp các ví dụ số trong tài liệu giảng dạy — ví dụ này là ví dụ AMS ở slide trang 48, kỳ vọng kết quả đúng bằng 55."*

Đợi kết quả `158 passed`.

## Bước 6 — Kết luận (30 giây)

> *"Ba đóng góp chính: xác nhận đầy đủ ba cận lý thuyết của DGIM trên dữ liệu thật; một giả thuyết nghiên cứu độc lập về phân bổ ngân sách bộ nhớ, được suy dẫn bằng nhân tử Lagrange và kiểm chứng thực nghiệm; và bằng chứng hoàn hảo — biến thiên đúng bằng không phần trăm — cho tính bất biến với giao dịch rỗng của sáu độ đo tương quan."*

---

## Phương án dự phòng nếu API/Docker gặp sự cố khi demo trực tiếp

Nếu môi trường mạng nơi bảo vệ không ổn định:

1. Dùng ảnh chụp màn hình đã chuẩn bị sẵn của 4 màn hình dashboard (chụp trước, lưu trong `docs/bao_cao/screenshots/`).
2. Chạy trực tiếp một script thực nghiệm nhỏ, nhanh, không cần mạng:
   ```bash
   PYTHONIOENCODING=utf-8 pytest tests/test_mining.py -v
   ```
3. Mở trực tiếp file JSON kết quả (`docs/e9_e11_results.json`) làm bằng chứng số liệu đã có sẵn, không phụ thuộc hệ thống đang chạy.

## Câu hỏi phản biện dự kiến và câu trả lời ngắn

| Câu hỏi khả năng cao | Câu trả lời cốt lõi |
|---|---|
| Đây có phải luồng thời gian thực không? | Không — dữ liệu lịch sử phát lại có kiểm soát; thừa nhận rõ ở Chương 6, nhưng ràng buộc bộ nhớ và thuật toán một-lượt là thật |
| Vì sao không tính chính xác luôn? | 265 khu vực × nhiều loại truy vấn × N=10⁶ → bộ nhớ tuyến tính không kiểm soát được; đã đo: tiết kiệm 11,8× |
| Đâu là phần "khai phá dữ liệu", không chỉ là ước lượng thống kê? | Tầng FP-Growth (Q6) — luật đồng ùn tắc, không phải sketch |
| Kết quả có đúng không, hay chỉ tự nhóm tự kiểm tra? | Đối chiếu độc lập với thư viện `mlxtend`, sai lệch bằng 0 trên 20 phép thử |
