# PHASE 4 — THIẾT KẾ KIẾN TRÚC GIẢI PHÁP

# CityFlow

### Hệ giám sát giao thông đô thị dựa trên truy vấn cửa sổ trượt và khai phá mẫu đồng ùn tắc trên luồng dữ liệu chuyến đi quy mô lớn

**Nhóm 15** — Nguyễn Thuý Anh (B25CHHT076) · Trần Thị Thảo (B25CHHT113) · Trần Văn Hanh (B25CHHT092)
**Môn:** Khai phá dữ liệu — Lớp HTTT 02, khóa 2025–2027, PTIT
**Phiên bản:** Phase 4 — 2026-07-27

---

## MỤC LỤC

1. [Business Understanding](#1-business-understanding-crisp-dm-pha-1)
2. [Data Understanding — kế hoạch](#2-data-understanding--kế-hoạch-crisp-dm-pha-2)
3. [Kiến trúc tổng thể](#3-kiến-trúc-tổng-thể)
4. [Thiết kế tầng L1 — Sketch luồng](#4-thiết-kế-tầng-l1--sketch-luồng-from-scratch)
5. [Thiết kế tầng L3 — Khai phá mẫu](#5-thiết-kế-tầng-l3--khai-phá-mẫu-from-scratch)
6. [Thiết kế dữ liệu & CSDL](#6-thiết-kế-dữ-liệu--csdl)
7. [Thiết kế API](#7-thiết-kế-api)
8. [Thiết kế giao diện](#8-thiết-kế-giao-diện)
9. [Cấu trúc mã nguồn](#9-cấu-trúc-mã-nguồn)
10. [Ma trận thực nghiệm](#10-ma-trận-thực-nghiệm--phần-ăn-điểm-chính)
11. [Triển khai & Docker](#11-triển-khai--docker)
12. [Phân công & tiến độ](#12-phân-công--tiến-độ)
13. [Rủi ro & biện pháp](#13-rủi-ro--biện-pháp)
14. [Checklist đối chiếu](#14-checklist-đối-chiếu)

---

## 1. BUSINESS UNDERSTANDING *(CRISP-DM pha 1)*

### 1.1. Bối cảnh nghiệp vụ

Trung tâm điều hành giao thông của một đô thị lớn nhận **luồng sự kiện chuyến đi liên tục** từ hàng chục nghìn phương tiện. Để ra quyết định điều tiết (phân bổ phương tiện, điều chỉnh chu kỳ đèn, cảnh báo ùn tắc), trung tâm cần trả lời liên tục các câu hỏi dạng cửa sổ trượt trên **hàng trăm luồng song song** — mỗi khu vực địa lý là một luồng.

**Ràng buộc cốt lõi:**

> Slide chương Data Streaming, tr.53: *"N có thể rất lớn (hàng triệu phần tử). Có thể có nhiều luồng đồng thời — **không thể giữ nhiều cửa sổ**."*

Đây chính xác là tình huống của bài toán này. Với 265 khu vực taxi của New York, việc giữ cửa sổ đầy đủ $N = 10^6$ sự kiện cho mỗi khu vực đòi hỏi $265 \times 10^6$ bit chỉ cho một loại truy vấn — và trung tâm cần **nhiều loại truy vấn đồng thời** (số chuyến, doanh thu, tỷ lệ thanh toán tiền mặt, tỷ lệ chuyến dài…). Bộ nhớ tăng tuyến tính theo số luồng × số truy vấn × N.

### 1.2. Vì sao KHÔNG tính chính xác?

Đây là câu hỏi đầu tiên mọi phản biện sẽ đặt ra. Ba lý do định lượng:

| Lý do | Phân tích |
|---|---|
| **Bộ nhớ** | Cửa sổ đầy đủ: $O(N)$ bit/luồng. DGIM: $O(\log^2 N)$ bit/luồng. Với $N = 10^6$: $10^6$ bit ≈ 122 KB → $\approx (\log_2 10^6)^2 = 400$ bit ≈ 50 byte. **Tỷ lệ nén ≈ 2.400 lần.** Nhân với 265 luồng × 6 loại truy vấn: 194 MB → **83 KB**. |
| **Số luồng đồng thời** | Không phải 1 luồng mà 265 (khu vực) × nhiều vị từ. Chi phí nhân lên tuyến tính — đúng lập luận GV nêu ở tr.53. |
| **Tính vô hạn** | Luồng thực tế không kết thúc. Mọi cấu trúc $O(N)$ đều sụp đổ theo thời gian. |

**Cam kết trung thực:** dữ liệu NYC TLC là **dữ liệu lịch sử được phát lại (replay)**, không phải luồng trực tuyến thật. Báo cáo sẽ **nêu rõ điều này** như một giới hạn, kèm luận cứ: bài toán và ràng buộc bộ nhớ là thật (265 luồng × $10^6$ cửa sổ), chỉ nguồn phát là mô phỏng. Không được che giấu — đây là điểm phản biện dễ bị chất vấn nhất nếu không chủ động nêu trước.

### 1.3. Sáu câu hỏi nghiệp vụ hệ thống phải trả lời

| # | Câu hỏi | Thuật toán | Kiểu |
|:--:|---|---|---|
| **Q1** | Trong $N$ chuyến gần nhất, bao nhiêu chuyến xuất phát từ khu vực $z$? | **DGIM** | Đếm bit, cửa sổ trượt |
| **Q2** | Tổng doanh thu (hoặc tổng quãng đường) của $N$ chuyến gần nhất là bao nhiêu? | **DGIM mở rộng cho số nguyên** (tr.66) | Tổng số nguyên, cửa sổ trượt |
| **Q3** | Có bao nhiêu **tuyến đường phân biệt** (cặp đón–trả) hoạt động trong giờ qua? | **Flajolet-Martin** | Đếm phần tử phân biệt |
| **Q4** | Nhu cầu đang **tập trung bất thường** vào vài khu vực hay phân bố đều? | **AMS — số bất ngờ (mô-men bậc 2)** | Ước lượng mô-men |
| **Q5** | Giữ được mẫu đại diện nào để phân tích sâu mà không lưu toàn bộ luồng? | **Reservoir Sampling** | Lấy mẫu |
| **Q6** | **Những khu vực nào thường xuyên ùn tắc CÙNG NHAU?** Nếu A và B đang ùn tắc thì C có nguy cơ không? | **FP-Growth + độ đo null-invariant** | Khai phá mẫu & luật |

> 🔴 **Q6 là tầng bắt buộc, không được cắt.** Nó là câu trả lời cho phản biện *"đây là truy vấn xấp xỉ hay khai phá dữ liệu?"*. Q1–Q5 là hạ tầng sketch; **Q6 mới là khai phá dữ liệu**.

### 1.4. Tiêu chí thành công

**Tiêu chí nghiệp vụ:**
- Trả lời được cả 6 câu hỏi ở độ trễ dưới 100 ms/truy vấn
- Bộ nhớ toàn hệ thống dưới 500 MB cho 265 luồng × 6 vị từ
- Sinh được tập luật đồng ùn tắc đọc được, có thể hành động

**Tiêu chí kỹ thuật (đo được):**

| Chỉ số | Ngưỡng | Đối chiếu lý thuyết |
|---|---|---|
| Sai số tương đối DGIM ($r=1$) | ≤ 50% | Cận lý thuyết slide tr.64 |
| Sai số tương đối DGIM ($r=8$) | ≤ 10% | Quan hệ $O(1/r)$ |
| Bộ nhớ DGIM/luồng | $O(\log^2 N)$ | slide tr.58 |
| Sai số Flajolet-Martin (median-of-means, $m=64$) | ≤ 15% | slide tr.40–41 |
| Sai số AMS ($k=100$) | ≤ 20% | slide tr.47 |
| Thông lượng | ≥ 50.000 sự kiện/giây | — |
| Sai lệch FP-Growth from-scratch vs `mlxtend` | **0** (khớp tuyệt đối) | Kiểm định tính đúng đắn |

---

## 2. DATA UNDERSTANDING — KẾ HOẠCH *(CRISP-DM pha 2)*

### 2.1. Nguồn dữ liệu

**NYC TLC Trip Record Data** — công bố bởi New York City Taxi & Limousine Commission, tải công khai theo tháng.

⚠️ **Toàn bộ thông tin dưới đây cần xác minh khi tải thực tế** — đây là hiểu biết chung, chưa kiểm chứng trong phiên này. Việc **đầu tiên** của Phase 5 là tải 1 tháng và chạy notebook `01_data_understanding`.

| Tập dữ liệu | Quy mô ước tính | Ghi chú |
|---|---|---|
| **FHVHV** (Uber/Lyft — High Volume For-Hire) | ~18–20 triệu chuyến/tháng | **Tập chính** — lớn nhất, đúng tinh thần massive |
| **Yellow Taxi** | ~3–4 triệu chuyến/tháng | Tập phụ, đối chiếu |
| **Green Taxi** | ~50–100 nghìn chuyến/tháng | Không dùng |
| **Taxi Zone Lookup** | 265 khu vực | `LocationID`, `Borough`, `Zone`, `service_zone` |
| **Taxi Zone Shapefile** | 265 đa giác | Chuyển sang GeoJSON cho bản đồ |

**Kế hoạch quy mô:** 12 tháng FHVHV ⇒ **~230 triệu bản ghi**. Bắt đầu 1 tháng để phát triển, mở rộng dần khi benchmark.

### 2.2. Trường dữ liệu dự kiến (cần xác minh)

| Trường | Dùng cho |
|---|---|
| `pickup_datetime`, `dropoff_datetime` | Sắp thứ tự sự kiện, tính thời lượng chuyến |
| `PULocationID`, `DOLocationID` | **Định danh luồng** (265 khu vực), tuyến đường cho FM |
| `trip_miles` / `trip_distance` | DGIM số nguyên (Q2) |
| `base_passenger_fare`, `driver_pay`, `tips`, `tolls` | DGIM số nguyên (Q2 — doanh thu) |
| `trip_time` | Vị từ "chuyến dài" |
| `congestion_surcharge` | Vị từ "khu vực tính phí ùn tắc" |
| `shared_request_flag` | Vị từ bổ sung |

> 📌 **Đặc điểm quan trọng và có lợi:** từ tháng 7/2016, TLC **không còn công bố tọa độ GPS**, chỉ còn `LocationID` (1–265). Với đề tài khác đây là mất mát, nhưng với CityFlow đây là **thuận lợi**: dữ liệu đã được rời rạc hóa sẵn thành đúng **265 luồng song song** — chính là kịch bản "nhiều luồng đồng thời" của slide tr.53. Không cần tự phân vùng, không cần biện minh về cách chia lưới.

### 2.3. Checklist Data Understanding (notebook `01`)

- [ ] Đếm số bản ghi thật, so với ước tính
- [ ] Kiểm tra giá trị thiếu theo từng cột
- [ ] Kiểm tra tính hợp lệ: `dropoff > pickup`, `trip_miles > 0`, `LocationID ∈ [1,265]`
- [ ] Phân phối chuyến theo giờ/ngày/khu vực — phát hiện **tính phi dừng** (GV nhấn mạnh tr.7)
- [ ] Phát hiện `LocationID = 264, 265` (Unknown/NV) — cần loại hay giữ?
- [ ] Kiểm tra sự kiện lệch thứ tự thời gian (out-of-order) — ảnh hưởng thiết kế replay
- [ ] Phân phối `total_amount` → chọn số bit $m$ cho DGIM số nguyên
- [ ] Thống kê mô tả + trực quan hóa cơ sở

---

## 3. KIẾN TRÚC TỔNG THỂ

### 3.1. Sơ đồ tầng

```
┌─────────────────────────────────────────────────────────────────────┐
│  L6  BENCHMARK & EVALUATION HARNESS                                 │
│      Oracle chính xác (DuckDB)  ↔  So sánh sai số  →  Biểu đồ       │
│      ⭐ Đây là thành phần ăn điểm chính, không phải phụ trợ          │
└─────────────────────────────────────────────────────────────────────┘
          ▲                                              ▲
          │ đối chiếu                                    │ đối chiếu
┌─────────┴───────────────────────────────────────────────┴───────────┐
│  L5  WEB DASHBOARD          React + Vite + Tailwind + Leaflet       │
│      Bản đồ nhiệt 265 khu vực · Biểu đồ sai số · Bảng luật          │
└─────────────────────────────────────────────────────────────────────┘
          ▲ REST / WebSocket
┌─────────┴───────────────────────────────────────────────────────────┐
│  L4  API LAYER              FastAPI + Pydantic                      │
│      /window/count  /window/sum  /distinct  /surprise  /rules       │
└─────────────────────────────────────────────────────────────────────┘
          ▲
┌─────────┴───────────────────────────────────────────────────────────┐
│  L3  MINING LAYER  (FROM SCRATCH)                    ← Q6           │
│      Window Aggregator → Basket Builder → FP-Tree → FP-Growth       │
│      → Association Rules → 9 độ đo Interestingness + Imbalance Ratio│
│      → FPClose / FPMax (nén pattern)                                │
└─────────────────────────────────────────────────────────────────────┘
          ▲                                    ▲
          │ mẫu đại diện                       │ tổng hợp cửa sổ
┌─────────┴────────────────────────────────────┴──────────────────────┐
│  L2  STATE STORE                                                    │
│      Sketch in-memory  ──snapshot định kỳ──▶  PostgreSQL            │
└─────────────────────────────────────────────────────────────────────┘
          ▲
┌─────────┴───────────────────────────────────────────────────────────┐
│  L1  STREAMING SKETCH LAYER  (FROM SCRATCH)          ← Q1..Q5       │
│  ┌───────────────┬───────────────┬──────────┬────────┬───────────┐  │
│  │ DGIM Registry │ DGIM-Integer  │ Flajolet │  AMS   │ Reservoir │  │
│  │ 265×6 luồng   │ m luồng bit   │ -Martin  │        │           │  │
│  │      Q1       │      Q2       │    Q3    │   Q4   │    Q5     │  │
│  └───────────────┴───────────────┴──────────┴────────┴───────────┘  │
└─────────────────────────────────────────────────────────────────────┘
          ▲ sự kiện đơn lẻ, một lượt, không quay lại
┌─────────┴───────────────────────────────────────────────────────────┐
│  L0  INGESTION & REPLAY                                             │
│      Parquet → chuẩn hóa → sắp theo pickup_datetime → phát lại      │
│      có kiểm soát tốc độ (throttle)                                 │
└─────────────────────────────────────────────────────────────────────┘
          ▲
      NYC TLC Parquet (FHVHV + Yellow) + Taxi Zone GeoJSON
```

### 3.2. Nguyên tắc thiết kế bất di bất dịch

| # | Nguyên tắc | Lý do |
|:--:|---|---|
| **P1** | **Một lượt (one-pass), không quay lại.** Tầng L1 chỉ được thấy mỗi sự kiện đúng một lần và không được lưu nó. | Ràng buộc cốt lõi của mô hình luồng (slide tr.8). Vi phạm là hỏng toàn bộ luận điểm |
| **P2** | **Bộ nhớ sketch phải kiểm chứng được.** Mọi cấu trúc có hàm `memory_bytes()` đo thật, không ước lượng. | Để chứng minh $O(\log^2 N)$ bằng số liệu, không bằng lời |
| **P3** | **Oracle tách biệt hoàn toàn.** L6 tính chính xác bằng đường đi riêng (DuckDB), không dùng chung mã với L1. | Tránh lỗi "so sánh với chính mình" |
| **P4** | **From scratch trước, thư viện sau.** Mọi thuật toán tự cài; thư viện chỉ dùng để kiểm định chéo. | Quyết định đã chốt; đúng tín hiệu #2 của GV |
| **P5** | **Tham số là biến thực nghiệm, không phải hằng số.** $N, r, m, g, k, \text{min\_sup}$ đều cấu hình được. | Tín hiệu #3 của GV: tinh chỉnh tham số + so lý thuyết vs thực nghiệm |

---

## 4. THIẾT KẾ TẦNG L1 — SKETCH LUỒNG *(FROM SCRATCH)*

### 4.1. ⭐ DGIM đa luồng — thành phần lõi (Q1)

#### Ánh xạ sự kiện → luồng bit

Đây là **quyết định thiết kế quan trọng nhất** của cả đồ án.

Với mỗi sự kiện chuyến đi $e$ đến, hệ thống sinh **một bit cho mỗi luồng**:

$$\text{bit}_{S}(e) = \begin{cases} 1 & \text{nếu } e \text{ thỏa vị từ của luồng } S \\ 0 & \text{ngược lại}\end{cases}$$

**Tập luồng:**

| Nhóm luồng | Số lượng | Vị từ |
|---|:--:|---|
| Khu vực đón | 265 | `PULocationID == z` |
| Khu vực trả | 265 | `DOLocationID == z` |
| Thanh toán tiền mặt | 1 | `payment_type == cash` |
| Chuyến sân bay | 1 | `PU ∈ {JFK, LGA, EWR}` hoặc `DO ∈ {…}` |
| Chuyến dài | 1 | `trip_time > 1800s` |
| Có phụ phí ùn tắc | 1 | `congestion_surcharge > 0` |
| Chuyến đi chung | 1 | `shared_request_flag == Y` |
| **Tổng** | **535** | |

> 📌 **Điểm mấu chốt về hiệu năng:** với mỗi sự kiện, **534/535 luồng nhận bit 0**. Theo slide tr.62: *"Nếu bit = 0 — không cần thay đổi gì"*. Nên chi phí thực tế mỗi sự kiện là $O(1)$ khấu hao cho luồng nhận bit 1, cộng chi phí đẩy timestamp cho các luồng còn lại. **Tối ưu bắt buộc:** không lặp qua 535 luồng mỗi sự kiện — dùng **timestamp toàn cục dùng chung** và chỉ chạm vào các luồng nhận bit 1, dồn việc loại bucket hết hạn sang lúc truy vấn (lazy expiration). Đây là một đóng góp kỹ thuật đáng viết vào báo cáo.

#### Cấu trúc dữ liệu

```python
@dataclass(slots=True)
class Bucket:
    timestamp: int   # mod N, O(log N) bit
    size_exp: int    # log2(số bit 1), O(log log N) bit  → size = 2**size_exp

class DGIM:
    N: int                  # độ rộng cửa sổ
    r: int                  # số bucket tối đa mỗi kích thước (mặc định 2)
    buckets: deque[Bucket]  # mới nhất ở đầu trái
    now: int                # bộ đếm sự kiện toàn cục
```

**Bất biến (slide tr.60):**
1. Tối đa $r$ (mặc định 2) bucket cùng kích thước
2. Bucket không chồng lấn timestamp
3. Bucket mới nhỏ hơn bucket cũ hơn
4. Loại bucket khi `now - bucket.timestamp ≥ N`

#### Thuật toán

```python
def update(self, bit: int) -> None:
    self.now += 1
    self._expire()                                  # bất biến 4
    if bit == 0:
        return                                      # slide tr.62: không làm gì
    self.buckets.appendleft(Bucket(self.now, 0))    # bucket cỡ 1 = 2^0
    self._merge()                                   # bất biến 1, đệ quy

def _merge(self) -> None:
    exp = 0
    while True:
        same = [b for b in self.buckets if b.size_exp == exp]
        if len(same) <= self.r:
            break
        # gộp 2 bucket CŨ NHẤT cùng cỡ → 1 bucket cỡ gấp đôi
        old1, old2 = same[-1], same[-2]
        self.buckets.remove(old1)
        old2.size_exp += 1                          # timestamp giữ của bucket mới hơn
        exp += 1

def query(self, k: int | None = None) -> int:
    """Ước lượng số bit 1 trong k sự kiện gần nhất (k ≤ N)."""
    k = k or self.N
    self._expire()
    total, oldest = 0, None
    for b in self.buckets:
        if self.now - b.timestamp < k:
            total += 2 ** b.size_exp
            oldest = b
        else:
            break
    if oldest is not None:
        total -= 2 ** oldest.size_exp // 2          # slide tr.64: trừ nửa bucket cũ nhất
    return total
```

**Kiểm chứng:** slide tr.65 cho ví dụ bucket `1 1 2 4` ⇒ ước lượng $1+1+2+4/2 = 6$. Unit test bắt buộc phải tái hiện đúng con số này.

#### Chứng minh cận sai số *(sẽ trình bày đầy đủ trong báo cáo — tín hiệu #2 của GV)*

Gọi $c$ = số bit 1 thật trong cửa sổ, $\hat c$ = ước lượng, $B$ = kích thước bucket cũ nhất.
Sai số chỉ phát sinh từ bucket cũ nhất (các bucket khác nằm trọn trong cửa sổ):
- Trường hợp xấu nhất **ước lượng thừa**: chỉ 1 bit 1 của bucket cũ nhất còn trong cửa sổ ⇒ $\hat c - c \le B/2 - 1$
- Trường hợp xấu nhất **ước lượng thiếu**: toàn bộ $B$ bit 1 còn trong cửa sổ ⇒ $c - \hat c \le B/2$
- Theo bất biến 1, tổng các bucket nhỏ hơn ≥ $B - 1$ ⇒ $c \ge B$
- Do đó $\dfrac{|\hat c - c|}{c} \le \dfrac{B/2}{B} = \boxed{50\%}$

Với $r$ bucket mỗi kích thước, tổng bucket nhỏ hơn ≥ $r(B-1)$, cho $O(1/r)$ — sẽ kiểm chứng thực nghiệm ở E2.

### 4.2. ⭐⭐ DGIM mở rộng cho tổng số nguyên (Q2) — điểm khác biệt

> Slide tr.66: *"Tổng của $k$ số nguyên gần nhất: mỗi số nguyên có tối đa $m$ bit · Coi mỗi bit như một luồng riêng và đếm bit 1 trong $k$ phần tử gần nhất · Ước lượng $\sum_{i=0}^{m-1} c_i \cdot 2^i$"*

**Chưa nhóm nào dùng phần mở rộng này.** Đây là chỗ tạo khác biệt học thuật rõ nhất.

**Thiết kế:** ước lượng **tổng doanh thu** trong $N$ chuyến gần nhất.
- Lượng tử hóa `total_amount` thành số nguyên (đơn vị: đô-la, làm tròn)
- Chọn $m = 12$ bit ⇒ biểu diễn được 0–4.095 USD (đủ phủ mọi chuyến; giá trị vượt ⇒ kẹp trần, ghi nhận tỷ lệ kẹp)
- Duy trì **$m$ instance DGIM song song**, instance $i$ nhận bit thứ $i$ của giá trị
- Ước lượng: $\widehat{\text{sum}} = \sum_{i=0}^{m-1} \widehat{c_i}\cdot 2^i$

```python
class DGIMInteger:
    def __init__(self, N: int, m: int = 12, r: int = 2):
        self.bit_streams = [DGIM(N, r) for _ in range(m)]

    def update(self, value: int) -> None:
        for i, dgim in enumerate(self.bit_streams):
            dgim.update((value >> i) & 1)

    def query(self, k: int | None = None) -> int:
        return sum(d.query(k) << i for i, d in enumerate(self.bit_streams))
```

**🔬 Câu hỏi nghiên cứu riêng của đề tài (chưa có trong slide):**

> Sai số của mỗi luồng bit bị **khuếch đại theo trọng số $2^i$**. Luồng bit cao (i lớn) có ít bit 1 hơn (giá trị lớn hiếm) ⇒ bucket cũ nhất chiếm tỷ trọng lớn hơn ⇒ **sai số tương đối cao hơn**, lại còn được nhân với trọng số lớn nhất.
>
> **Giả thuyết H1:** sai số tổng thể bị chi phối bởi các luồng bit cao, và phân bổ $r$ **không đồng đều** (tăng $r$ cho bit cao, giảm cho bit thấp) sẽ cho sai số thấp hơn ở cùng ngân sách bộ nhớ so với phân bổ đồng đều.

Đây là **đóng góp học thuật thật sự** — kiểm chứng được bằng thực nghiệm E4, và kết quả âm tính vẫn là kết quả hợp lệ.

### 4.3. Flajolet-Martin (Q3)

Đếm số **tuyến đường phân biệt** (cặp `PULocationID → DOLocationID`, tối đa $265^2 = 70.225$ tuyến) hoạt động trong cửa sổ.

```python
class FlajoletMartin:
    """m hàm băm, chia g nhóm: trung bình trong nhóm → trung vị các trung bình
       (slide tr.40: 'Tốt nhất: kết hợp cả hai')"""
    def __init__(self, m: int = 64, g: int = 8, seed: int = 42): ...

    def _trailing_zeros(self, h: int) -> int: ...     # r(s), slide tr.37

    def update(self, item) -> None:
        for j in range(self.m):
            self.R[j] = max(self.R[j], self._trailing_zeros(self.hash(j, item)))

    def estimate(self) -> float:
        group_means = [mean(2**R for R in group) for group in chunks(self.R, self.g)]
        return median(group_means)
```

**Thực nghiệm E5:** so sánh 3 chiến lược tổng hợp — trung bình thuần (nhạy outlier), trung vị thuần (luôn là lũy thừa của 2), median-of-means — đúng ba lựa chọn GV nêu ở tr.40.

### 4.4. AMS — số bất ngờ (Q4)

Đo mức độ **tập trung nhu cầu**: mô-men bậc 2 của phân phối tần suất khu vực đón.

- Phân phối đều (nhu cầu trải khắp thành phố) ⇒ số bất ngờ **thấp**
- Phân phối lệch (vài khu vực hút hết chuyến — sự kiện lớn, ùn tắc) ⇒ số bất ngờ **cao**

Slide tr.45 nói rõ: *"Ứng dụng: phát hiện điểm bất thường (anomaly), tắc nghẽn mạng"* — khớp trực tiếp bài toán.

```python
class AMS:
    """k biến ngẫu nhiên; dùng Reservoir Sampling vì n không biết trước (slide tr.51)"""
    def __init__(self, k: int = 100): ...

    def update(self, item) -> None:
        self.n += 1
        for var in self.variables:
            if var.val == item:
                var.c += 1
        self._reservoir_replace(item)      # xác suất k/n

    def estimate_moment(self, order: int = 2) -> float:
        # slide tr.47: n(2c−1);  tr.50 tổng quát: n(c^k − (c−1)^k)
        return mean(self.n * (v.c**order - (v.c-1)**order) for v in self.variables)
```

**Bài tập GV giao (slide tr.50) sẽ được giải trong báo cáo:** chứng minh công thức tổng quát bậc $k$, và tính tay số bất ngờ + mô-men bậc 3 cho luồng `3,1,4,1,3,4,2,1,2`. Đối chiếu với kết quả code.

### 4.5. Reservoir Sampling (Q5)

Giữ mẫu $s = 100.000$ chuyến đại diện để (a) cấp dữ liệu cho tầng khai phá L3, (b) phân tích sâu ad-hoc.

**⚠️ Bài học từ slide tr.16–17 — chọn đúng đơn vị lấy mẫu:** GV chứng minh bằng đại số rằng lấy mẫu sai đơn vị cho ước lượng chệch ($\frac{b}{10a+19b} \ne \frac{b}{a+b}$).

Với CityFlow: nếu muốn ước lượng *"tỷ lệ khu vực có ≥2 chuyến trong cửa sổ"*, lấy mẫu **theo chuyến** sẽ chệch; phải lấy mẫu **theo khu vực** (băm `LocationID`, giữ nếu $h(z) \le a$). **Báo cáo sẽ trình bày cả hai cách và đo độ chệch thực tế** — tái hiện bài học của GV trên dữ liệu thật.

---

## 5. THIẾT KẾ TẦNG L3 — KHAI PHÁ MẪU *(FROM SCRATCH)*

> 🔴 Tầng bắt buộc. Trả lời Q6 và trả lời phản biện *"đâu là phần khai phá dữ liệu?"*

### 5.1. Xây dựng giỏ hàng — quyết định thiết kế then chốt

| Thành phần | Định nghĩa |
|---|---|
| **Giao dịch (basket)** | Một **cửa sổ thời gian 15 phút** |
| **Item** | `"zone_z_hot"` — khu vực $z$ đang ở trạng thái nhu cầu cao trong cửa sổ đó |
| **Item bổ sung** | `"hour_morning_peak"`, `"dow_weekend"`, `"weather_?"` *(không dùng thời tiết — giữ phạm vi)* |

**⚠️ Vấn đề rời rạc hóa và cách giải quyết:**

Nếu định nghĩa "hot" bằng **ngưỡng tuyệt đối** (VD > 500 chuyến/15 phút), kết quả sẽ tầm thường: *"Midtown Manhattan luôn hot"* — không mang thông tin.

**Giải pháp: chuẩn hóa theo từng khu vực.**
$$\text{zone } z \text{ hot trong cửa sổ } w \iff \text{count}(z,w) > P_{80}\big(\{\text{count}(z,\cdot)\}\big)$$
tức vượt **phân vị 80 của chính khu vực đó** trong lịch sử. Khi đó luật tìm được mang nghĩa *"khu vực A bận hơn bình thường thì khu vực C cũng bận hơn bình thường"* — thông tin thật sự có thể hành động.

Sẽ thực nghiệm với $P_{70}, P_{80}, P_{90}$ và báo cáo ảnh hưởng lên số luật sinh ra.

### 5.2. FP-Growth từ đầu

Cài đặt đầy đủ theo slide tr.21–33:

```
fptree.py        FPTree, FPNode, header table, f-list (sắp giảm dần tần suất)
fpgrowth.py      conditional pattern base → conditional FP-tree → đệ quy
                 + tối ưu single prefix path (slide tr.31: Reduction + Concatenation)
apriori.py       cài đặt đối chứng — đo số candidate sinh ra để minh chứng
                 3 điểm nghẽn GV nêu ở tr.19
fpclose.py       closed patterns
fpmax.py         max patterns
```

**Kiểm định tính đúng đắn:** tái hiện đúng ví dụ chuẩn của GV (slide tr.22, min_sup=3, f-list `f:4, c:4, a:3, b:3, m:3, p:3`) làm unit test, rồi đối chiếu toàn bộ tập frequent itemset với `mlxtend.frequent_patterns.fpgrowth` — **phải khớp tuyệt đối**.

### 5.3. ⭐ Độ đo interestingness — tín hiệu chấm điểm #4

Cài đặt **cả 9 độ đo** + Imbalance Ratio:

| Độ đo | Công thức | Null-invariant? |
|---|---|:---:|
| Support | $P(A\cap B)$ | — |
| Confidence | $P(B\mid A)$ | ✅ (nhưng không đối xứng) |
| **Lift** | $\dfrac{P(A\cap B)}{P(A)P(B)}$ | ❌ |
| **$\chi^2$** | thống kê chi-bình phương | ❌ |
| AllConf | $\dfrac{\sup(A,B)}{\max\{\sup A,\sup B\}}$ | ✅ |
| Coherence | $\dfrac{\sup(A,B)}{\sup A+\sup B-\sup(A,B)}$ | ✅ |
| Cosine | $\dfrac{\sup(A,B)}{\sqrt{\sup A\cdot\sup B}}$ | ✅ |
| **Kulczynski** | $\dfrac{P(A\mid B)+P(B\mid A)}{2}$ | ✅ |
| MaxConf | $\max\left\{\dfrac{\sup(A,B)}{\sup A},\dfrac{\sup(A,B)}{\sup B}\right\}$ | ✅ |
| Imbalance Ratio | $\dfrac{\lvert\sup A-\sup B\rvert}{\sup A+\sup B-\sup(A,B)}$ | ✅ |

**🔬 Thực nghiệm E10 — kiểm chứng null-invariance trên dữ liệu thật:**

Dữ liệu CityFlow có **rất nhiều giao dịch null** — với một cặp khu vực $(A,B)$ bất kỳ, phần lớn cửa sổ 15 phút **không có** khu vực nào trong hai khu vực đó hot. Đây đúng là kịch bản GV cảnh báo.

Thiết kế thực nghiệm: **tăng dần số giao dịch null** (mở rộng khoảng thời gian phân tích sang các khung giờ đêm ít hoạt động) và quan sát:
- Lift và $\chi^2$ **thay đổi mạnh** theo số giao dịch null
- 5 độ đo null-invariant **giữ nguyên**

⇒ Chứng minh bằng số liệu thật điều GV dạy bằng ví dụ giả định. **Đây là đóng góp học thuật của đồ án.**

### 5.4. Nén pattern (M5)

Đo **tỷ lệ nén**: `#closed / #all` và `#max / #all` theo `min_sup`.
Slide tr.13 nói closed cho *"lossless compression"* — sẽ kiểm chứng bằng cách tái tạo lại toàn bộ frequent itemset từ tập closed và xác nhận không mất mát.

---

## 6. THIẾT KẾ DỮ LIỆU & CSDL

### 6.1. Phân vai công cụ

| Công cụ | Vai trò | Lý do chọn |
|---|---|---|
| **Parquet (đĩa)** | Dữ liệu thô | Định dạng gốc của TLC, nén cột hiệu quả |
| **DuckDB** | **Oracle tính chính xác + ETL** | Xử lý hàng trăm triệu dòng Parquet trên máy cá nhân, nhanh hơn pandas nhiều lần, không cần server. Đây là lựa chọn kỹ thuật có chủ đích, sẽ biện luận trong báo cáo |
| **PostgreSQL** | Lưu kết quả phục vụ API | Metadata khu vực, ảnh chụp sketch, tổng hợp cửa sổ, luật đã khai phá, kết quả benchmark |
| **RAM** | Sketch đang chạy | Bản chất của thuật toán luồng |

### 6.2. Lược đồ PostgreSQL

```sql
-- Danh mục khu vực
CREATE TABLE zones (
    location_id   SMALLINT PRIMARY KEY,      -- 1..265
    borough       TEXT NOT NULL,
    zone_name     TEXT NOT NULL,
    service_zone  TEXT,
    geometry      JSONB                      -- GeoJSON polygon
);

-- Ảnh chụp sketch định kỳ (để API trả lời không cần giữ tiến trình)
CREATE TABLE sketch_snapshots (
    id            BIGSERIAL PRIMARY KEY,
    stream_key    TEXT NOT NULL,             -- 'pu_zone_161', 'revenue_global', ...
    sketch_type   TEXT NOT NULL,             -- 'dgim' | 'dgim_int' | 'fm' | 'ams'
    event_seq     BIGINT NOT NULL,           -- vị trí trong luồng
    state         JSONB NOT NULL,            -- bucket / R / biến AMS
    memory_bytes  INTEGER NOT NULL,          -- P2: đo thật
    captured_at   TIMESTAMPTZ DEFAULT now()
);
CREATE INDEX ON sketch_snapshots (stream_key, event_seq DESC);

-- Tổng hợp cửa sổ 15 phút (đầu vào tầng khai phá)
CREATE TABLE window_aggregates (
    window_start  TIMESTAMPTZ NOT NULL,
    location_id   SMALLINT REFERENCES zones,
    trip_count    INTEGER NOT NULL,
    total_revenue NUMERIC(12,2),
    is_hot        BOOLEAN NOT NULL,          -- vượt phân vị của chính khu vực
    PRIMARY KEY (window_start, location_id)
);

-- Frequent itemsets
CREATE TABLE frequent_itemsets (
    id            BIGSERIAL PRIMARY KEY,
    run_id        UUID NOT NULL,
    items         SMALLINT[] NOT NULL,
    support_count INTEGER NOT NULL,
    support_rel   REAL NOT NULL,
    is_closed     BOOLEAN NOT NULL,
    is_maximal    BOOLEAN NOT NULL
);

-- Luật kết hợp + đầy đủ 10 độ đo
CREATE TABLE association_rules (
    id            BIGSERIAL PRIMARY KEY,
    run_id        UUID NOT NULL,
    antecedent    SMALLINT[] NOT NULL,
    consequent    SMALLINT[] NOT NULL,
    support       REAL, confidence REAL, lift REAL, chi_square REAL,
    all_conf      REAL, coherence REAL, cosine REAL,
    kulczynski    REAL, max_conf REAL, imbalance_ratio REAL
);
CREATE INDEX ON association_rules (run_id, kulczynski DESC);

-- Kết quả benchmark (L6)
CREATE TABLE benchmark_results (
    id            BIGSERIAL PRIMARY KEY,
    experiment    TEXT NOT NULL,             -- 'E1'..'E11'
    params        JSONB NOT NULL,            -- {N, r, m, g, k, min_sup}
    exact_value   DOUBLE PRECISION,
    estimated     DOUBLE PRECISION,
    rel_error     DOUBLE PRECISION,
    memory_bytes  BIGINT,
    elapsed_ms    DOUBLE PRECISION,
    created_at    TIMESTAMPTZ DEFAULT now()
);
```

---

## 7. THIẾT KẾ API

**FastAPI + Pydantic.** Mọi endpoint ước lượng đều trả kèm **giá trị chính xác và sai số** khi oracle có sẵn — biến chính API thành công cụ minh chứng.

| Method | Endpoint | Mô tả |
|---|---|---|
| `GET` | `/api/zones` | Danh mục 265 khu vực + GeoJSON |
| `GET` | `/api/window/count?zone={z}&k={k}` | **Q1** — DGIM: `{estimated, exact, rel_error, memory_bytes, n_buckets}` |
| `GET` | `/api/window/sum?metric=revenue&k={k}` | **Q2** — DGIM số nguyên + phân rã sai số theo vị trí bit |
| `GET` | `/api/distinct/routes?window={w}` | **Q3** — Flajolet-Martin |
| `GET` | `/api/surprise?window={w}` | **Q4** — AMS, kèm mô-men bậc 2 và 3 |
| `GET` | `/api/sample?n={n}` | **Q5** — Reservoir |
| `GET` | `/api/rules?measure=kulczynski&min_sup={s}&top_k={k}` | **Q6** — luật, xếp theo độ đo tùy chọn |
| `GET` | `/api/rules/compare?rule_id={id}` | So sánh thứ hạng luật theo cả 10 độ đo |
| `GET` | `/api/bench/{experiment}` | Kết quả E1–E11 |
| `GET` | `/api/heatmap?k={k}` | Ước lượng DGIM cho cả 265 khu vực (vẽ bản đồ nhiệt) |
| `WS` | `/ws/stream` | Đẩy sự kiện và trạng thái sketch theo thời gian thực |

**Ví dụ phản hồi `/api/window/count`:**
```json
{
  "zone": 161, "zone_name": "Midtown Center", "k": 1000000,
  "estimated": 48128, "exact": 47903,
  "absolute_error": 225, "relative_error": 0.0047,
  "theoretical_bound": 0.5,
  "memory_bytes": 312, "n_buckets": 26,
  "params": {"N": 1000000, "r": 2}
}
```

> Trường `theoretical_bound` xuất hiện trong **mọi** phản hồi — mỗi lần gọi API là một lần đối chiếu thực nghiệm với lý thuyết.

---

## 8. THIẾT KẾ GIAO DIỆN

**Công nghệ:** React + Vite + TailwindCSS + Plotly.js + react-leaflet
*(Yêu cầu ban đầu ưu tiên React/Tailwind; Vite nhẹ hơn Next.js và không cần SSR cho ứng dụng nội bộ. **Phương án dự phòng nếu thiếu thời gian: Streamlit** — chấp nhận UI kém hơn để đảm bảo có sản phẩm chạy được.)*

### Bốn màn hình

**① Live Monitor** — màn hình demo chính khi bảo vệ
- Bản đồ nhiệt 265 khu vực NYC, màu theo ước lượng DGIM trong $N$ chuyến gần nhất
- Thanh trượt điều chỉnh $N$ trực tiếp → bản đồ cập nhật tức thì
- Chỉ số trực tiếp: số tuyến phân biệt (FM) · số bất ngờ (AMS) · thông lượng · **tổng bộ nhớ sketch**
- Điều khiển replay: play / pause / tốc độ

**② Accuracy Lab** — màn hình ăn điểm
- Biểu đồ **ước lượng vs chính xác** theo thời gian cho khu vực được chọn
- Phân phối sai số + **đường cận lý thuyết 50%** vẽ chồng lên
- Đường cong **sai số theo $r$** đối chiếu đường $O(1/r)$ lý thuyết
- Đường cong **bộ nhớ theo $N$** đối chiếu $O(\log^2 N)$
- ⭐ **Phân rã sai số theo vị trí bit** cho DGIM số nguyên (kiểm chứng giả thuyết H1)

**③ Pattern Explorer**
- Bảng luật đồng ùn tắc, **chuyển đổi độ đo xếp hạng** bằng một cú nhấp
- ⭐ **So sánh song song:** cùng tập luật xếp theo Lift vs theo Kulczynski — thấy ngay thứ hạng đảo lộn
- Biểu đồ **độ nhạy với giao dịch null**: Lift/$\chi^2$ trôi, 5 độ đo null-invariant phẳng
- Trực quan hóa luật trên bản đồ (tiền đề → hệ quả)

**④ Benchmark Dashboard**
- Toàn bộ kết quả E1–E11 dạng bảng + biểu đồ
- Bảng đối chiếu from-scratch vs thư viện
- So sánh FP-Growth vs Apriori: thời gian, bộ nhớ, số candidate theo `min_sup`

---

## 9. CẤU TRÚC MÃ NGUỒN

```
cityflow/
├── docker-compose.yml
├── Dockerfile.api
├── Dockerfile.web
├── pyproject.toml
├── README.md
├── .env.example
│
├── data/                          # .gitignore
│   ├── raw/                       # parquet TLC
│   ├── reference/                 # taxi_zone_lookup.csv, taxi_zones.geojson
│   └── processed/
│
├── notebooks/
│   ├── 01_data_understanding.ipynb
│   ├── 02_data_preparation.ipynb
│   ├── 03_sketch_validation.ipynb      # worked example tính tay ↔ code
│   ├── 04_pattern_mining.ipynb
│   ├── 05_interestingness_analysis.ipynb
│   └── 06_final_evaluation.ipynb
│
├── src/cityflow/
│   ├── sketches/                  # ⭐ FROM SCRATCH
│   │   ├── dgim.py
│   │   ├── dgim_integer.py
│   │   ├── flajolet_martin.py
│   │   ├── ams.py
│   │   ├── reservoir.py
│   │   ├── bloom.py               # tùy chọn: lọc khu vực quan tâm
│   │   ├── registry.py            # quản lý 535 luồng, lazy expiration
│   │   └── base.py                # giao diện chung + memory_bytes()
│   │
│   ├── mining/                    # ⭐ FROM SCRATCH
│   │   ├── fptree.py
│   │   ├── fpgrowth.py
│   │   ├── fpclose.py
│   │   ├── fpmax.py
│   │   ├── apriori.py             # đối chứng
│   │   ├── basket_builder.py      # rời rạc hóa theo phân vị từng khu vực
│   │   ├── rules.py
│   │   └── interestingness.py     # 9 độ đo + imbalance ratio
│   │
│   ├── ingest/
│   │   ├── loader.py              # parquet → sự kiện chuẩn hóa
│   │   ├── replay.py              # phát lại theo thứ tự thời gian, có throttle
│   │   └── schema.py
│   │
│   ├── oracle/                    # P3: đường đi độc lập
│   │   ├── exact_window.py        # đếm chính xác bằng DuckDB
│   │   ├── exact_distinct.py
│   │   └── exact_moments.py
│   │
│   ├── bench/                     # ⭐ L6
│   │   ├── experiments.py         # E1..E11
│   │   ├── runner.py
│   │   ├── plots.py
│   │   └── crosscheck.py          # from-scratch ↔ mlxtend/datasketch
│   │
│   ├── api/
│   │   ├── main.py
│   │   ├── routers/
│   │   └── deps.py
│   │
│   ├── db/
│   │   ├── models.py
│   │   ├── session.py
│   │   └── migrations/
│   │
│   └── config.py                  # P5: mọi tham số cấu hình được
│
├── web/                           # React + Vite + Tailwind
│   ├── src/
│   │   ├── pages/{LiveMonitor,AccuracyLab,PatternExplorer,Benchmark}.tsx
│   │   ├── components/
│   │   └── api/
│   └── package.json
│
├── tests/
│   ├── test_dgim.py               # tái hiện ví dụ slide tr.63, tr.65
│   ├── test_dgim_integer.py
│   ├── test_flajolet_martin.py    # tái hiện ví dụ tr.38
│   ├── test_ams.py                # tái hiện ví dụ tr.48 (kết quả = 55)
│   ├── test_reservoir.py          # kiểm định xác suất s/n
│   ├── test_fpgrowth.py           # tái hiện ví dụ tr.22
│   ├── test_interestingness.py    # tái hiện ví dụ basketball/cereal tr.36
│   └── test_crosscheck.py
│
└── docs/                          # tài liệu thiết kế và kết quả thực nghiệm
```

> 📌 Thư mục `tests/` được thiết kế để **mỗi ví dụ số trong slide đều trở thành một unit test**. Đây vừa là kiểm định tính đúng đắn, vừa là bằng chứng trực tiếp trong báo cáo rằng nhóm hiểu bài giảng.

---

## 10. MA TRẬN THỰC NGHIỆM — PHẦN ĂN ĐIỂM CHÍNH

*Đây là phần đáp ứng tín hiệu chấm điểm #3 của giảng viên (tinh chỉnh tham số + so sánh lý thuyết vs thực nghiệm).*

| # | Thực nghiệm | Biến độc lập | Đo | Đối chiếu lý thuyết |
|:--:|---|---|---|---|
| **E1** | Độ chính xác DGIM theo độ rộng cửa sổ | $N \in \{10^4,10^5,10^6,10^7\}$ | Phân phối sai số tương đối | Cận 50% (tr.64) |
| **E2** | ⭐ Sai số DGIM theo $r$ | $r \in \{1,2,4,8,16\}$ | Sai số trung bình & tối đa | Quan hệ $O(1/r)$ (tr.64) |
| **E3** | Bộ nhớ DGIM theo $N$ | $N$ như E1 | `memory_bytes()` thật | $O(\log^2 N)$ (tr.58) |
| **E4** | ⭐⭐ **Phân rã sai số DGIM số nguyên theo vị trí bit** | $m \in \{8,10,12,14\}$; phân bổ $r$ đều vs không đều | Đóng góp sai số của từng luồng bit | **Giả thuyết H1 — câu hỏi nghiên cứu riêng** |
| **E5** | Flajolet-Martin: chiến lược tổng hợp | $m \in \{16,32,64,128\}$, $g \in \{1,4,8,16\}$ | Sai số của mean / median / median-of-means | tr.40–41 |
| **E6** | AMS theo số biến | $k \in \{10,50,100,500\}$ | Sai số mô-men bậc 2 và 3 | tr.47, tr.50 |
| **E7** | Thông lượng theo số luồng đồng thời | 1 → 535 luồng | Sự kiện/giây, bộ nhớ tổng | Kiểm chứng lập luận §1.2 |
| **E8** | Reservoir: đơn vị lấy mẫu | Theo chuyến vs theo khu vực | Độ chệch ước lượng | **Tái hiện bài học tr.16–17 trên dữ liệu thật** |
| **E9** | FP-Growth vs Apriori | `min_sup` ∈ 5 mức | Thời gian, bộ nhớ, **số candidate** | 3 điểm nghẽn Apriori (tr.19) |
| **E10** | ⭐⭐ **Độ nhạy với giao dịch null** | Tăng dần số giao dịch null | Thứ hạng luật theo 10 độ đo | **Chứng minh null-invariance trên dữ liệu thật (tr.36–39)** |
| **E11** | Nén pattern | `min_sup` ∈ 5 mức | `#closed/#all`, `#max/#all`, kiểm tra tái tạo không mất mát | tr.13 |
| **E12** | Kiểm định chéo from-scratch ↔ thư viện | — | Sai lệch phải bằng **0** | Tính đúng đắn |

**Ba thực nghiệm tạo khác biệt:** E4 (câu hỏi nghiên cứu riêng), E10 (chứng minh điều GV dạy bằng dữ liệu thật), E8 (tái hiện bài học lấy mẫu).

---

## 11. TRIỂN KHAI & DOCKER

```yaml
# docker-compose.yml — mục tiêu: một lệnh `docker compose up` là chạy
services:
  db:
    image: postgres:16-alpine
    environment: [POSTGRES_DB=cityflow, POSTGRES_USER=cityflow, POSTGRES_PASSWORD=cityflow]
    volumes: ["pgdata:/var/lib/postgresql/data", "./sql/init.sql:/docker-entrypoint-initdb.d/init.sql"]
    healthcheck: {test: ["CMD-SHELL", "pg_isready -U cityflow"], interval: 5s}

  api:
    build: {context: ., dockerfile: Dockerfile.api}
    depends_on: {db: {condition: service_healthy}}
    volumes: ["./data:/app/data:ro"]
    ports: ["8000:8000"]

  replay:                      # sinh luồng sự kiện, chạy nền
    build: {context: ., dockerfile: Dockerfile.api}
    command: python -m cityflow.ingest.replay --speed 1000
    depends_on: [api]

  web:
    build: {context: ./web, dockerfile: ../Dockerfile.web}
    ports: ["3000:80"]
    depends_on: [api]

volumes: {pgdata: {}}
```

**Kịch bản demo (script bảo vệ):**
1. `docker compose up -d` → hệ thống lên
2. `make load-data MONTH=2024-01` → tải & nạp dữ liệu
3. Mở `localhost:3000` → Live Monitor, bấm play → bản đồ nhiệt chuyển động
4. Kéo thanh $N$ → cho thấy cửa sổ trượt phản ứng
5. Sang Accuracy Lab → chỉ vào đường cận 50% và sai số thực tế nằm dưới
6. Sang Pattern Explorer → đổi độ đo từ Lift sang Kulczynski → **thứ hạng luật đảo lộn ngay trước mắt hội đồng**
7. Sang Benchmark → bảng E1–E12

---

## 12. PHÂN CÔNG & TIẾN ĐỘ

### 12.1. Phân công theo module

| Vai trò | Phụ trách | Sản phẩm |
|---|---|---|
| **TV-A · Streaming Core** | DGIM, DGIM-Integer, Registry (lazy expiration), Reservoir | `sketches/` + unit test tái hiện slide |
| **TV-B · Sketch & Benchmark** | Flajolet-Martin, AMS, Oracle (DuckDB), toàn bộ L6 + biểu đồ | `oracle/`, `bench/`, E1–E12 |
| **TV-C · Mining & Product** | FP-Growth/FPClose/FPMax, 10 độ đo, API, CSDL, Dashboard | `mining/`, `api/`, `db/`, `web/` |

> Gợi ý: TV-C là khối lượng lớn nhất. **Sau tuần 4, TV-A chuyển sang hỗ trợ dashboard** (khi phần sketch đã ổn định).

### 12.2. Tiến độ 10 tuần

| Tuần | Mốc | Đầu ra kiểm chứng được |
|:--:|---|---|
| **1** | Data Understanding + Ingest/Replay | Notebook 01 · số liệu thật đã xác minh · replay chạy được |
| **2** | DGIM + DGIM-Integer từ đầu | Unit test tái hiện đúng ví dụ slide tr.63, tr.65 |
| **3** | FM + AMS + Reservoir + Registry 535 luồng | Test tái hiện tr.38, tr.48 (=55) · registry chạy 1 tháng dữ liệu |
| **4** | Oracle + khung benchmark | E1, E2, E3 có kết quả |
| **5** | ⭐ E4 (giả thuyết H1) + E5–E8 | Trả lời được H1 đúng hay sai |
| **6** | FP-Growth từ đầu + basket builder | Test tr.22 · kiểm định chéo mlxtend khớp tuyệt đối |
| **7** | 10 độ đo + ⭐ E10 + E11 | Bằng chứng null-invariance trên dữ liệu thật |
| **8** | API + CSDL + Dashboard | `docker compose up` chạy end-to-end |
| **9** | Mở rộng quy mô (12 tháng) + E7 + E9 + E12 | Toàn bộ ma trận thực nghiệm hoàn tất |
| **10** | Báo cáo + slide + script demo | Bộ tài liệu hoàn chỉnh |

**Cột mốc không thể trượt:** hết tuần 4 phải có E1–E3. Nếu trượt ⇒ kích hoạt phương án dự phòng (§13).

---

## 13. RỦI RO & BIỆN PHÁP

| # | Rủi ro | Mức | Biện pháp |
|:--:|---|:--:|---|
| **R1** | Dữ liệu TLC khác kỳ vọng (đổi lược đồ, đổi quy mô, khó tải) | 🔴 Cao | **Việc đầu tiên của Phase 5** là tải 1 tháng và xác minh. Dự phòng: Yellow Taxi (lược đồ ổn định nhiều năm) |
| **R2** | Python thuần quá chậm cho 535 luồng × 230 triệu sự kiện | 🟠 TB | ① Lazy expiration (§4.1) ② `__slots__` + `deque` ③ Nếu vẫn chậm: giảm quy mô xuống 3 tháng và **báo cáo trung thực thông lượng đo được** — E7 chính là chỗ trình bày giới hạn này, không phải chỗ giấu |
| **R3** | Phản biện *"đây là truy vấn xấp xỉ, không phải khai phá dữ liệu"* | 🔴 Cao | **Tầng L3 (Q6) là bắt buộc.** Báo cáo phải mở đầu chương Thực nghiệm bằng kết quả khai phá mẫu, không phải bằng sai số DGIM |
| **R4** | Phản biện *"dữ liệu lịch sử, không phải luồng thật"* | 🟠 TB | Thừa nhận thẳng ở §1.2 kèm luận cứ: bài toán và ràng buộc bộ nhớ là thật; chỉ nguồn phát là mô phỏng. **Che giấu mới là lỗi** |
| **R5** | Giả thuyết H1 (E4) cho kết quả âm tính | 🟢 Thấp | Kết quả âm tính **vẫn là kết quả hợp lệ** và vẫn viết được. Đây là lý do H1 được đặt dưới dạng giả thuyết kiểm chứng chứ không phải khẳng định |
| **R6** | Dashboard React tốn thời gian quá dự kiến | 🟠 TB | Chốt cứng: **hết tuần 8 chưa xong React ⇒ chuyển Streamlit**. Có sản phẩm chạy được quan trọng hơn UI đẹp |
| **R7** | Phình phạm vi | 🟠 TB | Danh sách "không làm" cố định: không dự báo, không deep learning, không dữ liệu thời tiết, không tối ưu tuyến |
| **R8** | Rời rạc hóa "hot" cho kết quả tầm thường | 🟡 TB | Đã xử lý bằng chuẩn hóa phân vị theo từng khu vực (§5.1); sẽ thử 3 mức phân vị |

---

## 14. CHECKLIST ĐỐI CHIẾU

### 14.1. Với 8 tiêu chí chọn đề tài

| | Tiêu chí | Đáp ứng |
|:--:|---|---|
| C1 | Lõi ≥2 thuật toán MMDS | ✅ **6 thuật toán**: DGIM, DGIM-Integer, FM, AMS, Reservoir, FP-Growth (+FPClose/FPMax/Apriori) |
| C2 | Không trùng 16 nhóm | ✅ DGIM làm lõi — 0/16 nhóm; Smart City — 0/16 nhóm |
| C3 | Thuật toán khớp bản chất bài toán | ✅ Bài toán **đúng nguyên văn** tình huống slide tr.53 |
| C4 | Dữ liệu đủ lớn | ✅ ~230 triệu bản ghi *(cần xác minh Phase 5)* |
| C5 | Ground truth định lượng | ✅✅ **Hoàn hảo** — giá trị chính xác tính được offline |
| C6 | Đủ 6 pha CRISP-DM | ✅ Business Understanding §1 · Data Understanding §2 · Preparation §5.1 · Modeling §4–5 · Evaluation §10 · Deployment §11 |
| C7 | Khai thác ≥2 khoảng trống | ✅ **G1** (DGIM) · **G6** (null-invariant) · **G3/M5** (nén pattern) · **M3** (lý thuyết vs thực nghiệm) · **M4** (from scratch) |
| C8 | Sản phẩm chạy được | ✅ API + Dashboard + PostgreSQL + Docker một lệnh |

### 14.2. Với 3 tín hiệu chấm điểm của giảng viên

| Tín hiệu | Đáp ứng |
|---|---|
| **#2 Chứng minh toán học** | Chứng minh cận 50% của DGIM (§4.1) · Giải bài tập GV giao ở tr.50 (§4.4) · Chứng minh không chệch AMS · Chứng minh quy nạp Reservoir |
| **#3 Tinh chỉnh tham số + lý thuyết vs thực nghiệm** | **Toàn bộ §10** — 12 thực nghiệm, mỗi thực nghiệm đối chiếu một công thức trong slide. Trường `theoretical_bound` có trong mọi phản hồi API |
| **#4 Độ đo null-invariant** | 10 độ đo cài đặt đầy đủ (§5.3) · **E10 chứng minh trên dữ liệu thật** · Màn hình Pattern Explorer cho phép đảo thứ hạng trực tiếp trước hội đồng |

### 14.3. Với yêu cầu sản phẩm của đồ án

| Yêu cầu | Đáp ứng |
|---|---|
| Source Code · Dataset · Notebook · REST API · Web App · Dashboard · Database · Docker · README | ✅ Toàn bộ (§9, §11) |
| Trained Model | ⚠️ **Đề tài này không có mô hình huấn luyện** — sản phẩm tri thức là **tập luật đồng ùn tắc** đã khai phá, lưu trong `association_rules`. Đây là bản chất của khai phá mẫu, không phải thiếu sót. Sẽ nêu rõ trong báo cáo |
| So sánh nhiều thuật toán · Feature Engineering · Explainability | ✅ FP-Growth vs Apriori (E9) · 3 chiến lược FM (E5) · rời rạc hóa phân vị (§5.1) · luật kết hợp **vốn đã tự giải thích** |
| Cross-Validation · ROC/AUC · SHAP | ❌ **Không áp dụng** — đây là bài toán khai phá mẫu và ước lượng, không phải phân loại có giám sát. Áp đặt các độ đo này sẽ là gượng ép. Thay thế bằng bộ độ đo phù hợp ở §1.4 và §10 |

---

## 15. TÓM TẮT PHASE 4

**Ba quyết định kiến trúc quan trọng nhất:**

1. **Ánh xạ 535 luồng bit + lazy expiration** (§4.1) — biến bài toán thành đúng kịch bản "nhiều luồng đồng thời" của slide tr.53, và giải quyết được vấn đề hiệu năng mà cách làm ngây thơ sẽ vấp phải.

2. **Tầng khai phá mẫu (Q6) là bắt buộc, không phải tùy chọn** (§5) — đây là lá chắn trước phản biện *"đâu là phần khai phá dữ liệu?"*.

3. **Rời rạc hóa "hot" bằng phân vị theo từng khu vực** (§5.1) — nếu dùng ngưỡng tuyệt đối, toàn bộ tầng khai phá sẽ cho kết quả tầm thường ("Manhattan luôn bận"). Chi tiết nhỏ này quyết định tầng L3 có giá trị hay vô nghĩa.

**Hai đóng góp học thuật của đồ án (vượt ra ngoài slide):**
- **E4 / Giả thuyết H1** — phân bổ $r$ không đồng đều theo vị trí bit trong DGIM mở rộng cho số nguyên
- **E10** — chứng minh tính null-invariance bằng dữ liệu thật quy mô lớn, thay vì ví dụ giả định

---

*Đầu ra Phase 4. Phase 5 (Thực hiện Data Mining — bắt đầu bằng xác minh dữ liệu R1) sẽ khởi động sau khi được xác nhận.*
