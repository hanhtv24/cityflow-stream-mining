# PHASE 5 · BƯỚC 3 — KẾT QUẢ THỰC NGHIỆM E1, E2, E3

## Kiểm chứng DGIM trên 19,66 triệu sự kiện thật

**Ngày:** 2026-07-27
**Dữ liệu:** NYC TLC FHVHV 2024-01 — 19.663.928 sự kiện đã sắp theo `pickup_datetime`
**Cài đặt:** DGIM from scratch, [`src/cityflow/sketches/dgim.py`](../src/cityflow/sketches/dgim.py)
**Script:** [`scripts/03_validate_dgim.py`](../scripts/03_validate_dgim.py) · **Kết quả:** [`e1_e3_results.json`](e1_e3_results.json)
**Kiểm định đơn vị:** 33/33 đạt — [`tests/test_dgim.py`](../tests/test_dgim.py)

---

## 0. TÓM TẮT

| Thực nghiệm | Cận lý thuyết (slide) | Kết quả đo thật | Kết luận |
|---|---|---|---|
| **E1** | Sai số ≤ 50% (tr.64) | **0/3.178** phép truy vấn vi phạm. Sai số TB 6,9–13,8%, max 46,3% | ✅ **Xác nhận** |
| **E2** | Sai số $\propto O(1/r)$ (tr.64) | Tích `sai số × r` = 23,8% · 20,7% · 19,4% · 20,6% — **gần như hằng số** | ✅ **Xác nhận** |
| **E3** | Bộ nhớ $O(\log^2 N)$ (tr.58) | $N$ tăng **500×** → bộ nhớ tăng **1,46×** | ✅ **Xác nhận** (tốt hơn cận) |

**Phát hiện bổ sung quan trọng:** DGIM chỉ có lợi về bộ nhớ khi $N \gtrsim 10^5$. Ở $N = 10^4$ nó **tốn gấp 7 lần** so với lưu cửa sổ đầy đủ. Chi tiết §4.3.

---

## 1. THIẾT KẾ THỰC NGHIỆM

### 1.1. Bốn khu vực đại diện

Chọn theo mật độ sự kiện để phủ nhiều chế độ vận hành khác nhau:

| LocationID | Tên | Số chuyến đón/tháng | Vai trò |
|---:|---|---:|---|
| 132 | JFK Airport | 374.293 | Luồng dày đặc nhất |
| 161 | Midtown Center | 242.893 | Luồng dày |
| 61 | Crown Heights North | 256.556 | Luồng trung bình |
| 5 | Arden Heights | ~1.400 | **Luồng cực thưa** |

Khu vực thưa là ca kiểm thử quan trọng nhất: khi cửa sổ chỉ chứa vài bit 1, bucket cũ nhất chiếm tỷ trọng lớn trong tổng, nên sai số tương đối dễ vượt cận nhất.

### 1.2. Oracle độc lập *(nguyên tắc P3)*

Giá trị chính xác tính bằng **tổng tiền tố** (`numpy.cumsum`) trên toàn mảng — thuật toán $O(n)$ bộ nhớ mà chính DGIM sinh ra để tránh. Không dùng chung một dòng mã nào với DGIM, nên không có nguy cơ "so sánh với chính mình".

### 1.3. 🔴 Một sai lầm phương pháp luận đã mắc và đã sửa

**Lần chạy đầu tiên cho sai số 129.311%** — vi phạm cận 50% ở 3.033/3.178 phép truy vấn.

Nguyên nhân **không phải** ở DGIM (đã qua 33 unit test bao gồm kiểm chứng cận 50% trên luồng tổng hợp) mà ở **harness đo đạc**: tôi nạp toàn bộ luồng vào sketch rồi mới truy vấn tại các mốc thời gian **quá khứ**.

Cách làm đó sai vì hai lý do độc lập:

1. Truy vấn cộng cả các bucket có timestamp **ở tương lai** so với mốc truy vấn.
2. Nghiêm trọng hơn: **lịch sử gộp bucket** đã bị dữ liệu tương lai làm sai lệch. Kể cả khi lọc bỏ bucket tương lai, cấu trúc thu được vẫn không phải trạng thái mà thuật toán thực sự có tại thời điểm $t$.

**Manh mối phát hiện:** bảng E3 cho `#bucket = 27` **y hệt nhau với mọi giá trị N**, và bộ nhớ giống nhau đến từng byte. Điều đó bất khả thi — cửa sổ rộng hơn phải giữ nhiều bucket hơn.

**Khắc phục:** phát lại luồng **một lượt**, tại mỗi mốc truy vấn $t$ chỉ nạp đúng các sự kiện xảy ra tới $t$. Đồng thời thêm chặn phòng vệ `cutoff < ts ≤ t_now` trong `query()`.

> Ghi lại sai lầm này trong báo cáo là có chủ ý. Nó minh họa rằng **kiểm chứng một thuật toán luồng đòi hỏi harness cũng phải tôn trọng ngữ nghĩa luồng** — và rằng con số vô lý (129.311%) là dấu hiệu lỗi đo đạc, không phải lỗi thuật toán.

---

## 2. E1 — SAI SỐ THEO ĐỘ RỘNG CỬA SỔ $N$

**Cấu hình:** $r = 2$ (sơ đồ chuẩn "1 hoặc 2 bucket mỗi cỡ", slide tr.60) · 200 mốc truy vấn rải đều mỗi cấu hình.

| Khu vực | $N$ | Đáp án đúng TB | Sai số TB | Sai số max | Vi phạm cận 50% |
|---|---:|---:|---:|---:|---:|
| JFK Airport | 10.000 | 192 | 13,05% | 42,03% | **0** |
| JFK Airport | 100.000 | 1.903 | 12,97% | 45,90% | **0** |
| JFK Airport | 1.000.000 | 19.096 | 11,39% | 42,57% | **0** |
| JFK Airport | 5.000.000 | 93.243 | 10,81% | 33,14% | **0** |
| Midtown Center | 10.000 | 124 | 11,81% | 39,87% | **0** |
| Midtown Center | 100.000 | 1.235 | 12,28% | 46,33% | **0** |
| Midtown Center | 1.000.000 | 12.288 | 11,92% | 33,60% | **0** |
| Midtown Center | 5.000.000 | 62.259 | 11,61% | 27,81% | **0** |
| Crown Heights North | 10.000 | 131 | 13,76% | 43,06% | **0** |
| Crown Heights North | 100.000 | 1.304 | 11,61% | 41,97% | **0** |
| Crown Heights North | 1.000.000 | 13.019 | 11,18% | 33,41% | **0** |
| Crown Heights North | 5.000.000 | 64.917 | 12,24% | 25,10% | **0** |
| Arden Heights (thưa) | 10.000 | **3** | 6,94% | 33,33% | **0** |
| Arden Heights (thưa) | 100.000 | 29 | 13,29% | 41,18% | **0** |
| Arden Heights (thưa) | 1.000.000 | 288 | 10,87% | 29,57% | **0** |
| Arden Heights (thưa) | 5.000.000 | 1.425 | 9,37% | 18,72% | **0** |

### Nhận xét

**① Cận 50% được xác nhận tuyệt đối.** 3.178 phép truy vấn, **0 vi phạm**. Sai số lớn nhất quan sát được là 46,33% — sát nhưng không vượt cận.

**② Sai số trung bình ổn định quanh 11–13%**, gần như **không phụ thuộc $N$**. Điều này phù hợp lý thuyết: sai số bị chi phối bởi kích thước bucket cũ nhất so với tổng, mà tỷ lệ đó do $r$ quyết định chứ không do $N$.

**③ Khu vực cực thưa hoạt động tốt.** Với $N = 10^4$, cửa sổ chỉ chứa **trung bình 3 chuyến** ở Arden Heights, vậy mà sai số TB chỉ 6,94%. Lý do: khi số bit 1 ít hơn số bucket mà cấu trúc cho phép, DGIM lưu được **chính xác** từng bit 1 mà không cần gộp.

**④ Sai số giảm nhẹ khi $N$ tăng** (13,05% → 10,81% ở JFK). Cửa sổ rộng chứa nhiều bit 1 hơn, nên phần bất định của bucket cũ nhất chiếm tỷ trọng nhỏ hơn.

---

## 3. ⭐ E2 — KIỂM CHỨNG QUAN HỆ $O(1/r)$

**Cấu hình:** khu vực 161 (Midtown Center), $N = 1.000.000$.

| $r$ | Sai số TB | Sai số max | #bucket | Bộ nhớ (byte) | **Sai số × $r$** |
|---:|---:|---:|---:|---:|---:|
| 2 | 11,916% | 33,600% | 21 | 11.412 | **23,83%** |
| 4 | 5,182% | 14,340% | 41 | 11.212 | **20,73%** |
| 8 | 2,429% | 6,202% | 85 | 13.268 | **19,43%** |
| 16 | 1,290% | 3,091% | 159 | 14.052 | **20,64%** |

### Đây là kết quả sạch nhất của cả thực nghiệm

Slide tr.64 phát biểu: *"Giảm sai số bằng cách duy trì $r$ hoặc $r-1$ bucket mỗi kích thước · Sai số: $O(1/r)$."*

Nếu quan hệ $O(1/r)$ đúng thì tích $\text{sai số} \times r$ phải là **hằng số**. Đo được: **23,83% · 20,73% · 19,43% · 20,64%** — dao động trong khoảng hẹp quanh ≈ 21%, trong khi $r$ thay đổi **8 lần**.

Diễn giải trực tiếp: tăng $r$ từ 2 lên 16 (**8×**) làm sai số giảm từ 11,916% xuống 1,290% (**9,2×**). Tỷ lệ giảm gần khớp tỷ lệ tăng của $r$.

### Đánh đổi bộ nhớ đặc biệt thuận lợi

| $r$ | Sai số | Bộ nhớ | So với $r=2$ |
|---:|---:|---:|---|
| 2 | 11,92% | 11.412 B | — |
| 16 | 1,29% | 14.052 B | sai số **giảm 9,2×**, bộ nhớ chỉ **tăng 1,23×** |

Số bucket tăng 7,6× (21 → 159) nhưng bộ nhớ chỉ tăng 1,23×, vì trong Python phần lớn dung lượng là **overhead của đối tượng `deque` theo tầng**, không phải bản thân các timestamp. Đây là chi tiết cài đặt cụ thể của Python, sẽ nêu rõ trong báo cáo để tránh khái quát hóa sai sang ngôn ngữ khác.

**Khuyến nghị vận hành:** với hệ thống thật, chọn $r = 8$ hoặc $16$ thay vì mặc định $r = 2$ — sai số dưới 2,5% với chi phí bộ nhớ gần như không đổi.

---

## 4. E3 — BỘ NHỚ THEO $N$

| $N$ | #bucket | Python (byte) | Lý thuyết (byte) | Cửa sổ đầy (byte) | Tiết kiệm |
|---:|---:|---:|---:|---:|---:|
| 10.000 | 13 | 8.908 | 57 | 1.250 | **0,1×** ⚠️ |
| 100.000 | 17 | 9.780 | 86 | 12.500 | 1,3× |
| 1.000.000 | 21 | 11.412 | 121 | 125.000 | 11,0× |
| 5.000.000 | 24 | 13.016 | 149 | 625.000 | **48,0×** |

### 4.1. Tốc độ tăng trưởng — cận được xác nhận

| Đại lượng | Hệ số tăng khi $N$: $10^4 \to 5\times10^6$ |
|---|---:|
| $N$ | **500×** |
| Bộ nhớ đo thật | **1,46×** |
| Dự đoán theo $\log^2 N$ | 2,80× |
| Nếu tuyến tính theo $N$ | 500× |

Bộ nhớ tăng **1,46×** khi $N$ tăng **500×** — chẳng những dưới tuyến tính mà còn **tốt hơn cả cận $\log^2 N$**.

**Vì sao tốt hơn cận:** cận $O(\log^2 N)$ giả định cửa sổ có thể chứa tới $N$ bit 1. Thực tế khu vực 161 chỉ có 242.893 chuyến trong cả tháng, nên số bucket bị chặn bởi $\log_2(\text{số bit 1})$ chứ không bởi $\log_2 N$. Với $N = 5\times10^6$, cửa sổ chứa ~62.000 bit 1 thay vì 5 triệu.

Đây là ví dụ cho thấy **cận trên là cận trên**: dữ liệu thưa thực tế cho kết quả tốt hơn trường hợp xấu nhất trong lý thuyết.

### 4.2. Khoảng cách giữa Python và lý thuyết

| $N$ | Lý thuyết | Python | Bội số |
|---:|---:|---:|---:|
| 10.000 | 57 B | 8.908 B | 156× |
| 5.000.000 | 149 B | 13.016 B | 87× |

Khoảng cách ~100× là **chi phí đối tượng của Python**: mỗi timestamp là một `int` 28 byte thay vì $\log_2 N \approx 20$ bit, và mỗi `deque` tốn ~500 byte overhead cố định.

Cận $O(\log^2 N)$ nói về **độ tăng trưởng**, không hứa hằng số nhỏ. Bội số **giảm dần** (156× → 87×) khi $N$ tăng, xác nhận rằng phần overhead cố định bị pha loãng dần.

### 4.3. 🔴 Điểm giao — phát hiện cần báo cáo trung thực

**Ở $N = 10.000$, DGIM tốn 8.908 byte trong khi lưu cửa sổ đầy đủ dạng mảng bit chỉ tốn 1.250 byte. DGIM tệ hơn 7 lần.**

Điểm hòa vốn nằm quanh $N \approx 10^5$ (tỷ lệ 1,3×). Chỉ từ $N \ge 10^6$ ưu thế mới rõ rệt (11×), và đạt 48× ở $N = 5\times10^6$.

**Ý nghĩa:** DGIM **không** là lựa chọn đúng cho mọi bài toán cửa sổ trượt. Nó chỉ thắng khi cửa sổ đủ rộng để chi phí tiệm cận vượt qua chi phí cố định. Với CityFlow — nơi $N = 10^6$ là cấu hình vận hành và có 535 luồng song song — DGIM nằm đúng vùng có lợi.

Nhưng nếu ai đó áp dụng DGIM cho cửa sổ 10.000 phần tử, họ sẽ **mất** bộ nhớ chứ không tiết kiệm. Đây là loại kết luận mà một báo cáo chỉ đo ở một giá trị $N$ duy nhất sẽ bỏ sót.

---

## 5. ĐỐI CHIẾU VỚI TIÊU CHÍ THÀNH CÔNG *(Phase 4 §1.4)*

| Chỉ số | Ngưỡng đặt ra | Đo thật | |
|---|---|---|:--:|
| Sai số DGIM ($r = 2$) | ≤ 50% | **max 46,33%, TB 11,9%** | ✅ |
| Sai số DGIM ($r = 8$) | ≤ 10% | **2,43%** | ✅ vượt xa |
| Bộ nhớ DGIM/luồng | $O(\log^2 N)$ | **tăng 1,46× khi $N$ tăng 500×** | ✅ |

> Ghi chú: Phase 4 §1.4 ghi ngưỡng cho "$r = 1$". Cấu hình đó đã được chứng minh là **suy biến** và bị từ chối ở constructor (xem §6). Ngưỡng được diễn giải lại cho $r = 2$ — cấu hình nhỏ nhất hợp lệ.

---

## 6. PHÁT HIỆN PHỤ — $r = 1$ LÀ CẤU HÌNH SUY BIẾN

Trong quá trình viết unit test, cấu hình $r = 1$ cho sai số **414%** ($N = 2000$, mật độ 0,05: đáp án đúng 100, ước lượng 514).

**Nguyên nhân:** slide tr.64 mô tả sơ đồ *"duy trì $r$ **hoặc** $r-1$ bucket mỗi kích thước"*, nên $r = 1$ nghĩa là "0 hoặc 1 bucket mỗi cỡ". Khi mỗi cỡ chỉ được giữ một bucket, mọi bucket bị gộp ngay khi có bạn cùng cỡ, tạo **phản ứng dây chuyền dồn toàn bộ luồng vào một bucket khổng lồ**. Bucket gộp kế thừa timestamp của bit 1 **gần nhất**, nên nó không bao giờ hết hạn dù chứa các bit 1 đã ra khỏi cửa sổ từ lâu.

Quan sát trực tiếp: bucket cỡ **1024** mang timestamp **19985** trong khi cửa sổ chỉ bắt đầu từ vị trí 18000.

Với $r \ge 2$ luôn tồn tại "bucket em" giữ lại timestamp mới, nên bucket gộp mang timestamp **cũ** và hết hạn đúng lúc.

**Xử lý:** constructor từ chối $r < 2$ kèm thông báo giải thích. Có unit test riêng (`test_r_below_2_is_rejected`).

---

## 7. GHI CHÚ VỀ MỘT ĐIỂM KHÔNG NHẤT QUÁN TRONG SLIDE

Slide tr.63 minh họa: trạng thái `1 1 2 4` nhận thêm bit 1 → `1 1 1 2 4` → gộp 2 bucket cỡ 1 cũ nhất → `1 2 2 4`, rồi viết tiếp *"Có 2 bucket cỡ 2: tiếp tục gộp đệ quy thành 1 bucket cỡ 4"*.

Nhưng bất biến nêu ở tr.60 là *"Tối đa **1 hoặc 2** bucket cùng kích thước"* — nên trạng thái `1 2 2 4` là **hợp lệ** và không cần gộp tiếp.

Cài đặt này theo **bất biến tr.60** (gộp khi số bucket vượt $r$). Với $r = 2$, phép gộp tầng tiếp theo chỉ kích hoạt khi xuất hiện bucket cỡ 2 **thứ ba**. Unit test `test_slide_p63_merge_cascade` kiểm chứng cả hai tình huống.

---

## 8. KẾT LUẬN

**Ba cận lý thuyết trên slide đều được xác nhận bằng dữ liệu thật quy mô lớn**, không phải bằng luồng ngẫu nhiên mô phỏng.

Kết quả có giá trị nhất là **E2**: tích `sai số × r` giữ gần như hằng số qua 8 lần thay đổi $r$ — một xác nhận trực tiếp và sạch sẽ cho quan hệ $O(1/r)$.

Ba phát hiện đi kèm đều đáng đưa vào báo cáo:
1. **Điểm giao bộ nhớ** — DGIM tệ hơn cửa sổ đầy đủ khi $N \lesssim 10^5$
2. **$r = 1$ suy biến** — hệ quả trực tiếp của cách phát biểu "$r$ hoặc $r-1$" trên slide
3. **Sai lầm harness** — kiểm chứng thuật toán luồng đòi hỏi harness cũng tôn trọng ngữ nghĩa luồng

**Khuyến nghị cấu hình vận hành cho CityFlow:** $r = 8$ (sai số 2,43%, bộ nhớ 13.268 byte/luồng) thay vì mặc định $r = 2$.

---

*Bước tiếp theo: DGIM mở rộng cho tổng số nguyên (Q2) và kiểm chứng giả thuyết H1 — thực nghiệm E4.*
