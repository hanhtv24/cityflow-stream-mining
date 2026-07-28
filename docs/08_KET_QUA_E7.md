# PHASE 5 · BƯỚC 6 — KẾT QUẢ THỰC NGHIỆM E7

## Thông lượng và bộ nhớ của 535 luồng song song

**Ngày:** 2026-07-28
**Dữ liệu:** NYC TLC FHVHV 2024-01, 3.000.000 sự kiện · $N = 10^6$
**Cài đặt:** [`src/cityflow/sketches/registry.py`](../src/cityflow/sketches/registry.py)
**Script:** [`scripts/06_experiment_registry.py`](../scripts/06_experiment_registry.py) · **Kết quả:** [`e7_results.json`](e7_results.json)
**Kiểm định đơn vị:** 88/88 đạt

---

## 0. TÓM TẮT

| Chỉ số | Ngưỡng Phase 4 | Đo thật | |
|---|---|---|:--:|
| Thông lượng | ≥ 50.000 sự kiện/giây | **87.933/giây** | ✅ |
| Bộ nhớ 535 luồng | < 500 MB | **5,66 MB** | ✅ vượt xa |
| Sai số qua registry | — | 1,39% TB · 3,09% max | ✅ |
| Sai số doanh thu (Q2) | — | **0,82%** | ✅ |

**Phát hiện chính:** cấu hình mà E5 chọn vì độ chính xác ($m=256$) **chiếm 97,2% tổng thời gian xử lý**. Tối ưu từng thành phần riêng lẻ dẫn tới một hệ thống chậm gấp 12 lần mức cần thiết.

---

## 1. 🔴 Nút thắt cổ chai không nằm ở nơi thiết kế dự đoán

Lần đo đầu tiên: **7.077 sự kiện/giây** — thấp hơn mục tiêu 50.000 tới **7 lần**. Cả tháng dữ liệu sẽ mất 46 phút.

Phase 4 §13 (R2) dự đoán rủi ro hiệu năng nằm ở **535 luồng DGIM**. Đo từng thành phần trên 200.000 sự kiện cho kết quả ngược lại:

| Thành phần | Thời gian | Thông lượng | % tổng |
|---|---:|---:|---:|
| DGIM `pu_zone` (265 luồng) | 0,09s | 2.198.977/s | 0,3% |
| DGIM `do_zone` (265 luồng) | 0,09s | 2.206.422/s | 0,3% |
| DGIM 5 vị từ | 0,14s | 1.441.847/s | 0,5% |
| DGIM-Integer doanh thu | 0,27s | 736.068/s | 1,0% |
| **Flajolet-Martin ($m=256$)** | **27,28s** | **7.330/s** | **🔴 97,2%** |
| AMS ($k=100$) | 0,07s | 2.702.907/s | 0,3% |
| Reservoir | 0,12s | 1.638.602/s | 0,4% |

**Toàn bộ 535 luồng DGIM cộng lại chỉ chiếm ~1,5% thời gian.** Tối ưu hóa lazy expiration đã làm tốt phần việc của nó.

Nguyên nhân: Flajolet-Martin chạy **$m = 256$ phép băm cho MỖI sự kiện** trong vòng lặp Python thuần — 768 triệu lời gọi hàm cho 3 triệu sự kiện.

> **Bài học:** E5 chọn $m = 256$ vì nó cho sai số 6,4% thay vì 14,2% ở $m = 64$. Quyết định đó đúng khi xét riêng độ chính xác, nhưng $m=256$ đắt gấp **36 lần** $m=8$ về tính toán. Tối ưu từng thành phần cô lập không cho hệ thống tối ưu.

## 2. Khắc phục — vector hóa, không phải giảm độ chính xác

Có hai lối thoát: giảm $m$ (mất độ chính xác), hoặc vector hóa. Chọn vector hóa.

`update_many()` tính cả $m$ giá trị băm cho cả lô trong một phép numpy:

```python
z = block[:, None] ^ seeds[None, :]     # (kích thước lô, m)
z = z + c1
z = (z ^ (z >> 30)) * c2
z = (z ^ (z >> 27)) * c3
z = z ^ (z >> 31)
lowbit = z & (~z + 1)                   # z & -z cho số không dấu
r = np.bitwise_count(lowbit - 1)        # số số 0 ở cuối
np.maximum(best, r.max(axis=0), out=best)
```

### Vì sao xử lý theo lô KHÔNG phá vỡ ngữ nghĩa luồng

Trạng thái của Flajolet-Martin chỉ là $R_j = \max$ trên các phần tử. **Phép max có tính kết hợp và lũy đẳng**, nên kết quả không phụ thuộc thứ tự hay cách nhóm. Miễn là truy vấn xảy ra ở biên lô, đây là mô hình **vi-lô (micro-batch)** hợp lệ — đúng cách các hệ thống xử lý luồng thực tế vận hành.

**DGIM thì tuyệt đối KHÔNG được làm vậy:** trạng thái của nó phụ thuộc thứ tự và timestamp. Trong `update_batch()`, DGIM/AMS/Reservoir vẫn chạy tuần tự trong vòng lặp; chỉ Flajolet-Martin được gom lô.

Ranh giới này được ghi rõ trong docstring và có unit test bảo vệ.

### Kiểm định tính đúng đắn

Ba unit test bảo đảm đường vector hóa không phải "xấp xỉ giống" mà **khớp tuyệt đối**:

| Test | Nội dung |
|---|---|
| `test_update_many_matches_scalar_exactly` | Vector $R$ khớp **từng phần tử** với đường vô hướng, ở $m \in \{8, 64, 256\}$ |
| `test_update_many_is_order_and_chunk_independent` | Đảo ngược thứ tự và đổi kích thước lô (64 vs 4096) cho cùng kết quả |
| `test_update_many_handles_empty_and_zero` | Lô rỗng và giá trị 0 |

### Kết quả

| | Trước | Sau | Tăng tốc |
|---|---:|---:|---:|
| Flajolet-Martin đơn lẻ ($m=256$) | 7.330/s | 124.844/s | **17×** |
| **Toàn registry** | **7.077/s** | **87.933/s** | **12,4×** |

Không phải đánh đổi độ chính xác — vẫn giữ nguyên $m = 256$ và sai số 6,4%.

---

## 3. E7a — Bộ nhớ của 535 luồng

| Nhóm | Bộ nhớ | |
|---|---:|---:|
| 265 luồng `pu_zone` | 2.690.856 B | 2,69 MB |
| 265 luồng `do_zone` | 2.717.220 B | 2,72 MB |
| 5 vị từ | 80.088 B | 0,08 MB |
| DGIM-Integer doanh thu | 139.112 B | 0,14 MB |
| Flajolet-Martin | 20.616 B | 0,02 MB |
| AMS | 12.008 B | 0,01 MB |
| **Tổng (không kể mẫu)** | **5.659.900 B** | **5,66 MB** |
| Reservoir (100.000 mẫu) | 6.400.984 B | 6,40 MB |
| **Tổng cộng** | 12.060.884 B | 12,06 MB |

Tổng bucket: **39.613** trên 535 luồng — trung bình 74 bucket/luồng.

### Đối chiếu với lập luận nền tảng của đề tài

Phase 4 §1.2 lập luận rằng giữ cửa sổ đầy đủ cho nhiều luồng là bất khả thi. Đo thật:

| | Bộ nhớ |
|---|---:|
| 535 luồng × $N = 10^6$ dạng mảng bit | 66.875.000 B (66,9 MB) |
| Sketch | 5.659.900 B (5,7 MB) |
| **Tiết kiệm** | **11,8×** |

**Trung thực về con số này:** 11,8× thấp hơn nhiều so với tỷ lệ 2.400× tính theo lý thuyết ở Phase 4 §1.2. Nguyên nhân đã được [05_KET_QUA_E1_E3 §4.2](05_KET_QUA_E1_E3.md) chỉ ra — chi phí đối tượng của Python (~100×) ăn mất phần lớn ưu thế tiệm cận. Con số lý thuyết đúng về **độ tăng trưởng**, không đúng về hằng số trong Python.

Đáng chú ý: **Reservoir Sampling chiếm 53% tổng bộ nhớ** (6,40 MB) — nhiều hơn cả 535 luồng DGIM cộng lại. Nó lưu mẫu thật chứ không phải bản tóm tắt, nên $O(s)$ chứ không phải $O(\log N)$. Nếu cần siết bộ nhớ, đây là chỗ cắt đầu tiên.

---

## 4. E7b — Giá trị của lazy expiration

| Cách làm | Thông lượng |
|---|---:|
| Lazy — chỉ chạm luồng nhận bit 1 | **2.641.676/s** |
| Ngây thơ — gọi `update(bit)` cho cả 265 luồng | 51.417/s |

**Tăng tốc 51×.** Ngoại suy cho cả tháng: 0,1 phút so với 0,1 giờ.

Cơ sở là slide tr.62 (*"Nếu bit = 0 — không cần thay đổi gì"*). Nếu bỏ qua nhận xét một dòng này của bài giảng, hệ thống sẽ chậm hơn 51 lần.

---

## 5. E7c — Độ chính xác đầu-cuối qua registry

Cấu hình vận hành ($r = 8$, $m = 8$ với `sqrt_weighted`), đối chiếu với oracle chính xác:

| Khu vực | Ước lượng | Chính xác | Sai số |
|---|---:|---:|---:|
| 132 (JFK) | 19.754 | 19.162 | 3,09% |
| 161 (Midtown) | 11.529 | 11.445 | 0,73% |
| 61 (Crown Heights) | 13.390 | 13.379 | 0,08% |
| 237 (Upper East Side) | 7.246 | 7.161 | 1,19% |
| 5 (Arden Heights, thưa) | 274 | 269 | 1,86% |

**Trung bình 1,39% · lớn nhất 3,09%.**

**Tổng doanh thu (Q2):** ước lượng 24.773.062 vs chính xác 24.978.278 → **sai số 0,82%**.

Cả hai đều tốt hơn kết quả của các thực nghiệm riêng lẻ, vì cấu hình vận hành dùng $r = 8$ thay vì $r = 2$ mặc định.

---

## 6. KẾT LUẬN

**Cả bốn tiêu chí kỹ thuật của Phase 4 §1.4 đã đạt.** Q1–Q5 hoạt động đúng ở quy mô thật.

**Hai bài học phương pháp luận:**

1. **Tối ưu cục bộ không cộng dồn thành tối ưu toàn cục.** E5 chọn $m=256$ đúng khi xét riêng độ chính xác, nhưng biến nó thành 97,2% chi phí hệ thống. Chỉ đo ở mức toàn hệ thống mới lộ ra.

2. **Phải đo trước khi tối ưu.** Phase 4 dự đoán nút thắt ở 535 luồng DGIM và thiết kế lazy expiration để xử lý. Dự đoán đó đúng (lazy cho 51×) nhưng **không đủ** — nút thắt thật nằm ở một thành phần khác hoàn toàn, chỉ chiếm một dòng trong thiết kế.

---

*Bước tiếp theo: tầng khai phá mẫu (Q6) — FP-Growth from scratch, 10 độ đo interestingness, thực nghiệm E9–E11. Theo [07_KET_QUA_E5_E6 §10](07_KET_QUA_E5_E6.md), đây là thành phần mang thông tin chính chứ không phải phần bổ sung.*
