# KNOWLEDGE BASE NỘI BỘ — MÔN KHAI PHÁ DỮ LIỆU (Advanced Data Mining)

**Lớp:** Hệ thống Thông tin 02, khóa 2025–2027 (PTIT)
**Giảng viên:** Thanh-Ha DO
**Nhóm thực hiện:** Nhóm 15 — Nguyễn Thuý Anh (B25CHHT076), Trần Thị Thảo (B25CHHT113), Trần Văn Hanh (B25CHHT092)
**Phiên bản:** Phase 1 — 2026-07-27
**Trạng thái:** Hoàn tất phân tích tài liệu đầu vào hiện có. Còn 4 nhóm tài liệu thiếu (xem §0.2).

---

## 0. KIỂM KÊ TÀI LIỆU ĐẦU VÀO

### 0.1. Tài liệu ĐÃ nhận và đã đọc toàn văn

| # | Tệp | Dung lượng | Số trang | Nội dung | Ngày trên slide |
|---|-----|-----------|----------|----------|-----------------|
| 1 | `Data_Mining_Course_Master.pdf` | 1.77 MB | 39 | **Mining Frequent Pattern, Association and Correlations** | 19/01/2026 |
| 2 | `Data_Mining_Course_Master-4.pdf` | 437 KB | 35 | **Finding Similar Items** (Shingling, Min-Hashing, LSH) | 04/06/2026 |
| 3 | `Data_Mining_Course_Master-6.pdf` | 507 KB | 67 | **Luồng dữ liệu (Data Streaming — Phần I & II)** | — |
| 4 | `Nhóm BTL Môn Khai Phá Dữ Liệu.xlsx` | 13.7 KB | 1 sheet | Danh sách 17 nhóm + đề tài đã đăng ký | — |

**Tổng:** 141 trang slide + 1 bảng đăng ký đề tài.

### 0.2. Tài liệu CHƯA nhận — ⚠️ khoảng trống thông tin

Bốn nhóm tài liệu mà đề bài (ROLE) yêu cầu phân tích nhưng **không tồn tại trong thư mục**. Tôi **không suy diễn thay** cho các mục này; mọi phát biểu liên quan trong tài liệu này đều được đánh dấu rõ là **[GIẢ ĐỊNH]**.

| # | Tài liệu thiếu | Mức ảnh hưởng | Hệ quả nếu không có |
|---|---------------|---------------|---------------------|
| A | **Dataset** của môn (nếu giảng viên chỉ định) | 🔴 Cao | Nhóm phải tự chọn dataset công khai; rủi ro lệch yêu cầu |
| B | **Data Dictionary** | 🔴 Cao | Không có mô tả thuộc tính chuẩn để đối chiếu |
| C | **Tiêu chí chấm điểm / Rubric** | 🔴 Cao | §7 chỉ là rubric **giả định**, cần xác minh |
| D | **Slide các buổi còn lại** (đánh số tệp gợi ý ít nhất 6 chương: `-4`, `-6` ⇒ thiếu chương 1,2,3,5 và có thể ≥7) | 🟠 Trung bình | Có thể bỏ sót thuật toán được dạy (VD: PageRank/Link Analysis, Clustering quy mô lớn, Recommendation Systems, Dimensionality Reduction — đều là các chương chuẩn của MMDS) |
| E | **Đề cương môn học / văn bản hướng dẫn BTL** | 🟠 Trung bình | Không rõ ràng buộc về số trang, hình thức nộp, deadline, quy mô nhóm |

> **Yêu cầu hành động:** Nếu bạn có 5 mục trên (kể cả file scan, ảnh chụp màn hình, hay tin nhắn Zalo của giảng viên), hãy cung cấp. Đặc biệt **(C) rubric** và **(D) slide còn thiếu** sẽ thay đổi đáng kể lựa chọn đề tài ở Phase 3.

---

## 1. NHỮNG KIẾN THỨC ĐÃ HỌC TRONG MÔN

### 1.1. Phát hiện then chốt: đây KHÔNG phải môn Data Mining "cổ điển"

Đây là kết luận quan trọng nhất của Phase 1, và nó định hình toàn bộ chiến lược đề tài.

**Bằng chứng:**

1. Tiêu đề slide: *"**Advanced** Data Mining"* và *"**Thuật toán cho Khoa học Dữ liệu**"*.
2. Giáo trình tham chiếu được nêu đích danh **hai lần** (slide *Finding Similar Items*, tr.3 và tr.35; slide *Streaming*, tr.8 và tr.54 trích hình trực tiếp):
   > Leskovec, Rajaraman & Ullman, *Mining of Massive Datasets* (MMDS), 3rd ed. — http://www.mmds.org
3. Ba chương đã có slide đều là chương của MMDS: Ch.6 (Frequent Itemsets), Ch.3 (Finding Similar Items), Ch.4 (Mining Data Streams).
4. **Không có một slide nào** về: decision tree, random forest, SVM, logistic regression, gradient boosting, neural network, cross-validation, ROC/AUC, confusion matrix, SHAP/LIME.
5. 16/17 nhóm đã đăng ký đề tài đều bám vào đúng 3 chương này (chi tiết §8).

**Hệ quả — mâu thuẫn cần giải quyết:**

Yêu cầu trong ROLE prompt (so sánh nhiều mô hình, XGBoost/LightGBM, Cross-Validation, Hyperparameter Tuning, SHAP, ROC-AUC, Confusion Matrix) thuộc về **Predictive Modeling cổ điển** — mảng này **không nằm trong nội dung được dạy** theo bằng chứng hiện có.

Nếu đề tài chỉ làm ML cổ điển, nhóm có nguy cơ bị đánh giá **"không áp dụng kiến thức môn học"** — đây là lý do trượt điểm phổ biến nhất ở BTL cao học.

**Chiến lược khuyến nghị (sẽ triển khai ở Phase 3):**

> **Lõi bắt buộc = thuật toán MMDS** (FPM / LSH / Streaming) — đảm bảo đúng trọng tâm chấm điểm.
> **Lớp bọc = sản phẩm Information Systems** (API + Dashboard + DB + Docker) — đáp ứng yêu cầu "sản phẩm thực tế".
> **Lớp ML bổ sung = tùy chọn, có kiểm soát** — chỉ thêm khi nó *giải quyết một bài toán mà thuật toán MMDS đặt ra* (VD: mô hình phân loại dùng chính các frequent pattern làm feature — kỹ thuật *discriminative frequent pattern analysis*, được nhắc trực tiếp ở slide FPM tr.4 và tr.34). Cách này khiến ML **nằm trong** khung môn học chứ không phải phần gắn thêm.

*(Ba nhóm 6, 9, 17 đã chọn hướng thuần Computer Vision/ML — đây là rủi ro của họ, không phải chuẩn mực để noi theo. Xem §8.)*

### 1.2. Bản đồ nội dung 3 chương đã có slide

```
CHƯƠNG A — Frequent Patterns, Association & Correlations        (39 tr)
├── Basic Concepts
│   ├── Frequent pattern analysis — Agrawal, Imielinski, Swami (AIS93)
│   └── The Market-Basket Model
├── Mining Frequent Items
│   ├── Khái niệm: itemset, k-itemset, support count, relative support
│   ├── Closed patterns / Max-patterns (nén không mất mát)
│   ├── Downward Closure Property (Apriori property)
│   ├── Apriori — Agrawal & Srikant, VLDB'94
│   ├── FP-Growth — Han, Pei & Yin, SIGMOD'00
│   └── ECLAT (vertical format) — Zaki et al., KDD'97
└── Interestingness Measures
    ├── Lift, χ²  → KHÔNG null-invariant
    └── AllConf, Coherence, Cosine, Kulczynski, MaxConf → null-invariant

CHƯƠNG B — Finding Similar Items                                (35 tr)
├── The Similar Items Problem (bài toán O(N²) và mục tiêu O(N))
│   └── Jaccard similarity / distance
├── Shingling (k-shingles, char-level vs word-level, hashing)
├── Min-Hashing (định lý min-hash, signature matrix, one-pass algorithm)
└── Locality-Sensitive Hashing (banding b×r, S-curve, tuning t≈(1/b)^(1/r))

CHƯƠNG C — Data Streaming (Phần I & II)                         (67 tr)
├── Giới thiệu mô hình luồng (vô hạn, phi dừng, one-pass, bộ nhớ giới hạn)
├── Lấy mẫu: fixed-proportion, hash-based, Reservoir Sampling
├── Lọc: Hash filter, Bloom Filter (k* = (n/m)·ln2)
├── Đếm phần tử phân biệt: Flajolet-Martin
├── Ước lượng mô-men: AMS (surprise number / moment bậc k)
└── Cửa sổ trượt: DGIM (exponential buckets, sai số ≤ 50%)
```

---

## 2. CÁC THUẬT TOÁN DATA MINING ĐÃ ĐƯỢC GIẢNG DẠY (chi tiết đầy đủ)

### 2.A. NHÓM FREQUENT PATTERN MINING

#### A.1. Nền tảng khái niệm

| Khái niệm | Định nghĩa (theo slide) |
|-----------|------------------------|
| **Itemset** | Tập một hoặc nhiều item; *k-itemset* $X = \{x_1,\dots,x_k\}$ |
| **Support count** | Tần suất/số lần xuất hiện của itemset $X$ |
| **Relative support** | Tỷ lệ giao dịch chứa $X$ = $P(X)$ |
| **Frequent itemset** | $X$ có support ≥ `min_sup` |
| **Association rule** | $X \rightarrow Y$ với support $s = P(X \cup Y)$, confidence $c = P(Y\mid X)$ |
| **Closed pattern** | $X$ frequent và **không tồn tại** super-pattern $Y \supset X$ có **cùng support** |
| **Max-pattern** | $X$ frequent và **không tồn tại** super-pattern $Y \supset X$ nào frequent |

**Ví dụ chuẩn của giảng viên** (dùng lại được trong báo cáo):
```
Tid  Items bought
10   Beer, Nuts, Diaper
20   Beer, Coffee, Diaper
30   Beer, Diaper, Eggs
40   Nuts, Eggs, Milk
50   Nuts, Coffee, Diaper, Eggs, Milk
```
minsup = 50%, minconf = 50%
→ Frequent: Beer:3, Nuts:3, Diaper:4, Eggs:3, {Beer,Diaper}:3
→ Rules: Beer→Diaper (60%, 100%); Diaper→Beer (60%, 75%)

**Vì sao cần closed/max-pattern:** một pattern dài $\{a_1,\dots,a_{100}\}$ chứa $2^{100}-1 \approx 1.27\times10^{30}$ sub-pattern. Closed patterns cho **nén không mất mát** (lossless compression).

#### A.2. Downward Closure Property (nguyên lý Apriori)

> Mọi tập con của một frequent itemset cũng phải frequent.
> ⇒ Nếu $\{beer, diaper, nuts\}$ frequent thì $\{beer, diaper\}$ cũng frequent.

**Apriori pruning principle:** nếu một itemset không frequent thì **không sinh/không kiểm tra** mọi superset của nó.

#### A.3. Apriori — Agrawal & Srikant, VLDB'94

Pseudo-code (nguyên văn slide tr.18):
```
L1 = {frequent items};
for (k = 1; Lk != ∅; k++) do
begin
    Ck+1 = candidates generated from Lk;
    for each transaction t in database do
        increment the count of all candidates in Ck+1 that are contained in t
    Lk+1 = candidates in Ck+1 with min_support
end
return ∪k Lk;
```

**Ba điểm nghẽn tính toán** (giảng viên nêu rõ — cần đo được trong thực nghiệm):
1. Quét CSDL nhiều lần (multiple scans)
2. Số lượng candidate khổng lồ
3. Chi phí đếm support cho candidate

**Ba hướng cải thiện:** giảm số lần quét · thu nhỏ tập candidate · tăng tốc đếm support.

#### A.4. FP-Growth — Han, Pei & Yin, SIGMOD'00

**Triết lý:** *"Grow long patterns from short ones using local frequent items only."*
Nếu `abc` frequent → chiếu DB lên `abc` (DB|abc) → nếu `d` là local frequent trong DB|abc thì `abcd` frequent.

**Quy trình 2 bước:**

*Bước 1 — Nén CSDL thành FP-tree:*
1. Quét DB lần 1 → tìm frequent 1-itemsets
2. Sắp xếp item theo tần suất **giảm dần** (f-list)
3. Quét DB lần 2 → dựng FP-tree, bắt đầu từ item tần suất cao nhất trong mỗi giao dịch

*Ví dụ chuẩn của giảng viên (min_sup = 3):*
```
TID  Items bought              (ordered) frequent items
100  {f,a,c,d,g,i,m,p}         {f,c,a,m,p}
200  {a,b,c,f,l,m,o}           {f,c,a,b,m}
300  {b,f,h,j,o,w}             {f,b}
400  {b,c,k,s,p}               {c,b,p}
500  {a,f,c,e,l,p,m,n}         {f,c,a,m,p}
```
f-list: f:4, c:4, a:3, b:3, m:3, p:3

*Bước 2 — Khai phá từ FP-tree:*
- Với mỗi frequent item $p$: đi theo header table, gom mọi **transformed prefix path** → **conditional pattern base** của $p$
- Dựng **conditional FP-tree** từ pattern base (chỉ giữ item frequent trong base)
- **Đệ quy** cho tới khi cây rỗng hoặc chỉ còn một đường (single path → sinh mọi tổ hợp sub-path)

*Trường hợp đặc biệt — single prefix path:* tách thành 2 phần: **Reduction** (thu gọn prefix path thành 1 node) + **Concatenation** (ghép kết quả prefix path với subtree còn lại).

**Ưu điểm (giảng viên liệt kê rõ — dùng làm luận điểm so sánh trong báo cáo):**
1. **Divide-and-conquer:** phân rã cả tác vụ lẫn CSDL theo pattern đã tìm được → tìm kiếm tập trung trên CSDL nhỏ hơn
2. Không sinh candidate, không kiểm tra candidate
3. CSDL được nén bằng cấu trúc FP-tree
4. Không quét lặp lại toàn bộ CSDL
5. Thao tác cơ bản chỉ là đếm local frequent item và dựng sub FP-tree — không có tìm kiếm/so khớp pattern

**Cài đặt tham chiếu:** FPGrowth+ (Grahne & Zhu, FIMI'03)

#### A.5. ECLAT — Zaki et al., KDD'97

- **Vertical format:** $t(AB) = \{T_{11}, T_{25}, \dots\}$ — tid-list của các giao dịch chứa itemset $AB$
- **Suy diễn:** $t(X) = t(Y)$ ⇒ X và Y luôn xuất hiện cùng nhau; $t(X) \subseteq t(Y)$ ⇒ mọi giao dịch có X đều có Y
- **Diffsets** để tăng tốc: chỉ lưu phần khác biệt
  Ví dụ: $t(X)=\{T_1,T_2,T_3\}$, $t(XY)=\{T_1,T_3\}$ ⇒ $\text{Diffset}(XY,X)=\{T_2\}$
- **CHARM** (Zaki & Hsiao, SDM'02) cho closed patterns

#### A.6. ⭐ Interestingness Measures — điểm nhấn của giảng viên

Giảng viên dành **4/39 slide** (10% thời lượng chương) cho phần này. Đây là **tín hiệu chấm điểm mạnh**: đa số nhóm sẽ dừng ở support/confidence; nhóm nào dùng đúng độ đo null-invariant sẽ nổi bật rõ rệt.

**Vấn đề của support & confidence — ví dụ kinh điển:**
```
              Basketball  Not Basketball  Row Sum
Cereal           2000          1750         3750
Not Cereal       1000           250         1250
Column Sum       3000          2000         5000
```
- Luật `play basketball → eat cereal` [support 40%, confidence 66.7%] **gây hiểu nhầm**
- Vì tỷ lệ chung ăn cereal là 75% > 66.7% ⇒ chơi bóng rổ thực ra **làm giảm** xác suất ăn cereal
- Luật `play basketball → NOT eat cereal` [20%, 33.3%] chính xác hơn dù support/confidence thấp hơn

**Lift:**
$$\text{lift}(A,B) = \frac{P(A \cap B)}{P(A)\cdot P(B)}$$
$\text{lift}(B,C) = \dfrac{2000/5000}{(3000/5000)(3750/5000)} = 0.89$ (tương quan âm)
$\text{lift}(B,\neg C) = \dfrac{1000/5000}{(3000/5000)(1250/5000)} = 1.33$ (tương quan dương)

**Phê phán tiếp:** `"buy walnuts → buy milk [1%, 80%]"` gây hiểu nhầm nếu 85% khách hàng vốn đã mua sữa.

**Tính null-invariance** (bất biến với giao dịch null — giao dịch không chứa cả A lẫn B):

| Độ đo | Công thức | Null-invariant? |
|-------|-----------|-----------------|
| $\chi^2(a,b)$ | thống kê chi-bình phương | ❌ **Không** |
| Lift$(a,b)$ | $P(a,b)/[P(a)P(b)]$ | ❌ **Không** |
| AllConf$(a,b)$ | $\dfrac{\sup(a,b)}{\max\{\sup(a),\sup(b)\}}$ | ✅ Có |
| Coherence$(a,b)$ | $\dfrac{\sup(a,b)}{\sup(a)+\sup(b)-\sup(a,b)}$ | ✅ Có |
| Cosine$(a,b)$ | $\dfrac{\sup(a,b)}{\sqrt{\sup(a)\cdot\sup(b)}}$ | ✅ Có |
| Kulczynski$(a,b)$ | $\dfrac{P(a\mid b)+P(b\mid a)}{2}$ | ✅ Có |
| MaxConf$(a,b)$ | $\max\left\{\dfrac{\sup(a,b)}{\sup(a)}, \dfrac{\sup(a,b)}{\sup(b)}\right\}$ | ✅ Có |

**Ba thuộc tính đánh giá độ đo** (Tan, Kumar, Srivastava @ KDD'02 — hơn 20 độ đo đã được đề xuất):
- **P1:** bằng 0 khi A và B độc lập thống kê
- **O1:** đối xứng khi hoán vị biến
- **O4:** null invariance

| Ký hiệu | Độ đo | Miền giá trị | P1 | O1 | O4 |
|---------|-------|--------------|----|----|----|
| $\phi$ | φ-coefficient | $[-1,1]$ | Yes | Yes | No |
| $c$ | Confidence | $[0,1]$ | No | No** | Yes |
| IS | Cosine | $[0,\sqrt{P(A,B)}]$ | No | Yes | Yes |
| $\zeta$ | Jaccard | $[0,1]$ | Yes | No | Yes |

> **Kết luận của giảng viên (nguyên văn Key Insight, tr.39):** *"Null-(transaction) invariance is crucial for correlation analysis."* — Không độ đo nào thỏa mãn **tất cả** thuộc tính.

#### A.7. Các mở rộng được nêu tên (dùng cho phần "Hướng phát triển")

| Hướng | Thuật toán | Nguồn |
|-------|-----------|-------|
| Closed / max itemsets | CLOSET, FPclose, FPMax | DMKD'00, FIMI'03 |
| Sequential patterns | PrefixSpan, CloSpan, BIDE | ICDE'01, SDM'03, ICDE'04 |
| Graph patterns | gSpan, CloseGraph | ICDM'02, KDD'03 |
| Constraint-based mining | Convertible constraints, gPrune | ICDE'01, PAKDD'03 |
| Iceberg data cubes | H-tree, H-cubing, Star-cubing | SIGMOD'01, VLDB'03 |
| Pattern-growth clustering | MaPle | ICDM'03 |
| **Pattern-growth classification** | **Discriminative frequent patterns** | **Cheng et al., ICDE'07** |

> ⭐ Dòng cuối cùng là **cầu nối hợp pháp giữa FPM và Machine Learning** — cho phép nhóm thêm lớp phân loại/ROC-AUC mà vẫn ở trong khuôn khổ môn học.

---

### 2.B. NHÓM FINDING SIMILAR ITEMS

#### B.0. Learning objectives do giảng viên nêu (tr.3) — dùng làm checklist báo cáo

1. Giải thích vì sao tìm item tương tự là bài toán DM nền tảng
2. Biểu diễn tài liệu thành tập bằng **k-shingling**
3. Tính **min-hash signature** gọn và hiểu tính chất then chốt của nó
4. Áp dụng **LSH** để tìm candidate pairs hiệu quả
5. **Phân tích false positives / false negatives** trong pipeline LSH
6. **Tinh chỉnh tham số $b, r, k, n$** cho một ngưỡng tương tự cho trước

#### B.1. Bài toán và động lực

**Ứng dụng:** near-duplicate web pages · phát hiện đạo văn · recommendation (khách hàng mua sản phẩm tương tự) · so khớp ảnh/video · genomics.

**Thách thức quy mô:** so sánh tất cả cặp = $\binom{N}{2} = O(N^2)$.
Với $N = 10^9$ trang web ⇒ $\approx 5\times10^{17}$ phép so sánh — **hoàn toàn bất khả thi**.

**Mục tiêu:** giảm về $O(N)$ hoặc $O(N\cdot k)$ với $k$ nhỏ, vẫn tìm được **phần lớn** cặp thực sự tương tự.
**Ý tưởng cốt lõi:** *không cần kết quả chính xác — chấp nhận sai số nhỏ, có kiểm soát.*

#### B.2. Jaccard Similarity

$$\text{sim}(S_1,S_2) = \frac{|S_1 \cap S_2|}{|S_1 \cup S_2|} \qquad d(S_1,S_2) = 1 - \text{sim}(S_1,S_2)$$

#### B.3. Pipeline ba bước

```
Raw Documents ──Shingling──> Sets ──Min-Hash──> Signatures ──LSH──> Candidate Pairs ──verify──> Similar Pairs
                 text→sets            sets→sigs           sigs→candidates
```

#### B.4. Shingling

**Định nghĩa:** k-shingle (= k-gram) là **chuỗi con liên tiếp độ dài k**. Tài liệu $D$ được biểu diễn bằng **tập tất cả k-shingle phân biệt**.

**Vì sao không dùng tập từ (bag of words):** từ cực phổ biến ("the", "of", "and") sẽ chi phối điểm Jaccard — hai tài liệu không liên quan vẫn có vẻ tương tự chỉ vì cùng chứa stop word.
Ví dụ: $D_1=\{$the,cat,sat,on,mat$\}$, $D_2=\{$the,dog,sat,on,mat$\}$ ⇒ sim $=4/6\approx0.67$ (sai lệch).

**Chọn k:** k phải đủ lớn để một shingle bất kỳ **khó xuất hiện ngẫu nhiên** trong tài liệu khác.

| Cấp độ | Tham số | Khuyến nghị |
|--------|---------|-------------|
| **Ký tự** | $\|\Sigma\|=27$ (26 chữ + space); $27^5 = 14{,}348{,}907$ 5-shingle khả dĩ | $k=5$ cho email (~1K ký tự); $k=9$ cho web page (~100K ký tự) |
| **Từ** | $\|V\| \approx 50{,}000$ | $k=2$ tốt cho hầu hết tài liệu; $k=3$ cho tài liệu rất dài. Tự động tránh lạm phát do stop word |

**Hashing shingles:** ánh xạ mỗi shingle sang số nguyên (VD hash 32-bit) để giảm lưu trữ:
`{the cat, cat sat, sat on, ...} → {17304, 82514, 3901, ...}`

**Ví dụ chuẩn:** $D_1$="the cat sat on the mat", $D_2$="the cat sat on a mat", 2-word shingles ⇒ $|D_1\cap D_2|=3$, $|D_1\cup D_2|=7$, sim $=3/7\approx0.43$.

**Boolean matrix:** hàng = mọi shingle khả dĩ (universe $U$); cột = tài liệu; ô $(r,c)=1$ ⟺ tài liệu $c$ chứa shingle $r$. Vấn đề: ma trận khổng lồ (tỷ shingle × triệu tài liệu).

#### B.5. Min-Hashing

**Định nghĩa:** cho hoán vị ngẫu nhiên $\pi$ của các hàng $1,\dots,|U|$:
$$h_\pi(D) = \text{chỉ số hàng ĐẦU TIÊN (theo thứ tự } \pi\text{) mà } D \text{ có giá trị } 1$$

**⭐ ĐỊNH LÝ MIN-HASH:**
$$P\big[h_\pi(D_1) = h_\pi(D_2)\big] = \text{sim}(D_1,D_2) = \frac{|D_1\cap D_2|}{|D_1\cup D_2|}$$

**Phác thảo chứng minh (giảng viên trình bày đầy đủ — nên tái hiện trong báo cáo):**
- Xét tập $D_1 \cup D_2$ (các hàng có ít nhất một cột bằng 1)
- Mỗi hàng trong $D_1\cup D_2$ có xác suất **bằng nhau** được $\pi$ xếp đầu tiên: $P[\pi(r)=\min\pi(D_1\cup D_2)] = 1/|D_1\cup D_2|$
- Gọi $r^*$ là hàng thắng. Ta có $h_\pi(D_1)=h_\pi(D_2)$ **khi và chỉ khi** $r^* \in D_1\cap D_2$
- Vì $r^*$ phân bố đều trên $D_1\cup D_2$ ⇒ $P = \dfrac{|D_1\cap D_2|}{|D_1\cup D_2|}$ ∎

**Signature matrix:** dùng $n$ hoán vị độc lập:
$$\text{sig}(D) = \big(h_{\pi_1}(D), h_{\pi_2}(D), \dots, h_{\pi_n}(D)\big)$$
$$\widehat{\text{sim}}(D_1,D_2) = \frac{|\{i : h_{\pi_i}(D_1)=h_{\pi_i}(D_2)\}|}{n}$$
Theo luật số lớn, $n\to\infty \Rightarrow \widehat{\text{sim}}\to\text{sim}$. **Thực tế $n = 100$–$500$**; $n=100$ cho sai số < 1%.

**Cài đặt hiệu quả** (hoán vị thật quá tốn kém):
Dùng $h_i(r) = (a_i\cdot r + b_i) \bmod p$ với $a_i,b_i$ ngẫu nhiên, $p$ nguyên tố $\geq |U|$.

Thuật toán **one-pass** (khởi tạo $\text{sig}(i,D)=+\infty$):
```
for each row r in boolean matrix:          # mỗi shingle
    compute h1(r), h2(r), ..., hn(r)
    for each document D with a 1 in row r:
        sig(i,D) ← min(sig(i,D), hi(r))    for i = 1..n
```
Chỉ cần **một lượt quét** toàn bộ shingle.

#### B.6. Locality-Sensitive Hashing (LSH)

**Vấn đề còn lại:** so sánh mọi cặp signature vẫn là $O(N^2\cdot n)$.

**Mục tiêu:** tìm $f(x,y)$ sao cho sim$(x,y)\geq t$ ⇒ candidate (xác suất cao); sim$(x,y)<t$ ⇒ không candidate (xác suất cao).

**Kỹ thuật banding:** chia $n$ hàng của signature matrix thành $b$ band, mỗi band $r$ hàng ($n = b\cdot r$).
- Mỗi band: hash **đoạn cột $r$ hàng** vào một trong $k$ bucket
- Hai tài liệu là **candidate pair** nếu hash vào **cùng bucket ở ít nhất một band**

**⭐ PHÂN TÍCH XÁC SUẤT (S-curve):**
Với hai tài liệu có độ tương tự $s$:
1. $P[\text{khớp toàn bộ } r \text{ hàng của một band}] = s^r$
2. $P[\text{lệch ít nhất 1 hàng trong band đó}] = 1-s^r$
3. $P[\text{lệch ở MỌI band}] = (1-s^r)^b$
4. $$\boxed{f(s) = P[\text{trở thành candidate pair}] = 1-(1-s^r)^b}$$

**Ngưỡng xấp xỉ:** $t \approx (1/b)^{1/r}$ — điểm mà $f(t)\approx 1/2$, nơi S-curve dốc nhất.

**Hai ví dụ số của giảng viên** (nên tái hiện + mở rộng trong thực nghiệm):

*Ví dụ 1 — độ tương tự cao, $s=0.80$, $b=20$, $r=5$:*
1. $0.8^5 = 0.328$
2. $1-0.328 = 0.672$
3. $0.672^{20} = 0.00035$
4. $P[\text{candidate}] = 1-0.00035 = \mathbf{99.965\%}$
→ Chỉ 0.035% cặp thực sự tương tự bị bỏ sót (false negative)

*Ví dụ 2 — độ tương tự thấp, $s=0.30$, $b=20$, $r=5$:*
1. $0.3^5 = 0.00243$
2. $1-0.00243 = 0.99757$
3. $P[\text{candidate}] = 1-0.99757^{20} = \mathbf{4.74\%}$
→ 95.26% cặp không tương tự bị loại **không tốn chi phí kiểm chứng**
→ Kiểm tra ngưỡng: $t\approx(1/20)^{1/5} = 0.05^{0.2}\approx 0.55$ — xác nhận $s=0.30$ nằm dưới ngưỡng

**Bảng tinh chỉnh tham số của giảng viên:**

| Cấu hình | $b$ | $r$ | Hiệu ứng |
|----------|-----|-----|----------|
| $n=100$, $t=0.5$ | 20 | 5 | Cân bằng |
| $n=100$, $t=0.8$ | 25 | 4 | S-curve dốc hơn; ít FN ở $s$ cao |
| $n=100$, $t=0.3$ | 10 | 10 | S-curve thoải; bắt được cặp tương tự thấp |
| $n=300$, $t=0.5$ | 60 | 5 | Dốc hơn nhiều; FP và FN đều thấp |

> **Quy tắc ngón tay cái:** $b$ lớn ⇒ hạ ngưỡng; $r$ lớn ⇒ nâng ngưỡng; tăng $n$ ⇒ giảm đồng thời cả FP lẫn FN.

**Độ phức tạp toàn pipeline:** $O(N\cdot k)$ shingling + $O(N\cdot n)$ signature + $O(N\cdot b)$ LSH + $O(\text{candidates}\cdot n)$ verification — **tất cả dưới tuyến tính so với $N^2$**.

#### B.7. Mở rộng được nêu tên

- **LSH families khác:** Cosine similarity (random hyperplane projections), Euclidean distance (random projection LSH)
- **Nền tảng lý thuyết:** Indyk & Motwani (1998) — bài báo LSH gốc; Broder et al. (1997) — resemblance & containment
- **SimHash** (Charikar, 2002) — dùng rộng rãi trong search engine
- **FAISS** (Meta AI) — thư viện ANN quy mô tỷ vector

---

### 2.C. NHÓM DATA STREAMING

#### C.1. Mô hình luồng dữ liệu

**Bối cảnh ứng dụng:** cảm biến IoT (nhiệt độ, độ ẩm, GPS, nhịp tim) · giao dịch tần số cao (triệu lệnh/giây, quyết định trong micro-giây) · cập nhật Twitter/Facebook · truy vấn search engine · cuộc gọi, gói tin IP.

**Đặc điểm (nguyên văn slide tr.7):**
- Tốc độ đầu vào do **nguồn bên ngoài** kiểm soát — bộ xử lý **không** điều khiển được
- **Vô hạn** — không biết trước kích thước
- **Phi dừng (non-stationary)** — phân phối thay đổi theo mùa/ngày/giờ
- Mô hình: chuỗi vô hạn $S = (i_1, i_2, \dots, i_k, \dots)$

**Kiến trúc xử lý:** Streams → Processor (Limited Working Storage) → Output; hỗ trợ **Standing Queries** (thường trực) và **Ad-Hoc Queries**; có Archival Storage.

**Ràng buộc cốt lõi:** *"Phải xử lý ngay — nếu không sẽ mất dữ liệu mãi mãi!"*

> **Nguyên tắc xuyên suốt chương:** **Đánh đổi độ chính xác lấy tốc độ và bộ nhớ.**

**Năm bài toán nghiên cứu:** (1) Sampling · (2) Filtering · (3) Count-Distinct · (4) Moment Estimation · (5) Sliding Window Queries.

#### C.2. Lấy mẫu (Sampling)

**Hai bài toán con:** lấy mẫu **tỷ lệ cố định** (giữ tỷ lệ $p$) · giữ mẫu **kích thước cố định** (luôn đúng $s$ phần tử).

**⭐ Vì sao lấy mẫu ngây thơ SAI** (bài học quan trọng, giảng viên dẫn giải chi tiết):

Bài toán: luồng bộ (user, query, time); hỏi *"tỷ lệ truy vấn trùng lặp là bao nhiêu?"*. Giữ 10% luồng.
Gọi $a$ = số truy vấn xuất hiện đúng 1 lần, $b$ = số truy vấn xuất hiện 2 lần. Tổng $a+2b$ phần tử. **Đáp án đúng: $\dfrac{b}{a+b}$.**

- $P(\text{truy vấn đơn được chọn}) = \dfrac{a}{10}$
- $P(\text{truy vấn đôi được chọn cả hai lần}) = \dfrac{b}{100}$
- $P(\text{truy vấn đôi được chọn đúng 1 lần}) = \dfrac{18b}{100}$

Ước lượng thu được:
$$\frac{b/100}{a/10 + b/100 + 18b/100} = \frac{b}{10a+19b} \;\neq\; \frac{b}{a+b}$$

**Giải pháp — lấy mẫu theo ĐƠN VỊ đúng (theo user, không theo query):**
- Băm khóa (tên người dùng) đồng đều vào $b$ bucket
- Giữ bộ dữ liệu nếu giá trị băm $\leq a$ ⇒ tỷ lệ mẫu $= a/b$ (VD $a=3, b=10$ ⇒ mẫu 30%)

> **Bài học của giảng viên:** *"Phải cẩn thận chọn đúng đơn vị lấy mẫu tùy theo bài toán cụ thể."*

**Reservoir Sampling** (giữ đúng $s$ phần tử, mỗi phần tử có xác suất $s/n$):
```
1. Lưu s phần tử đầu tiên vào hồ chứa
2. Khi phần tử thứ n đến (n > s):
   • Với xác suất s/n : giữ phần tử mới, thay thế ngẫu nhiên 1 phần tử trong hồ chứa
   • Với xác suất 1−s/n: bỏ qua
```

**Chứng minh quy nạp** (giảng viên trình bày đầy đủ):
- *Cơ sở:* $s$ phần tử đầu có xác suất $s/s = 1$ ✓
- *Giả thuyết:* sau $n$ phần tử, mỗi phần tử có xác suất $s/n$
- *Bước quy nạp:* xác suất phần tử $n+1$ ở lại mẫu:
$$\underbrace{\left(1-\frac{s}{n+1}\right)}_{\text{không được chọn}} + \underbrace{\frac{s}{n+1}\cdot\frac{s-1}{s}}_{\text{được chọn nhưng không bị thay}} = \frac{n}{n+1}$$
- Phần tử cũ có xác suất $s/n$, "sống sót" với xác suất $n/(n+1)$:
$$\frac{s}{n}\cdot\frac{n}{n+1} = \frac{s}{n+1} \;\checkmark$$

#### C.3. Lọc (Filtering)

**Bài toán:** chỉ cho qua một số phần tử nhất định nhưng **không đủ bộ nhớ** lưu toàn bộ khóa so sánh. Ví dụ điển hình: lọc spam — hàng triệu email/phút, không thể giữ danh sách toàn bộ email hợp lệ trong RAM.

**Lọc bằng một hàm băm:**
1. Tập khóa $I$ cần giữ (địa chỉ email hợp lệ)
2. Mảng bit $B$ gồm $n$ bit, khởi tạo 0
3. Hàm băm $h$ miền $[0,n)$; với mỗi $i\in I$: đặt $B[h(i)]=1$
4. Xử lý luồng: cho qua phần tử $s$ nếu $B[h(s)]=1$

**Đặc tính:** **không có false negative** (mọi phần tử hợp lệ đều qua), nhưng **có false positive**.

**Xác suất false positive:** tương đương ném $m$ mũi tên vào $n$ ô:
$$P_{FP} = 1 - e^{-m/n}$$

*Ví dụ:* $|I|=10^9$ email hợp lệ, $|B|=1\text{GB}=8\times10^9$ bit ⇒ $1-e^{-1/8} \approx 0.1175$ ⇒ **11.75% spam vẫn lọt qua**.

**⭐ BLOOM FILTER:**
- Mảng bit $B$ gồm $n$ bit + **$k$ hàm băm** $h_1,\dots,h_k$
- Khởi tạo: với mỗi khóa $i\in I$ và mỗi $h_j$: đặt $B[h_j(i)]=1$
- Kiểm tra: cho qua $s$ **chỉ khi tất cả $k$ bit** $h_1(s),\dots,h_k(s)$ đều bằng 1

**Phân tích:** tương đương ném $k\cdot m$ mũi tên vào $n$ ô ⇒ tỷ lệ bit 1 = $1-e^{-km/n}$
$$\boxed{P_{FP} = \left(1-e^{-km/n}\right)^k}$$

**Số hàm băm tối ưu:**
$$\boxed{k^* = \frac{n}{m}\ln 2}$$

*Ví dụ của giảng viên:* $m=10^9$, $n=8\times10^9$ bit ⇒ $k^* = 8\ln 2 \approx 5.5 \approx 6$
⇒ FP giảm từ **11.75%** (1 hàm băm) xuống **≈ 2.2%** (6 hàm băm)

**Tổng kết Bloom Filter:** không có false negative · FP tối thiểu, điều chỉnh qua $k$ · các hàm băm chạy **song song** · có thể chia $B$ thành $k$ phần.
**Ứng dụng thực tế được nêu tên:** Google Bigtable, Apache Cassandra, Redis, trình duyệt web (kiểm tra URL độc hại).

#### C.4. Đếm phần tử phân biệt — Flajolet-Martin

**Ứng dụng:** bao nhiêu từ khác nhau xuất hiện trên các trang web (phát hiện spam)? · bao nhiêu sản phẩm phân biệt bán trong tuần? · bao nhiêu IP duy nhất truy cập máy chủ?

**Thuật toán:**
1. Chọn hàm băm $h$ ánh xạ $N$ phần tử thành ít nhất $\log_2 N$ bit
2. Với mỗi phần tử $s$: tính $r(s)$ = **số số 0 ở cuối** (trailing zeros) của biểu diễn nhị phân
   VD: $h(s) = 12_{10} = 1100_2$ ⇒ 2 số 0 cuối ⇒ $r(s)=2$
3. Duy trì $R = \max_s r(s)$ trên toàn luồng
4. **Ước lượng: số phần tử phân biệt $\approx 2^R$**

**Trực giác:** với hàm băm đồng đều, tỷ lệ $2^{-r}$ phần tử có ít nhất $r$ số 0 ở cuối ⇒ cần khoảng $2^r$ phần tử để xuất hiện một phần tử có $r$ số 0 cuối.

**Nhược điểm & khắc phục:** kỳ vọng $E[2^R]$ có thể rất lớn (phương sai cao). Dùng $m$ hàm băm:
- Trung bình → dễ bị outlier
- Trung vị → tốt hơn nhưng kết quả luôn là lũy thừa của 2
- **Tốt nhất:** chia $m$ hàm băm thành $g$ nhóm → tính **trung bình trong mỗi nhóm** → lấy **trung vị của các trung bình**

| Phương pháp | Bộ nhớ | Độ chính xác |
|-------------|--------|--------------|
| Lưu toàn bộ | $O(N)$ | Chính xác 100% |
| FM đơn | $O(\log N)$ bit | Cao nhưng có outlier |
| FM kết hợp | $O(m\log N)$ bit | Tốt, kiểm soát được |

#### C.5. Ước lượng mô-men — AMS

**Định nghĩa:** luồng $S$ có $N$ giá trị phân biệt, $m_i$ = số lần phần tử thứ $i$ xuất hiện. Mô-men bậc $n$:
$$\sum_{i\in S}(m_i)^n$$

*Ví dụ:* luồng `a, b, a, c, a, b` ⇒ $m_a=3, m_b=2, m_c=1$
- Bậc 0: $1+1+1=3$ (**số phần tử phân biệt**)
- Bậc 1: $3+2+1=6$ (**độ dài luồng**)
- Bậc 2: $9+4+1=14$ (**số bất ngờ / surprise number**)

**Số bất ngờ (surprise number)** — đo mức độ không đồng đều của phân phối:
- Phân phối đồng đều, tần suất 5,4,4,4,3 ⇒ $25+16+16+16+9 = 82$
- Phân phối có ngoại lệ, tần suất 16,1,1,1,1 ⇒ $256+4 = 260$
> Số bất ngờ lớn ⇒ phân phối lệch. **Ứng dụng: phát hiện bất thường (anomaly), tắc nghẽn mạng.**

**Thuật toán AMS (Alon-Matias-Szegedy):** duy trì các biến ngẫu nhiên $X$ với `X.val` (giá trị phần tử) và `X.c` (số lần phần tử đó xuất hiện **từ vị trí chọn trở đi**):
```
1. Chọn ngẫu nhiên vị trí i từ 1 đến n
2. Khi luồng đến vị trí i: X.val = s_i, X.c = 1
3. Mỗi lần gặp lại X.val trong luồng: X.c += 1
```

**Ước lượng mô-men bậc 2:** $\hat f = n(2\,X.c - 1)$. Với $k$ biến:
$$\hat f = \frac{n}{k}\sum_{j=1}^{k}\big(2X_j.c - 1\big)$$

**Ví dụ đầy đủ của giảng viên** ($n=15$): `a b c b d a c d a b d c a a b`
$m_a=5, m_b=4, m_c=3, m_d=3$ ⇒ số bất ngờ thực tế $= 25+16+9+9 = 59$

| Biến | Vị trí | val | c (cuối luồng) |
|------|--------|-----|----------------|
| $X_1$ | 3 | c | 3 |
| $X_2$ | 8 | d | 2 |
| $X_3$ | 13 | a | 2 |

$$\hat f = \frac{15}{3}\big[(2\cdot3-1)+(2\cdot2-1)+(2\cdot2-1)\big] = 5(5+3+3) = 55$$

**Chứng minh tính không chệch** (giảng viên trình bày đầy đủ):
Đặt $f(X)=n(2c-1)$, $c_t$ = số lần phần tử xuất hiện từ vị trí $t$ tới cuối:
$$E[f(X)] = \frac1n\sum_{t=1}^{n}n(2c_t-1) = \sum_{t=1}^{n}(2c_t-1) = \sum_a\big(1+3+\dots+(2m_a-1)\big) = \sum_a (m_a)^2$$
⇒ Theo kỳ vọng, công thức cho **chính xác** mô-men bậc 2. ∎

**Tổng quát cho mô-men bậc $k$:** $n\big(c^k - (c-1)^k\big)$

**⭐ BÀI TẬP GIẢNG VIÊN GIAO (slide tr.50):**
> 1. Chứng minh công thức tổng quát cho mô-men bậc $k$.
> 2. Cho luồng `3, 1, 4, 1, 3, 4, 2, 1, 2` — tính số bất ngờ (mô-men bậc 2) và mô-men bậc 3.

*(Tín hiệu: giảng viên coi trọng suy diễn thủ công. Báo cáo nên có phần "worked example" tính tay.)*

**Luồng vô hạn (không biết $n$):** dùng **Reservoir Sampling** để chọn $k$ vị trí — nhận phần tử mới làm biến mới với xác suất $k/n$; trong công thức ước lượng dùng **độ dài hiện tại** của luồng làm $n$.

#### C.6. Cửa sổ trượt — DGIM

**Bài toán:** cho luồng bit 0/1, trả lời *"có bao nhiêu bit 1 trong $k$ bit gần nhất ($k \leq N$)?"* khi **không thể lưu $N$ bit**.
Câu hỏi minh họa của giảng viên: *"Trong 1 triệu gói tin IP gần nhất, có bao nhiêu gói từ địa chỉ bị nghi ngờ?"*

**Ý tưởng ban đầu — cửa sổ mũ:** tóm tắt vùng luồng trong các **bucket kích thước tăng theo cấp số nhân**, lưu số đếm bit 1 mỗi bucket.
*Ưu:* chỉ cần $O(\log^2 N)$ bit; cập nhật dễ; sai số ≤ 50% nếu bit 1 phân bố đều.
*Nhược lớn:* nếu **tất cả** bit 1 nằm trong vùng chưa biết ⇒ **sai số không giới hạn**.

**⭐ DGIM cải tiến — bucket chứa số bit 1 CỐ ĐỊNH (lũy thừa của 2: 1,1,2,4,8,16,…)**

Mỗi bucket lưu:
- **Timestamp** của bit cuối — lưu dạng `timestamp mod N` ⇒ $O(\log N)$ bit
- **Số bit 1** — luôn là lũy thừa của 2 ⇒ chỉ cần $O(\log\log N)$ bit

**Ràng buộc bất biến trên bucket:**
1. Tối đa **1 hoặc 2** bucket cùng kích thước
2. Các bucket **không chồng lấn** timestamp
3. Bucket mới **nhỏ hơn** bucket cũ hơn
4. Bucket bị **loại bỏ** khi timestamp cuối > $N$

**Cập nhật khi bit mới đến:**
```
Loại bỏ bucket cuối nếu timestamp > N
Nếu bit = 0: không thay đổi gì
Nếu bit = 1:
    Tạo bucket mới kích thước 1
    Nếu có 3 bucket cùng kích thước 1: gộp 2 bucket CŨ NHẤT thành bucket kích thước 2
    Lặp đệ quy cho các kích thước lớn hơn
```
*Minh họa:* `1 1 2 4` + bit 1 → `1 1 1 2 4` → (3 bucket cỡ 1, gộp 2 cũ nhất) → `1 2 2 4` → (2 bucket cỡ 2, gộp đệ quy) → `1 2 4 4`… hoặc `1 2 2 4`

**Truy vấn:**
1. Cộng kích thước **tất cả bucket trừ bucket cũ nhất**
2. Cộng thêm **một nửa** kích thước bucket cũ nhất (vì không biết bao nhiêu phần của nó nằm trong cửa sổ $N$)

*Ví dụ:* bucket `1 1 2 4` ⇒ ước lượng $= 1+1+2+\frac{4}{2} = 6$
- Nếu số thực là 5 ⇒ sai số $1/5 = 20\%$
- Nếu số thực là 8 ⇒ sai số $2/8 = 25\%$
- **Sai số luôn ≤ 50%**

**Giảm sai số:** duy trì $r$ hoặc $r-1$ bucket mỗi kích thước ⇒ sai số $O(1/r)$ — đánh đổi giữa bộ nhớ và độ chính xác.

**Mở rộng:**
- Truy vấn $k < N$: "cắt" tại $k$ và dùng cùng công thức ước lượng
- **Tổng của $k$ số nguyên gần nhất** (mỗi số tối đa $m$ bit): coi mỗi bit như một luồng riêng, ước lượng $\sum_{i=0}^{m-1} c_i\cdot 2^i$ với $c_i$ là ước lượng DGIM cho bit thứ $i$

#### C.7. Bảng tổng kết chương Streaming (nguyên văn slide tr.67)

| Bài toán | Thuật toán | Bộ nhớ | Sai số |
|----------|-----------|--------|--------|
| Lấy mẫu cố định | Reservoir | $O(s)$ | 0 (chính xác) |
| Lọc | Bloom Filter | $O(n)$ bit | FP có kiểm soát |
| Count-Distinct | Flajolet-Martin | $O(\log N)$ bit | Xấp xỉ |
| Mô-men bậc 2 | AMS | $O(k)$ | Xấp xỉ |
| Cửa sổ trượt | DGIM | $O(\log^2 N)$ bit | ≤ 50% |

---

## 3. CÁC KỸ THUẬT TIỀN XỬ LÝ DỮ LIỆU

**⚠️ Ghi chú trung thực:** Slide hiện có **không** dạy tiền xử lý cổ điển (xử lý thiếu giá trị, chuẩn hóa, phát hiện outlier, PCA…). Các kỹ thuật đó là **kiến thức tiên quyết**, không phải trọng tâm chấm điểm. Dưới đây là các phép biến đổi dữ liệu **thực sự được yêu cầu bởi 3 chương đã học**:

| # | Kỹ thuật | Thuộc chương | Vì sao cần |
|---|----------|--------------|-----------|
| 1 | **Transactionization** — gom dòng log/hóa đơn thành "giỏ hàng" (basket) | FPM | Đầu vào bắt buộc của Apriori/FP-Growth/ECLAT |
| 2 | **Item encoding & taxonomy rollup** — quy item chi tiết lên cấp danh mục | FPM | Giảm độ thưa (sparsity); nếu không, mọi itemset đều dưới min_sup |
| 3 | **Discretization / Binning** — rời rạc hóa thuộc tính liên tục thành item | FPM | Bắt buộc khi khai phá luật trên dữ liệu số (VD: nhiệt độ → `temp=high`) |
| 4 | **Shingling** — văn bản → tập k-gram | LSH | Bước 1 của pipeline tìm item tương tự |
| 5 | **Text normalization** — lowercase, bỏ dấu câu, chuẩn hóa khoảng trắng | LSH | Ảnh hưởng trực tiếp tới Jaccard; cần ghi rõ trong báo cáo |
| 6 | **Hashing / feature hashing** — ánh xạ shingle/khóa → số nguyên | LSH, Streaming | Giảm bộ nhớ; là kỹ thuật cốt lõi của cả 3 chương |
| 7 | **Sampling như bước tiền xử lý** — reservoir, hash-based theo đơn vị đúng | Streaming | Giảm quy mô có kiểm soát sai số; **chọn sai đơn vị lấy mẫu ⇒ ước lượng chệch** (§C.2) |
| 8 | **Vertical format transform** — horizontal (TID→items) ⇄ vertical (item→TID-list) | FPM | Bắt buộc cho ECLAT; là một điểm so sánh hiệu năng |
| 9 | **Chuẩn hóa timestamp & sinh luồng sự kiện** — sắp xếp theo thời gian, replay | Streaming | Để mô phỏng luồng từ dataset tĩnh |
| 10 | **Khử trùng lặp (deduplication)** trước khi khai phá | LSH | Chính LSH là công cụ; đồng thời là bước làm sạch |

---

## 4. CÁC PHƯƠNG PHÁP ĐÁNH GIÁ MÔ HÌNH

### 4.1. Đánh giá thuộc khung môn học (ưu tiên cao — chắc chắn được tính điểm)

**Cho Frequent Pattern Mining:**
- Độ đo luật: support, confidence, **lift**, $\chi^2$
- Độ đo null-invariant: **AllConf, Coherence, Cosine, Kulczynski, MaxConf** (+ Imbalance Ratio)
- Số lượng pattern sinh ra theo `min_sup` (đường cong)
- **Thời gian chạy** và **bộ nhớ đỉnh** theo `min_sup` và theo kích thước CSDL
- **Khả năng mở rộng (scalability)** — Apriori vs FP-Growth vs ECLAT
- Số candidate sinh ra (chỉ Apriori) — minh chứng cho 3 điểm nghẽn ở §A.3
- Tỷ lệ nén: #closed patterns / #all patterns

**Cho LSH:**
- **Precision / Recall của candidate pairs** so với ground truth Jaccard brute-force
- **Tỷ lệ False Positive / False Negative** — so sánh **thực nghiệm vs lý thuyết** $f(s)=1-(1-s^r)^b$
- Vẽ **S-curve thực nghiệm** chồng lên S-curve lý thuyết ⇒ minh chứng hiểu bài
- **Speedup** so với brute-force $O(N^2)$
- Sai số ước lượng Jaccard theo số hàm băm $n$ (kỳ vọng < 1% tại $n=100$)

**Cho Streaming:**
- **Sai số tương đối** của ước lượng so với giá trị chính xác (tính offline)
- **Bộ nhớ thực tế** (bytes) vs bộ nhớ lý thuyết ($O(\log N)$, $O(\log^2 N)$…)
- **Thông lượng** (items/giây)
- Tỷ lệ FP thực nghiệm của Bloom Filter vs công thức $(1-e^{-km/n})^k$; đường cong FP theo $k$ và kiểm chứng $k^*=(n/m)\ln 2$
- Sai số DGIM theo $r$ (bucket mỗi kích thước) — kiểm chứng cận 50% và $O(1/r)$

### 4.2. Đánh giá ML cổ điển (chỉ dùng nếu đề tài có lớp dự báo/phân loại)

Cross-Validation (k-fold, stratified) · Confusion Matrix · Precision / Recall / F1 / Accuracy · ROC-AUC, PR-AUC · Hyperparameter tuning (Grid/Random/Bayesian) · Explainability (SHAP, LIME).

**Cho Recommendation (nếu có):** Precision@K, Recall@K, MAP@K, NDCG@K, Coverage, Diversity, Novelty.

> **[GIẢ ĐỊNH]** Các độ đo ở §4.2 hữu ích để nâng chất lượng sản phẩm nhưng **không thay thế** được §4.1. Báo cáo phải đặt §4.1 làm trọng tâm.

---

## 5. CÁC CÔNG CỤ ĐƯỢC PHÉP SỬ DỤNG

**⚠️ [GIẢ ĐỊNH — chưa có văn bản nào của giảng viên quy định công cụ].** Danh sách dưới đây được đề xuất dựa trên (a) nội dung slide và (b) yêu cầu công nghệ trong ROLE. **Cần xác minh với giảng viên** — đặc biệt câu hỏi: *có bắt buộc tự cài đặt thuật toán từ đầu (from scratch) hay được dùng thư viện?*

> **Khuyến nghị an toàn:** cài đặt **from scratch** phần thuật toán lõi (đây chính là phần được chấm), rồi **đối chiếu kết quả với thư viện** để chứng minh tính đúng đắn. Đây là cách vừa chắc điểm vừa thể hiện trình độ.

| Nhóm | Công cụ |
|------|---------|
| **FPM** | `mlxtend` (apriori, fpgrowth, fpmax, association_rules), `efficient-apriori`, `pyECLAT`, `PySpark MLlib FPGrowth`, Weka |
| **LSH** | `datasketch` (MinHash, MinHashLSH, LSHForest, HyperLogLog), `faiss`, `simhash`, cài đặt tay bằng `numpy` |
| **Streaming** | `river` (online ML), `pybloom-live` / `bloom-filter2`, `datasketch.HyperLogLog`, Kafka + Faust (nếu cần luồng thật), cài đặt tay DGIM/AMS/FM |
| **Backend** | Python 3.11+, FastAPI, Pydantic, Uvicorn |
| **ML** | scikit-learn, XGBoost, LightGBM, SHAP |
| **Visualization** | Plotly, Streamlit / Dash |
| **Frontend** | React / Next.js + TailwindCSS |
| **Database** | PostgreSQL (+ Redis nếu cần cache/streaming state) |
| **Deployment** | Docker, Docker Compose |
| **Notebook** | Jupyter Lab |
| **Báo cáo** | LaTeX (khuyến nghị, dễ trình bày công thức) hoặc Word |

---

## 6. TIÊU CHÍ CHẤM ĐIỂM

**🔴 KHÔNG CÓ TÀI LIỆU RUBRIC NÀO ĐƯỢC CUNG CẤP.**

Tôi **không bịa** rubric. Dưới đây là **rubric giả định** xây dựng từ (a) trọng số thời lượng slide, (b) các điểm giảng viên nhấn mạnh, (c) thông lệ BTL cao học PTIT. **Phải được người dùng xác minh trước Phase 3.**

### [GIẢ ĐỊNH] Rubric dự kiến

| # | Tiêu chí | Trọng số dự kiến | Căn cứ suy đoán |
|---|----------|-----------------|-----------------|
| 1 | **Áp dụng đúng thuật toán trong môn học** | 25–30% | 16/17 nhóm bám sát 3 chương; đây là trục chính của môn |
| 2 | **Độ sâu kỹ thuật** — hiểu và trình bày được cơ chế, chứng minh, độ phức tạp | 15–20% | GV trình bày đầy đủ 3 chứng minh (min-hash, reservoir, AMS) và giao bài tập chứng minh |
| 3 | **Thực nghiệm & phân tích tham số** — tuning, đường cong, so sánh lý thuyết vs thực nghiệm | 15–20% | GV dành nhiều slide cho tuning $b,r,k,n,k^*$; có bảng trade-off riêng |
| 4 | **Chất lượng dữ liệu & tiền xử lý** | 10% | Bài học "chọn đúng đơn vị lấy mẫu" |
| 5 | **Sản phẩm demo hoạt động** | 10–15% | Yêu cầu của ROLE; thông lệ BTL |
| 6 | **Báo cáo & trình bày** | 10–15% | Chuẩn luận văn |
| 7 | **Tính mới / không trùng lặp** | 5–10% | 17 nhóm cùng lớp ⇒ trùng lặp bị trừ điểm |

### Câu hỏi cần hỏi giảng viên

1. Có rubric/barem chấm điểm cụ thể không?
2. Có bắt buộc cài đặt thuật toán from scratch không, hay được dùng thư viện?
3. Dataset có bị giới hạn (phải dùng dataset chỉ định) không?
4. Có yêu cầu về quy mô dữ liệu tối thiểu (để thể hiện "massive datasets") không?
5. Hình thức nộp: báo cáo + code + demo trực tiếp? Số trang tối đa?
6. Có được dùng nội dung ngoài slide (VD chương MMDS chưa dạy) không?
7. Ngôn ngữ báo cáo: tiếng Việt hay tiếng Anh?

---

## 7. NHỮNG LƯU Ý CỦA GIẢNG VIÊN (suy ra từ bằng chứng trong slide)

**⚠️ Không có văn bản "lưu ý" riêng. 8 điểm dưới đây được suy ra từ cách giảng viên tổ chức slide — mỗi điểm đều có trích dẫn nguồn.**

| # | Tín hiệu | Bằng chứng | Hệ quả cho đề tài |
|---|----------|-----------|-------------------|
| 1 | **MMDS là kim chỉ nam** | Trích dẫn đích danh 2 lần; slide streaming dùng hình gốc từ mmds.org | Đề tài phải theo tinh thần *massive datasets*: xấp xỉ, one-pass, bộ nhớ giới hạn — không phải ML bảng nhỏ |
| 2 | **Coi trọng chứng minh toán học** | Trình bày đầy đủ 3 chứng minh: định lý min-hash (tr.19), quy nạp reservoir (tr.20–21), kỳ vọng AMS (tr.49) | Báo cáo **phải có** phần suy diễn công thức, không chỉ gọi thư viện |
| 3 | **Coi trọng tinh chỉnh tham số + phân tích sai số** | Slide riêng cho $b,r$ trade-off (tr.32); công thức $k^*$ (tr.32 streaming); 2 ví dụ số S-curve (tr.30–31) | Thực nghiệm **phải có** đường cong tham số và so sánh lý thuyết vs thực nghiệm |
| 4 | **Nhấn mạnh giới hạn của support/confidence** | 4 slide liên tiếp về interestingness + null-invariance (tr.36–39) | Nếu làm FPM: **bắt buộc** dùng Kulczynski/Cosine/AllConf, không dừng ở support/confidence |
| 5 | **Nhấn mạnh chọn sai đơn vị lấy mẫu gây ước lượng chệch** | Dẫn giải đại số đầy đủ $\frac{b}{10a+19b}\neq\frac{b}{a+b}$ (tr.16–17) | Nếu có lấy mẫu: phải biện luận rõ đơn vị lấy mẫu |
| 6 | **Giao bài tập tính tay** | Slide tr.50: "Bài tập — chứng minh công thức tổng quát; tính mô-men bậc 2 và 3 cho luồng cho sẵn" | Báo cáo nên có "worked example" tính tay để đối chiếu với code |
| 7 | **Nêu ứng dụng công nghiệp thực tế** | Bigtable, Cassandra, Redis, trình duyệt (tr.33); FAISS, SimHash (tr.35) | Phần "cơ sở lý thuyết" nên liên hệ hệ thống thực tế ⇒ đúng chất Information Systems |
| 8 | **Song ngữ** | Chương FPM & LSH: tiếng Anh; chương Streaming: tiếng Việt | Báo cáo tiếng Việt được chấp nhận; thuật ngữ nên để song ngữ |

---

## 8. NHỮNG ĐỀ TÀI ĐÃ CÓ NHÓM ĐĂNG KÝ

**Nguồn:** `Nhóm BTL Môn Khai Phá Dữ Liệu.xlsx` — Lớp HTTT 02, khóa 2025-2027. Tổng 17 nhóm.

| Nhóm | Thành viên | Đề tài | Chương |
|------|-----------|--------|--------|
| 1 | Đặng Anh Quân, Đỗ Đức Long, Trần Hồng Ánh | Ứng dụng Apriori/FP-Growth khai phá luật kết hợp trong dữ liệu mua hàng | A — FPM |
| 2 | Nguyễn Ngọc Minh, Vũ Trung Kiên, Kim Anh Dũng | MinHash & LSH gợi ý phim dựa trên đánh giá MovieLens | B — LSH |
| 3 | Nguyễn Mai Hạnh, Lê Quang Đức, Vũ Quốc Hùng | Data Streaming — cổng kiểm soát & phát hiện Spam/IP độc hại thời gian thực | C — Streaming |
| 4 | Đào Văn Tâm, Lâm Thành Trung, Nguyễn Xuân Tùng | Streaming (Flajolet-Martin, AMS, Bloom Filter) phát hiện đột biến chủ đề trên luồng tin tức | C — Streaming |
| 5 | Nguyễn Ngọc Anh, Nguyễn Thế Huy Hoàng, Mekdala Nounou | Phân khúc khách hàng & khai phá hành vi mua sắm bán lẻ trực tuyến — RFM + K-means + Apriori | A + ngoài |
| 6 | Hoàng Thị Thuỳ Giang, Nguyễn Huy Long, Phạm Đắc Lâm Bách | Phát hiện cảnh bạo lực trong video bằng học máy + đặc trưng CNN | ❌ ngoài syllabus |
| 7 | Nguyễn Đức Anh, Trịnh Đình Đại, Lê Đức Trung | Data Streaming phát hiện khu vực ô nhiễm bất thường | C — Streaming |
| 8 | Nguyễn Văn Toàn, Khamsing Outhaihueng, Hà Phương Nguyên | GameRecommender — frequent pattern mining & association rules gợi ý game Steam | A — FPM |
| 9 | Đinh Hải Dương, Đặng Thùy Trang, Trần Quang Đức Dũng | Thu thập dữ liệu và thử nghiệm tìm kiếm bằng hình ảnh | ❌ ngoài (có thể chạm LSH) |
| 10 | Nguyễn Việt Hưng, Nguyễn Thùy Linh, Đỗ Anh Quang | Phân tích so sánh Apriori, FP-Growth, ECLAT: hiệu năng, bộ nhớ, khả năng mở rộng | A — FPM |
| 11 | Nguyễn Công Đạt, Trương Tuấn Hiệp | Shingling, MinHash, LSH phát hiện đánh giá sản phẩm gần trùng lặp | B — LSH |
| 12 | Nguyễn Ngọc Chung, Phí Đức Nguyên Phương, Nguyễn Quốc Việt | Apriori & FP-Growth dự báo dịch sốt xuất huyết dựa trên dữ liệu khí hậu | A — FPM |
| 13 | Lê Thiện Đức, Lê Thiện Văn, Vũ Hải Nam | Phát hiện trùng lặp tài liệu học thuật quy mô lớn bằng Shingling, MinHash, LSH | B — LSH |
| 14 | Nguyễn Mạnh Cường, Trần Duy Khánh, Nguyễn Đức Hoàng | So sánh Bloom Filter và Counting Bloom Filter trong lọc dữ liệu tốc độ cao | C — Streaming |
| **15** | **Nguyễn Thuý Anh, Trần Thị Thảo, Trần Văn Hanh** | **⬅️ CHƯA ĐĂNG KÝ (nhóm của chúng ta)** | — |
| 16 | Phạm Văn Thọ, Bùi Giang Linh | Luật kết hợp & Market-Basket Model phân tích hành vi mua sắm khách hàng | A — FPM |
| 17 | Trần Đình Dũng, Phạm Minh Hiếu, Nguyễn Quốc Việt | So sánh thuật toán ML phân loại ảnh cháy dựa trên HOG + Color Histogram | ❌ ngoài syllabus |

### Phân bố theo chương (16 nhóm đã đăng ký)

```
Chương A — Frequent Pattern Mining      ██████████████████  6 nhóm (37.5%)   [1, 5, 8, 10, 12, 16]
Chương B — Finding Similar Items        █████████            3 nhóm (18.8%)   [2, 11, 13]
Chương C — Data Streaming               ████████████         4 nhóm (25.0%)   [3, 4, 7, 14]
Ngoài syllabus (CV/ML thuần)            █████████            3 nhóm (18.8%)   [6, 9, 17]
```

**Nhận xét sơ bộ (phân tích đầy đủ ở Phase 2):**
- **Chương A bão hòa nặng** — 6 nhóm, trong đó 3 nhóm (1, 16, và một phần 5) làm gần như **cùng một bài toán market-basket bán lẻ**. Rủi ro trùng lặp cực cao.
- **Chương B & C còn dư địa** nhưng các "use case sách giáo khoa" (phát hiện trùng tài liệu, lọc spam, đếm distinct IP) đều **đã bị lấy**.
- **Không nhóm nào** kết hợp ≥2 chương thành một hệ thống thống nhất.
- **Không nhóm nào** làm về: Process Mining, Sequential Pattern Mining, Fraud Detection tài chính, Telecom churn, hệ hỗ trợ quyết định (DSS), Concept Drift trên luồng, Educational Data Mining.

---

## 9. DANH SÁCH CHỦ ĐỀ CẦN TRÁNH

### 9.1. 🔴 TUYỆT ĐỐI TRÁNH — trùng trực tiếp

| Chủ đề | Trùng với nhóm | Lý do |
|--------|---------------|-------|
| Market-basket / luật kết hợp trên dữ liệu bán lẻ, siêu thị, thương mại điện tử | 1, 5, 16 | 3 nhóm cùng bài toán — thêm nhóm thứ 4 gần như chắc chắn bị đánh giá thấp về tính mới |
| So sánh hiệu năng Apriori vs FP-Growth vs ECLAT | 10 | Nhóm 10 làm đúng đề tài này |
| Gợi ý sản phẩm/nội dung bằng frequent patterns + association rules | 8 | GameRecommender Steam |
| Gợi ý phim bằng MinHash/LSH trên MovieLens | 2 | Trùng cả thuật toán lẫn dataset |
| Phát hiện trùng lặp tài liệu / đạo văn bằng Shingling+MinHash+LSH | 13 | Đây là use case sách giáo khoa, đã bị lấy |
| Phát hiện review sản phẩm gần trùng lặp | 11 | Trùng trực tiếp |
| Lọc spam / IP độc hại thời gian thực bằng Bloom Filter | 3 | Trùng trực tiếp |
| So sánh Bloom Filter vs Counting Bloom Filter | 14 | Trùng trực tiếp |
| Phát hiện đột biến chủ đề trên luồng tin tức (FM + AMS + Bloom) | 4 | Trùng trực tiếp |
| Phát hiện bất thường ô nhiễm môi trường bằng streaming | 7 | Trùng trực tiếp |
| Dự báo dịch bệnh bằng luật kết hợp trên dữ liệu khí hậu | 12 | Trùng trực tiếp |

### 9.2. 🟠 TRÁNH — rủi ro cao dù không trùng

| Chủ đề | Rủi ro |
|--------|--------|
| **Bất kỳ đề tài Computer Vision thuần** (phân loại ảnh, nhận diện video) | Không dùng thuật toán nào của môn học ⇒ rủi ro "lạc đề". Nhóm 6, 9, 17 đang gánh rủi ro này — **không nên bắt chước** |
| **Phân loại/hồi quy tabular thuần túy** (churn, credit scoring bằng XGBoost) | Không có thuật toán MMDS nào ⇒ cùng rủi ro trên |
| Dataset đồ chơi (< 10.000 dòng) | Mâu thuẫn tinh thần "Mining of **Massive** Datasets"; không thể chứng minh scalability |
| Dùng thư viện như hộp đen, không cài đặt/giải thích thuật toán | Trái với tín hiệu #2 và #3 ở §7 |
| Chỉ báo cáo support & confidence | Trái trực tiếp với 4 slide về null-invariance (tín hiệu #4, §7) |
| Đề tài chỉ có notebook, không có sản phẩm chạy được | Trái yêu cầu của ROLE và thông lệ BTL cao học |

### 9.3. 🟢 KHOẢNG TRỐNG CÒN LẠI (đầu vào cho Phase 2 & 3)

Các hướng **chưa nhóm nào chạm tới**, đồng thời vẫn nằm **trong** khung 3 chương đã học:

1. **Kết hợp đa chương thành một kiến trúc thống nhất** — VD: LSH để khử trùng + Streaming để xử lý online + FPM để sinh tri thức. Không nhóm nào làm.
2. **Sequential Pattern Mining** (PrefixSpan/CloSpan/BIDE) — được giảng viên nêu tên ở §A.7 nhưng **không nhóm nào dùng**. Là mở rộng hợp pháp của FPM.
3. **Discriminative Frequent Pattern Analysis** (Cheng et al. ICDE'07) — cầu nối chính danh giữa FPM và ML, được nêu tên trong slide, chưa ai dùng.
4. **Constraint-based mining** (convertible constraints, gPrune) — được nêu tên, chưa ai dùng.
5. **Closed / Max patterns** (CLOSET, FPclose, FPMax) — được dạy kỹ (2 slide) nhưng **không nhóm nào** khai thác góc nén pattern.
6. **Concept drift / phân phối phi dừng trên luồng** — giảng viên nhấn mạnh tính "phi dừng" (§C.1) nhưng không nhóm nào xử lý.
7. **DGIM & sliding-window queries** — chiếm 15 slide (22% chương Streaming) nhưng **chưa nhóm nào** đặt DGIM làm trọng tâm.
8. **Reservoir sampling & AMS surprise number** làm lõi (nhóm 4 chỉ dùng phụ).
9. **Cosine LSH / SimHash / random hyperplane** — nêu ở §B.7, chưa ai dùng (cả 3 nhóm LSH đều dùng Jaccard MinHash).
10. **Lĩnh vực ứng dụng chưa ai chạm:** Process Mining · Telecom · Ngân hàng/Fraud · Logistics · Giáo dục (EDM) · Y tế lâm sàng · ERP/CRM · Smart City giao thông · An ninh mạng (ngoài spam) · Nông nghiệp.

---

## 10. TỔNG KẾT PHASE 1

### Ba kết luận định hình toàn bộ dự án

1. **Đây là môn MMDS, không phải môn ML cổ điển.** Đề tài phải lấy thuật toán FPM / LSH / Streaming làm **lõi**, không phải phần trang trí. Lớp ML (nếu có) phải được nối vào qua cầu nối chính danh — *discriminative frequent patterns* — chứ không gắn rời.

2. **Chương Frequent Pattern Mining đã bão hòa (6/16 nhóm).** Nhóm 15 nên tránh hoàn toàn hướng market-basket bán lẻ. Dư địa tốt nhất nằm ở: kết hợp đa chương · các thuật toán được nêu tên nhưng chưa ai dùng (Sequential Pattern, Closed/Max, SimHash, DGIM) · lĩnh vực ứng dụng chưa ai chạm.

3. **Ba tín hiệu chấm điểm rõ nhất của giảng viên:** (a) chứng minh toán học, (b) tinh chỉnh tham số + so sánh lý thuyết vs thực nghiệm, (c) độ đo null-invariant thay vì chỉ support/confidence. Bất kỳ đề tài nào được chọn cũng phải đáp ứng cả ba.

### Trạng thái các mục yêu cầu của Phase 1

| # | Yêu cầu | Trạng thái |
|---|---------|-----------|
| 1 | Kiến thức đã học trong môn | ✅ Hoàn tất (§1) |
| 2 | Các thuật toán đã được giảng dạy | ✅ Hoàn tất (§2) — 3 chương, 13 thuật toán |
| 3 | Kỹ thuật tiền xử lý dữ liệu | ✅ Hoàn tất (§3) — có ghi chú khoảng trống |
| 4 | Phương pháp đánh giá mô hình | ✅ Hoàn tất (§4) |
| 5 | Công cụ được phép sử dụng | ⚠️ **[GIẢ ĐỊNH]** (§5) — cần xác minh |
| 6 | Tiêu chí chấm điểm | 🔴 **THIẾU TÀI LIỆU** (§6) — rubric giả định, cần xác minh |
| 7 | Lưu ý của giảng viên | ⚠️ Suy ra từ bằng chứng slide (§7) — không có văn bản gốc |
| 8 | Đề tài đã có nhóm đăng ký | ✅ Hoàn tất (§8) — 16/17 nhóm |
| 9 | Chủ đề cần tránh | ✅ Hoàn tất (§9) |

---

*Tài liệu này là đầu ra của Phase 1. Phase 2 (phân tích chi tiết đề tài các nhóm khác, bảng so sánh đầy đủ, đánh giá khả năng trùng lặp) sẽ bắt đầu sau khi được xác nhận.*
