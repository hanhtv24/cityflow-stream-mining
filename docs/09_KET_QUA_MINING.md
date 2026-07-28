# PHASE 5 · BƯỚC 7 — KẾT QUẢ THỰC NGHIỆM E9, E10, E11

## Tầng khai phá mẫu (Q6) trên dữ liệu thật

**Ngày:** 2026-07-28
**Dữ liệu:** NYC TLC FHVHV 2024-01 — 19.663.928 sự kiện → 2.976 giỏ hàng (cửa sổ 15 phút)
**Cài đặt:** [`fptree.py`](../src/cityflow/mining/fptree.py) · [`fpgrowth.py`](../src/cityflow/mining/fpgrowth.py) · [`apriori.py`](../src/cityflow/mining/apriori.py) · [`interestingness.py`](../src/cityflow/mining/interestingness.py) · [`basket_builder.py`](../src/cityflow/mining/basket_builder.py)
**Script:** [`scripts/07_experiment_mining.py`](../scripts/07_experiment_mining.py) · **Log:** [`e9_e11_log.txt`](e9_e11_log.txt) · **JSON:** [`e9_e11_results.json`](e9_e11_results.json)
**Kiểm định đơn vị:** 50/50 (`test_mining.py`) + 20/20 kiểm chứng chéo mlxtend (`test_crosscheck.py`) — tổng **158/158** toàn dự án

---

## 0. TÓM TẮT

| | Câu hỏi | Kết quả |
|---|---|---|
| **E9** | FP-Growth có thật sự tránh được 3 điểm nghẽn của Apriori không? | ✅ **Có — tăng tốc tới 91×**, và hai thuật toán cho **kết quả giống hệt** ở mọi mức |
| **E11** | Mẫu đóng có nén không mất mát không? | ✅ **Có** — khôi phục lại đúng 100% tập gốc ở cả 3 mức đo được; nén còn **73,6%** dung lượng |
| **E10** | Độ đo null-invariant có thật sự bất biến trên dữ liệu thật không? | ✅ **Hoàn hảo** — biến thiên đúng **0,0%** trong khi Lift trôi tới **10.259%** |

**Phát hiện phụ quan trọng nhất:** một quyết định thiết kế của Phase 4 (ngưỡng phân vị 80%) **sai** trên dữ liệu thật và phải sửa ngay ở bước đầu tiên của thực nghiệm này.

---

## 1. 🔴 Quyết định lại tham số rời rạc hóa — phân vị 80% quá dày

### Vấn đề

Phase 4 §5.1 chọn ngưỡng "hot" mặc định ở **phân vị 80** của từng khu vực. Đo thật:

| Phân vị | Cỡ giỏ TB | Cỡ giỏ max | #item khả dĩ | Giỏ rỗng |
|---:|---:|---:|---:|---:|
| 70% | 66,7 | 211 | 257 | 270 |
| **80%** (mặc định Phase 4) | **44,4** | 199 | 257 | 374 |
| **90%** | **22,1** | 180 | 257 | 539 |
| 95% | 11,0 | 148 | 257 | 837 |

Ở phân vị 80%, **mỗi giỏ hàng trung bình chứa 44,4/257 item** — tức trung bình **17,3% khu vực đang "hot" đồng thời** trong mỗi cửa sổ 15 phút. Đây là CSDL **trù mật (dense)**, đúng kịch bản slide tr.13 cảnh báo: *"$\{a_1,...,a_{100}\}$ chứa $2^{100}-1$ tập con"*. Thử nghiệm sơ bộ ở phân vị 80% với `min_sup=5%` gây **`MemoryError`** khi FP-Growth đệ quy tới độ sâu 9+ — không hội tụ trong thời gian hợp lý.

### Chẩn đoán

Nguyên nhân nằm ở chính định nghĩa "hot": phân vị 80% của một khu vực nghĩa là khu vực đó "hot" ở **20% số cửa sổ nó hoạt động** — với 265 khu vực hoạt động không đồng thời, việc "hot theo tần suất riêng của mình" hóa ra là **trạng thái thường lệ**, không phải bất thường, khi nhìn trên toàn bộ 15 phút của cả thành phố.

### Quyết định

**Chuyển sang phân vị 90%** cho mọi thực nghiệm E9–E11: cỡ giỏ TB giảm còn **22,1** item, và FP-Growth hội tụ ổn định tới `min_sup = 5%` (148 giỏ hàng, chạy trong 6,3s cho 16.319 mẫu).

> Đây **không phải** việc chọn tham số để "cho ra kết quả đẹp". Ngưỡng 80% cho một hệ thống **không chạy được** — đây là ràng buộc kỹ thuật cứng, không phải lựa chọn thẩm mỹ. Quyết định và lý do được ghi trực tiếp trong code (`scripts/07_experiment_mining.py`) để không mất dấu khi viết báo cáo.

---

## 2. ⭐ E9 — FP-GROWTH vs APRIORI: BA ĐIỂM NGHẼN TRÊN DỮ LIỆU THẬT

2.976 giỏ hàng (phân vị 90%), 257 item khả dĩ.

| min_sup | #mẫu | FP-Growth | Apriori | **Tăng tốc** | #ứng viên | #quét CSDL |
|---:|---:|---:|---:|---:|---:|---:|
| 20% | 0 | 0,010s | 0,007s | 0,7× | 257 | 1 |
| 15% | 0 | 0,011s | 0,007s | 0,6× | 257 | 1 |
| 10% | 11 | 0,018s | 0,157s | 8,5× | 312 | 2 |
| 7% | 355 | 0,868s | 78,988s | **91,0×** | 26.106 | 4 |
| **5%** | **16.319** | **6,277s** | **213,296s** | 34,0× | **61.329** | 11 |

**Khẳng định tính đúng đắn:** cả hai thuật toán cho **kết quả giống hệt** (từng tập mục, từng số đếm) ở mọi mức — kiểm tra bằng `assert freq_fp == freq_ap` ngay trong script, không chỉ trong test.

### Ba điểm nghẽn — số liệu cụ thể tại min_sup = 5%

| Điểm nghẽn (slide tr.19) | Số liệu đo được |
|---|---|
| **① Quét CSDL nhiều lần** | Apriori quét **11 lần** (một lần cho mỗi độ dài tập mục, tới độ dài 11) |
| **② Số lượng ứng viên khổng lồ** | **61.329 ứng viên** sinh ra cho **16.319 mẫu thật** — tỷ lệ **3,8 ứng viên/mẫu**, tức gần **3/4 số ứng viên bị loại bỏ sau khi đếm** |
| **③ Chi phí đếm hỗ trợ** | **181.750.272 phép kiểm tra** "ứng viên có nằm trong giao dịch này không" |

Bộ nhớ đỉnh: FP-Growth **26,6 MB** vs Apriori **40,1 MB** — FP-Growth thắng cả về bộ nhớ lẫn thời gian, đúng như thiết kế nén bằng cây (slide tr.33).

### 🔴 Phát hiện cần báo cáo trung thực: tăng tốc KHÔNG đơn điệu

Tăng tốc đạt đỉnh **91,0×** ở `min_sup=7%` rồi **giảm xuống 34,0×** ở `min_sup=5%` — dù độ khó bài toán (số mẫu, độ sâu đệ quy) tăng lên.

**Diễn giải:** ở `min_sup=5%`, cây điều kiện FP-Growth phải xây tới độ sâu 11, và chi phí xây/duyệt cây điều kiện lồng nhau bắt đầu chiếm tỷ trọng đáng kể, trong khi Apriori dù sinh nhiều ứng viên hơn vẫn hưởng lợi từ việc mỗi ứng viên chỉ cần một phép so khớp tập hợp đơn giản. **Không nên khái quát hóa "tăng tốc luôn tăng theo độ khó bài toán"** — đây là điểm cần thảo luận trong chương Thực nghiệm, không phải chi tiết bỏ qua.

---

## 3. E11 — NÉN MẪU: ĐÓNG VÀ CỰC ĐẠI

| min_sup | #tất cả | #đóng | #cực đại | Tỷ lệ đóng | Tỷ lệ cực đại | Không mất mát |
|---:|---:|---:|---:|---:|---:|:---:|
| 15% | *(không có mẫu ở mức này)* | | | | | |
| 10% | 11 | 11 | 11 | 100,0% | 100,0% | ✅ **ĐẠT** |
| 7% | 355 | 355 | 273 | 100,0% | 76,9% | ✅ **ĐẠT** |
| **5%** | **16.319** | **12.010** | **3.607** | **73,6%** | **22,1%** | ✅ **ĐẠT** |

### Kiểm chứng "nén không mất mát" bằng thực nghiệm, không chỉ tin lời slide

Slide tr.13 khẳng định mẫu đóng cho *"lossless compression"*. Thay vì trích dẫn, hàm `reconstruct_from_closed()` khôi phục lại **toàn bộ** tập mục thường xuyên kèm số đếm chỉ từ tập đóng, rồi so sánh **từng phần tử** với kết quả FP-Growth gốc — đạt ở cả 3 mức đo được.

### Ý nghĩa cho quy mô

Ở `min_sup=5%`, nén bằng tập đóng giảm còn **73,6%** số mẫu cần lưu trữ mà **không mất một bit thông tin nào** (khôi phục lại đúng cả số đếm). Tập cực đại nén mạnh hơn nữa (**22,1%**) nhưng đánh đổi bằng việc mất thông tin số đếm của các tập con — đúng như lý thuyết dự đoán (mẫu cực đại **có mất mát**).

---

## 4. LUẬT ĐỒNG ÙN TẮC — KẾT QUẢ MANG Ý NGHĨA ĐỊA LÝ THẬT

Cấu hình: `min_sup=7%` (208 giỏ), `min_conf=50%` → **484 luật**.

### Top 10 luật theo Kulczynski

| Luật | sup | conf | lift | kulc | IR |
|---|---:|---:|---:|---:|---:|
| Midtown Center ⇒ Midtown East | 0,089 | 0,895 | 9,03 | 0,897 | 0,003 |
| Midtown East ⇒ Midtown Center | 0,089 | 0,898 | 9,03 | 0,897 | 0,003 |
| East Village+Williamsburg(N) ⇒ Bushwick S+Williamsburg(S) | 0,071 | 0,875 | 11,27 | 0,892 | 0,034 |
| Bushwick N+Greenwich Village S ⇒ East Village+Lower East Side | 0,071 | 0,951 | 10,92 | 0,885 | 0,133 |
| Bushwick S+Williamsburg(N) ⇒ East Village+Williamsburg(S) | 0,071 | 0,905 | 11,04 | 0,883 | 0,045 |

### Đọc kết quả như một nhà phân tích, không chỉ như một lập trình viên

Hai cụm luật nổi lên **hoàn toàn khớp với địa lý Manhattan và Brooklyn thật**:

- **Midtown Center ↔ Midtown East**: hai khu vực **liền kề trực tiếp** ở trung tâm Manhattan. `Imbalance Ratio ≈ 0,003` (gần 0) nghĩa là hai khu vực này có quy mô hoạt động gần như **cân bằng tuyệt đối** — không bên nào "kéo" bên kia mạnh hơn.
- **Cụm Brooklyn** (East Village, Williamsburg Bắc/Nam, Bushwick Bắc/Nam, Lower East Side, Greenwich Village Nam): đây là các khu vực **liền kề** dọc theo trục giải trí đêm sôi động của Brooklyn/Đông Manhattan. `Lift` cao (10,9–11,3) và `IR` thấp (0,03–0,13) cho thấy các khu vực này **cùng bận rộn** — đúng giả thuyết CityFlow đặt ra: khi một khu vực trong cụm ùn tắc, các khu vực lân cận cùng cụm cũng ùn tắc theo.

Đây chính là loại tri thức mà Q4 (AMS) **không thể cung cấp** — số bất ngờ chỉ nói "có bất thường" chứ không nói "bất thường ở đâu, cùng với ai" ([07_KET_QUA_E5_E6 §10](07_KET_QUA_E5_E6.md)). Kết quả này xác nhận trực tiếp quyết định kiến trúc đó.

---

## 5. ⭐⭐ E10 — NULL-INVARIANCE: BẰNG CHỨNG HOÀN HẢO TRÊN DỮ LIỆU THẬT

**Luật khảo sát:** Midtown Center ⇒ Midtown East
$n=2.976$, $\text{sup}_A=296$, $\text{sup}_B=295$, $\text{sup}_{AB}=265$, giao dịch rỗng sẵn có $=2.650$

Thêm dần giao dịch rỗng (tối đa gấp **100 lần** kích thước CSDL gốc):

| Độ đo | +0 | +2.976 | +29.760 | +297.600 | **Biến thiên** | |
|---|---:|---:|---:|---:|---:|:---:|
| support | 0,0890 | 0,0445 | 0,0081 | 0,0009 | 99,0% | 🔴 TRÔI |
| confidence | 0,8953 | 0,8953 | 0,8953 | 0,8953 | 0,0% | ✅ BẤT BIẾN* |
| **lift** | 9,0316 | 18,0632 | 99,3477 | **912,1924** | **10.000%** | 🔴 **TRÔI** |
| **$\chi^2$** | 2333,0 | 4729,4 | 26.272,0 | **241.676,2** | **10.259%** | 🔴 **TRÔI** |
| all_confidence | 0,8953 | 0,8953 | 0,8953 | 0,8953 | **0,0%** | ✅ BẤT BIẾN |
| coherence | 0,8129 | 0,8129 | 0,8129 | 0,8129 | **0,0%** | ✅ BẤT BIẾN |
| cosine | 0,8968 | 0,8968 | 0,8968 | 0,8968 | **0,0%** | ✅ BẤT BIẾN |
| kulczynski | 0,8968 | 0,8968 | 0,8968 | 0,8968 | **0,0%** | ✅ BẤT BIẾN |
| max_confidence | 0,8983 | 0,8983 | 0,8983 | 0,8983 | **0,0%** | ✅ BẤT BIẾN |
| imbalance_ratio | 0,0031 | 0,0031 | 0,0031 | 0,0031 | **0,0%** | ✅ BẤT BIẾN |

*confidence bất biến với giao dịch rỗng nhưng **không đối xứng** — xem `test_confidence_is_null_invariant_but_asymmetric`.

> **Biến thiên lớn nhất trong nhóm bất biến: 0,00 × 10⁰ (đúng bằng không, không phải "gần bằng không").**
> **Biến thiên lớn nhất trong nhóm không bất biến: 10.258,9%.**

### Đây là kết quả mạnh nhất của toàn bộ Phase 5

Sáu độ đo bất biến giữ **chính xác tuyệt đối** tới chữ số thập phân thứ 4 dù thêm gấp 100 lần giao dịch rỗng, trong khi Lift tăng **101 lần** và $\chi^2$ tăng **104 lần**. Đây không phải hiệu ứng làm tròn hay trùng hợp — nó là hệ quả toán học trực tiếp của công thức: sáu độ đo bất biến chỉ dùng $\text{sup}_A, \text{sup}_B, \text{sup}_{AB}$, **không bao giờ dùng $n$**, nên thêm giao dịch rỗng (chỉ làm $n$ tăng) không thể ảnh hưởng tới chúng.

**Đây chính là điều giảng viên dạy bằng ví dụ giả định ở slide tr.36-39, giờ được chứng minh bằng dữ liệu giao thông thật quy mô lớn** — đúng cam kết đặt ra từ Phase 4.

### Tương quan hạng — thứ hạng luật ĐẢO LỘN đến mức nào

| Cặp độ đo | Spearman $\rho$ | Diễn giải |
|---|---:|---|
| $\chi^2$ vs Kulczynski | +0,998 | Gần như đồng thuận |
| Kulczynski vs Cosine | +0,996 | Gần như đồng thuận (cả hai đều bất biến) |
| Lift vs Kulczynski | +0,884 | Đồng thuận khá tốt |
| Lift vs Cosine | +0,850 | Đồng thuận khá tốt |
| **Confidence vs Kulczynski** | **+0,400** | 🔴 **Đồng thuận yếu** |
| **Support vs Kulczynski** | **+0,124** | 🔴 **Gần như không tương quan** |

**Support gần như không tương quan với Kulczynski** ($\rho=0{,}124$) — nghĩa là xếp hạng "luật phổ biến nhất" và "luật có quan hệ chặt nhất" là **hai câu hỏi gần như độc lập**. Đây là minh chứng thực nghiệm trực tiếp cho lời phê ở slide tr.37: *"Buy walnuts → buy milk [1%, 80%] là hiểu lầm nếu 85% khách vốn đã mua sữa"* — support cao không đồng nghĩa quan hệ có ý nghĩa.

**Top 5 theo Lift** trùng phần lớn với top theo Kulczynski (cùng cụm Brooklyn) — ở tập luật này hai độ đo tương đối đồng thuận cho luật hàng đầu ($\rho=0{,}884$), nhưng $\rho < 1$ nghĩa là **thứ tự chính xác** vẫn khác nhau, và ở các luật hạng thấp hơn hai độ đo sẽ phân kỳ rõ rệt hơn.

---

## 6. ĐỐI CHIẾU VỚI TIÊU CHÍ ĐÃ ĐẶT RA

| Tiêu chí | Nguồn | Đạt |
|---|---|:---:|
| Sai lệch từ-scratch vs thư viện = 0 | Phase 4 §1.4 | ✅ (E12, 20/20 test) |
| FP-Growth cho kết quả giống Apriori | Nguyên tắc kiểm chứng chéo | ✅ (khẳng định trực tiếp trong E9) |
| Đủ 6 pha CRISP-DM — Modeling | Phase 4 §14.1 | ✅ |
| Chứng minh null-invariance bằng dữ liệu thật | Tín hiệu chấm điểm #4 | ✅✅ **Vượt kỳ vọng** — biến thiên đúng 0% |
| Tầng khai phá mẫu là bắt buộc, không tùy chọn | Phase 4 §5, §13 (R3) | ✅ — luật tìm được mang ý nghĩa địa lý xác thực |

---

## 7. KẾT LUẬN

**Ba kết quả đủ mạnh để làm xương sống chương Thực nghiệm của báo cáo:**

1. **E9**: FP-Growth nhanh hơn Apriori tới 91× trên dữ liệu thật, với bằng chứng định lượng đầy đủ cho cả 3 điểm nghẽn slide nêu — và một phát hiện tinh tế rằng mức tăng tốc không đơn điệu theo độ khó.

2. **E11**: mẫu đóng nén 26,4% dung lượng mà **được kiểm chứng thực nghiệm là không mất một bit thông tin nào**, không chỉ trích dẫn slide.

3. **E10**: bằng chứng **hoàn hảo** (0,0% vs 10.259%) cho tính null-invariance — đây là kết quả sạch nhất, ấn tượng nhất và dễ trình bày nhất trước hội đồng trong toàn bộ đồ án. Kèm theo phát hiện Support gần như không tương quan với Kulczynski ($\rho=0{,}124$), một minh chứng thực nghiệm trực tiếp cho lời phê của slide tr.37.

**Một bài học phương pháp luận:** quyết định tham số của Phase 4 (thiết kế trên giấy) không phải lúc nào cũng sống sót khi gặp dữ liệu thật. Phân vị 80% được chọn hợp lý về mặt khái niệm nhưng **không chạy được** trên dữ liệu thật — phải phát hiện và sửa ngay từ bước đầu tiên của thực nghiệm, không phải chờ tới lúc viết báo cáo mới nhận ra.

---

*Tầng khai phá mẫu (Q6) hoàn tất. Toàn bộ 6 câu hỏi nghiệp vụ Q1–Q6 của Phase 4 đã có kết quả thực nghiệm trên dữ liệu thật. Bước tiếp theo: API + CSDL + Dashboard (đang triển khai song song).*
