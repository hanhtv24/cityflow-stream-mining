# CHƯƠNG 2. CƠ SỞ LÝ THUYẾT

## 2.1. Mô hình luồng dữ liệu

Một luồng dữ liệu (data stream) là một chuỗi vô hạn các phần tử $S = (i_1, i_2, \ldots, i_k, \ldots)$ đến liên tục, với hai đặc điểm phân biệt nó khỏi cơ sở dữ liệu truyền thống:

- **Vô hạn:** không biết trước kích thước dữ liệu.
- **Phi dừng (non-stationary):** phân phối dữ liệu có thể thay đổi theo thời gian (mùa, ngày, giờ).

Ràng buộc cơ bản của mô hình xử lý luồng: bộ xử lý chỉ có **bộ đệm giới hạn**, không thể lưu toàn bộ luồng, và phải xử lý mỗi phần tử **ngay khi đến** — nếu bỏ lỡ, dữ liệu mất vĩnh viễn. Nguyên tắc thiết kế xuyên suốt là *đánh đổi độ chính xác lấy tốc độ và bộ nhớ*: chấp nhận câu trả lời xấp xỉ có kiểm soát sai số để đạt được khả năng xử lý dưới tuyến tính.

Năm bài toán nghiên cứu kinh điển trên luồng dữ liệu, đều được vận dụng trong đồ án:

1. Lấy mẫu (Sampling)
2. Lọc phần tử (Filtering)
3. Đếm phần tử phân biệt (Count-Distinct)
4. Ước lượng mô-men (Moment Estimation)
5. Truy vấn trên cửa sổ trượt (Sliding Window Queries)

## 2.2. DGIM — Đếm bit 1 trong cửa sổ trượt

### 2.2.1. Phát biểu bài toán

Cho luồng bit $S$ và độ rộng cửa sổ $N$, trả lời truy vấn *"có bao nhiêu bit 1 trong $N$ (hoặc $k \le N$) phần tử gần nhất?"* mà không thể lưu $N$ bit đầy đủ.

### 2.2.2. Ý tưởng: cửa sổ mũ (exponential windows)

DGIM (Datar, Gionis, Indyk, Motwani) tóm tắt luồng bằng các **bucket**, mỗi bucket lưu:
- Timestamp của bit 1 **cuối cùng** trong bucket (dạng modulo $N$).
- Kích thước bucket — là **lũy thừa của 2** ($1, 1, 2, 4, 8, \ldots$).

**Bốn bất biến cấu trúc:**

1. Tối đa $r$ bucket cùng kích thước (thường $r=2$: sơ đồ "1 hoặc 2 bucket").
2. Các bucket không chồng lấn timestamp.
3. Bucket mới nhỏ hơn (hoặc bằng) bucket cũ hơn.
4. Bucket bị loại khi timestamp cuối đã ra khỏi cửa sổ $N$.

### 2.2.3. Cập nhật

Khi bit mới đến: nếu bit = 0, không làm gì. Nếu bit = 1, tạo bucket cỡ 1 mới; nếu xuất hiện $r+1$ bucket cùng cỡ, gộp hai bucket **cũ nhất** thành một bucket cỡ gấp đôi, lặp lại đệ quy nếu cần.

### 2.2.4. Truy vấn và cận sai số

Ước lượng số bit 1 trong $k$ phần tử gần nhất: cộng kích thước mọi bucket nằm trong cửa sổ, **trừ đi một nửa** kích thước bucket cũ nhất (vì không biết chính xác bao nhiêu phần của nó còn nằm trong cửa sổ).

**Định lý (cận sai số):** với $r=2$, sai số tương đối của ước lượng DGIM không vượt quá **50%**. Chứng minh: gọi $B$ là kích thước bucket cũ nhất, $c$ là số bit 1 thật trong cửa sổ. Trường hợp xấu nhất ước lượng thừa xảy ra khi chỉ 1 bit của bucket cũ nhất còn trong cửa sổ; trường hợp xấu nhất ước lượng thiếu xảy ra khi toàn bộ $B$ bit còn trong cửa sổ. Theo bất biến 1, tổng các bucket nhỏ hơn $B$ ít nhất bằng $B-1$, nên $c \ge B$, và:

$$\frac{|\hat c - c|}{c} \le \frac{B/2}{B} = 50\%$$

Với $r$ bucket mỗi kích thước, sai số giảm theo quan hệ $O(1/r)$: tăng $r$ giúp giảm sai số với chi phí bộ nhớ tăng thêm không đáng kể.

**Độ phức tạp bộ nhớ:** mỗi bucket cần $O(\log N)$ bit cho timestamp và $O(\log\log N)$ bit cho kích thước; số bucket tối đa là $O(r\log N)$, cho tổng bộ nhớ $O(r\log^2 N)$ — logarit theo $N$, so với $O(N)$ của việc lưu cửa sổ đầy đủ.

### 2.2.5. Mở rộng: tổng của các số nguyên

DGIM mở rộng cho bài toán ước lượng **tổng** (không chỉ đếm) của $k$ số nguyên gần nhất: mỗi số nguyên có tối đa $m$ bit, mỗi vị trí bit được coi là một luồng bit riêng và đếm bằng một instance DGIM độc lập. Ước lượng tổng:

$$\widehat{\text{sum}} = \sum_{i=0}^{m-1} \hat c_i \cdot 2^i$$

với $\hat c_i$ là ước lượng DGIM của luồng bit thứ $i$. Phần mở rộng này được nêu tên trong tài liệu giảng dạy nhưng không triển khai chi tiết cách phân bổ ngân sách bộ nhớ giữa các luồng bit — khoảng trống này được đồ án khai thác thành câu hỏi nghiên cứu độc lập (Chương 5, thực nghiệm E4).

## 2.3. Flajolet-Martin — Đếm phần tử phân biệt

### 2.3.1. Ý tưởng

Cho hàm băm $h$ ánh xạ phần tử vào ít nhất $\log_2 N$ bit đồng đều ngẫu nhiên, định nghĩa $r(s)$ là số bit 0 liên tiếp **ở cuối** biểu diễn nhị phân của $h(s)$. Với hàm băm lý tưởng, tỷ lệ phần tử có $r(s) \ge r$ là $2^{-r}$, nên cần khoảng $2^r$ phần tử phân biệt để một phần tử có $r$ số 0 cuối xuất hiện.

**Ước lượng:** $R = \max_s r(s)$ trên toàn luồng; số phần tử phân biệt $\approx 2^R$.

### 2.3.2. Giảm phương sai

Ước lượng đơn có phương sai rất lớn (vì $2^R$ tăng theo cấp số nhân theo $R$). Ba chiến lược tổng hợp nhiều hàm băm độc lập:

- **Trung bình** các $2^{R_j}$ — nhạy cảm với ngoại lệ.
- **Trung vị** các $2^{R_j}$ — ổn định hơn, nhưng kết quả luôn là lũy thừa của 2.
- **Kết hợp (khuyến nghị):** chia $m$ hàm băm thành $g$ nhóm, lấy trung bình trong mỗi nhóm, rồi lấy trung vị của các trung bình đó — phá vỡ ràng buộc lũy thừa 2 của trung vị thuần trong khi vẫn giảm ảnh hưởng ngoại lệ.

## 2.4. AMS — Ước lượng mô-men của luồng

### 2.4.1. Định nghĩa mô-men

Cho luồng $S$ với $N$ giá trị phân biệt, $m_i$ là số lần phần tử thứ $i$ xuất hiện, mô-men bậc $k$ của luồng: $\sum_i m_i^k$.

- Mô-men bậc 0 = số phần tử phân biệt.
- Mô-men bậc 1 = độ dài luồng.
- Mô-men bậc 2 = **số bất ngờ (surprise number)** — đo mức độ không đồng đều của phân phối tần suất.

### 2.4.2. Thuật toán Alon-Matias-Szegedy

Với bộ nhớ chỉ đủ cho vài biến: chọn ngẫu nhiên vị trí $i$ trong luồng, duy trì `X.val = s_i` và `X.c` = số lần gặp lại giá trị đó kể từ vị trí $i$.

**Ước lượng mô-men bậc 2:** $\hat f = n(2 \cdot X.c - 1)$, tổng quát cho bậc $k$: $\hat f = n(c^k - (c-1)^k)$. Với $k$ biến độc lập, lấy trung bình để giảm phương sai. Có thể chứng minh kỳ vọng của ước lượng bằng đúng mô-men thật (ước lượng không chệch).

**Ứng dụng:** phát hiện điểm bất thường (anomaly), tắc nghẽn — số bất ngờ lớn nghĩa là phân phối lệch (tập trung vào một số ít phần tử).

## 2.5. Reservoir Sampling

Bài toán: giữ đúng $s$ phần tử đại diện từ luồng có độ dài $n$ không biết trước, sao cho mỗi phần tử có xác suất bằng nhau ($s/n$) nằm trong mẫu.

**Thuật toán:** lưu $s$ phần tử đầu tiên; khi phần tử thứ $n > s$ đến, giữ nó với xác suất $s/n$ (thay thế ngẫu nhiên một phần tử cũ), bỏ qua với xác suất $1-s/n$.

**Chứng minh quy nạp:** xác suất phần tử thứ $n+1$ ở lại mẫu sau khi phần tử $n+2$ đến bằng $\left(1-\frac{s}{n+1}\right) + \frac{s}{n+1}\cdot\frac{s-1}{s} = \frac{n}{n+1}$; kết hợp với giả thiết quy nạp phần tử cũ có xác suất $s/n$, xác suất sống sót: $\frac{s}{n}\cdot\frac{n}{n+1} = \frac{s}{n+1}$ ✓.

**Lưu ý về đơn vị lấy mẫu:** lấy mẫu sai đơn vị phân tích (theo bản ghi thay vì theo khóa) có thể cho ước lượng **chệch**. Ví dụ: nếu cần ước lượng tỷ lệ truy vấn trùng lặp trên luồng (người dùng, truy vấn), lấy mẫu theo từng bản ghi cho công thức $\frac{b}{10a+19b}$ trong khi đáp án đúng là $\frac{b}{a+b}$ — sai lệch hệ thống. Giải pháp: lấy mẫu theo **khóa** (băm khóa vào $b$ bucket, giữ nếu giá trị băm $< a$), giữ toàn bộ bản ghi của một tỷ lệ khóa thay vì một tỷ lệ bản ghi.

## 2.6. Khai phá mẫu phổ biến

### 2.6.1. Khái niệm cơ bản

Cho cơ sở dữ liệu giao dịch, một **itemset** $X$ có độ hỗ trợ (support) là tần suất xuất hiện; $X$ **thường xuyên** nếu độ hỗ trợ $\ge$ ngưỡng `min_sup`. Tính chất **đóng xuống** (downward closure): mọi tập con của một itemset thường xuyên cũng thường xuyên — nền tảng của mọi thuật toán tỉa.

### 2.6.2. Apriori

Sinh ứng viên cỡ $k+1$ từ tập thường xuyên cỡ $k$, tỉa ứng viên có tập con không thường xuyên, quét lại cơ sở dữ liệu để đếm hỗ trợ, lặp lại. **Ba điểm nghẽn:** (1) quét cơ sở dữ liệu nhiều lần, (2) số ứng viên khổng lồ, (3) chi phí đếm hỗ trợ cho từng ứng viên.

### 2.6.3. FP-Growth

Tiếp cận theo triết lý *phát triển mẫu dài từ mẫu ngắn, không sinh ứng viên*:

1. Quét cơ sở dữ liệu một lần để đếm tần suất item, giữ item thường xuyên, sắp giảm dần tần suất (f-list).
2. Quét lần hai để xây **cây FP** — mỗi giao dịch được chèn theo thứ tự f-list, dùng chung tiền tố với các giao dịch khác để nén.
3. Khai phá đệ quy: với mỗi item (duyệt ngược f-list), xây **cơ sở mẫu điều kiện** (các tiền tố dẫn tới item đó), xây **cây điều kiện** từ cơ sở đó, lặp lại đệ quy.
4. Tối ưu hóa đường đơn: khi cây điều kiện chỉ còn một nhánh, mọi tổ hợp con của nhánh đó đều là mẫu thường xuyên — sinh trực tiếp bằng tổ hợp thay vì đệ quy tiếp.

**Ưu điểm:** không sinh/kiểm tra ứng viên tường minh, nén cơ sở dữ liệu bằng cấu trúc cây, chia để trị thu hẹp dần bài toán con.

### 2.6.4. Mẫu đóng và mẫu cực đại

Một itemset dài chứa số mũ tập con — cần nén tập kết quả. Itemset $X$ **đóng (closed)** nếu không tồn tại tập cha $Y \supset X$ có cùng độ hỗ trợ; tập đóng cho **nén không mất mát** — khôi phục lại toàn bộ tập thường xuyên kèm số đếm. Itemset $X$ **cực đại (maximal)** nếu không tồn tại tập cha thường xuyên nào chứa nó; nén mạnh hơn nhưng **mất thông tin** số đếm của các tập con.

## 2.7. Độ đo tương quan luật kết hợp

### 2.7.1. Vấn đề của support/confidence

Luật $A \to B$ với độ tin cậy (confidence) cao có thể **gây hiểu lầm**: nếu $B$ đã phổ biến sẵn trong toàn bộ dữ liệu (VD 85% khách hàng vốn đã mua sữa), một độ tin cậy 80% cho luật *"mua óc chó → mua sữa"* không phản ánh mối liên hệ thật sự — $A$ có thể thậm chí làm **giảm** khả năng xảy ra $B$ so với nền.

### 2.7.2. Tính bất biến với giao dịch rỗng (null-invariance)

Một **giao dịch rỗng** đối với cặp $(A,B)$ là giao dịch không chứa cả $A$ lẫn $B$. Một độ đo **bất biến với giao dịch rỗng** nếu giá trị của nó không đổi khi thêm/bớt giao dịch rỗng. Tính chất này quan trọng vì trong cơ sở dữ liệu thưa, phần lớn giao dịch là rỗng đối với một cặp bất kỳ — một độ đo phụ thuộc số giao dịch rỗng thì phụ thuộc vào phạm vi dữ liệu được chọn phân tích, một tính chất không hợp lý về mặt thống kê.

**Mười độ đo được cài đặt trong đồ án:**

| Độ đo | Công thức | Bất biến? |
|---|---|:---:|
| Support | $P(A\cap B)$ | — |
| Confidence | $P(B\vert A)$ | Có (không đối xứng) |
| Lift | $\dfrac{P(A\cap B)}{P(A)P(B)}$ | **Không** |
| $\chi^2$ | thống kê chi-bình phương | **Không** |
| All-Confidence | $\dfrac{\sup(A,B)}{\max\{\sup A,\sup B\}}$ | Có |
| Coherence (Jaccard) | $\dfrac{\sup(A,B)}{\sup A+\sup B-\sup(A,B)}$ | Có |
| Cosine | $\dfrac{\sup(A,B)}{\sqrt{\sup A\cdot\sup B}}$ | Có |
| Kulczynski | $\dfrac{P(A\vert B)+P(B\vert A)}{2}$ | Có |
| Max-Confidence | $\max\left\{\dfrac{\sup(A,B)}{\sup A},\dfrac{\sup(A,B)}{\sup B}\right\}$ | Có |
| Imbalance Ratio | $\dfrac{\vert\sup A-\sup B\vert}{\sup A+\sup B-\sup(A,B)}$ | Có |

Sáu độ đo bất biến chỉ dùng $\sup A, \sup B, \sup(A,B)$ — **không bao giờ dùng** tổng số giao dịch $n$ — nên về mặt hình thức không thể bị ảnh hưởng bởi việc thêm giao dịch rỗng (chỉ làm $n$ thay đổi). Lift và $\chi^2$ đều có $n$ trong công thức, nên trôi theo số giao dịch rỗng. Tính chất này được kiểm chứng bằng thực nghiệm định lượng trên dữ liệu thật ở Chương 5 (E10).

## 2.8. Quy trình CRISP-DM

Đồ án tuân theo quy trình chuẩn CRISP-DM (Cross-Industry Standard Process for Data Mining) gồm sáu pha: Hiểu bài toán nghiệp vụ (Business Understanding), Hiểu dữ liệu (Data Understanding), Chuẩn bị dữ liệu (Data Preparation), Mô hình hóa (Modeling), Đánh giá (Evaluation), Triển khai (Deployment). Cấu trúc Chương 3–6 của báo cáo ánh xạ trực tiếp theo sáu pha này.
