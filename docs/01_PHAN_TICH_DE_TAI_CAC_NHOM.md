# PHASE 2 — PHÂN TÍCH ĐỀ TÀI CÁC NHÓM KHÁC

**Phạm vi:** 16 đề tài đã đăng ký (nhóm 1–14, 16, 17). Nhóm 15 (nhóm ta) chưa đăng ký.
**Nguồn dữ liệu:** `Nhóm BTL Môn Khai Phá Dữ Liệu.xlsx` — cột đề tài là **văn bản tự do do sinh viên tự khai**.
**Phiên bản:** Phase 2 — 2026-07-27

---

## 0. PHƯƠNG PHÁP & GIỚI HẠN CỦA PHÂN TÍCH

### 0.1. ⚠️ Ranh giới giữa dữ kiện và suy luận

Bảng đăng ký **chỉ có tên đề tài** — không có đề cương, không có mô tả dataset, không có danh sách thuật toán chi tiết. Do đó:

| Loại thông tin | Nguồn | Độ tin cậy |
|---|---|---|
| Tên đề tài, thành viên, mã HV | Trích trực tiếp từ file Excel | ✅ **Dữ kiện** |
| Thuật toán được nêu **đích danh** trong tên đề tài | Trích trực tiếp | ✅ **Dữ kiện** |
| Thuật toán **không nêu tên** | Suy đoán từ bài toán + slide đã học | ⚠️ **[SUY LUẬN]** |
| Dataset (14/16 nhóm không nêu) | Suy đoán từ domain + dataset công khai phổ biến | ⚠️ **[SUY LUẬN]** |
| Điểm mạnh / điểm yếu | Đánh giá học thuật dựa trên bài toán và thuật toán | 🔍 **Nhận định chuyên môn** |

Mọi ô đã suy đoán đều được đánh dấu **[SL]**. Tôi không bịa ra dataset hay thuật toán mà nhóm bạn không nêu.

### 0.2. Thang đo khả năng trùng lặp

| Mức | Ký hiệu | Định nghĩa | Hệ quả cho nhóm 15 |
|---|---|---|---|
| Rất cao | 🔴 ≥75% | Cùng thuật toán **và** cùng bài toán **và** cùng domain | Tuyệt đối tránh |
| Cao | 🟠 50–75% | Cùng thuật toán **và** cùng bài toán, khác domain/dataset | Tránh |
| Trung bình | 🟡 25–50% | Cùng nhóm thuật toán, khác bài toán | Chỉ chọn nếu có khác biệt phương pháp luận rõ rệt |
| Thấp | 🟢 <25% | Khác cả thuật toán lẫn bài toán | An toàn |

### 0.3. Bốn tiêu chí đánh giá học thuật (dùng nhất quán cho cả 16 nhóm)

1. **Độ phù hợp syllabus** — có dùng thuật toán được dạy làm lõi không?
2. **Tính đúng đắn phương pháp luận** — thuật toán có phù hợp với bài toán không? (đây là chỗ nhiều nhóm mắc lỗi)
3. **Khả năng đánh giá định lượng** — có ground truth để đo không?
4. **Sản phẩm & tính mới** — có hệ thống chạy được không, có gì vượt slide không?

---

## 1. BẢNG TỔNG HỢP 16 ĐỀ TÀI

*(Bảng nén — phân tích chi tiết từng nhóm ở §2)*

| Nhóm | SL | Đề tài (rút gọn) | Hướng NC | Dataset | Thuật toán | Phù hợp syllabus | Trùng lặp cao nhất |
|:---:|:--:|---|---|---|---|:---:|---|
| 1 | 3 | Apriori/FP-Growth khai phá luật kết hợp dữ liệu mua hàng | FPM cổ điển | Không nêu **[SL]** Online Retail/Groceries | Apriori, FP-Growth | ✅ Cao | 🔴 vs **16** |
| 2 | 3 | MinHash & LSH gợi ý phim MovieLens | LSH → Recommendation | **MovieLens** (nêu rõ) | MinHash, LSH | ✅ Cao | 🟡 vs 11, 13 |
| 3 | 3 | Streaming — cổng phát hiện Spam/IP độc hại real-time | Stream filtering | Không nêu **[SL]** CIC-IDS/log tự sinh | **[SL]** Bloom Filter (+FM?) | ✅ Cao | 🟠 vs **14** |
| 4 | 3 | Streaming (FM, AMS, Bloom) phát hiện đột biến chủ đề tin tức | Stream moments / burst | Không nêu **[SL]** RSS/GDELT/AG News | Flajolet-Martin, AMS, Bloom | ✅ **Rất cao** | 🟡 vs 3, 7 |
| 5 | 3 | RFM + K-means + Apriori bán lẻ trực tuyến | Customer analytics lai | Không nêu **[SL]** Online Retail II (UCI) | RFM, K-means, Apriori | ⚠️ **Một nửa** | 🟠 vs **1, 16** |
| 6 | 3 | Phát hiện cảnh bạo lực trong video (CNN + ML) | Computer Vision | Không nêu **[SL]** RWF-2000/Hockey Fight | CNN, ML classifier | ❌ **Không** | 🟢 |
| 7 | 3 | Streaming phát hiện khu vực ô nhiễm bất thường | Stream anomaly (IoT) | Không nêu **[SL]** OpenAQ/Beijing PM2.5 | Không nêu **[SL]** DGIM/AMS | ⚠️ Chưa rõ | 🟡 vs 3, 4 |
| 8 | 3 | GameRecommender — FPM + AR gợi ý game Steam | FPM → Recommendation | **Steam** (nêu domain) | Apriori/FP-Growth + AR | ✅ Cao | 🟡 vs 1, 16, 2 |
| 9 | 3 | Thu thập dữ liệu & thử nghiệm tìm kiếm bằng hình ảnh | CBIR | Tự thu thập (nêu rõ) | **Không nêu** | ❓ **Không xác định** | 🟢 |
| 10 | 3 | So sánh Apriori vs FP-Growth vs ECLAT (hiệu năng/bộ nhớ/scalability) | Benchmark thuật toán | Không nêu **[SL]** FIMI datasets | Apriori, FP-Growth, ECLAT | ✅ **Rất cao** | 🟡 "nuốt" phần benchmark của 1,5,8,12,16 |
| 11 | **2** | Shingling/MinHash/LSH phát hiện review gần trùng lặp | LSH near-duplicate | Không nêu **[SL]** Amazon/Yelp Reviews | Shingling, MinHash, LSH | ✅ Cao | 🔴 vs **13** |
| 12 | 3 | Apriori & FP-Growth dự báo dịch sốt xuất huyết từ khí hậu | FPM → Healthcare | Không nêu **[SL]** NOAA + số liệu ca bệnh | Apriori, FP-Growth | ✅ Cao (nhưng ⚠️ sai công cụ) | 🟡 vs 1, 16 |
| 13 | 3 | Phát hiện trùng lặp tài liệu học thuật quy mô lớn | LSH near-duplicate | Không nêu **[SL]** arXiv/CORE/S2ORC | Shingling, MinHash, LSH | ✅ Cao | 🔴 vs **11** |
| 14 | 3 | So sánh Bloom Filter vs Counting Bloom Filter | Benchmark cấu trúc DL | Không nêu **[SL]** luồng tổng hợp | Bloom Filter, Counting BF | ✅ Cao (hẹp) | 🟠 vs **3** |
| 16 | **2** | Luật kết hợp & Market-Basket phân tích hành vi mua sắm | FPM cổ điển | Không nêu | Không nêu tên cụ thể | ✅ Cao | 🔴 vs **1** |
| 17 | 3 | So sánh ML phân loại ảnh cháy (HOG + Color Histogram) | Computer Vision | Không nêu **[SL]** FIRE Dataset (Kaggle) | HOG, ColorHist + ML | ❌ **Không** | 🟢 vs lớp; 🟡 vs 6 |

---

## 2. PHÂN TÍCH CHI TIẾT TỪNG NHÓM

### 🅐 CỤM FREQUENT PATTERN MINING — 6 nhóm

---

#### **Nhóm 1** — Ứng dụng Apriori/FP-Growth khai phá luật kết hợp trong dữ liệu mua hàng

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Frequent Pattern Mining cổ điển trên giỏ hàng |
| **Dataset** | Không nêu. **[SL]** Online Retail (UCI), Groceries (R arules), Instacart |
| **Thuật toán** | Apriori, FP-Growth (nêu đích danh) |
| **Điểm mạnh** | Đúng trọng tâm chương A · Cực nhiều tài liệu tham khảo · Dễ triển khai đúng hạn · Rủi ro kỹ thuật gần bằng 0 |
| **Điểm yếu** | ① **Đề tài sách giáo khoa** — chính là ví dụ mở đầu của slide (beer & diaper), tính mới ≈ 0. ② Tên đề tài không nêu **bài toán nghiệp vụ** nào cần giải — chỉ là "ứng dụng thuật toán", thiếu Business Understanding. ③ Không nêu độ đo nào ngoài "luật kết hợp" ⇒ nguy cơ dừng ở support/confidence, đi ngược tín hiệu #4 của giảng viên. ④ Không có dấu hiệu của sản phẩm/giao diện. |
| **Trùng lặp** | 🔴 **Rất cao vs Nhóm 16** (gần như cùng đề tài, chỉ khác cách diễn đạt) · 🟠 Cao vs Nhóm 5 · 🟡 vs 8, 10, 12 |

---

#### **Nhóm 5** — Phân khúc khách hàng & khai phá hành vi mua sắm bán lẻ trực tuyến (RFM, K-means, Apriori)

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Customer Analytics lai — segmentation + association rules theo phân khúc |
| **Dataset** | Không nêu. **[SL]** Online Retail II (UCI) — gần như chắc chắn, vì cụm từ "bán lẻ trực tuyến" là cách dịch chuẩn của dataset này |
| **Thuật toán** | RFM scoring, K-means, Apriori |
| **Điểm mạnh** | ① **Gần Information Systems nhất trong cụm FPM** — RFM là công cụ CRM thực tế. ② Ý tưởng "sinh luật riêng cho từng phân khúc" là hướng đi hay hơn hẳn nhóm 1/16. ③ Có pipeline BI rõ ràng, dễ ra dashboard. |
| **Điểm yếu** | ① ⚠️ **RFM và K-means KHÔNG có trong bất kỳ slide nào** ⇒ ~2/3 đề tài nằm ngoài syllabus, Apriori chỉ đóng vai phụ. ② Trùng dataset & domain với nhóm 1 và 16. ③ K-means trên RFM là bài tập nhập môn — không thể hiện độ khó bậc thạc sĩ. |
| **Trùng lặp** | 🟠 **Cao vs Nhóm 1 và 16** (cùng dataset bán lẻ, cùng Apriori) |

---

#### **Nhóm 8** — GameRecommender: FPM & association rules gợi ý game Steam

| Mục | Nội dung |
|---|---|
| **Hướng NC** | FPM ứng dụng vào Recommendation System |
| **Dataset** | Steam (nêu domain). **[SL]** `steam-200k` hoặc Steam Reviews trên Kaggle |
| **Thuật toán** | Frequent pattern mining + association rules |
| **Điểm mạnh** | ① Domain **mới hơn hẳn** bán lẻ — tránh được cụm 1/5/16. ② Có sản phẩm rõ ràng (recommender có tên riêng "GameRecommender"). ③ Dataset thú vị, dễ demo trực quan. |
| **Điểm yếu** | ① **Association rules là kỹ thuật gợi ý thế hệ cũ**, thua xa collaborative filtering / matrix factorization — reviewer sẽ hỏi "vì sao không dùng CF?". ② Đánh giá recommender cần Precision@K / NDCG@K, nhưng luật kết hợp **không sinh ra ranking tự nhiên** — phải chế thêm heuristic, dễ bị chê thiếu chặt chẽ. ③ Thư viện game Steam có **long tail cực nặng** ⇒ min_sup phải rất thấp ⇒ bùng nổ số pattern (đúng điểm nghẽn #2 của Apriori). |
| **Trùng lặp** | 🟡 vs 1, 16 (cùng AR) · 🟡 vs 2 (cùng bài toán recommendation) |

---

#### **Nhóm 10** — Phân tích so sánh Apriori, FP-Growth và ECLAT: hiệu năng, bộ nhớ, khả năng mở rộng

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Benchmark thực nghiệm thuật toán |
| **Dataset** | Không nêu. **[SL]** Bộ chuẩn FIMI (T10I4D100K, chess, mushroom, retail, kosarak) |
| **Thuật toán** | Apriori, FP-Growth, ECLAT |
| **Điểm mạnh** | ① **Bám sát nhất nội dung slide** — đo đúng 3 điểm nghẽn Apriori mà giảng viên nêu (số lần quét, số candidate, chi phí đếm support). ② Kết quả định lượng rõ ràng, dễ vẽ đồ thị scalability. ③ Bắt buộc phải cài đặt/hiểu cả 3 thuật toán ⇒ ghi điểm ở tiêu chí "độ sâu kỹ thuật". |
| **Điểm yếu** | ① **Không có bài toán nghiệp vụ nào** — thuần benchmark, không có Business Understanding, không có Deployment ⇒ trượt hoàn toàn 2/6 pha CRISP-DM. ② Không có sản phẩm/giao diện. ③ Tính mới = 0: đã có hàng chục benchmark công bố (FIMI workshop tồn tại chính vì việc này). ④ Rủi ro bị đánh giá "bài tập lập trình, không phải đồ án". |
| **Trùng lặp** | 🟡 với mọi nhóm FPM — nhưng theo chiều **ngược lại**: nhóm 10 "nuốt" mất phần so sánh hiệu năng, khiến **1, 5, 8, 12, 16 không nên nhấn mạnh benchmark** nữa |

---

#### **Nhóm 12** — Apriori & FP-Growth dự báo dịch sốt xuất huyết dựa trên dữ liệu khí hậu

| Mục | Nội dung |
|---|---|
| **Hướng NC** | FPM ứng dụng Healthcare / dịch tễ |
| **Dataset** | Không nêu. **[SL]** Dữ liệu khí hậu (NOAA/NASA POWER) ghép số ca bệnh (WHO/Bộ Y tế/DengueNet) |
| **Thuật toán** | Apriori, FP-Growth |
| **Điểm mạnh** | ① Domain y tế công cộng có giá trị xã hội cao. ② **Bắt buộc phải rời rạc hóa (discretization)** biến khí hậu liên tục thành item ⇒ thể hiện được kỹ thuật tiền xử lý §3 của KB. ③ Domain hoàn toàn khác biệt so với 15 nhóm còn lại. |
| **Điểm yếu** | ① 🔴 **Sai lệch phương pháp luận nghiêm trọng:** luật kết hợp **không phải công cụ dự báo**. Nó mô tả **đồng xuất hiện trong cùng một giao dịch**, không có khái niệm độ trễ thời gian (lag) hay hướng nhân quả. Dự báo dịch cần time-series / lag features / mô hình SIR. Reviewer sẽ chất vấn ngay ở câu hỏi đầu tiên. ② Dữ liệu khí hậu theo tuần/tháng ⇒ chỉ vài trăm–vài nghìn "giao dịch" ⇒ **hoàn toàn không "massive"**, đi ngược tinh thần MMDS. ③ Ghép 2 nguồn dữ liệu khác độ phân giải không gian–thời gian là bài toán khó, dễ sai. |
| **Trùng lặp** | 🟢 Thấp về domain · 🟡 về thuật toán |
| **📌 Bài học cho nhóm 15** | Đây là **lỗi mẫu cần tránh**: chọn domain hấp dẫn rồi ép thuật toán vào bài toán nó không giải được. |

---

#### **Nhóm 16** — Luật kết hợp & Market-Basket Model phân tích hành vi mua sắm khách hàng

| Mục | Nội dung |
|---|---|
| **Hướng NC** | FPM cổ điển |
| **Dataset** | Không nêu |
| **Thuật toán** | Không nêu tên cụ thể (chỉ "luật kết hợp" + "Market-Basket Model") |
| **Điểm mạnh** | An toàn tuyệt đối · Đúng chương A |
| **Điểm yếu** | ① **Đề tài chung chung nhất lớp** — "Market-Basket Model" chính là tên một mục trong slide, không phải bài toán. ② Không nêu thuật toán, không nêu dataset, không nêu bài toán nghiệp vụ. ③ Chỉ **2 thành viên** nhưng phạm vi lại rộng và mơ hồ. ④ Trùng gần như hoàn toàn với nhóm 1. |
| **Trùng lặp** | 🔴 **Rất cao vs Nhóm 1** · 🟠 vs Nhóm 5 |

---

### 🅑 CỤM FINDING SIMILAR ITEMS — 3 nhóm

---

#### **Nhóm 2** — MinHash & LSH gợi ý phim dựa trên đánh giá MovieLens

| Mục | Nội dung |
|---|---|
| **Hướng NC** | LSH ứng dụng cho Collaborative Filtering |
| **Dataset** | **MovieLens** (nêu đích danh) — ✅ dữ kiện |
| **Thuật toán** | MinHash, LSH |
| **Điểm mạnh** | ① Dataset chuẩn có **ground truth sẵn** ⇒ đánh giá được Precision@K, Recall@K. ② Có sản phẩm rõ (hệ gợi ý). ③ Đúng chương B, dùng đúng pipeline giáo trình. ④ MovieLens đủ lớn (25M ratings) để thể hiện scalability. |
| **Điểm yếu** | ① ⚠️ **Jaccard làm mất thông tin rating:** phải nhị phân hóa (đã xem / chưa xem), vứt bỏ toàn bộ điểm 1–5 sao. Người thích phim 5⭐ và người ghét phim 1⭐ trở nên "giống nhau". ② Cho recommendation, **cosine similarity phù hợp hơn Jaccard** — mà cosine LSH (random hyperplane) lại được nêu ngay trong slide tr.35. Nhóm 2 chọn công cụ dưới tối ưu ngay khi công cụ tốt hơn có sẵn trong bài giảng. ③ MovieLens là dataset "quốc dân" — giảm điểm tính mới. |
| **Trùng lặp** | 🟡 vs 11, 13 (cùng MinHash/LSH, khác bài toán) |

---

#### **Nhóm 11** — Shingling, MinHash, LSH phát hiện đánh giá sản phẩm gần trùng lặp

| Mục | Nội dung |
|---|---|
| **Hướng NC** | LSH near-duplicate detection trên văn bản ngắn |
| **Dataset** | Không nêu. **[SL]** Amazon Product Reviews / Yelp Open Dataset |
| **Thuật toán** | Shingling, MinHash, LSH (đủ 3 bước pipeline) |
| **Điểm mạnh** | ① **Use case thực tế cao** — phát hiện trang trại review giả (review farm) là bài toán có giá trị thương mại. ② Dễ tạo ground truth bằng cách chèn bản sao nhân tạo. ③ Pipeline đúng chuẩn giáo trình. |
| **Điểm yếu** | ① 🔴 **Gần như trùng hoàn toàn nhóm 13** — cùng 3 thuật toán, cùng bài toán near-duplicate, chỉ khác corpus (review vs paper). ② **Chỉ 2 thành viên** — nhóm nhỏ nhất lớp cùng nhóm 16. ③ Review giả hiện đại được **paraphrase bằng LLM** ⇒ Jaccard trên shingle **không bắt được**; cần semantic similarity. Đây là hạn chế nội tại cần thừa nhận. ④ Review rất ngắn (20–50 từ) ⇒ tập shingle nhỏ ⇒ ước lượng Jaccard nhiễu hơn tài liệu dài. |
| **Trùng lặp** | 🔴 **Rất cao vs Nhóm 13** |

---

#### **Nhóm 13** — Phát hiện trùng lặp tài liệu học thuật quy mô lớn bằng Shingling, MinHash và LSH

| Mục | Nội dung |
|---|---|
| **Hướng NC** | LSH near-duplicate detection trên văn bản dài |
| **Dataset** | Không nêu. **[SL]** arXiv metadata/fulltext, CORE, S2ORC |
| **Thuật toán** | Shingling, MinHash, LSH |
| **Điểm mạnh** | ① Cụm từ **"quy mô lớn"** trong tên đề tài cho thấy nhóm hiểu tinh thần MMDS — điểm cộng. ② Tài liệu học thuật **dài** ⇒ tập shingle lớn ⇒ ước lượng Jaccard ổn định hơn nhóm 11. ③ Ground truth dễ tạo (chèn bản near-duplicate nhân tạo với tỷ lệ sửa đổi biết trước). ④ Đúng use case gốc mà giảng viên nêu (slide tr.5: *plagiarism detection*). |
| **Điểm yếu** | ① **Tính mới = 0** — đây chính **là** ví dụ minh họa trong sách MMDS chương 3. Không có gì vượt slide. ② Trùng nặng nhóm 11. ③ Không rõ có sản phẩm/giao diện hay chỉ notebook. |
| **Trùng lặp** | 🔴 **Rất cao vs Nhóm 11** |

---

### 🅒 CỤM DATA STREAMING — 4 nhóm

---

#### **Nhóm 3** — Cổng kiểm soát & phát hiện Spam/IP độc hại thời gian thực

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Stream filtering / an ninh mạng |
| **Dataset** | Không nêu. **[SL]** CIC-IDS2017, UNSW-NB15, blacklist Spamhaus, hoặc log tự sinh |
| **Thuật toán** | Không nêu đích danh. **[SL]** Bloom Filter là chắc chắn (đây là use case mở đầu chương C); có thể thêm Flajolet-Martin đếm IP duy nhất |
| **Điểm mạnh** | ① **Có sản phẩm rõ ràng nhất cụm streaming** — từ "cổng" (gateway) hàm ý một hệ thống chạy được. ② Demo real-time rất ấn tượng khi bảo vệ. ③ Đúng use case sách giáo khoa của Bloom Filter (slide tr.23). ④ Domain an ninh mạng dễ kể chuyện. |
| **Điểm yếu** | ① ⚠️ **Vấn đề khái niệm:** Bloom Filter chỉ trả lời *"phần tử này có trong tập cho trước không?"* — tức là **tra cứu blacklist**, không phải **"phát hiện"**. Muốn *phát hiện* IP độc hại mới (chưa có trong blacklist) cần mô hình khác hẳn. Tên đề tài hứa nhiều hơn công cụ có thể làm. ② Use case y hệt slide ⇒ tính mới thấp. ③ Trùng nặng nhóm 14 (cùng Bloom Filter làm lõi). ④ Ground truth cho "IP độc hại" khó xác thực. |
| **Trùng lặp** | 🟠 **Cao vs Nhóm 14** · 🟡 vs 4 |

---

#### **Nhóm 4** — Streaming (Flajolet-Martin, AMS, Bloom Filter) phát hiện đột biến chủ đề trên luồng tin tức

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Stream moment estimation / burst detection |
| **Dataset** | Không nêu. **[SL]** RSS feeds, GDELT, AG News, Kaggle News Category |
| **Thuật toán** | Flajolet-Martin, AMS, Bloom Filter (nêu đủ 3) |
| **Điểm mạnh** | ① **Nhóm dùng nhiều thuật toán streaming nhất** — 3 thuật toán, thể hiện độ phủ tốt. ② **AMS được dùng đúng mục đích:** surprise number đo độ lệch phân phối, và slide tr.45 nói rõ *"Ứng dụng: phát hiện điểm bất thường (anomaly)"* ⇒ khớp trực tiếp với chủ ý của giảng viên. ③ Bài toán burst detection có ý nghĩa thực tế (trending topics). |
| **Điểm yếu** | ① ⚠️ **Thiếu mảnh ghép then chốt: không có DGIM.** Phát hiện "đột biến" bắt buộc phải so sánh **cửa sổ hiện tại vs quá khứ** — đó chính xác là bài toán sliding window mà DGIM giải. Dùng FM/AMS trên toàn luồng cho **giá trị tích lũy**, không cho **tín hiệu đột biến**. ② Ground truth cho "đột biến chủ đề" rất mơ hồ ⇒ khó đánh giá định lượng, dễ rơi vào mô tả định tính. ③ Ghép 3 thuật toán vào một hệ thống mạch lạc là thách thức thiết kế không nhỏ. |
| **Trùng lặp** | 🟡 vs 3, 7 |

---

#### **Nhóm 7** — Data Streaming phát hiện khu vực có mức độ ô nhiễm bất thường

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Stream anomaly detection trên dữ liệu IoT/cảm biến |
| **Dataset** | Không nêu. **[SL]** OpenAQ, Beijing PM2.5 (UCI), AirVisual, dữ liệu quan trắc VN |
| **Thuật toán** | **Không nêu** — điểm yếu lớn nhất |
| **Điểm mạnh** | ① Dữ liệu cảm biến là **ví dụ mở đầu chương C** của giảng viên (slide tr.4: IoT, nhiệt độ, độ ẩm, GPS) ⇒ đúng tinh thần. ② Domain Smart City có ý nghĩa xã hội. ③ Nhiều nguồn dữ liệu mở, dễ lấy. |
| **Điểm yếu** | ① 🔴 **Không nêu thuật toán nào** ⇒ đề tài chưa định hình, rủi ro cao nhất cụm streaming. ② ⚠️ **Dữ liệu chất lượng không khí thường lấy mẫu theo giờ** ⇒ vài chục nghìn điểm/năm/trạm ⇒ **hoàn toàn vừa RAM**, không hề "massive". Phải mô phỏng tốc độ cao một cách nhân tạo, và reviewer sẽ hỏi *"vì sao không tính chính xác?"* — câu hỏi chí mạng cho mọi đề tài streaming dùng dữ liệu nhỏ. ③ "Bất thường" chưa được định nghĩa (vượt ngưỡng WHO? lệch so với lịch sử? lệch so với trạm lân cận?). |
| **Trùng lặp** | 🟡 vs 3, 4 |
| **📌 Bài học cho nhóm 15** | Đề tài streaming **phải chọn được nguồn dữ liệu thật sự có tốc độ cao**, nếu không sẽ không biện minh được vì sao cần thuật toán xấp xỉ. |

---

#### **Nhóm 14** — So sánh Bloom Filter và Counting Bloom Filter trong lọc dữ liệu tốc độ cao

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Benchmark cấu trúc dữ liệu xác suất |
| **Dataset** | Không nêu. **[SL]** Luồng tổng hợp (synthetic) + có thể log thật |
| **Thuật toán** | Bloom Filter, Counting Bloom Filter |
| **Điểm mạnh** | ① **Counting Bloom Filter KHÔNG có trong slide** ⇒ có yếu tố mở rộng ngoài bài giảng — điểm cộng nhỏ về tính mới. ② Đo lường sạch sẽ: FP rate, bộ nhớ, thông lượng — dễ kiểm chứng công thức $(1-e^{-km/n})^k$ và $k^*=(n/m)\ln 2$. ③ Đúng tín hiệu #3 của giảng viên (tinh chỉnh tham số + so lý thuyết vs thực nghiệm). |
| **Điểm yếu** | ① 🔴 **Phạm vi quá hẹp** — toàn bộ đồ án xoay quanh **một cấu trúc dữ liệu**, và đó là *filtering*, không phải *mining*. Khó viết đủ 7 chương báo cáo. ② ⚠️ **So sánh khập khiễng về mặt khái niệm:** Counting BF tồn tại để hỗ trợ **xóa phần tử** — nếu bài toán không có nhu cầu xóa thì CBF đơn thuần tốn bộ nhớ hơn mà không lợi ích gì. Phải xây dựng kịch bản có xóa (VD: cửa sổ trượt) thì so sánh mới có nghĩa. ③ Không có bài toán nghiệp vụ, không có sản phẩm ⇒ cùng rủi ro "bài tập lập trình" như nhóm 10. |
| **Trùng lặp** | 🟠 **Cao vs Nhóm 3** (cùng Bloom Filter làm lõi) |

---

### 🅧 CỤM NGOÀI SYLLABUS — 3 nhóm

---

#### **Nhóm 6** — Phát hiện cảnh bạo lực trong video (học máy + đặc trưng CNN)

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Computer Vision / Video Classification |
| **Dataset** | Không nêu. **[SL]** RWF-2000, Hockey Fight, Movies Fight, Real Life Violence Situations |
| **Thuật toán** | CNN feature extraction + ML classifier |
| **Điểm mạnh** | ① Sản phẩm demo ấn tượng về thị giác. ② Có so sánh mô hình ⇒ khớp yêu cầu ML cổ điển. ③ Dataset chuẩn có sẵn. |
| **Điểm yếu** | ① 🔴 **Không dùng bất kỳ thuật toán nào của môn học.** Không FPM, không LSH, không Streaming. Rủi ro bị đánh giá "lạc đề" là **cao nhất lớp**. ② Chi phí tính toán lớn (video), rủi ro không kịp deadline. ③ Đây thực chất là đồ án môn **Thị giác máy tính** (mà lớp có học kỳ này — thư mục `thi_giac_may_tinh` tồn tại) ⇒ dễ bị nghi ngờ nộp trùng môn. |
| **Trùng lặp** | 🟢 Thấp vs lớp · 🟡 vs 17 (cùng CV) |

---

#### **Nhóm 9** — Thu thập dữ liệu và thử nghiệm tìm kiếm bằng hình ảnh

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Content-Based Image Retrieval |
| **Dataset** | Tự thu thập (nêu rõ trong tên đề tài) |
| **Thuật toán** | **Không nêu** |
| **Điểm mạnh** | ① Nếu dùng **LSH trên embedding ảnh** (cosine LSH / random hyperplane, slide tr.35) hoặc **FAISS** (cũng nêu ở tr.35) thì **CÓ chạm syllabus** và trở thành đề tài hợp lệ. ② Tự thu thập dữ liệu thể hiện công sức Data Engineering. |
| **Điểm yếu** | ① 🔴 **Tên đề tài mơ hồ nhất lớp** — "thử nghiệm" không phải mục tiêu nghiên cứu; không nêu thuật toán, không nêu tiêu chí đánh giá. ② Nếu dùng CNN embedding + brute-force search ⇒ hoàn toàn lạc đề. ③ Thu thập dữ liệu tự phát ⇒ không có ground truth ⇒ khó đánh giá định lượng. |
| **Trùng lặp** | 🟢 Thấp · 🟡 vs 2/11/13 **nếu** dùng LSH |

---

#### **Nhóm 17** — So sánh các thuật toán học máy phân loại ảnh cháy (HOG + Color Histogram)

| Mục | Nội dung |
|---|---|
| **Hướng NC** | Computer Vision / Image Classification cổ điển |
| **Dataset** | Không nêu. **[SL]** FIRE Dataset (Kaggle), BoWFire |
| **Thuật toán** | HOG, Color Histogram + các bộ phân loại ML (SVM/RF/…) |
| **Điểm mạnh** | ① Phạm vi rõ ràng, dễ hoàn thành. ② Có so sánh nhiều mô hình + confusion matrix + ROC ⇒ khớp yêu cầu ML cổ điển. ③ Đặc trưng thủ công (HOG/ColorHist) nhẹ, chạy nhanh. |
| **Điểm yếu** | ① 🔴 **Không dùng thuật toán nào của môn học.** ② HOG + Color Histogram là kỹ thuật **tiền deep-learning** (2005–2010) — thiếu tính hiện đại. ③ Cũng thuộc phạm vi môn Thị giác máy tính. |
| **Trùng lặp** | 🟢 vs lớp · 🟡 vs 6 |

---

## 3. BẢN ĐỒ BÃO HÒA & MA TRẬN TRÙNG LẶP

### 3.1. Mật độ theo chương

```
Chương A — Frequent Pattern Mining     ████████████████████████  6 nhóm   BÃO HÒA 🔴
  ├─ Market-basket bán lẻ              ███████████████           3 nhóm   [1, 5, 16]  ← chen chúc nhất
  ├─ Recommendation                    █████                     1 nhóm   [8]
  ├─ Benchmark thuật toán              █████                     1 nhóm   [10]
  └─ Healthcare                        █████                     1 nhóm   [12]

Chương C — Data Streaming              ████████████████          4 nhóm   ĐÔNG 🟠
  ├─ Filtering / Bloom                 ██████████                2 nhóm   [3, 14]     ← chồng lấn
  ├─ Moments / burst                   █████                     1 nhóm   [4]
  └─ IoT anomaly                       █████                     1 nhóm   [7]

Chương B — Finding Similar Items       ████████████              3 nhóm   VỪA 🟡
  ├─ Near-duplicate văn bản            ██████████                2 nhóm   [11, 13]    ← chồng lấn
  └─ Recommendation                    █████                     1 nhóm   [2]

Ngoài syllabus                         ████████████              3 nhóm   [6, 9, 17]
```

### 3.2. Bốn cặp trùng lặp nghiêm trọng đã tồn tại

| Cặp | Mức | Bản chất trùng |
|---|:---:|---|
| **1 ↔ 16** | 🔴 | Cùng thuật toán (Apriori/AR), cùng bài toán (market-basket), cùng domain (mua sắm). Chỉ khác cách đặt tên. |
| **11 ↔ 13** | 🔴 | Cùng pipeline Shingling→MinHash→LSH, cùng bài toán near-duplicate văn bản. Chỉ khác corpus. |
| **3 ↔ 14** | 🟠 | Cùng Bloom Filter làm lõi, cùng bài toán lọc tốc độ cao. |
| **1/16 ↔ 5** | 🟠 | Cùng dataset bán lẻ + cùng Apriori; nhóm 5 chỉ thêm RFM/K-means. |

> **Hàm ý cho nhóm 15:** ba trong bốn cặp này sẽ **cạnh tranh trực tiếp với nhau khi chấm**. Nhóm 15 vào sau cùng — lợi thế duy nhất là **không được phép trùng với ai**. Đề tài phải phân biệt được bằng một câu.

---

## 4. CÁC CHỦ ĐỀ ĐÃ QUÁ PHỔ BIẾN

| Xếp hạng | Chủ đề | Số nhóm | Đánh giá |
|:---:|---|:---:|---|
| 1 | **Market-basket / luật kết hợp trên dữ liệu mua sắm** | 3–4 (1, 16, 5, một phần 8) | Bão hòa tuyệt đối. Nhóm thứ 5 chắc chắn bị chê "thiếu tính mới" |
| 2 | **Near-duplicate detection bằng Shingling+MinHash+LSH** | 2 (11, 13) | Đây **là** ví dụ trong sách. Đã có 2 nhóm làm y hệt |
| 3 | **Bloom Filter cho lọc dữ liệu tốc độ cao** | 2 (3, 14) | Use case mở đầu chương C. Đã kín |
| 4 | **Apriori vs FP-Growth vs ECLAT benchmark** | 1 (10) — nhưng độc quyền | Nhóm 10 đã "chiếm" trọn góc so sánh hiệu năng |
| 5 | **Computer Vision không liên quan môn học** | 3 (6, 9, 17) | Phổ biến vì dễ, nhưng là **rủi ro**, không phải xu hướng đáng theo |

---

## 5. CÁC CHỦ ĐỀ KHÔNG NÊN CHỌN

### 5.1. 🔴 Loại bỏ hoàn toàn (trùng trực tiếp)

Đã liệt kê đầy đủ 11 mục tại **§9.1 của Knowledge Base**. Tóm tắt: mọi biến thể của market-basket bán lẻ · so sánh Apriori/FP-Growth/ECLAT · gợi ý bằng association rules · gợi ý phim bằng MinHash · phát hiện trùng lặp tài liệu/review · lọc spam/IP bằng Bloom · so sánh Bloom vs Counting Bloom · burst detection tin tức · anomaly ô nhiễm · dự báo dịch bệnh bằng luật kết hợp.

### 5.2. 🟠 Loại bỏ vì rủi ro phương pháp luận (bài học từ 3 nhóm mắc lỗi)

| Lỗi mẫu | Nhóm mắc | Quy tắc rút ra cho nhóm 15 |
|---|:---:|---|
| **Ép thuật toán vào bài toán nó không giải được** | 12 (AR để "dự báo") | Thuật toán phải khớp **bản chất** bài toán, không chỉ khớp domain hấp dẫn |
| **Chọn dữ liệu quá nhỏ cho thuật toán xấp xỉ** | 7, 12 | Nếu dữ liệu vừa RAM thì không biện minh được vì sao cần thuật toán xấp xỉ. **Phải có dữ liệu ≥ hàng triệu bản ghi** hoặc luồng thật sự tốc độ cao |
| **Tên đề tài hứa nhiều hơn công cụ làm được** | 3 ("phát hiện" bằng Bloom), 9 ("thử nghiệm") | Tên đề tài phải mô tả **chính xác** những gì thuật toán thực sự làm |
| **Đề tài thuần benchmark, không có bài toán nghiệp vụ** | 10, 14 | Phải có đủ 6 pha CRISP-DM, đặc biệt Business Understanding và Deployment |
| **Bỏ syllabus để làm CV/ML thuần** | 6, 9, 17 | Lõi bắt buộc phải là thuật toán MMDS |
| **Thiếu mảnh ghép thuật toán mà bài toán đòi hỏi** | 4 (burst detection thiếu DGIM) | Kiểm tra: bài toán đòi hỏi những thành phần nào, đã có đủ chưa? |

### 5.3. 🟡 Cân nhắc kỹ

- **Bất kỳ đề tài nào chỉ dùng 1 thuật toán** — nhóm 14 cho thấy phạm vi quá hẹp khó viết đủ báo cáo bậc thạc sĩ.
- **Bất kỳ đề tài nào chỉ dừng ở support/confidence** — đi ngược 4 slide về null-invariance.

---

## 6. KHOẢNG TRỐNG NGHIÊN CỨU CÒN LẠI

Phân tầng theo ba trục: **thuật toán · phương pháp luận · lĩnh vực ứng dụng**.

### 6.1. Khoảng trống theo THUẬT TOÁN — được dạy/nêu tên nhưng **0 nhóm** dùng

| # | Thuật toán / kỹ thuật | Vị trí trong slide | Trạng thái | Mức hấp dẫn |
|:--:|---|---|:---:|:---:|
| G1 | **DGIM & sliding-window queries** | Chương C, **15 slide = 22% chương** | 0 nhóm dùng làm lõi | ⭐⭐⭐⭐⭐ |
| G2 | **Sequential Pattern Mining** (PrefixSpan, CloSpan, BIDE) | Chương A tr.34 | 0 nhóm | ⭐⭐⭐⭐⭐ |
| G3 | **Closed / Max patterns** (CLOSET, FPclose, FPMax) | Chương A, 2 slide riêng + tr.34 | 0 nhóm | ⭐⭐⭐⭐ |
| G4 | **Discriminative frequent patterns** (Cheng et al. ICDE'07) | Chương A tr.4, tr.34 | 0 nhóm | ⭐⭐⭐⭐⭐ |
| G5 | **Cosine LSH / random hyperplane / SimHash** (Charikar 2002) | Chương B tr.35 | 0 nhóm (cả 3 nhóm LSH đều dùng Jaccard) | ⭐⭐⭐⭐ |
| G6 | **Độ đo null-invariant** (Kulczynski, AllConf, Coherence, Cosine, MaxConf) | Chương A, **4 slide = 10% chương** | 0 nhóm nêu trong tên đề tài | ⭐⭐⭐⭐⭐ |
| G7 | **Reservoir Sampling làm lõi** | Chương C, 4 slide + chứng minh quy nạp | 0 nhóm (chỉ có thể dùng phụ) | ⭐⭐⭐ |
| G8 | **AMS / surprise number làm lõi** | Chương C, 8 slide + chứng minh kỳ vọng | Chỉ nhóm 4 dùng phụ | ⭐⭐⭐⭐ |
| G9 | **Constraint-based mining** (convertible constraints, gPrune) | Chương A tr.34 | 0 nhóm | ⭐⭐⭐ |
| G10 | **Graph pattern mining** (gSpan, CloseGraph) | Chương A tr.34 | 0 nhóm | ⭐⭐⭐ |

> **G1, G4, G6 là ba khoảng trống giá trị nhất:** đều được giảng viên đầu tư thời lượng hoặc nêu đích danh, đều chưa ai chạm, và đều **dễ biện minh** trong báo cáo bằng chính slide.

### 6.2. Khoảng trống theo PHƯƠNG PHÁP LUẬN

| # | Khoảng trống | Vì sao có giá trị |
|:--:|---|---|
| M1 | **Kiến trúc kết hợp ≥2 chương thành một hệ thống thống nhất** | **Không nhóm nào làm.** Đây là khác biệt mạnh nhất có thể tạo ra: chứng minh hiểu cả môn học, không chỉ một chương |
| M2 | **Concept drift / phân phối phi dừng** | Giảng viên nhấn mạnh tính "phi dừng" ngay slide tr.7 chương C, nhưng **0 nhóm** xử lý. Là hạn chế nội tại của mọi hệ streaming |
| M3 | **So sánh lý thuyết vs thực nghiệm có hệ thống** (S-curve, $k^*$, cận sai số DGIM) | Đúng tín hiệu #3 của giảng viên; chỉ nhóm 14 chạm một phần |
| M4 | **Cài đặt from scratch + kiểm định chéo với thư viện** | Đúng tín hiệu #2; nhóm 15 đã chốt làm điều này ⇒ lợi thế sẵn có |
| M5 | **Đánh giá nén pattern** (closed/max vs all patterns) | Slide nói rõ closed cho "lossless compression" nhưng 0 nhóm đo tỷ lệ nén |
| M6 | **Phân tích chi phí–lợi ích bộ nhớ/độ chính xác định lượng** | Bảng tổng kết tr.67 của giảng viên chính là lời mời làm việc này |

### 6.3. Khoảng trống theo LĨNH VỰC ỨNG DỤNG

| Lĩnh vực | Đã có nhóm? | Ghi chú |
|---|:---:|---|
| Bán lẻ / e-commerce | 🔴 3–4 nhóm | Kín |
| Giải trí (phim, game) | 🟠 2 nhóm | Gần kín |
| An ninh mạng (spam/IP) | 🟠 2 nhóm | Gần kín |
| Tin tức / mạng xã hội | 🟡 1 nhóm | Còn góc |
| Môi trường / IoT | 🟡 1 nhóm | Còn góc |
| Y tế | 🟡 1 nhóm (và làm sai công cụ) | Còn nhiều dư địa |
| Học thuật / giáo dục | 🟡 1 nhóm (chỉ chống đạo văn) | **Educational Data Mining còn trống** |
| **Ngân hàng / Tài chính / Fraud** | 🟢 **0 nhóm** | ⭐ Trống hoàn toàn |
| **Viễn thông (Telecom)** | 🟢 **0 nhóm** | ⭐ Trống hoàn toàn |
| **Logistics / Chuỗi cung ứng** | 🟢 **0 nhóm** | ⭐ Trống hoàn toàn |
| **ERP / CRM / Process Mining** | 🟢 **0 nhóm** | ⭐ Trống hoàn toàn |
| **Smart City — giao thông** | 🟢 **0 nhóm** | ⭐ Trống hoàn toàn |
| **Web/App analytics — clickstream** | 🟢 **0 nhóm** | ⭐ Trống hoàn toàn |
| **Y tế lâm sàng — tương tác thuốc** | 🟢 **0 nhóm** | ⭐ **Giảng viên nêu đích danh** ở slide tr.9 mà không ai lấy |

> 📌 **Phát hiện đáng chú ý:** slide chương A tr.9 (*Other Applications*) nêu **hai** ứng dụng ngoài bán lẻ:
> - *Plagiarism: baskets are sentences, items are documents* → nhóm 13 đã lấy
> - *"Side-effects in drug combinations: baskets are patients; items are drugs and their side effects"* → **chưa ai lấy**
>
> Đây là ứng dụng **được chính giảng viên gợi ý** nhưng bị bỏ trống — một chỉ dấu rất mạnh cho Phase 3.

---

## 7. MƯỜI HƯỚNG PHÔI THAI CHO ĐỀ TÀI MỚI

*(Đầu vào cho Phase 3 — chưa phải đề xuất chính thức, chưa xếp hạng)*

| # | Hướng | Khoảng trống khai thác | Lĩnh vực trống |
|:--:|---|---|---|
| S1 | **Hệ phát hiện gian lận giao dịch 3 tầng:** Bloom+DGIM lọc & đếm cửa sổ trượt → MinHash/LSH phát hiện cụm giao dịch gần trùng (fraud ring) → FPM sinh luật gian lận | M1, G1, G6 | Ngân hàng/Fraud |
| S2 | **Process Mining trên event log ERP** bằng Sequential Pattern Mining (PrefixSpan/BIDE) + AMS surprise number phát hiện nút thắt cổ chai | G2, G8 | ERP/Process Mining |
| S3 | **Hệ cảnh báo sớm rời mạng viễn thông** dùng discriminative frequent patterns làm đặc trưng đầu vào cho bộ phân loại | G4, M1 | Telecom |
| S4 | **Khai phá lộ trình học tập từ log LMS** (sequential patterns) → DSS cảnh báo sinh viên nguy cơ | G2 | Educational DM |
| S5 | **Phát hiện tương tác thuốc bất lợi** từ dữ liệu báo cáo tác dụng phụ — closed/max patterns + độ đo null-invariant | G3, G6 | Y tế lâm sàng — **GV gợi ý** |
| S6 | **Hệ giám sát clickstream thời gian thực** với DGIM làm lõi cho truy vấn cửa sổ trượt + Reservoir Sampling phân tầng | G1, G7, M2 | Web analytics |
| S7 | **Phát hiện & theo dõi lan truyền tin giả** bằng SimHash/cosine LSH (khử biến thể paraphrase) + DGIM đếm lan truyền | G5, G1, M1 | Mạng xã hội |
| S8 | **Tối ưu tuyến vận tải/kho** — luật kết hợp trên đơn hàng + sequential patterns trên chuỗi sự kiện giao hàng | G2, G6 | Logistics |
| S9 | **Hệ phát hiện concept drift trên luồng giao dịch** — AMS surprise number + reservoir sampling phân tầng + cảnh báo tái huấn luyện | M2, G7, G8 | Xuyên ngành |
| S10 | **DSS bán chéo (cross-sell) cho ngân hàng** — FPM với đầy đủ 5 độ đo null-invariant + Imbalance Ratio, dashboard cho nhân viên tín dụng | G6, M5 | Ngân hàng/CRM |

---

## 8. TIÊU CHÍ CHỌN ĐỀ TÀI CHO NHÓM 15

Rút ra từ toàn bộ Phase 1 + Phase 2. Mọi đề xuất ở Phase 3 sẽ được chấm theo 8 tiêu chí này.

| # | Tiêu chí | Ngưỡng bắt buộc |
|:--:|---|---|
| C1 | **Lõi là thuật toán MMDS** | ≥ 2 thuật toán được dạy, đóng vai trò lõi (không phải trang trí) |
| C2 | **Không trùng lặp** | 🟢 Thấp với cả 16 nhóm |
| C3 | **Thuật toán khớp bản chất bài toán** | Tránh lỗi mẫu của nhóm 12 |
| C4 | **Quy mô dữ liệu biện minh được** | ≥ 1 triệu bản ghi, hoặc luồng tốc độ cao thật sự |
| C5 | **Có ground truth định lượng** | Đo được precision/recall/sai số, không chỉ mô tả định tính |
| C6 | **Đủ 6 pha CRISP-DM** | Đặc biệt Business Understanding + Deployment (nhóm 10, 14 thiếu) |
| C7 | **Khai thác ≥ 2 khoảng trống §6** | Ưu tiên G1, G4, G6, M1, M2 |
| C8 | **Có sản phẩm chạy được** | API + Dashboard + DB + Docker theo yêu cầu ROLE |

---

## 9. TÓM TẮT PHASE 2

**Bốn kết luận:**

1. **Bốn cặp đề tài đã trùng nhau từ trước** (1↔16, 11↔13, 3↔14, 1/16↔5). Các nhóm này sẽ tự cạnh tranh khi chấm. Nhóm 15 vào sau — bắt buộc phải khác biệt rõ ràng.

2. **Sáu lỗi phương pháp luận đã hiện diện trong lớp** (§5.2). Nhóm 15 có lợi thế thấy trước và tránh được — đặc biệt lỗi "chọn dữ liệu quá nhỏ cho thuật toán xấp xỉ" (nhóm 7, 12) và lỗi "ép thuật toán vào bài toán không phù hợp" (nhóm 12).

3. **Mười khoảng trống thuật toán, sáu khoảng trống phương pháp luận, bảy lĩnh vực hoàn toàn trống.** Ba khoảng trống giá trị nhất: **DGIM làm lõi** (22% chương C, 0 nhóm) · **discriminative frequent patterns** (cầu nối chính danh sang ML) · **độ đo null-invariant** (10% chương A, 0 nhóm nêu).

4. **Không nhóm nào kết hợp ≥2 chương.** Đây là cơ hội khác biệt mạnh nhất còn lại — và cũng là cách duy nhất chứng minh nắm được toàn bộ môn học thay vì một mảnh.

---

*Đầu ra Phase 2. Phase 3 (đề xuất tối thiểu 15 đề tài với đầy đủ 11 thuộc tính mỗi đề tài + xếp hạng theo 8 tiêu chí §8) sẽ bắt đầu sau khi được xác nhận.*
