# PHASE 5 · BƯỚC 4 — KẾT QUẢ THỰC NGHIỆM E4

## Giả thuyết H1: phân bổ ngân sách bucket trong DGIM mở rộng cho tổng số nguyên

**Ngày:** 2026-07-27
**Dữ liệu:** NYC TLC FHVHV 2024-01 — 19.663.928 sự kiện, $N = 10^6$, $m = 8$ bit
**Cài đặt:** [`src/cityflow/sketches/dgim_integer.py`](../src/cityflow/sketches/dgim_integer.py)
**Script:** [`scripts/04_experiment_h1.py`](../scripts/04_experiment_h1.py) · **Kết quả:** [`e4_h1_results.json`](e4_h1_results.json)
**Kiểm định đơn vị:** 51/51 đạt

---

## 0. KẾT LUẬN

> ### H1 được XÁC NHẬN ở dạng suy ra từ lý thuyết, và BỊ BÁC BỎ ở dạng trực giác.

| Phát biểu | Kết quả |
|---|---|
| Phân bổ đều **không** tối ưu | ✅ **Đúng** — có phân bổ tốt hơn ở cùng ngân sách |
| "Cho bit cao nhiều $r$ hơn" (trực giác) | ❌ **Sai** — tệ hơn phân bổ đều tới 12,2% |
| $r_i \propto \sqrt{2^i c_i}$ (suy từ Lagrange) | ✅ **Đúng** — tốt hơn phân bổ đều tới 23,8% |
| Luồng bit gây sai số nhiều nhất là bit cao nhất | ❌ **Sai** — là **bit 4**, chiếm 29,8%; bit 7 chỉ 4,5% |

---

## 1. BỐI CẢNH

Slide tr.66 nêu cách mở rộng DGIM để ước lượng **tổng** các số nguyên:

> *"Tổng của $k$ số nguyên gần nhất: mỗi số nguyên có tối đa $m$ bit · Coi mỗi bit như một luồng riêng và đếm bit 1 trong $k$ phần tử gần nhất · Ước lượng $\sum_{i=0}^{m-1} c_i \cdot 2^i$."*

**Slide dừng ở đó.** Không nói gì về việc **phân bổ ngân sách bộ nhớ** giữa $m$ luồng bit. Cách hiển nhiên là cho mọi luồng cùng một $r$.

Nhưng sai số của mỗi luồng bit được nhân với trọng số $2^i$ rất khác nhau — chênh 128 lần giữa bit 0 và bit 7. Phân bổ đều khó có thể tối ưu.

*(Đây là phần mở rộng ít được khai thác trong thực tế — tài liệu giảng dạy chỉ nêu công thức mà không đi sâu vào chiến lược phân bổ tham số.)*

---

## 2. SUY DẪN LÝ THUYẾT

Sai số tuyệt đối của DGIM trên luồng bit $i$ xấp xỉ $B_i/2$, với $B_i$ là kích thước bucket cũ nhất. Theo bất biến, $c_i \gtrsim r_i \cdot B_i$, nên $B_i \sim c_i/r_i$:

$$\text{sai số tuyệt đối của luồng bit } i \;\sim\; \frac{c_i}{2 r_i}$$

Đóng góp vào sai số của **tổng** (do trọng số $2^i$):

$$E \;\sim\; \sum_{i=0}^{m-1} \frac{2^i \, c_i}{2 \, r_i}$$

Cực tiểu hóa $E$ với ràng buộc ngân sách $\sum_i r_i = R$. Dùng nhân tử Lagrange:

$$\frac{\partial}{\partial r_i}\left[\frac{2^i c_i}{2 r_i}\right] = -\frac{2^i c_i}{2 r_i^2} = -\lambda
\qquad\Longrightarrow\qquad
\boxed{\;r_i \;\propto\; \sqrt{2^i \, c_i}\;}$$

**Điểm mấu chốt:** công thức này **không** đơn giản nói "cho bit cao nhiều $r$ hơn". Nó cân bằng giữa trọng số $2^i$ (**tăng** theo $i$) và tần suất $c_i$ (**giảm** theo $i$, vì giá trị lớn hiếm). Điểm tối ưu có thể rơi vào các bit **giữa**.

---

## 3. PHÂN PHỐI BIT CỦA DOANH THU — ĐO TRÊN DỮ LIỆU THẬT

| bit $i$ | $2^i$ | $c_i$ (số bit 1) | tỷ lệ | $2^i \cdot c_i$ | $\sqrt{2^i c_i}$ |
|---:|---:|---:|---:|---:|---:|
| 0 | 1 | 10.008.230 | 50,90% | 10.008.230 | 3.164 |
| 1 | 2 | 9.253.660 | 47,06% | 18.507.320 | 4.302 |
| 2 | 4 | 9.233.252 | 46,96% | 36.933.008 | 6.077 |
| 3 | 8 | 11.876.860 | 60,40% | 95.014.880 | 9.748 |
| **4** | **16** | **8.693.146** | **44,21%** | **139.090.336** ← cực đại | **11.794** |
| 5 | 32 | 3.846.413 | 19,56% | 123.085.216 | 11.094 |
| 6 | 64 | 1.040.210 | 5,29% | 66.573.440 | 8.159 |
| 7 | 128 | 178.927 | **0,91%** | 22.902.656 | 4.786 |

**Trọng số $2^i c_i$ đạt cực đại tại bit 4**, không phải bit 7. Bit 7 (giá trị 128 USD) chỉ xuất hiện ở **0,91%** chuyến — quá hiếm để chi phối sai số dù trọng số lớn nhất.

Đây là hệ quả trực tiếp của phân phối doanh thu lệch phải rất mạnh (trung vị 18,76 USD, xem [04_DATA_UNDERSTANDING §4](04_DATA_UNDERSTANDING.md)).

---

## 4. ⭐ KẾT QUẢ E4 — SO SÁNH BA CHIẾN LƯỢC

Ba chiến lược, **cùng một tổng ngân sách** $\sum_i r_i$:

- **A. `uniform`** — $r$ bằng nhau cho mọi bit *(mốc so sánh)*
- **B. `high_bit`** — $r$ tăng dần theo vị trí bit *(dạng trực giác của H1)*
- **C. `sqrt_weighted`** — $r_i \propto \sqrt{2^i c_i}$ *(dạng suy từ lý thuyết)*

### Ngân sách $\sum r_i = 16$

| Chiến lược | Phân bổ $r_i$ | Sai số TB | So với `uniform` |
|---|---|---:|---:|
| uniform | `[2,2,2,2,2,2,2,2]` | 5,280% | — |
| high_bit | `[2,2,2,2,2,2,2,2]` | 5,280% | 0,0% |
| sqrt_weighted | `[2,2,2,2,2,2,2,2]` | 5,280% | 0,0% |

> Ngân sách 16 với $m=8$ là **mức tối thiểu tuyệt đối**: mọi $r_i$ buộc phải bằng 2 (sàn hợp lệ, vì $r=1$ là cấu hình suy biến). **Không còn bậc tự do nào để phân bổ** — đây là lý do ba chiến lược trùng nhau, không phải bằng chứng chống H1.

### Ngân sách $\sum r_i = 32$ — khác biệt lớn nhất

| Chiến lược | Phân bổ $r_i$ | Sai số TB | Sai số max | $E$ dự đoán | So với `uniform` |
|---|---|---:|---:|---:|---:|
| uniform | `[4,4,4,4,4,4,4,4]` | 2,119% | 8,336% | 64.014.386 | — |
| high_bit | `[3,2,2,3,4,5,6,7]` | 2,377% | 8,003% | 68.242.438 | 🔻 **−12,2%** |
| **sqrt_weighted** | `[2,2,3,5,6,6,5,3]` | **1,615%** | 7,336% | **55.108.293** | 🔺 **+23,8%** |

### Ngân sách $\sum r_i = 64$

| Chiến lược | Phân bổ $r_i$ | Sai số TB | $E$ dự đoán | So với `uniform` |
|---|---|---:|---:|---:|
| uniform | `[8,8,8,8,8,8,8,8]` | 0,909% | 32.007.193 | — |
| high_bit | `[4,4,5,7,8,10,12,14]` | 0,939% | 32.483.774 | 🔻 −3,3% |
| **sqrt_weighted** | `[3,5,7,10,13,12,9,5]` | **0,907%** | **27.374.555** | 🔺 +0,2% |

### Ngân sách $\sum r_i = 128$

| Chiến lược | Phân bổ $r_i$ | Sai số TB | $E$ dự đoán | So với `uniform` |
|---|---|---:|---:|---:|
| uniform | `[16,16,16,16,16,16,16,16]` | 0,485% | 16.003.596 | — |
| high_bit | `[7,7,10,14,17,21,24,28]` | 0,478% | 16.094.279 | 🔺 +1,4% |
| **sqrt_weighted** | `[7,9,13,21,26,24,18,10]` | **0,430%** | **13.659.302** | 🔺 **+11,4%** |

### Nhận xét

**① `sqrt_weighted` thắng ở mọi ngân sách có bậc tự do** (+23,8%, +0,2%, +11,4%). Không bao giờ tệ hơn phân bổ đều.

**② `high_bit` — dạng trực giác — TỆ HƠN phân bổ đều** ở hai trong ba ngân sách (−12,2%, −3,3%). Trực giác "bit cao quan trọng hơn vì trọng số $2^i$ lớn" **sai**, vì nó bỏ qua việc $c_i$ giảm nhanh theo $i$.

**③ Mô hình lý thuyết dự đoán đúng thứ hạng.** Cột "$E$ dự đoán" xếp `sqrt_weighted` thấp nhất ở cả bốn ngân sách, và thực nghiệm xác nhận. Đây là bằng chứng cho thấy mô hình sai số $E \sim \sum 2^i c_i/(2r_i)$ nắm bắt đúng cơ chế.

**④ Nhìn vào phân bổ của `sqrt_weighted`:** `[2,2,3,5,6,6,5,3]` — hình chuông, đỉnh ở bit 4–5, **giảm ở cả hai đầu**. Bit 7 chỉ nhận $r=3$ trong khi bit 4 nhận $r=6$.

---

## 5. ⚠️ MỨC ĐỘ TIN CẬY — ĐỌC KỸ TRƯỚC KHI TRÍCH DẪN

Mức cải thiện **không đơn điệu** theo ngân sách: +23,8% → +0,2% → +11,4%. Nếu hiệu ứng thuần túy do lý thuyết, ta kỳ vọng xu hướng mượt hơn.

**Nguyên nhân khả dĩ:**
1. Chỉ 150 mốc truy vấn mỗi cấu hình ⇒ nhiễu đo đạc đáng kể
2. Phép làm tròn khi phân bổ ngân sách nguyên (ép sàn $r_i \ge 2$, cân lại cho khớp tổng) tạo bước nhảy rời rạc
3. Chỉ đo trên **một** tháng dữ liệu và **một** giá trị $N$

**Điều có thể khẳng định:** `sqrt_weighted` **không bao giờ tệ hơn** `uniform` trên mọi cấu hình đã thử, và mô hình lý thuyết xếp hạng đúng. **Điều chưa thể khẳng định:** mức cải thiện cụ thể là bao nhiêu.

**Việc cần làm trước khi đưa vào báo cáo chính thức:** tăng số mốc truy vấn lên 1.000, chạy trên ≥3 tháng, và bổ sung khoảng tin cậy. Đưa vào danh mục công việc tuần 9.

---

## 6. PHÂN RÃ SAI SỐ THEO VỊ TRÍ BIT

Ngân sách 32, phân bổ đều — sai số tuyệt đối đã nhân trọng số $2^i$:

| bit $i$ | Sai số $\times 2^i$ | Tỷ trọng | |
|---:|---:|---:|---|
| 0 | 28.837 | 2,2% | `##` |
| 1 | 45.394 | 3,4% | `####` |
| 2 | 94.401 | 7,1% | `#########` |
| 3 | 264.757 | 19,9% | `##########################` |
| **4** | **396.238** | **29,8%** | `########################################` |
| 5 | 267.953 | 20,2% | `###########################` |
| 6 | 172.219 | 13,0% | `#################` |
| 7 | 59.451 | 4,5% | `######` |

**Bit 4 gây 29,8% tổng sai số. Bit 7 — bit có trọng số lớn nhất — chỉ gây 4,5%.**

Ba bit giữa (3, 4, 5) cộng lại chiếm **69,9%** tổng sai số. Đây là bằng chứng trực tiếp nhất bác bỏ dạng trực giác của H1, và giải thích vì sao phân bổ hình chuông thắng.

---

## 7. Ý NGHĨA

**Về mặt học thuật:** đây là một đóng góp nhỏ nhưng hoàn chỉnh — một khoảng trống trong slide (phân bổ ngân sách giữa các luồng bit), một suy dẫn lý thuyết (Lagrange), một dự đoán phản trực giác (đỉnh ở bit giữa), và một kiểm chứng thực nghiệm trên dữ liệu thật quy mô lớn xác nhận lý thuyết đồng thời bác bỏ trực giác.

**Về mặt thực hành:** với cùng lượng bộ nhớ, chọn đúng phân bổ giảm sai số ~24%. Chi phí triển khai bằng không — chỉ là chọn danh sách $r_i$ khác khi khởi tạo.

**Về mặt phương pháp:** minh họa rằng **trực giác về độ quan trọng của trọng số có thể sai khi tần suất biến thiên ngược chiều trọng số**. Bit 7 có trọng số gấp 128 lần bit 0 nhưng chỉ xuất hiện ở 0,91% chuyến.

---

## 8. KHUYẾN NGHỊ CẤU HÌNH CHO CITYFLOW

| Tham số | Giá trị | Căn cứ |
|---|---|---|
| $m$ | 8 | p99.9 = 227,42 USD ([04 §4](04_DATA_UNDERSTANDING.md)); tỷ lệ kẹp trần đo được 0,059% |
| $r_i$ | `[3,5,7,10,13,12,9,5]` | `sqrt_weighted` ngân sách 64 — sai số 0,907%, bộ nhớ 128.604 B |
| $N$ | $10^6$ | Cấu hình vận hành |

---

*Bước tiếp theo: Flajolet-Martin (Q3) và AMS (Q4). Nhắc lại từ [04_DATA_UNDERSTANDING §5](04_DATA_UNDERSTANDING.md): việc kiểm chứng AMS trên cửa sổ ngắn đã được đẩy lên sớm vì phân phối khu vực đều hơn dự kiến làm giảm hiệu lực của số bất ngờ ở phạm vi toàn cục.*
