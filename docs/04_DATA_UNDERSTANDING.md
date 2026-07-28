# PHASE 5 · BƯỚC 1 — DATA UNDERSTANDING

## Xác minh rủi ro R1 trên dữ liệu thật

**Ngày thực hiện:** 2026-07-27
**Dữ liệu:** NYC TLC Trip Records, tháng 01/2024
**Công cụ:** DuckDB 1.5.5 · Python 3.12.9
**Script:** [`scripts/01_data_understanding.py`](../scripts/01_data_understanding.py)
**Log đầy đủ:** [`data_understanding_log.txt`](data_understanding_log.txt) · **Kết quả máy đọc:** [`data_understanding_results.json`](data_understanding_results.json)

> Mọi con số trong tài liệu này là **số liệu đo thật**, không phải ước lượng. Các giả định của Phase 4 được đối chiếu và ghi rõ đúng/sai.

---

## 0. TÓM TẮT ĐIỀU HÀNH

**R1 đã được xác minh — dữ liệu phù hợp, nhưng ba giả định của Phase 4 sai và cần điều chỉnh thiết kế.**

| Kết luận | Chi tiết |
|---|---|
| ✅ **Quy mô đạt yêu cầu** | 19.66 triệu bản ghi/tháng · 12 tháng ≈ **236 triệu** — thỏa C4 |
| ✅ **Chất lượng dữ liệu xuất sắc** | **0 giá trị thiếu** trên toàn bộ 11 cột CityFlow sử dụng |
| ✅ **Giả định về khu vực đúng** | 265 khu vực · sân bay = {1, 132, 138} đúng như Phase 4 |
| 🔴 **Sai #1 — thứ tự sự kiện** | **44.67% bản ghi lệch thứ tự thời gian** theo thứ tự file |
| 🔴 **Sai #2 — tham số m** | Phase 4 giả định $m=12$; số liệu thật cho $m=8$ (hoặc 11) |
| 🟡 **Sai #3 — độ lệch phân phối** | Phase 4 lo "Midtown luôn bận"; thực tế top-10 chỉ chiếm **13.3%** |

---

## 1. QUY MÔ VÀ LƯỢC ĐỒ

### 1.1. Đối chiếu với ước tính Phase 4

| Tập dữ liệu | Ước tính Phase 4 | **Đo thật** | Kết luận |
|---|---|---|---|
| FHVHV 2024-01 | ~18–20 triệu | **19.663.930** | ✅ Đúng |
| Yellow 2024-01 | ~3–4 triệu | **2.964.624** | ✅ Đúng |
| Số khu vực | 265 | **265** | ✅ Đúng |
| Kích thước FHVHV | — | 472,8 MB (parquet) | — |

**Ngoại suy 12 tháng:** $19{,}66 \times 12 \approx \mathbf{236}$ **triệu bản ghi**, ~5,7 GB parquet.
Đĩa còn trống 35 GB ⇒ khả thi, nhưng nên xử lý tuần tự theo tháng thay vì nạp toàn bộ.

### 1.2. Lược đồ FHVHV (24 cột) — 11 cột CityFlow sử dụng

| Cột | Kiểu | Vai trò trong CityFlow |
|---|---|---|
| `pickup_datetime` | TIMESTAMP | Thứ tự sự kiện, khóa cửa sổ |
| `dropoff_datetime` | TIMESTAMP | Kiểm tra tính hợp lệ |
| `PULocationID` | INTEGER | **Định danh luồng** (265 luồng khu vực đón) |
| `DOLocationID` | INTEGER | 265 luồng khu vực trả · tuyến đường cho FM |
| `trip_miles` | DOUBLE | Vị từ, DGIM số nguyên (biến thể) |
| `trip_time` | BIGINT | Vị từ "chuyến dài" |
| `base_passenger_fare` | DOUBLE | DGIM số nguyên (doanh thu) |
| `tips`, `tolls` | DOUBLE | Thành phần doanh thu |
| `congestion_surcharge` | DOUBLE | Vị từ "phụ phí ùn tắc" |
| `shared_request_flag` | VARCHAR | Vị từ "đi chung" |

**⚠️ Khác biệt so với Yellow Taxi:** FHVHV **không có cột `total_amount` sẵn** (Yellow thì có) và **không có `payment_type`**.

**Hệ quả điều chỉnh thiết kế:**
- Doanh thu phải tự tính: `base_passenger_fare + tips + tolls`
- **Vị từ "thanh toán tiền mặt" ở Phase 4 §4.1 KHÔNG khả thi** với FHVHV — Uber/Lyft không có tiền mặt. Thay bằng vị từ khác (xem §6).

---

## 2. CHẤT LƯỢNG DỮ LIỆU

### 2.1. Giá trị thiếu — kết quả bất ngờ tích cực

| Cột | Số null | Tỷ lệ |
|---|---:|---:|
| Tất cả 11 cột CityFlow sử dụng | **0** | **0,00%** |

Không cần bất kỳ chiến lược xử lý thiếu giá trị nào. Điều này rút ngắn đáng kể bước Data Preparation.

### 2.2. Tính hợp lệ

| Kiểm tra | Số bản ghi | Tỷ lệ | Xử lý |
|---|---:|---:|---|
| `dropoff ≤ pickup` | 2 | 0,00001% | Loại |
| `trip_miles ≤ 0` | 3.286 | 0,017% | Giữ, đánh dấu |
| `trip_time ≤ 0` | 2 | 0,00001% | Loại |
| `PULocationID` ngoài [1,265] | **0** | 0% | — |
| `DOLocationID` ngoài [1,265] | **0** | 0% | — |
| Doanh thu âm | 167 | 0,0008% | Kẹp về 0, ghi nhận |

**Khoảng thời gian:** `2024-01-01 00:00:00` → `2024-01-31 23:59:59` — biên tháng sạch, **không tràn sang tháng khác**.

> 📌 Điều này quan trọng: cho phép **sắp xếp theo từng tháng rồi nối lại** để có thứ tự toàn cục đúng, thay vì phải sắp xếp toàn bộ 236 triệu bản ghi một lần.

### 2.3. Khu vực đặc biệt

**Sân bay — xác nhận giả định Phase 4 hoàn toàn đúng:**

| LocationID | Tên | Borough |
|---:|---|---|
| 1 | Newark Airport | EWR |
| 132 | JFK Airport | Queens |
| 138 | LaGuardia Airport | Queens |

**Khu vực Unknown:** LocationID **264** (Borough `N/A`) và **265** (Borough `Unknown`).

| Trường | Số bản ghi unknown | Tỷ lệ | Quyết định |
|---|---:|---:|---|
| `PULocationID` | 765 | 0,004% | Không đáng kể |
| `DOLocationID` | **741.161** | **3,77%** | 🔴 **Không thể bỏ qua** |

**Quyết định thiết kế:** **giữ lại** các bản ghi này. Với nhóm luồng theo khu vực trả, gộp 264/265 thành **một luồng `unknown` riêng** thay vì loại bỏ — loại bỏ 3,77% sẽ làm lệch ground truth của mọi ước lượng liên quan đến khu vực trả, và ground truth sạch chính là điểm mạnh số một của đề tài này (tiêu chí C5).

**Khu vực không bao giờ là điểm đón:** 262/265 khu vực xuất hiện làm điểm đón ⇒ **3 khu vực có 0 sự kiện**.
Hệ quả: `SketchRegistry` phải xử lý được luồng rỗng (query trên DGIM không có bucket nào phải trả 0, không được lỗi).

---

## 3. 🔴 PHÁT HIỆN #1 — 44,67% BẢN GHI LỆCH THỨ TỰ THỜI GIAN

### Số liệu

```
Bản ghi có pickup_datetime < bản ghi liền trước (theo thứ tự file): 8.784.851 / 19.663.930
Tỷ lệ: 44,67%
```

**File parquet KHÔNG được sắp xếp theo `pickup_datetime`.**

### Vì sao đây là phát hiện nghiêm trọng

Toàn bộ tính đúng đắn của tầng L1 phụ thuộc vào **thứ tự sự kiện**:

- **DGIM** lưu timestamp và loại bucket khi `now - timestamp ≥ N`. Nếu sự kiện đến sai thứ tự, bất biến "bucket mới nhỏ hơn bucket cũ hơn" (Phase 4 §4.1) bị phá vỡ.
- **Cửa sổ trượt** mất hoàn toàn ý nghĩa nếu "N sự kiện gần nhất" không thật sự là gần nhất theo thời gian.
- **AMS** dùng vị trí trong luồng làm cơ sở chọn mẫu ngẫu nhiên.

Nếu không phát hiện điều này và cứ đọc parquet tuần tự để nạp vào sketch, **mọi kết quả thực nghiệm sẽ sai mà không có dấu hiệu báo lỗi nào** — kiểu lỗi nguy hiểm nhất.

### Điều chỉnh thiết kế

Thêm **bước tiền xử lý bắt buộc** vào tầng L0:

```
raw/fhvhv_tripdata_YYYY-MM.parquet
    │
    ├─ lọc bản ghi không hợp lệ (dropoff ≤ pickup, trip_time ≤ 0)
    ├─ tính cột dẫn xuất: total_revenue, is_airport, is_long_trip, ...
    ├─ ORDER BY pickup_datetime            ← BƯỚC MỚI, BẮT BUỘC
    └─▶ processed/events_YYYY-MM.parquet
```

Vì biên tháng sạch (§2.2), sắp xếp theo từng tháng rồi nối lại cho **thứ tự toàn cục đúng** — không cần sắp xếp 236 triệu bản ghi một lần.

**Giá trị học thuật:** đây không phải chi tiết kỹ thuật vụn vặt mà là minh họa cho một vấn đề kinh điển của hệ thống luồng — phân biệt **event time** và **processing time**. Sẽ được trình bày trong chương Data Preparation của báo cáo.

---

## 4. 🔴 PHÁT HIỆN #2 — THAM SỐ $m$ CỦA DGIM SỐ NGUYÊN

### Phân phối doanh thu thực tế

Doanh thu $=$ `base_passenger_fare + tips + tolls`:

| Thống kê | Giá trị (USD) |
|---|---:|
| Nhỏ nhất | −36,63 |
| Trung vị (p50) | 18,76 |
| Trung bình | 26,07 |
| p95 | 68,52 |
| p99 | 123,87 |
| **p99.9** | **227,42** |
| Lớn nhất | **1.961,28** |
| Số bản ghi âm | 167 |

### Chốt tham số

| Lựa chọn | $m$ | Phủ | Tỷ lệ bị kẹp trần |
|---|:--:|---|---|
| Theo p99.9 | **8** | 0–255 USD | ~0,1% |
| Theo max | **11** | 0–2047 USD | 0% |
| ~~Phase 4 giả định~~ | ~~12~~ | ~~0–4095~~ | Thừa 1 bit vô ích |

**Quyết định:** mặc định $m = 8$, có kẹp trần tại 255 USD, **ghi nhận và báo cáo tỷ lệ bị kẹp**.
$m$ vẫn là **biến độc lập của thực nghiệm E4** — sẽ chạy $m \in \{8, 10, 11, 12\}$.

### 🔬 Tác động tích cực lên giả thuyết H1

Phát hiện này **làm giả thuyết H1 thú vị hơn**, không phải làm hỏng nó.

Phân phối doanh thu lệch phải rất mạnh (trung vị 18,76 nhưng max 1.961). Nghĩa là:

- Bit thấp (0–4, tức giá trị 1–16 USD): **rất nhiều bit 1**, bucket dày, sai số tương đối thấp
- Bit cao (6–7, tức giá trị 64–128 USD): **rất ít bit 1** (chỉ ~1% chuyến vượt 124 USD), bucket thưa, bucket cũ nhất chiếm tỷ trọng lớn ⇒ **sai số tương đối cao**
- Mà bit cao lại được nhân với trọng số lớn nhất ($2^7 = 128$)

⇒ Đây **chính xác là điều kiện H1 dự đoán**: sai số tổng bị chi phối bởi các luồng bit cao. Dữ liệu thật cho một môi trường kiểm chứng lý tưởng.

**Cập nhật H1 với số liệu cụ thể:**
> Với $m=8$ trên phân phối doanh thu FHVHV, phân bổ $r$ không đồng đều theo hướng $r_7 > r_6 > \dots > r_0$ sẽ cho sai số tổng thấp hơn phân bổ đồng đều $r_i = 2$ ở cùng tổng ngân sách bộ nhớ.

---

## 5. 🟡 PHÁT HIỆN #3 — PHÂN PHỐI KHU VỰC ĐỀU HƠN DỰ KIẾN

### Top 10 khu vực đón

| Hạng | ID | Tên khu vực | Số chuyến | Tỷ lệ |
|---:|---:|---|---:|---:|
| 1 | 132 | JFK Airport | 374.293 | 1,90% |
| 2 | 138 | LaGuardia Airport | 345.116 | 1,76% |
| 3 | 79 | East Village | 269.982 | 1,37% |
| 4 | 61 | Crown Heights North | 256.556 | 1,30% |
| 5 | 230 | Times Sq/Theatre District | 246.353 | 1,25% |
| 6 | 161 | Midtown Center | 242.893 | 1,24% |
| 7 | 231 | TriBeCa/Civic Center | 232.205 | 1,18% |
| 8 | 68 | East Chelsea | 219.684 | 1,12% |
| 9 | 246 | West Chelsea/Hudson Yards | 218.496 | 1,11% |
| 10 | 234 | Union Sq | 218.090 | 1,11% |

**Top 10 chỉ chiếm 13,3% tổng số chuyến.** Không khu vực nào vượt 2%.

### Tác động lên thiết kế

**① Rời rạc hóa "hot" (Phase 4 §5.1) — vẫn giữ nguyên quyết định, nhưng vì lý do khác.**

Nỗi lo ban đầu là *"Midtown luôn hot nên luật sẽ tầm thường"*. Số liệu cho thấy nỗi lo đó **nhẹ hơn dự kiến** — không có khu vực nào áp đảo.

Tuy nhiên **vẫn phải chuẩn hóa theo phân vị của từng khu vực**, vì chênh lệch tuyệt đối giữa khu vực lớn nhất (374 nghìn) và nhỏ nhất vẫn rất lớn. Ngưỡng tuyệt đối sẽ khiến các khu vực nhỏ **không bao giờ** hot và không bao giờ xuất hiện trong luật.

**② 🔴 Rủi ro mới cho AMS (Q4).**

Số bất ngờ (mô-men bậc 2) đo độ lệch phân phối. Với phân phối tương đối đều như thế này, số bất ngờ sẽ **thấp và ổn định** ⇒ khả năng phát hiện bất thường của AMS có thể yếu.

**Biện pháp:** thay vì tính AMS trên phân phối khu vực **toàn cục**, tính trên **cửa sổ ngắn** (15 phút). Trong cửa sổ ngắn, một sự kiện lớn (trận đấu, buổi hòa nhạc, gián đoạn tàu điện) sẽ tạo độ lệch rõ rệt hơn nhiều so với thống kê cả tháng. **Đây là điều chỉnh cần kiểm chứng sớm ở tuần 3**, không chờ đến tuần 5.

---

## 6. ĐIỀU CHỈNH TẬP LUỒNG (Phase 4 §4.1)

Vị từ "thanh toán tiền mặt" không khả thi (FHVHV không có `payment_type`). Tập luồng cập nhật:

| Nhóm luồng | Số lượng | Vị từ | Trạng thái |
|---|:--:|---|---|
| Khu vực đón | 265 | `PULocationID == z` | ✅ Giữ |
| Khu vực trả | 265 | `DOLocationID == z` (264/265 gộp thành `unknown`) | ✅ Giữ, có điều chỉnh |
| ~~Thanh toán tiền mặt~~ | ~~1~~ | ~~`payment_type == cash`~~ | ❌ **Loại — không có cột** |
| Chuyến sân bay | 1 | `PU ∈ {1,132,138}` hoặc `DO ∈ {1,132,138}` | ✅ Giữ |
| Chuyến dài | 1 | `trip_time > 1800` | ✅ Giữ |
| Có phụ phí ùn tắc | 1 | `congestion_surcharge > 0` | ✅ Giữ |
| Chuyến đi chung | 1 | `shared_request_flag == 'Y'` | ✅ Giữ |
| **Chuyến giá cao** | 1 | `revenue > p95 (68,52 USD)` | 🆕 **Thêm — thay thế** |
| **Tổng** | **535** | | |

Tổng vẫn là **535 luồng** như thiết kế Phase 4.

---

## 7. GROUND TRUTH CHO FLAJOLET-MARTIN

**Số tuyến (cặp đón–trả) phân biệt trong tháng: 58.911** (trên tối đa lý thuyết $265^2 = 70.225$, tức 83,9%).

### 🔬 Vấn đề độ hạt của Flajolet-Martin

FM ước lượng $2^R$ — **luôn là lũy thừa của 2**. Với giá trị thật 58.911:

$$2^{15} = 32.768 \quad < \quad 58.911 \quad < \quad 65.536 = 2^{16}$$

| Ước lượng FM | Sai số tương đối |
|---:|---:|
| $2^{15} = 32.768$ | **−44,4%** |
| $2^{16} = 65.536$ | **+11,2%** |

**Ước lượng FM đơn lẻ không thể tốt hơn hai con số này.** Đây chính là nhược điểm slide tr.40 nêu: *"Dùng trung vị — tốt hơn, nhưng kết quả luôn là lũy thừa của 2"*.

Giải pháp của slide — **trung bình trong nhóm rồi lấy trung vị các trung bình** — phá vỡ ràng buộc lũy thừa của 2 vì phép lấy trung bình sinh giá trị liên tục.

⇒ **Thực nghiệm E5 giờ có một câu hỏi sắc nét và một con số cụ thể để hướng tới:**
> Chiến lược median-of-means có đưa sai số xuống dưới 11,2% (cận tốt nhất của FM đơn) hay không, và cần bao nhiêu hàm băm $m$ để đạt được?

Ngưỡng thành công 15% đặt ra ở Phase 4 §1.4 giờ có thể đánh giá chính xác: nó **nằm giữa** hai cận nói trên, nên là mục tiêu hợp lý nhưng không tầm thường.

---

## 8. XÁC NHẬN TÍNH PHI DỪNG *(slide tr.7)*

Phân phối chuyến theo giờ trong ngày:

| Giờ | Số chuyến | | Giờ | Số chuyến |
|---:|---:|---|---:|---:|
| 00h | 697.067 | | 12h | 832.440 |
| 01h | 492.869 | | 13h | 867.183 |
| 02h | 368.463 | | 14h | 957.194 |
| 03h | 296.869 | | 15h | 983.663 |
| **04h** | **295.770** ← thấp nhất | | 16h | 1.018.763 |
| 05h | 344.232 | | 17h | 1.169.233 |
| 06h | 548.915 | | **18h** | **1.217.661** ← cao nhất |
| 07h | 863.545 | | 19h | 1.156.888 |
| 08h | 1.040.792 | | 20h | 1.059.668 |
| 09h | 915.835 | | 21h | 1.016.300 |
| 10h | 820.397 | | 22h | 1.001.910 |
| 11h | 806.770 | | 23h | 891.503 |

**Tỷ lệ cao điểm / thấp điểm = 4,1×**

> Slide tr.7: *"Phi dừng (non-stationary) — phân phối dữ liệu có thể thay đổi (theo mùa, ngày, giờ)"*

Số liệu xác nhận trực tiếp phát biểu này với hệ số 4,1×. Đây là **bằng chứng thực nghiệm** cho phần cơ sở lý thuyết của báo cáo, và là lý do chính đáng để hệ thống dùng cửa sổ trượt thay vì thống kê tích lũy.

---

## 9. CHECKLIST §2.3 CỦA PHASE 4

| | Mục kiểm tra | Kết quả |
|:--:|---|---|
| ✅ | Đếm số bản ghi thật | 19.663.930 — đúng ước tính |
| ✅ | Giá trị thiếu theo cột | 0 trên toàn bộ 11 cột sử dụng |
| ✅ | Tính hợp lệ | < 0,02% bản ghi có vấn đề |
| ✅ | Phân phối theo giờ/ngày/khu vực | Xác nhận phi dừng 4,1× |
| ✅ | LocationID 264/265 | PU 0,004% · **DO 3,77%** — giữ lại, gộp thành luồng riêng |
| ✅ | Sự kiện lệch thứ tự | **44,67% — cần sắp xếp lại** |
| ✅ | Phân phối `total_amount` | Chốt $m = 8$ (không phải 12) |
| ✅ | Xác minh LocationID sân bay | {1, 132, 138} — đúng giả định |

---

## 10. TÁC ĐỘNG LÊN KẾ HOẠCH

| Thay đổi | Ảnh hưởng tiến độ |
|---|---|
| Thêm bước sắp xếp theo `pickup_datetime` vào L0 | +0,5 ngày tuần 1 |
| Đổi $m$ mặc định 12 → 8, thêm cơ chế kẹp trần | Không đáng kể |
| Đổi vị từ "tiền mặt" → "chuyến giá cao" | Không đáng kể |
| Gộp 264/265 thành luồng `unknown` | Không đáng kể |
| **Kiểm chứng sớm AMS trên cửa sổ ngắn** | **Đưa từ tuần 5 lên tuần 3** |

**Không có thay đổi nào ảnh hưởng đến kiến trúc tổng thể.** Cả 6 câu hỏi nghiệp vụ Q1–Q6 giữ nguyên, 8 tiêu chí C1–C8 vẫn được thỏa mãn.

---

## 11. KẾT LUẬN

**R1 đóng — dữ liệu đã được xác minh và phù hợp với đề tài.**

Ba điều chỉnh thiết kế bắt buộc, tất cả đều nhỏ về công sức nhưng quan trọng về tính đúng đắn:

1. **Sắp xếp theo `pickup_datetime` trước khi phát lại** — nếu bỏ qua, mọi kết quả sai mà không báo lỗi
2. **$m = 8$ thay vì 12**, kèm kẹp trần và ghi nhận tỷ lệ kẹp
3. **Kiểm chứng AMS trên cửa sổ ngắn ngay tuần 3** — phân phối đều hơn dự kiến làm giảm hiệu lực của số bất ngờ trên phạm vi toàn cục

Đồng thời, hai phát hiện **làm mạnh thêm** phần thực nghiệm:
- Phân phối doanh thu lệch phải mạnh tạo môi trường lý tưởng để kiểm chứng **giả thuyết H1** (E4)
- Con số 58.911 tuyến phân biệt cho **E5 một mục tiêu định lượng sắc nét**: median-of-means có vượt được cận 11,2% của FM đơn hay không

---

*Bước tiếp theo: xây dựng tầng L0 (Ingestion & Replay) với bước sắp xếp bắt buộc, rồi cài đặt DGIM from scratch.*
