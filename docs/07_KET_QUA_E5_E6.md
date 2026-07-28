# PHASE 5 · BƯỚC 5 — KẾT QUẢ THỰC NGHIỆM E5 VÀ E6

## Flajolet-Martin (Q3) và AMS / số bất ngờ (Q4)

**Ngày:** 2026-07-28
**Dữ liệu:** NYC TLC FHVHV 2024-01 — 19.663.928 sự kiện
**Cài đặt:** [`flajolet_martin.py`](../src/cityflow/sketches/flajolet_martin.py) · [`ams.py`](../src/cityflow/sketches/ams.py) · [`reservoir.py`](../src/cityflow/sketches/reservoir.py)
**Script:** [`scripts/05_experiment_fm_ams.py`](../scripts/05_experiment_fm_ams.py) · **Kết quả:** [`e5_e6_results.json`](e5_e6_results.json)
**Kiểm định đơn vị:** 83/83 đạt

---

## 0. TÓM TẮT

| | Câu hỏi | Kết quả |
|---|---|---|
| **E5** | Chiến lược tổng hợp của slide có vượt được cận 11,2% của ước lượng $2^R$ đơn không? | ⚠️ **Không, nếu dùng nguyên như slide.** Có, nếu hiệu chuẩn độ chệch và dùng $m \ge 128$ |
| **E6** | Số bất ngờ có phát hiện được ùn tắc bất thường không? | ⚠️ **Ước lượng chính xác (7,1% ở $k=100$) nhưng TÍN HIỆU YẾU** — chỉ 2,7× sau chuẩn hóa |

**Hai phát hiện quan trọng:**
1. Sơ đồ tổng hợp của slide **chệch lên có hệ thống ~2,3 lần**; hằng số $\varphi = 0{,}77351$ kinh điển **làm tệ thêm** vì nó dành cho biến thể khác.
2. Cảnh báo ở [04_DATA_UNDERSTANDING §5](04_DATA_UNDERSTANDING.md) **được xác nhận**: phân phối khu vực quá đều khiến số bất ngờ mất phần lớn hiệu lực. Điều này **củng cố lý do tầng khai phá mẫu (Q6) là bắt buộc**.

---

# PHẦN A — E5: FLAJOLET-MARTIN

## 1. Bài toán và cận lý thuyết

Đếm số **tuyến phân biệt** (cặp khu vực đón–trả). Ground truth cả tháng: **58.911** tuyến trên tối đa lý thuyết $265^2 = 70.225$.

Vì $2^R$ luôn là lũy thừa của 2:

$$2^{15} = 32.768 \;<\; \mathbf{58.911} \;<\; 65.536 = 2^{16}$$

| Ước lượng | Sai số |
|---:|---:|
| $2^{15}$ | −44,4% |
| $2^{16}$ | **+11,2%** |

⇒ **Không ước lượng $2^R$ đơn lẻ nào có thể tốt hơn 11,2%.** Đây là cận cứng cần vượt qua.

## 2. Một tối ưu hóa hợp lệ cho harness đo đạc

Nạp Flajolet-Martin bằng **tập phân biệt** thay vì toàn bộ luồng cho kết quả **hoàn toàn giống nhau**: trạng thái FM chỉ là $R_j = \max$ trên các phần tử, mà `max` là phép lũy đẳng.

Nếu không tối ưu, E5 phải chạy $19{,}7 \times 10^6 \times 64 = 1{,}26$ **tỷ** phép băm trong Python.

> Đây là tối ưu cho **harness**, không phải cho hệ thống luồng — hệ thống thật vẫn phải xử lý từng sự kiện vì nó không biết trước tập phân biệt. Đã có unit test `test_duplicates_do_not_change_estimate` bảo đảm tính lũy đẳng.

## 3. 🔴 Phát hiện 1 — Sơ đồ của slide chệch lên có hệ thống

Đo trên 25 hạt giống × 4 mức cardinality ($m=64$, $g=8$):

| Chiến lược tổng hợp | Bội số chệch | Dao động | Độ ổn định |
|---|---:|---|---:|
| `mean` — trung bình các $2^{R_j}$ | **3,84×** | 3,50–4,69 | ±15% |
| `median` — trung vị các $2^{R_j}$ | 0,82× | 0,82–1,02 | ±12% |
| `median_of_means` — **khuyến nghị của slide** | **2,32×** | 2,29–2,59 | ±6% |
| `loglog` — $2^{\overline{R}}$ (ngoài slide) | 1,24× | 1,21–1,31 | **±2%** |

**Cả bốn chiến lược đều chệch, nhưng bội số ỔN ĐỊNH qua nhiều bậc độ lớn** ⇒ hiệu chỉnh được bằng một hằng số. Đây đúng là cách HyperLogLog xử lý bằng các hằng số $\alpha_m$.

### Vì sao hằng số $\varphi = 0{,}77351$ không dùng được

$\varphi$ của Flajolet & Martin (1985) được suy ra cho biến thể **stochastic averaging** — chia luồng vào bucket theo bit cao rồi lấy max trong từng bucket. Sơ đồ mà slide tr.40 mô tả **khác hẳn**: $m$ hàm băm **độc lập**, mỗi hàm lấy max trên **toàn bộ** luồng.

Vì ước lượng vốn đã chệch **lên** 2,32 lần, chia thêm cho $\varphi < 1$ (tức nhân 1,29) chỉ làm sai số tăng: đo được **219,7%** so với 147,3% khi không hiệu chỉnh gì.

## 4. Kết quả E5a — so sánh chiến lược ($m=64$, $g=8$, 20 hạt giống)

| Chiến lược | Ước lượng TV | Sai số TV | Sai số p90 | Hệ số biến thiên |
|---|---:|---:|---:|---:|
| `single` ($2^{R_0}$) | 65.536 | 72,2% | 790,0% | 140,6% |
| `mean_raw` | 262.016 | 344,8% | 1270,5% | 114,6% |
| `mean_cal` | 68.205 | 35,8% | 256,7% | 114,6% |
| `median_raw` | 65.536 | **11,2%** | 44,4% | 19,7% |
| `median_cal` | 80.000 | 35,8% | 35,8% | 19,7% |
| `median_of_means_raw` *(slide)* | 145.664 | 147,3% | 305,1% | 33,0% |
| `median_of_means_cal` | 62.873 | 15,2% | 74,8% | 33,0% |
| `loglog_raw` | 76.284 | 29,5% | 60,9% | 18,0% |
| **`loglog_cal`** | **63.055** | **14,0%** | **33,0%** | **18,0%** |
| `median_of_means_phi` | 188.316 | 219,7% | 423,7% | 33,0% |

### Đọc bảng này cho đúng

**`median_raw` đạt 11,2% nhưng đó là ăn may.** Nó ước lượng đúng $2^{16} = 65.536$ — chính là lũy thừa của 2 gần với sự thật. Cột **p90 = 44,4%** phơi bày điều đó: khi rơi vào $2^{15}$ thay vì $2^{16}$, sai số nhảy lên 44%. Nó không thật sự "vượt cận", nó **chính là cận**.

**`loglog_cal` mới là ước lượng dùng được:** sai số trung vị 14,0%, **p90 chỉ 33,0%** (thấp nhất bảng), hệ số biến thiên 18,0% (thấp nhất bảng). Ổn định là thứ quan trọng trong vận hành, không phải một lần đo may mắn.

## 5. 🔴 Phát hiện 2 — Hằng số hiệu chuẩn phụ thuộc $m$ (lỗi đã tìm và sửa)

Chạy E5b lần đầu với **một** hằng số hiệu chuẩn duy nhất:

| $m$ | Sai số TV | Hệ số biến thiên |
|---:|---:|---:|
| 64 | 16,6% | 16,2% |
| 128 | **22,7%** ⬆ | 13,4% ⬇ |
| 256 | **24,0%** ⬆ | **6,3%** ⬇ |

**Sai số TĂNG trong khi phương sai GIẢM** — mâu thuẫn logic. Tăng $m$ phải làm ước lượng tốt hơn.

**Chẩn đoán:** hệ số biến thiên giảm đơn điệu chứng tỏ bản thân ước lượng đang tốt lên. Nếu phương sai giảm mà sai số tăng thì phần sai số còn lại phải là **độ chệch** — và độ chệch đó **thay đổi theo $m$**. Hằng số cố định hiệu chuẩn đúng ở $m=64$ nhưng sai ở $m$ khác, ăn mất phần lợi thu được.

**Khắc phục:** hiệu chuẩn riêng cho từng $m$ trên **dữ liệu tổng hợp** (không dùng dữ liệu NYC TLC, để tránh rò rỉ thông tin từ tập đánh giá sang tham số):

| $m$ | 8 | 16 | 32 | 64 | 128 | 256 |
|---|---:|---:|---:|---:|---:|---:|
| $\alpha_m$ | 1,0183 | 1,2634 | 1,3052 | 1,2098 | 1,2330 | 1,2772 |

### Kết quả sau khi sửa — tính đơn điệu được khôi phục

| $m$ | Sai số TV | Sai số p90 | Hệ số biến thiên | Bộ nhớ (byte) |
|---:|---:|---:|---:|---:|
| 8 | 40,4% | 143,3% | 49,1% | 752 |
| 16 | 26,0% | 113,8% | 46,0% | 1.392 |
| 32 | 20,5% | 46,5% | 26,9% | 2.664 |
| 64 | 14,2% | 31,7% | 19,4% | 5.224 |
| **128** | **10,7%** | 25,4% | 13,6% | 10.312 |
| **256** | **6,4%** | **10,6%** | **6,7%** | 20.600 |

> ### ✅ Trả lời câu hỏi của E5
> **Cận 11,2% BỊ VƯỢT tại $m \ge 128$.** Tại $m = 256$: sai số trung vị **6,4%**, và ngay cả **p90 = 10,6%** cũng dưới cận — tức không chỉ trung bình tốt mà **hầu như mọi lần chạy đều tốt hơn** ước lượng $2^R$ đơn tốt nhất có thể.
>
> Nhưng **chỉ đạt được sau hai bước không có trong slide**: hiệu chuẩn độ chệch, và hiệu chuẩn riêng theo $m$.

### ⚠️ Một lỗi tôi tự gây ra trong quá trình sửa

Khi refactor, tôi bỏ phép chia `/PHI` khỏi công thức `estimate_loglog` nhưng vẫn giữ hằng số 1,6037 vốn **đã bao gồm** `/PHI` bên trong. Hệ quả: ước lượng bị chia hai lần, cho kết quả **thiếu** 19,3% thay vì 14,0%.

Phát hiện được nhờ tỷ số thô đo lại chỉ ra $2^{\overline R}/n \approx 1{,}24$ chứ không phải 1,60 — và $1{,}6037 \times 0{,}77351 = 1{,}2405$ khớp đúng. Ghi lại để nhắc: **hằng số hiệu chuẩn phải luôn ghi rõ nó hiệu chuẩn cho công thức nào.**

## 6. Đối chiếu tiêu chí Phase 4

| Chỉ số | Ngưỡng ([Phase 4 §1.4](03_THIET_KE_KIEN_TRUC.md)) | Đo thật | |
|---|---|---|:--:|
| Sai số FM (median-of-means, $m=64$) | ≤ 15% | 15,2% (hiệu chuẩn) | ⚠️ Sát ngưỡng |
| Sai số FM (`loglog_cal`, $m=64$) | ≤ 15% | **14,0%** | ✅ |
| Sai số FM (`loglog_cal`, $m=256$) | ≤ 15% | **6,4%** | ✅ vượt xa |

**Khuyến nghị cấu hình CityFlow:** $m = 256$, chiến lược `loglog_cal`. Bộ nhớ 20.600 byte/bộ đếm — chấp nhận được vì chỉ cần một vài bộ đếm tuyến, không phải 265 cái.

---

# PHẦN B — E6: AMS VÀ SỐ BẤT NGỜ

## 7. Bối cảnh — một cảnh báo cần kiểm chứng

[04_DATA_UNDERSTANDING §5](04_DATA_UNDERSTANDING.md) phát hiện phân phối khu vực **đều hơn dự kiến** (top 10 chỉ chiếm 13,3%, không khu vực nào vượt 2%) và cảnh báo rằng số bất ngờ có thể mất hiệu lực. Việc kiểm chứng đã được **đẩy từ tuần 5 lên tuần 3**.

## 8. Độ chính xác của ước lượng AMS — tốt

2.976 cửa sổ 15 phút, 200 cửa sổ mẫu, đối chiếu với mô-men bậc 2 tính chính xác:

| $k$ | Sai số TV | Sai số p90 | Bộ nhớ (byte) |
|---:|---:|---:|---:|
| 10 | 17,3% | 46,9% | 1.472 |
| 50 | 10,5% | 22,8% | 5.984 |
| **100** | **7,1%** | 14,7% | 12.008 |
| 500 | **3,0%** | 7,4% | 45.424 |

**Ngưỡng Phase 4 (≤20% tại $k=100$) được vượt xa: 7,1%.**

Ước lượng $\hat f = \frac{n}{k}\sum_j (2X_j.c - 1)$ của slide tr.47 hoạt động đúng như lý thuyết. Chứng minh tính không chệch ở tr.49 được xác nhận qua unit test `test_ams_estimator_is_unbiased_on_average`.

## 9. 🔴 Nhưng TÍN HIỆU thì yếu

Đây mới là kết quả quan trọng của E6.

### Số bất ngờ thô — trông có vẻ tốt

| | Giá trị |
|---|---:|
| min | 7.495 |
| p25 | 180.520 |
| trung vị | 351.900 |
| p75 | 580.676 |
| max | 1.758.732 |
| **max / trung vị** | **5,0×** |

Chênh 5 lần giữa cửa sổ "bất thường nhất" và cửa sổ trung bình — nghe như một chỉ báo tốt.

### Nhưng phần lớn chênh lệch đó chỉ là KÍCH THƯỚC CỬA SỔ

Mô-men bậc 2 là $\sum_i m_i^2$, tăng theo **bình phương** số sự kiện trong cửa sổ. Mà [04_DATA_UNDERSTANDING §8](04_DATA_UNDERSTANDING.md) đã đo: giờ cao điểm có **4,1×** số chuyến so với giờ thấp điểm. Bình phương lên là **~17×**.

Nói cách khác: số bất ngờ thô cao ở 18h **không phải vì nhu cầu tập trung bất thường**, mà đơn giản vì 18h có nhiều chuyến hơn.

Chuẩn hóa bằng $n^2$ để loại bỏ hiệu ứng này:

| | Giá trị |
|---|---:|
| min | 0,00572 |
| trung vị | 0,00735 |
| max | 0,01955 |
| **max / trung vị** | **2,7×** |

**Tín hiệu thật chỉ còn 2,7×, không phải 5,0×.** Và khoảng giữa min và trung vị cực hẹp (0,00572 vs 0,00735 — chỉ 22%).

### Ý nghĩa

Slide tr.45 nêu *"Ứng dụng: phát hiện điểm bất thường (anomaly), tắc nghẽn mạng"*. Trên dữ liệu giao thông NYC, ứng dụng đó **hoạt động yếu** vì nhu cầu taxi trải khá đều trên 265 khu vực — không giống lưu lượng mạng nơi một địa chỉ IP có thể chiếm hoàn toàn.

Số bất ngờ **vẫn dùng được** như một chỉ báo phụ (2,7× là có phân biệt), nhưng **không đủ làm cơ chế phát hiện ùn tắc chính**.

## 10. ⭐ Hệ quả kiến trúc — củng cố lý do tầng Q6 tồn tại

Kết quả E6 **làm mạnh thêm** quyết định thiết kế ở [Phase 4 §5](03_THIET_KE_KIEN_TRUC.md) rằng tầng khai phá mẫu (Q6) là **bắt buộc**:

- Q4 (AMS) chỉ trả lời được *"nhu cầu có đang tập trung bất thường không?"* — và trả lời **yếu** trên dữ liệu này
- Q6 (FP-Growth) trả lời *"những khu vực NÀO thường xuyên ùn tắc CÙNG NHAU?"* — câu hỏi có tính hành động cao hơn hẳn, và không phụ thuộc vào việc phân phối có lệch hay không

Nếu CityFlow chỉ có tầng sketch, kết luận về phát hiện bất thường sẽ nghèo nàn. Tầng khai phá mẫu không phải phần trang trí để tránh lời phê *"đâu là khai phá dữ liệu?"* — nó là **thành phần mang thông tin chính**.

---

## 11. TỔNG KẾT VÀ CẤU HÌNH KHUYẾN NGHỊ

| Thành phần | Cấu hình | Sai số | Bộ nhớ |
|---|---|---:|---:|
| DGIM (Q1) | $r = 8$ | 2,43% | 13.268 B/luồng |
| DGIM-Integer (Q2) | $m=8$, `sqrt_weighted` ngân sách 64 | 0,907% | 128.604 B |
| **Flajolet-Martin (Q3)** | **$m=256$, `loglog_cal`** | **6,4%** | **20.600 B** |
| **AMS (Q4)** | **$k=100$** | **7,1%** | **12.008 B** |

**Ba bài học phương pháp luận từ E5–E6:**

1. **Hằng số từ tài liệu tham khảo phải kiểm tra điều kiện áp dụng.** $\varphi = 0{,}77351$ là hằng số đúng cho một biến thể khác của Flajolet-Martin; áp dụng mù làm sai số tăng từ 147% lên 220%.

2. **Sai số tăng trong khi phương sai giảm là dấu hiệu của độ chệch phụ thuộc tham số.** Nếu chỉ đo ở một giá trị $m$ sẽ không bao giờ phát hiện ra.

3. **Ước lượng chính xác không đồng nghĩa tín hiệu có ý nghĩa.** AMS ước lượng số bất ngờ với sai số 7,1% — nhưng bản thân số bất ngờ chỉ phân biệt được 2,7× trên dữ liệu này. Đo đúng một đại lượng vô dụng vẫn là vô dụng.

---

*Bước tiếp theo: SketchRegistry quản lý 535 luồng (E7 — thông lượng), rồi tầng khai phá mẫu FP-Growth với 10 độ đo interestingness (Q6, E9–E11).*
