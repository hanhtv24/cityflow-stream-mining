# CHƯƠNG 5. THỰC NGHIỆM

*(Chương này tương ứng pha Evaluation của CRISP-DM. Toàn bộ thực nghiệm chạy trên 19.663.928 sự kiện thật, đã qua xác minh chất lượng ở Chương 3. Tài liệu nguồn chi tiết: [`05`](../05_KET_QUA_E1_E3.md), [`06`](../06_KET_QUA_E4_GIA_THUYET_H1.md), [`07`](../07_KET_QUA_E5_E6.md), [`08`](../08_KET_QUA_E7.md), [`09`](../09_KET_QUA_MINING.md).)*

## 5.1. Phương pháp luận thực nghiệm chung

Mỗi thực nghiệm tuân theo một khuôn mẫu: (1) xác định cận lý thuyết cần kiểm chứng, (2) thiết kế oracle độc lập tính giá trị chính xác, (3) đo sai số/bộ nhớ/thời gian trên dữ liệu thật, (4) đối chiếu với cận lý thuyết. Một sai lầm phương pháp luận đã xảy ra và được sửa trong quá trình thực nghiệm đầu tiên (E1): phát lại toàn bộ luồng vào sketch trước khi truy vấn tại một mốc thời gian quá khứ cho sai số vô lý (129.311%) — nguyên nhân là lịch sử gộp bucket bị dữ liệu tương lai làm sai lệch. Khắc phục bằng cách phát lại **một lượt**, tôn trọng đúng ngữ nghĩa luồng: tại mỗi mốc truy vấn, sketch chỉ được thấy đúng các sự kiện đã xảy ra tới thời điểm đó.

## 5.2. E1–E3: Xác nhận cận lý thuyết của DGIM

| Thực nghiệm | Cận lý thuyết | Kết quả đo được |
|---|---|---|
| E1 | Sai số $\le 50\%$ (với $r=2$) | **0/3.178** phép truy vấn vi phạm; sai số trung bình 6,9–13,8%, tối đa 46,3% |
| E2 | Sai số $\propto O(1/r)$ | Tích (sai số $\times r$) dao động 19,4–23,8% qua $r\in\{2,4,8,16\}$ — gần như hằng số |
| E3 | Bộ nhớ $O(\log^2 N)$ | $N$ tăng 500 lần, bộ nhớ chỉ tăng 1,46 lần |

**Kết quả nổi bật (E2):** tăng $r$ từ 2 lên 16 (gấp 8 lần) làm sai số giảm từ 11,92% xuống 1,29% (giảm 9,2 lần) — khớp chặt với quan hệ $O(1/r)$ — trong khi bộ nhớ chỉ tăng 1,23 lần. Khuyến nghị vận hành: $r=8$ thay vì mặc định $r=2$, đạt sai số 2,43% với chi phí bộ nhớ không đáng kể.

**Phát hiện phụ (E3):** ở $N=10^4$, DGIM tiêu tốn bộ nhớ **nhiều hơn** 7 lần so với lưu cửa sổ đầy đủ dạng mảng bit — điểm hòa vốn nằm quanh $N\approx10^5$. DGIM chỉ có lợi khi cửa sổ đủ rộng để vượt qua chi phí cố định của cấu trúc dữ liệu Python.

## 5.3. E4: Giả thuyết nghiên cứu — phân bổ ngân sách DGIM mở rộng

Tài liệu giảng dạy nêu cách mở rộng DGIM cho tổng số nguyên nhưng không đề cập cách phân bổ ngân sách bộ nhớ ($r_i$) giữa các luồng bit. Đồ án suy dẫn công thức tối ưu bằng nhân tử Lagrange, cực tiểu hóa sai số dự đoán $E \sim \sum_i \frac{2^i c_i}{2r_i}$ với ràng buộc tổng ngân sách cố định:

$$r_i \propto \sqrt{2^i \cdot c_i}$$

trong đó $c_i$ là tần suất bit 1 tại vị trí $i$ đo trên dữ liệu thật. Công thức này **không** đơn giản ưu tiên bit cao (trực giác thông thường) mà cân bằng giữa trọng số $2^i$ (tăng theo $i$) và tần suất $c_i$ (giảm theo $i$ vì giá trị lớn hiếm gặp).

**Kết quả kiểm chứng** (ngân sách $\sum r_i = 32$):

| Chiến lược phân bổ | Sai số trung bình | So với phân bổ đều |
|---|---:|---:|
| Đều ($r_i$ bằng nhau) | 2,119% | — |
| Ưu tiên bit cao (trực giác) | 2,377% | **tệ hơn 12,2%** |
| Theo công thức Lagrange | **1,615%** | **tốt hơn 23,8%** |

Phân rã sai số theo vị trí bit xác nhận: bit thứ 4 (không phải bit cao nhất) đóng góp 29,8% tổng sai số — trực giác "ưu tiên bit cao" bị bác bỏ bằng số liệu cụ thể. Giả thuyết được xác nhận ở dạng suy diễn từ lý thuyết, bác bỏ ở dạng trực giác thông thường — một kết quả khoa học đầy đủ hai chiều.

## 5.4. E5–E6: Flajolet-Martin và AMS

### 5.4.1. Flajolet-Martin (Q3)

Ground truth: 58.911 tuyến phân biệt trong tháng. Vì ước lượng $2^R$ luôn là lũy thừa của 2, cận sai số tốt nhất có thể của ước lượng đơn là 11,2% (do $2^{16}=65.536$ là lũy thừa 2 gần nhất).

**Phát hiện quan trọng:** sơ đồ tổng hợp mà tài liệu giảng dạy khuyến nghị (trung vị của các trung bình theo nhóm) chệch lên có hệ thống khoảng **2,3 lần** — một độ chệch ổn định qua nhiều bậc độ lớn, hiệu chỉnh được bằng hằng số. Hằng số hiệu chỉnh kinh điển $\varphi=0{,}77351$ của Flajolet & Martin (1985) **không áp dụng được** — nó được suy ra cho một biến thể thuật toán khác (stochastic averaging), áp dụng nhầm làm sai số tăng thêm thay vì giảm. Sau khi hiệu chuẩn lại đúng cách (riêng theo số hàm băm $m$) trên dữ liệu tổng hợp độc lập, sai số vượt qua cận 11,2% tại $m\ge128$, đạt 6,4% tại $m=256$.

### 5.4.2. AMS (Q4)

Ước lượng chính xác: sai số 7,1% tại $k=100$ biến, 3,0% tại $k=500$ — vượt xa ngưỡng đặt ra (≤20%).

**Nhưng tín hiệu yếu:** số bất ngờ tăng theo bình phương số sự kiện trong cửa sổ, nên khi chuẩn hóa loại bỏ hiệu ứng kích thước cửa sổ, tỷ lệ giữa cửa sổ "bất thường nhất" và cửa sổ trung bình giảm từ 5,0 lần (thô) xuống chỉ còn **2,7 lần** — xác nhận định lượng cho phát hiện định tính ở Chương 3 rằng phân phối khu vực NYC khá đồng đều, khiến chỉ số bất ngờ ở phạm vi toàn cục có khả năng phân biệt hạn chế. Kết quả này củng cố quyết định thiết kế coi tầng khai phá mẫu (Q6) là bắt buộc: nó trả lời câu hỏi "ở đâu, cùng với ai" mà AMS không trả lời được.

## 5.5. E7: Thông lượng và bộ nhớ hệ thống 535 luồng

Lần đo đầu tiên chỉ đạt 7.077 sự kiện/giây — thấp hơn mục tiêu (50.000/giây) bảy lần. Phân tích từng thành phần cho thấy nguyên nhân **không** nằm ở 535 luồng DGIM (chỉ chiếm 1,5% thời gian xử lý) mà ở Flajolet-Martin với $m=256$ hàm băm chạy tuần tự trong Python (chiếm 97,2% thời gian) — một minh chứng rằng tối ưu cục bộ (chọn $m$ lớn để giảm sai số ở E5) không tự động cho tối ưu toàn cục.

Khắc phục bằng vector hóa: gom cả lô sự kiện thành một phép toán mảng (numpy) duy nhất cho cả $m$ hàm băm, tận dụng tính chất **kết hợp và lũy đẳng** của phép lấy giá trị lớn nhất (max) — điều kiện đủ để xử lý theo lô mà không thay đổi kết quả (đã kiểm chứng khớp tuyệt đối với đường xử lý từng phần tử). Kết quả: thông lượng đạt **87.933 sự kiện/giây**, vượt mục tiêu, tăng tốc 12,4 lần.

**Bộ nhớ:** 5,66 MB cho toàn bộ 535 luồng (không kể mẫu Reservoir), so với 66,9 MB nếu lưu cửa sổ đầy đủ — tiết kiệm 11,8 lần. Tỷ lệ thấp hơn ước tính lý thuyết ban đầu do chi phí cố định của đối tượng Python, nhưng xu hướng tăng trưởng dưới tuyến tính được xác nhận.

## 5.6. E9–E11: Tầng khai phá mẫu

### 5.6.1. Điều chỉnh tham số rời rạc hóa

Ngưỡng phân vị mặc định 80% (Chương 4) tạo ra giỏ hàng quá dày (trung bình 44,4/257 item mỗi giỏ) — cơ sở dữ liệu trù mật khiến FP-Growth không hội tụ ở ngưỡng hỗ trợ thấp. Chuyển sang phân vị 90% (giỏ hàng trung bình 22,1 item) giải quyết được vấn đề — một minh chứng cho việc tham số thiết kế trên giấy cần kiểm chứng lại khi gặp dữ liệu thật.

### 5.6.2. FP-Growth so với Apriori

| Ngưỡng hỗ trợ | Số mẫu | FP-Growth | Apriori | Tăng tốc |
|---:|---:|---:|---:|---:|
| 10% | 11 | 0,018s | 0,157s | 8,5× |
| 7% | 355 | 0,868s | 78,99s | **91,0×** |
| 5% | 16.319 | 6,28s | 213,3s | 34,0× |

Cả hai thuật toán cho kết quả **giống hệt nhau** tuyệt đối ở mọi mức — kiểm chứng tính đúng đắn trực tiếp. Tại ngưỡng 5%, Apriori sinh 61.329 ứng viên cho 16.319 mẫu thật (tỷ lệ 3,8 ứng viên/mẫu) và thực hiện 181.750.272 phép kiểm tra hỗ trợ — số liệu định lượng cho ba điểm nghẽn lý thuyết đã nêu ở Chương 2.

### 5.6.3. Nén bằng mẫu đóng

Ở ngưỡng 5%, mẫu đóng nén còn 73,6% số lượng, mẫu cực đại nén còn 22,1% — kiểm chứng bằng thực nghiệm (không chỉ trích dẫn) rằng việc khôi phục lại từ tập đóng cho kết quả khớp tuyệt đối với tập gốc ở mọi mức đo được, xác nhận tính chất "nén không mất mát".

### 5.6.4. E10 — Bằng chứng thực nghiệm cho tính bất biến với giao dịch rỗng

Đây là kết quả sạch nhất của toàn bộ đồ án. Thêm dần giao dịch rỗng (tối đa gấp 100 lần kích thước dữ liệu gốc) vào một luật khảo sát thật (Midtown Center ⇒ Midtown East):

| Nhóm độ đo | Biến thiên đo được |
|---|---:|
| Sáu độ đo bất biến (Confidence, All-Confidence, Coherence, Cosine, Kulczynski, Max-Confidence, Imbalance Ratio) | **đúng 0,0%** |
| Lift | 10.000% |
| $\chi^2$ | 10.259% |

Sáu độ đo bất biến giữ nguyên **chính xác tuyệt đối tới bốn chữ số thập phân**, trong khi Lift tăng 101 lần và $\chi^2$ tăng 104 lần. Kết quả này biến một khẳng định lý thuyết trừu tượng thành một minh chứng số học cụ thể trên dữ liệu giao thông thật quy mô lớn.

**Tương quan hạng bổ sung:** hệ số Spearman giữa Support và Kulczynski chỉ đạt $\rho=0{,}124$ — gần như không tương quan — xác nhận thực nghiệm cho nhận định lý thuyết rằng "luật phổ biến nhất" và "luật có quan hệ chặt nhất" là hai tiêu chí gần như độc lập.

## 5.7. E12: Kiểm định chéo tính đúng đắn

Cài đặt FP-Growth from scratch được đối chiếu với thư viện tham chiếu `mlxtend` trên ví dụ chuẩn của tài liệu giảng dạy và mười bộ dữ liệu ngẫu nhiên độc lập, ở nhiều mức ngưỡng hỗ trợ khác nhau. **Sai lệch bằng không** ở toàn bộ 20 phép kiểm chứng — điều kiện tiên quyết để mọi kết quả thực nghiệm khác được tin cậy.

## 5.8. Tổng hợp kiểm định đơn vị

Toàn bộ hệ thống được bảo vệ bởi **158 kiểm định đơn vị**, trong đó phần lớn tái hiện trực tiếp các ví dụ số cụ thể trong tài liệu giảng dạy (VD: ví dụ ước lượng DGIM = 6 và = 12 ở minh họa cửa sổ mũ, ví dụ AMS cho kết quả 55 trên luồng 15 phần tử, bài tập giáo viên giao về mô-men bậc 3) — vừa là kiểm định kỹ thuật, vừa là bằng chứng trực tiếp cho việc nhóm nắm vững nội dung bài giảng.
