# PHASE 3 — ĐỀ XUẤT ĐỀ TÀI CHO NHÓM 15

**Nhóm 15:** Nguyễn Thuý Anh (B25CHHT076) · Trần Thị Thảo (B25CHHT113) · Trần Văn Hanh (B25CHHT092)
**Số lượng đề xuất:** 16 đề tài, chia 6 cụm
**Phiên bản:** Phase 3 — 2026-07-27

---

## 0. GIẢ ĐỊNH & PHƯƠNG PHÁP

### 0.1. Giả định đang dùng (chưa được xác nhận — nêu rõ để bạn bác bỏ nếu sai)

| # | Giả định | Ảnh hưởng nếu sai |
|:--:|---|---|
| A1 | Nhóm có **3 thành viên**, khối lượng chia được 3 phần | Đề tài cụm A (3 tầng) sẽ quá tải nếu thực tế chỉ 1–2 người làm |
| A2 | Thời gian còn lại đủ cho ~8–10 tuần làm việc | Đề tài độ khó ⭐⭐⭐⭐⭐ cần bỏ nếu gấp |
| A3 | Nhóm có nền Python + SQL ở mức khá (suy từ việc bạn đang làm đồ án hệ phân tán có Docker/nginx) | Đề tài cần Data Engineering nặng (FAERS) sẽ rủi ro nếu nền yếu |
| A4 | Được dùng dataset công khai bất kỳ (§6 KB: không có dataset chỉ định) | Toàn bộ danh sách phải làm lại |
| A5 | Cài đặt **from scratch** phần lõi + đối chiếu thư viện (đã chốt) | — |

### 0.2. ⚠️ Cảnh báo về dataset

Mọi quy mô dataset dưới đây là **ước lượng theo hiểu biết chung**, **chưa được tôi tải về kiểm chứng trong phiên này**. Trước khi chốt đề tài ở Phase 4, **bắt buộc phải tải thử và đếm số dòng thật**. Tôi ghi rõ mức tin cậy cho từng dataset:
- ✅ **Chắc chắn tồn tại & công khai** — đã dùng rộng rãi trong cộng đồng
- ⚠️ **Cần kiểm chứng** — có thể đã đổi điều khoản, cần đăng ký, hoặc quy mô khác kỳ vọng

### 0.3. Thang đánh giá

| Thuộc tính | Thang |
|---|---|
| **Độ khó** | ⭐ (rất dễ) → ⭐⭐⭐⭐⭐ (rất khó) |
| **Tính mới** | ⭐ (đã có nhóm làm) → ⭐⭐⭐⭐⭐ (chưa ai chạm, khai thác khoảng trống GV nhấn mạnh) |
| **Khả năng đạt điểm cao** | ⭐ → ⭐⭐⭐⭐⭐ |
| **Khả năng thành sản phẩm** | ⭐ (chỉ notebook) → ⭐⭐⭐⭐⭐ (hệ thống real-time có UI) |

---

## 1. MƯỜI SÁU ĐỀ TÀI ĐỀ XUẤT

---

## 🅐 CỤM A — KIẾN TRÚC ĐA CHƯƠNG *(khai thác M1: không nhóm nào kết hợp ≥2 chương)*

---

### **Đ1. FraudRing-3T — Hệ phát hiện gian lận giao dịch tài chính theo kiến trúc ba tầng Streaming → LSH → Frequent Patterns**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Hệ thống chống gian lận hiện tại chấm điểm **từng giao dịch độc lập**, nên (a) không chịu nổi tốc độ luồng nếu tính chính xác mọi thống kê, và (b) **bỏ sót cấu trúc nhóm** — các tài khoản có hồ sơ hành vi gần trùng nhau thường cùng thuộc một chiến dịch gian lận. Cần một kiến trúc vừa xử lý được luồng tốc độ cao với bộ nhớ hằng số, vừa phát hiện được quan hệ tương tự giữa tài khoản, vừa sinh ra **luật gian lận đọc được** cho nhân viên rủi ro. |
| **Mục tiêu** | ① Tầng 1 (Streaming): tính đặc trưng rủi ro thời gian thực với bộ nhớ dưới tuyến tính — Bloom Filter (lọc blacklist), DGIM (đếm giao dịch/tài khoản trong cửa sổ trượt), Flajolet-Martin (đếm số thiết bị/người nhận phân biệt), Reservoir Sampling (lấy mẫu đại diện để phân tích sâu).<br>② Tầng 2 (LSH): xây "hồ sơ hành vi" mỗi tài khoản thành tập item → MinHash + LSH tìm **cụm tài khoản gần trùng**; đo mức làm giàu tỷ lệ gian lận trong cụm chứa tài khoản gian lận đã biết.<br>③ Tầng 3 (FPM): FP-Growth trên tập giao dịch có nhãn → sinh luật, xếp hạng bằng **5 độ đo null-invariant** + Imbalance Ratio thay vì support/confidence.<br>④ Đo sai số & bộ nhớ của cả 3 tầng so với tính chính xác offline. |
| **Đối tượng sử dụng** | Chuyên viên quản trị rủi ro ngân hàng · Đội vận hành hệ thống chống gian lận · Kiểm toán nội bộ |
| **Giá trị thực tiễn** | Giảm chi phí hạ tầng (bộ nhớ hằng số thay vì tuyến tính) · Phát hiện nhóm thay vì cá thể · Luật gian lận **giải thích được** — yêu cầu bắt buộc trong ngành tài chính (không dùng được mô hình hộp đen cho quyết định từ chối giao dịch) |
| **Dataset** | **PaySim** — mô phỏng chuyển tiền di động, ~6.3 triệu giao dịch, có nhãn `isFraud` ✅<br>Bổ sung/đối chiếu: **IEEE-CIS Fraud Detection** (Kaggle, ~590K giao dịch, giàu đặc trưng thiết bị/định danh — phù hợp tầng LSH) ✅ |
| **Thuật toán** | Bloom Filter · DGIM · Flajolet-Martin · Reservoir Sampling · MinHash · LSH banding · FP-Growth · Apriori (đối chứng) · Kulczynski/Cosine/AllConf/Coherence/MaxConf |
| **Độ khó** | ⭐⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — kết hợp cả 3 chương (M1, chưa nhóm nào làm) + DGIM (G1) + null-invariant (G6) + domain ngân hàng/fraud trống hoàn toàn |
| **Điểm cao** | ⭐⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐⭐ — FastAPI + dashboard real-time + PostgreSQL + Docker Compose; demo bảo vệ rất mạnh |
| **🔴 Rủi ro cần biết trước** | ① **PaySim là dữ liệu mô phỏng**, gian lận được sinh theo quy tắc đơn giản (chiếm tài khoản → TRANSFER → CASH_OUT). **"Vòng gian lận phối hợp" có thể không tồn tại trong dữ liệu** ⇒ nếu đặt tên tầng 2 là "phát hiện fraud ring" mà không tìm thấy gì, đó chính là **lỗi mẫu của nhóm 12** (hứa nhiều hơn dữ liệu cho phép).<br>**➜ Cách khắc phục bắt buộc:** đặt lại tầng 2 thành *"lan truyền rủi ro theo tương tự hành vi"* — đo xem tài khoản LSH-tương tự với tài khoản gian lận đã biết có tỷ lệ gian lận cao hơn nền bao nhiêu lần. Giả thuyết này **kiểm chứng được bằng nhãn có sẵn**, đúng hay sai đều là kết quả hợp lệ.<br>② Phạm vi rộng — bắt buộc chia 3 tầng cho 3 thành viên. |

---

### **Đ2. ClickShield — Phát hiện gian lận click quảng cáo trên luồng tốc độ cao**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Gian lận click (bot farm, click injection) gây thất thoát lớn cho ngân sách quảng cáo. Luồng click đạt hàng chục nghìn sự kiện/giây — không thể lưu trữ đầy đủ để tính thống kê chính xác. |
| **Mục tiêu** | DGIM đếm click/IP trong cửa sổ trượt · Flajolet-Martin đếm user phân biệt/chiến dịch · **AMS surprise number** phát hiện phân phối click lệch bất thường (dấu hiệu bot) · Bloom Filter lọc IP/device đã biết · MinHash/LSH gom cụm bot có hồ sơ hành vi giống nhau |
| **Đối tượng** | Đội AdOps · Nền tảng quảng cáo · Nhà quảng cáo |
| **Giá trị thực tiễn** | Bảo vệ ngân sách marketing; đo được tiền tiết kiệm |
| **Dataset** | **Criteo Display Advertising Challenge** (~45M dòng) ✅ · **Avazu CTR** (~40M dòng) ✅ · **TalkingData AdTracking Fraud Detection** (Kaggle, ~185M click, **có nhãn gian lận**) ⚠️ cần kiểm chứng còn tải được |
| **Thuật toán** | DGIM · Flajolet-Martin · AMS · Bloom Filter · MinHash/LSH |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐ — G1 + G8 + M1; nhưng **🟡 trùng nhẹ nhóm 3** ở khung "phát hiện lưu lượng độc hại thời gian thực" |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐⭐ |
| **Rủi ro** | TalkingData ~185M dòng có thể vượt khả năng máy cá nhân — cần lấy mẫu, mà lấy mẫu lại phải biện luận đúng đơn vị (bài học slide tr.17) |

---

### **Đ3. SupplyPulse — Giám sát luồng sự kiện chuỗi cung ứng & khai phá luật sự cố giao hàng**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Sự cố giao hàng (trễ, hỏng, hoàn) thường là **tổ hợp điều kiện** (tuyến + thời điểm + loại hàng + đối tác) chứ không do một yếu tố đơn lẻ. Cần vừa giám sát luồng sự kiện thời gian thực, vừa rút ra luật để phòng ngừa. |
| **Mục tiêu** | DGIM giám sát tỷ lệ sự cố theo cửa sổ trượt/tuyến · FP-Growth khai phá tổ hợp điều kiện dẫn tới sự cố · xếp hạng bằng độ đo null-invariant · Closed patterns để nén tập luật |
| **Đối tượng** | Quản lý vận hành logistics · Điều phối viên tuyến · Quản lý chất lượng dịch vụ |
| **Giá trị thực tiễn** | Giảm tỷ lệ giao hàng lỗi; cảnh báo sớm tuyến rủi ro |
| **Dataset** | **Olist Brazilian E-Commerce** (~100K đơn, có timestamp giao hàng) ⚠️ **quá nhỏ so với C4** · **DataCo Smart Supply Chain** (Kaggle, ~180K dòng) ⚠️ cũng nhỏ · Cần tìm nguồn lớn hơn hoặc mô phỏng |
| **Thuật toán** | DGIM · FP-Growth · FPClose · Null-invariant measures |
| **Độ khó** | ⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐ — Logistics trống hoàn toàn |
| **Điểm cao** | ⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **🔴 Rủi ro** | **Không tìm được dataset logistics công khai đủ lớn** ⇒ vi phạm C4, rơi vào đúng lỗi của nhóm 7 và 12. Đây là điểm yếu quyết định của đề tài này. |

---

## 🅑 CỤM B — SEQUENTIAL PATTERN MINING *(khai thác G2: PrefixSpan/CloSpan/BIDE được GV nêu tên, 0 nhóm dùng)*

> ⚠️ **Lưu ý chung cụm B:** Sequential Pattern Mining chỉ được **nêu tên** ở slide tr.34 (mục *Extension of Pattern Growth Mining Methodology*), **không được dạy chi tiết**. Đây vừa là cơ hội (tính mới cao, GV đã "cấp phép" bằng cách nêu tên) vừa là rủi ro (phải tự học và tự trình bày lý thuyết). **Cần hỏi giảng viên trước khi chốt.**

---

### **Đ4. ProcessLens — Khai phá quy trình nghiệp vụ từ nhật ký sự kiện ERP bằng Sequential Pattern Mining**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Quy trình nghiệp vụ **được thiết kế trên giấy** thường khác xa **quy trình thực thi trong hệ thống**. Doanh nghiệp không biết có bao nhiêu biến thể quy trình đang chạy, biến thể nào gây chậm trễ, và bước nào là nút thắt cổ chai. |
| **Mục tiêu** | ① PrefixSpan (from scratch) khai phá chuỗi hoạt động phổ biến từ event log<br>② BIDE khai phá **closed sequential patterns** → nén tập biến thể quy trình<br>③ **AMS surprise number** đo độ lệch phân phối tần suất giữa các biến thể → định vị nút thắt (đúng ứng dụng "phát hiện bất thường" mà GV nêu ở slide tr.45)<br>④ DGIM giám sát tỷ lệ biến thể lệch chuẩn theo cửa sổ trượt |
| **Đối tượng** | Chuyên viên phân tích nghiệp vụ (BA) · Quản lý vận hành ERP · Kiểm toán quy trình |
| **Giá trị thực tiễn** | Process Mining là ngành công nghiệp thật (Celonis, UiPath Process Mining). Kết quả dùng trực tiếp để tái thiết kế quy trình |
| **Dataset** | **BPI Challenge 2017** — quy trình xét duyệt khoản vay, ~1.2M sự kiện ✅ (4TU.ResearchData, công khai)<br>**BPI Challenge 2019** — quy trình mua hàng/thanh toán, ~1.6M sự kiện ✅ |
| **Thuật toán** | PrefixSpan · BIDE (closed sequential) · AMS · DGIM · FP-Growth (đối chứng phi tuần tự) |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — G2 + G8 + lĩnh vực ERP/Process Mining trống hoàn toàn |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ — dashboard trực quan hóa biến thể quy trình rất ấn tượng |
| **Rủi ro** | PrefixSpan ngoài phạm vi dạy chi tiết (xem cảnh báo cụm B) · Trực quan hóa process graph cần công sức frontend |

---

### **Đ5. LearnPath — Khai phá lộ trình học tập và hệ hỗ trợ quyết định cảnh báo sinh viên nguy cơ**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Hệ LMS ghi lại hàng triệu tương tác nhưng nhà trường chỉ nhìn được **điểm cuối kỳ**. Không biết **chuỗi hành vi học tập nào** dẫn tới thành công/thất bại, nên can thiệp luôn muộn. |
| **Mục tiêu** | ① PrefixSpan khai phá chuỗi hoạt động học phổ biến<br>② Tách **discriminative sequential patterns** — chuỗi xuất hiện nhiều ở nhóm đạt nhưng ít ở nhóm trượt<br>③ Dùng các pattern đó làm **đặc trưng đầu vào** cho bộ phân loại cảnh báo sớm (cầu nối G4)<br>④ DSS xếp hạng sinh viên rủi ro + giải thích bằng chính pattern |
| **Đối tượng** | Cố vấn học tập · Phòng đào tạo · Giảng viên phụ trách môn |
| **Giá trị thực tiễn** | Giảm tỷ lệ bỏ học; can thiệp sớm có bằng chứng |
| **Dataset** | **OULAD** (Open University Learning Analytics) — ~32K sinh viên, ~10M lượt click VLE ✅ · **EdNet** (Riiid, ~131M tương tác) ✅ nhưng rất lớn |
| **Thuật toán** | PrefixSpan · Discriminative pattern selection · FP-Growth · Classifier (RF/XGBoost) · SHAP |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — G2 + G4 + Educational Data Mining trống |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐⭐ — DSS có UI rõ ràng, đúng chất Information Systems |
| **Rủi ro** | Rủi ro cụm B · Tỷ lệ ML trong đề tài khá cao — phải giữ pattern mining làm lõi, không để classifier lấn át |

---

### **Đ6. CareFlow — Khai phá lộ trình điều trị lâm sàng bằng Sequential Pattern Mining**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Lộ trình điều trị thực tế của bệnh nhân lệch khỏi phác đồ chuẩn ở mức nào? Chuỗi can thiệp nào gắn với kết cục tốt hơn? |
| **Mục tiêu** | PrefixSpan/BIDE trên chuỗi sự kiện lâm sàng · so sánh lộ trình nhóm kết cục tốt vs xấu · AMS đo độ lệch |
| **Đối tượng** | Bác sĩ điều trị · Quản lý chất lượng bệnh viện · Bảo hiểm y tế |
| **Giá trị thực tiễn** | Chuẩn hóa phác đồ, giảm chi phí điều trị |
| **Dataset** | **MIMIC-IV** ⚠️ **cần đăng ký PhysioNet + hoàn thành khóa học CITI về đạo đức nghiên cứu** — thủ tục có thể mất vài tuần, **rủi ro deadline cao** |
| **Thuật toán** | PrefixSpan · BIDE · AMS |
| **Độ khó** | ⭐⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ |
| **Điểm cao** | ⭐⭐⭐ (bị trừ vì rủi ro không lấy được dữ liệu) |
| **Sản phẩm** | ⭐⭐⭐ |
| **🔴 Rủi ro** | **Rào cản truy cập dữ liệu là rủi ro chí mạng.** Không khuyến nghị trừ khi đã có sẵn quyền truy cập MIMIC |

---

## 🅒 CỤM C — DISCRIMINATIVE FREQUENT PATTERNS *(khai thác G4 — cầu nối chính danh sang ML, GV nêu tên tại slide tr.4 và tr.34)*

---

### **Đ7. ChurnPattern — Hệ cảnh báo sớm rời mạng viễn thông bằng đặc trưng mẫu phổ biến phân biệt**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Mô hình dự báo churn thường là hộp đen — bộ phận chăm sóc khách hàng biết "ai sắp rời" nhưng không biết **vì sao**, nên không thiết kế được ưu đãi giữ chân phù hợp. |
| **Mục tiêu** | ① FP-Growth khai phá frequent patterns từ hành vi thuê bao (đã rời rạc hóa)<br>② Chọn **discriminative patterns** (Information Gain / Fisher score) phân biệt churn vs non-churn — theo Cheng et al. ICDE'07 mà GV nêu tên<br>③ Dùng pattern làm feature cho classifier → so sánh với feature thô<br>④ Xếp hạng luật bằng độ đo null-invariant → sinh **kịch bản giữ chân** đọc được |
| **Đối tượng** | Bộ phận CRM/chăm sóc khách hàng viễn thông · Marketing giữ chân |
| **Giá trị thực tiễn** | Chi phí giữ chân thấp hơn nhiều chi phí thu hút mới; kịch bản giải thích được dùng trực tiếp |
| **Dataset** | **KKBox Churn Prediction** (WSDM Kaggle) — nhật ký nghe nhạc + giao dịch, **hàng chục triệu dòng** ✅ (churn dịch vụ thuê bao, tương đương bài toán viễn thông)<br>⚠️ *Tránh* IBM Telco Churn (7.043 dòng — vi phạm C4 nghiêm trọng) |
| **Thuật toán** | FP-Growth · Discriminative pattern selection · Null-invariant measures · Classifier + CV + ROC-AUC + SHAP |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — G4 chưa ai chạm; Telecom/thuê bao trống |
| **Điểm cao** | ⭐⭐⭐⭐⭐ — **đây là đề tài duy nhất thỏa mãn cùng lúc yêu cầu ML của ROLE và yêu cầu syllabus của môn, một cách chính danh** |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **Rủi ro** | Phải rời rạc hóa nhiều biến liên tục — làm cẩu thả sẽ mất thông tin và bị chất vấn |

---

### **Đ8. CreditPattern — Chấm điểm rủi ro tín dụng giải thích được bằng luật kết hợp phân biệt**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Quy định tài chính yêu cầu quyết định từ chối tín dụng phải **giải thích được**. Mô hình hộp đen không đáp ứng. |
| **Mục tiêu** | Như Đ7 nhưng cho tín dụng: pattern phân biệt vỡ nợ/không vỡ nợ → luật chấm điểm minh bạch → so sánh hiệu năng với mô hình hộp đen |
| **Đối tượng** | Chuyên viên thẩm định tín dụng · Quản trị rủi ro · Bộ phận tuân thủ |
| **Giá trị thực tiễn** | Đáp ứng yêu cầu giải trình pháp lý |
| **Dataset** | **Home Credit Default Risk** (Kaggle) — ~300K hồ sơ + bảng phụ `bureau`/`installments_payments` cỡ hàng chục triệu dòng ✅ |
| **Thuật toán** | FP-Growth · Discriminative patterns · Null-invariant measures · Classifier · SHAP |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐ — G4; Banking trống. Nhưng credit scoring là bài toán rất phổ biến ngoài lớp |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **Rủi ro** | Mất cân bằng lớp nặng · Ghép nhiều bảng là công việc Data Engineering đáng kể |

---

## 🅓 CỤM D — CLOSED/MAX PATTERNS + ĐỘ ĐO NULL-INVARIANT *(khai thác G3 + G6)*

---

### **Đ9. PharmaSafe — Phát hiện tổ hợp thuốc gây phản ứng bất lợi bằng Closed/Max Pattern Mining và độ đo tương quan null-invariant** ⭐

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Bệnh nhân dùng đồng thời nhiều thuốc. Phản ứng bất lợi thường phát sinh từ **tổ hợp**, không từ thuốc đơn lẻ — mà thử nghiệm lâm sàng gần như không kiểm tra hết tổ hợp. Khai phá dữ liệu báo cáo hậu thị trường là cách duy nhất phát hiện tín hiệu ở quy mô lớn.<br><br>📌 **Đây chính là ứng dụng giảng viên nêu đích danh** tại slide chương A tr.9: *"Side-effects in drug combinations: baskets are patients; items are drugs and their side effects"* — **và không nhóm nào lấy**. |
| **Mục tiêu** | ① Xây giỏ hàng: mỗi báo cáo = 1 bệnh nhân, item = {thuốc} ∪ {phản ứng}<br>② FP-Growth (from scratch) khai phá frequent itemsets<br>③ **FPClose / FPMax** khai phá closed & max patterns → **đo tỷ lệ nén** (M5, chưa nhóm nào đo)<br>④ Xếp hạng tín hiệu bằng **cả 7 độ đo**: support, confidence, Lift, χ², Kulczynski, Cosine, AllConf, Coherence, MaxConf + **Imbalance Ratio** → **chứng minh thực nghiệm vì sao null-invariance quan trọng** trên dữ liệu thật (dữ liệu FAERS có **cực nhiều giao dịch null** — phần lớn cặp thuốc–phản ứng không đồng xuất hiện ⇒ đây là **môi trường lý tưởng để chứng minh Lift và χ² thất bại**)<br>⑤ Đối chiếu tín hiệu tìm được với nhãn thuốc chính thức |
| **Đối tượng** | Cơ quan quản lý dược (Cục Quản lý Dược) · Dược sĩ lâm sàng · Bộ phận cảnh giác dược của hãng dược · Bác sĩ kê đơn |
| **Giá trị thực tiễn** | Cảnh giác dược (pharmacovigilance) là hoạt động bắt buộc theo luật ở mọi quốc gia. Phát hiện sớm tín hiệu an toàn cứu được người |
| **Dataset** | **FDA FAERS** (Adverse Event Reporting System) — công khai, tải trực tiếp theo quý, **hàng triệu báo cáo**, mỗi báo cáo có danh sách thuốc + danh sách phản ứng ✅<br>Đối chiếu (tùy chọn): **SIDER** hoặc dữ liệu nhãn thuốc openFDA ⚠️ cần kiểm chứng |
| **Thuật toán** | FP-Growth · Apriori (đối chứng) · **FPClose · FPMax** · 9 độ đo interestingness · Imbalance Ratio |
| **Độ khó** | ⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — **GV gợi ý trực tiếp mà 0 nhóm lấy** + G3 + G6 + M5 + Y tế lâm sàng trống |
| **Điểm cao** | ⭐⭐⭐⭐⭐ — bám sát nhất 2 trong 3 tín hiệu chấm điểm của GV |
| **Sản phẩm** | ⭐⭐⭐⭐ — cổng tra cứu tương tác thuốc + dashboard xếp hạng tín hiệu; **có thể build "kiểm tra đơn thuốc": nhập danh sách thuốc → cảnh báo tổ hợp rủi ro** |
| **Rủi ro** | ① **Chuẩn hóa tên thuốc trong FAERS rất bẩn** (nhập tay, nhiều biến thể, tên thương mại vs hoạt chất) ⇒ khối lượng tiền xử lý lớn. *Nhưng đây cũng là cơ hội: §3 KB liệt kê 10 kỹ thuật tiền xử lý, đề tài này dùng được nhiều nhất.*<br>② **Ground truth chỉ đánh giá được một phần** — không có danh sách vàng đầy đủ mọi tương tác thuốc. **Phải nêu rõ giới hạn này trong báo cáo, không được che giấu.**<br>③ Không được kết luận y khoa — chỉ báo cáo tín hiệu thống kê. Phải có tuyên bố miễn trừ. |

---

### **Đ10. CrossSell-DSS — Hệ hỗ trợ quyết định bán chéo sản phẩm tài chính với bộ độ đo tương quan đầy đủ**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Ngân hàng gợi ý sản phẩm bán chéo dựa trên luật support/confidence, dẫn tới gợi ý sai lệch: sản phẩm ai cũng có (tài khoản thanh toán) luôn xuất hiện ở vế phải mọi luật dù không mang thông tin. Đây **đúng là ví dụ "buy walnuts → buy milk"** mà GV phê phán ở slide tr.37. |
| **Mục tiêu** | Chứng minh thực nghiệm rằng xếp hạng luật bằng Kulczynski/Cosine/AllConf cho gợi ý bán chéo **tốt hơn** confidence; xây DSS cho nhân viên quan hệ khách hàng |
| **Đối tượng** | Nhân viên quan hệ khách hàng ngân hàng · Bộ phận Marketing sản phẩm |
| **Giá trị thực tiễn** | Tăng tỷ lệ chuyển đổi chiến dịch bán chéo |
| **Dataset** | **Santander Product Recommendation** (Kaggle) — ~13.6 triệu dòng, 24 sản phẩm tài chính/khách hàng/tháng ✅ **rất phù hợp** |
| **Thuật toán** | FP-Growth · Apriori · ECLAT (đối chứng) · 9 độ đo interestingness · Imbalance Ratio |
| **Độ khó** | ⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐ — G6 là trọng tâm; Banking/CRM trống. Nhưng "association rules cho recommendation" **🟡 chạm nhóm 8** về khung tiếp cận |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **Rủi ro** | Dữ liệu Santander có cấu trúc chuỗi thời gian theo tháng — nếu coi mỗi tháng là 1 giao dịch độc lập sẽ bị chất vấn về giả định |

---

## 🅔 CỤM E — DGIM & STREAMING LÀM LÕI *(khai thác G1: 22% chương C, 0 nhóm dùng)*

---

### **Đ11. CityFlow — Hệ giám sát giao thông đô thị với truy vấn cửa sổ trượt trên luồng chuyến đi quy mô lớn**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Trung tâm điều hành giao thông cần trả lời liên tục các truy vấn dạng *"trong N chuyến đi gần nhất, bao nhiêu chuyến xuất phát từ khu vực X?"*, *"bao nhiêu điểm đón phân biệt trong 1 giờ qua?"* trên hàng trăm luồng song song (mỗi khu vực một luồng) — **không thể giữ cửa sổ đầy đủ cho mọi luồng**. Đây **đúng nguyên văn tình huống GV nêu** ở slide tr.53: *"Có thể có nhiều luồng đồng thời — không thể giữ nhiều cửa sổ."* |
| **Mục tiêu** | ① **DGIM đa luồng** làm lõi — cài đặt from scratch đầy đủ ràng buộc bucket, kiểm chứng cận sai số 50% và quan hệ $O(1/r)$<br>② Mở rộng DGIM cho **tổng của $k$ số nguyên gần nhất** (slide tr.66 — coi mỗi bit là một luồng riêng, ước lượng $\sum c_i 2^i$) để ước lượng tổng doanh thu/quãng đường trong cửa sổ<br>③ Flajolet-Martin đếm điểm đón/trả phân biệt<br>④ AMS surprise number phát hiện tắc nghẽn (phân phối lệch)<br>⑤ FP-Growth trên "giỏ hàng" = tập khu vực hoạt động đồng thời trong mỗi khung 15 phút → luật đồng xuất hiện tắc nghẽn<br>⑥ **So sánh toàn diện ước lượng vs giá trị chính xác tính offline** |
| **Đối tượng** | Trung tâm điều hành giao thông đô thị · Nhà quy hoạch · Hãng gọi xe |
| **Giá trị thực tiễn** | Điều tiết tín hiệu, phân bổ phương tiện, quy hoạch tuyến |
| **Dataset** | **NYC TLC Trip Records** — công khai, hàng trăm triệu chuyến đi, có timestamp + zone đón/trả ✅ **quy mô lý tưởng cho MMDS** |
| **Thuật toán** | **DGIM (lõi)** · DGIM mở rộng cho số nguyên · Flajolet-Martin · AMS · Reservoir Sampling · FP-Growth |
| **Độ khó** | ⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — **G1 là khoảng trống lớn nhất chưa ai chạm** (15 slide) + mở rộng tr.66 chưa ai dùng + Smart City trống |
| **Điểm cao** | ⭐⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐⭐ — dashboard bản đồ nhiệt thời gian thực rất bắt mắt |
| **Điểm mạnh nổi bật** | ✅ **Ground truth hoàn hảo** — giá trị chính xác tính được offline, nên mọi sai số ước lượng đều đo được tuyệt đối. Đây là điều kiện lý tưởng cho tín hiệu #3 của GV (so sánh lý thuyết vs thực nghiệm).<br>✅ **Dữ liệu thật sự massive** — không phải "giả vờ streaming" như nhóm 7. |
| **Rủi ro** | ⚠️ Nguy cơ bị hỏi *"đây là truy vấn xấp xỉ hay khai phá dữ liệu?"* — **giống lời phê với nhóm 14**. **Bắt buộc phải có tầng FP-Growth (mục ⑤) để giữ chất "mining"**, không được bỏ. |

---

### **Đ12. DriftSentinel — Phát hiện trôi khái niệm trên luồng dữ liệu phi dừng**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | GV nhấn mạnh ngay slide tr.7 rằng luồng dữ liệu **phi dừng** — phân phối thay đổi theo mùa/ngày/giờ. Mô hình triển khai xong sẽ suy giảm âm thầm. **0 nhóm xử lý vấn đề này.** |
| **Mục tiêu** | Dùng **AMS surprise number** như chỉ báo trôi phân phối · Reservoir Sampling phân tầng giữ mẫu tham chiếu · DGIM theo dõi tỷ lệ lỗi trong cửa sổ trượt · cảnh báo khi cần huấn luyện lại |
| **Đối tượng** | Đội MLOps · Kỹ sư vận hành mô hình |
| **Giá trị thực tiễn** | Trực tiếp phục vụ MLOps — lĩnh vực đang thiếu công cụ nhẹ |
| **Dataset** | Bất kỳ luồng lớn có nhãn theo thời gian: Criteo · PaySim · Electricity (ELEC2, chuẩn cho drift nhưng nhỏ ⚠️) |
| **Thuật toán** | AMS · Reservoir Sampling · DGIM · Flajolet-Martin |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — M2 hoàn toàn trống, và GV đã "mở đường" bằng cách nhấn mạnh tính phi dừng |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐ — sản phẩm là công cụ giám sát, kém trực quan hơn Đ11 |
| **Rủi ro** | Khái niệm "trôi" cần định nghĩa chặt; AMS đo độ lệch phân phối tần suất, **không trực tiếp đo drift của quan hệ đặc trưng–nhãn** — cần cẩn thận không hứa quá (tránh lỗi mẫu nhóm 3) |

---

### **Đ13. StreamSLA — Giám sát cam kết chất lượng dịch vụ hạ tầng CNTT trên luồng nhật ký**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Đội vận hành cần trả lời *"tỷ lệ request lỗi trong 1 triệu request gần nhất?"* trên hàng nghìn dịch vụ song song |
| **Mục tiêu** | DGIM đa luồng cho tỷ lệ lỗi · FM đếm client phân biệt · Bloom lọc endpoint đã biết · FP-Growth khai phá tổ hợp điều kiện gây lỗi |
| **Đối tượng** | SRE · DevOps · Quản lý dịch vụ |
| **Giá trị thực tiễn** | Thay thế một phần chức năng của công cụ APM đắt tiền |
| **Dataset** | **Loghub** (bộ nhật ký hệ thống công khai: HDFS, BGL, Thunderbird — hàng chục triệu dòng) ✅ |
| **Thuật toán** | DGIM · Flajolet-Martin · Bloom Filter · FP-Growth |
| **Độ khó** | ⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐ — G1; nhưng **🟡 chạm nhóm 3** về khung "giám sát luồng hạ tầng" |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **Rủi ro** | Trùng nhẹ nhóm 3 · Kém hấp dẫn về mặt kể chuyện so với Đ11 |

---

## 🅕 CỤM F — BIẾN THỂ LSH *(khai thác G5: cosine LSH / SimHash, 0 nhóm dùng)*

---

### **Đ14. ProductMatch — Đối sánh thực thể sản phẩm xuyên sàn thương mại điện tử bằng LSH đa họ**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Cùng một sản phẩm được đăng trên nhiều sàn với tên gọi, đơn vị, mô tả khác nhau. So sánh giá xuyên sàn đòi hỏi **đối sánh thực thể (entity resolution)** ở quy mô hàng triệu — bài toán $O(N^2)$ kinh điển. |
| **Mục tiêu** | ① Jaccard MinHash LSH (chuẩn giáo trình) trên shingle tên sản phẩm<br>② **Cosine LSH bằng random hyperplane + SimHash** (G5 — chưa nhóm nào dùng)<br>③ **So sánh hai họ LSH** trên cùng bài toán: precision/recall/tốc độ/bộ nhớ — đây là đóng góp học thuật thật sự<br>④ Kiểm chứng S-curve thực nghiệm vs lý thuyết cho cả hai họ |
| **Đối tượng** | Sàn TMĐT · Dịch vụ so sánh giá · Đội chống hàng giả |
| **Giá trị thực tiễn** | So sánh giá, phát hiện listing trùng lặp/giả mạo |
| **Dataset** | **WDC Product Matching / WDC Products** (Web Data Commons, có cặp gán nhãn) ⚠️ cần kiểm chứng khả năng tải · **Amazon-Google / Abt-Buy** (chuẩn entity resolution, **nhỏ** ⚠️) · **Amazon Reviews metadata (UCSD)** — hàng triệu sản phẩm ✅ nhưng không có nhãn cặp trùng |
| **Thuật toán** | Shingling · MinHash · LSH banding · **Random hyperplane LSH · SimHash** |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐ — G5; nhưng **🟡 cùng họ bài toán với 11/13** (đều là near-duplicate/matching) |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **🔴 Rủi ro** | **Ground truth là điểm yếu** — dataset lớn thì không có nhãn cặp trùng; dataset có nhãn thì quá nhỏ (vi phạm C4). Phải giải quyết mâu thuẫn này trước khi chốt |

---

### **Đ15. FakeNewsTrace — Truy vết lan truyền biến thể nội dung sai lệch bằng SimHash và cửa sổ trượt**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Nội dung sai lệch lan truyền dưới dạng **biến thể được viết lại**, không phải bản sao nguyên văn. Jaccard trên shingle bắt kém các biến thể này (đúng điểm yếu tôi đã chỉ ra ở nhóm 11). |
| **Mục tiêu** | SimHash/cosine LSH gom biến thể cùng một nội dung gốc · DGIM đếm số lần xuất hiện của mỗi cụm trong cửa sổ trượt · AMS phát hiện cụm bùng nổ bất thường |
| **Đối tượng** | Đội kiểm chứng thông tin · Nền tảng mạng xã hội · Cơ quan quản lý |
| **Giá trị thực tiễn** | Rất cao về mặt xã hội |
| **Dataset** | **GDELT** ✅ (khổng lồ, cập nhật liên tục) · **FakeNewsNet** ⚠️ (cần crawl, có thể thiếu dữ liệu) · **LIAR** (nhỏ ⚠️) |
| **Thuật toán** | SimHash · Cosine LSH · DGIM · AMS · MinHash (đối chứng) |
| **Độ khó** | ⭐⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐⭐⭐ — G5 + G1 + M1 |
| **Điểm cao** | ⭐⭐⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **🔴 Rủi ro** | ① **🟡 Trùng khung với nhóm 4** ("đột biến chủ đề trên luồng tin tức") — dù thuật toán khác, đề tài nghe rất giống, dễ bị so sánh bất lợi<br>② Ground truth "tin giả" cực khó, đòi hỏi gán nhãn thủ công |

---

### **Đ16. JobMatch — Đối sánh hồ sơ ứng viên và mô tả công việc quy mô lớn bằng LSH**

| Thuộc tính | Nội dung |
|---|---|
| **Bài toán** | Nền tảng tuyển dụng phải so khớp hàng triệu CV với hàng trăm nghìn JD — bài toán $O(N \times M)$ |
| **Mục tiêu** | MinHash LSH trên tập kỹ năng · Cosine LSH trên biểu diễn văn bản · so sánh hai họ · phát hiện JD trùng lặp (tin tuyển dụng ma) |
| **Đối tượng** | Nền tảng tuyển dụng · Bộ phận nhân sự |
| **Giá trị thực tiễn** | Cao |
| **Dataset** | ⚠️ **Chưa xác định được nguồn công khai đủ lớn và có nhãn** — điểm yếu quyết định |
| **Thuật toán** | MinHash · LSH · Cosine LSH |
| **Độ khó** | ⭐⭐⭐ |
| **Tính mới** | ⭐⭐⭐ |
| **Điểm cao** | ⭐⭐ |
| **Sản phẩm** | ⭐⭐⭐⭐ |
| **🔴 Rủi ro** | Không có dataset ⇒ **không khuyến nghị**, đưa vào chỉ để hoàn chỉnh danh sách |

---

## 2. BẢNG CHẤM ĐIỂM THEO 8 TIÊU CHÍ

*(C1 lõi ≥2 thuật toán MMDS · C2 không trùng · C3 thuật toán khớp bài toán · C4 dữ liệu đủ lớn · C5 có ground truth · C6 đủ CRISP-DM · C7 khai thác ≥2 khoảng trống · C8 sản phẩm chạy được)*

| # | Đề tài | C1 | C2 | C3 | C4 | C5 | C6 | C7 | C8 | **Tổng** | Hạng |
|:--:|---|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|:--:|
| **Đ11** | **CityFlow** — DGIM giao thông đô thị | ✅✅ | ✅✅ | ✅ | ✅✅ | ✅✅ | ✅ | ✅✅ | ✅✅ | **15/16** | 🥇 **1** |
| **Đ9** | **PharmaSafe** — Tổ hợp thuốc & tác dụng phụ | ✅ | ✅✅ | ✅✅ | ✅✅ | ⚠️ | ✅✅ | ✅✅ | ✅ | **14/16** | 🥈 **2** |
| **Đ1** | **FraudRing-3T** — Fraud 3 tầng | ✅✅ | ✅✅ | ⚠️ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | **14/16** | 🥈 **2** |
| **Đ7** | **ChurnPattern** — Churn thuê bao | ✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅ | **14/16** | 🥈 **2** |
| **Đ4** | **ProcessLens** — Process Mining ERP | ⚠️ | ✅✅ | ✅✅ | ✅ | ✅ | ✅✅ | ✅✅ | ✅ | **13/16** | 5 |
| **Đ10** | **CrossSell-DSS** — Bán chéo ngân hàng | ✅ | ✅ | ✅ | ✅✅ | ✅ | ✅✅ | ✅✅ | ✅ | **12/16** | 6 |
| **Đ5** | **LearnPath** — EDM lộ trình học tập | ⚠️ | ✅✅ | ✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | **13/16** | 5 |
| **Đ2** | **ClickShield** — Gian lận click | ✅✅ | ⚠️ | ✅ | ✅✅ | ✅ | ✅ | ✅✅ | ✅✅ | **12/16** | 6 |
| **Đ12** | **DriftSentinel** — Concept drift | ✅ | ✅✅ | ⚠️ | ✅ | ✅ | ✅ | ✅✅ | ⚠️ | **11/16** | 9 |
| **Đ8** | **CreditPattern** — Rủi ro tín dụng | ✅ | ✅ | ✅✅ | ✅✅ | ✅✅ | ✅✅ | ✅ | ✅ | **12/16** | 6 |
| **Đ13** | **StreamSLA** — Giám sát SLA | ✅ | ⚠️ | ✅ | ✅✅ | ✅ | ✅ | ✅ | ✅ | **10/16** | 10 |
| **Đ14** | **ProductMatch** — Đối sánh sản phẩm | ✅ | ⚠️ | ✅ | ⚠️ | ❌ | ✅ | ✅ | ✅ | **8/16** | 12 |
| **Đ15** | **FakeNewsTrace** — Truy vết tin giả | ✅✅ | ⚠️ | ✅ | ✅ | ❌ | ✅ | ✅✅ | ✅ | **9/16** | 11 |
| **Đ3** | **SupplyPulse** — Chuỗi cung ứng | ✅ | ✅✅ | ✅ | ❌ | ✅ | ✅✅ | ✅ | ✅ | **9/16** | 11 |
| **Đ6** | **CareFlow** — Lộ trình lâm sàng | ⚠️ | ✅✅ | ✅✅ | ❌ | ⚠️ | ✅ | ✅✅ | ⚠️ | **8/16** | 12 |
| **Đ16** | **JobMatch** — Đối sánh CV–JD | ✅ | ⚠️ | ✅ | ❌ | ❌ | ✅ | ⚠️ | ✅ | **6/16** | 16 |

*Quy đổi: ✅✅ = 2 điểm · ✅ = 1.5 · ⚠️ = 0.75 · ❌ = 0*

---

## 3. TOP 3 KHUYẾN NGHỊ — PHÂN TÍCH SÂU

### 🥇 **#1 — Đ11. CityFlow** *(khuyến nghị mạnh nhất)*

**Vì sao đứng đầu:**

| Lý do | Chi tiết |
|---|---|
| **Khoảng trống lớn nhất còn nguyên** | DGIM chiếm **15 slide = 22% chương Streaming**, có ràng buộc bucket, chứng minh cận 50%, quan hệ $O(1/r)$, và mở rộng cho số nguyên (tr.66). **0/16 nhóm** dùng làm lõi |
| **Đúng nguyên văn tình huống GV nêu** | Slide tr.53: *"Có thể có nhiều luồng đồng thời — không thể giữ nhiều cửa sổ"* — CityFlow là hiện thực hóa trực tiếp câu này |
| **Ground truth hoàn hảo** | Giá trị chính xác tính được offline ⇒ mọi sai số ước lượng đo được tuyệt đối. **Điều kiện lý tưởng cho tín hiệu #3 của GV** (lý thuyết vs thực nghiệm) |
| **Dữ liệu thật sự massive** | NYC TLC hàng trăm triệu bản ghi — tránh được lỗi của nhóm 7 (dữ liệu nhỏ, "giả vờ streaming") |
| **Độ khó vừa phải** | ⭐⭐⭐ — DGIM là thuật toán có mô tả rõ ràng trong slide, cài đặt from scratch khả thi trong thời gian có |
| **Sản phẩm bắt mắt** | Dashboard bản đồ nhiệt thời gian thực |

**Điều kiện bắt buộc để không lặp lại lỗi nhóm 14:** phải giữ **tầng FP-Growth** (mục ⑤) để trả lời câu hỏi *"đâu là phần khai phá dữ liệu?"*. Không được cắt.

**Phân công 3 người:** (1) DGIM đa luồng + mở rộng số nguyên; (2) FM + AMS + Reservoir + khung benchmark sai số; (3) Tầng FP-Growth + API + Dashboard.

---

### 🥈 **#2 — Đ9. PharmaSafe** *(an toàn nhất, được lòng giảng viên nhất)*

**Vì sao đáng chọn:**

- 📌 **Giảng viên nêu đích danh ứng dụng này** ở slide tr.9 và **không ai lấy**. Khi bảo vệ, câu mở đầu có thể là: *"Đề tài này hiện thực hóa ứng dụng thầy/cô nêu ở slide chương Frequent Patterns."* — rất khó bị chê lạc đề.
- 🎯 **Bám sát 2/3 tín hiệu chấm điểm** (§7 KB): độ đo null-invariant (G6) và nén closed/max pattern (G3, M5).
- 🔬 **FAERS là môi trường lý tưởng để chứng minh null-invariance quan trọng** — dữ liệu có cực nhiều giao dịch null (đa số cặp thuốc–phản ứng không đồng xuất hiện), đúng kịch bản mà Lift và $\chi^2$ thất bại. Có thể **chứng minh bằng số liệu thật** điều GV dạy bằng ví dụ giả định. Đây là đóng góp học thuật thực sự.
- ⭐⭐⭐ độ khó vừa phải, an toàn về tiến độ.

**Điểm yếu phải thừa nhận thẳng thắn trong báo cáo:** ground truth chỉ đánh giá được một phần (không có danh sách vàng đầy đủ). **Không được che giấu** — nêu rõ là giới hạn nghiên cứu, kèm hướng khắc phục (đối chiếu nhãn thuốc chính thức trên một mẫu).

---

### 🥉 **#3 — Đ1. FraudRing-3T** *(tham vọng nhất, rủi ro cao nhất)*

**Vì sao hấp dẫn:** là đề tài duy nhất kết hợp **cả 3 chương** — khai thác M1, khác biệt mạnh nhất có thể tạo ra. Cấu trúc 3 tầng chia gọn cho 3 thành viên. Domain fraud trống hoàn toàn. Sản phẩm demo mạnh nhất.

**Vì sao xếp #3 dù điểm bằng #2:** rủi ro C3 (thuật toán khớp bài toán). PaySim là dữ liệu **mô phỏng** — nếu "vòng gian lận phối hợp" không tồn tại trong cách sinh dữ liệu, tầng LSH sẽ không tìm được gì có ý nghĩa, và nhóm rơi vào **đúng lỗi mẫu của nhóm 12**.

**Chỉ chọn nếu chấp nhận điều kiện:** đổi tên tầng 2 thành *"lan truyền rủi ro theo tương tự hành vi"* và đặt nó dưới dạng **giả thuyết kiểm chứng được** (*"tài khoản LSH-tương tự với tài khoản gian lận có tỷ lệ gian lận cao hơn nền k lần"*) — khi đó kết quả âm tính vẫn là kết quả hợp lệ, không phá hỏng đồ án.

---

### 🎖️ Ứng viên đáng chú ý — **Đ7. ChurnPattern**

Đây là **đề tài duy nhất giải quyết trọn vẹn mâu thuẫn** đã nêu ở §1.1 Knowledge Base: nó thỏa mãn **đồng thời** yêu cầu ML của ROLE (so sánh mô hình, CV, ROC-AUC, SHAP, hyperparameter tuning) **và** yêu cầu syllabus của môn — thông qua cầu nối chính danh *discriminative frequent patterns* (Cheng et al. ICDE'07, được GV nêu tên ở slide tr.34).

**Chọn Đ7 nếu** bạn muốn giữ nguyên toàn bộ phần Machine Learning trong ROLE mà không bị chê lạc đề.

---

## 4. TÓM TẮT & CÂU HỎI QUYẾT ĐỊNH

| Nếu ưu tiên… | Chọn |
|---|---|
| **Khoảng trống lớn nhất + ground truth sạch + sản phẩm đẹp** | 🥇 **Đ11 CityFlow** |
| **An toàn nhất + được lòng giảng viên nhất + độ khó vừa** | 🥈 **Đ9 PharmaSafe** |
| **Tham vọng nhất + khác biệt mạnh nhất (cả 3 chương)** | 🥉 **Đ1 FraudRing-3T** |
| **Giữ trọn phần Machine Learning trong ROLE một cách chính danh** | 🎖️ **Đ7 ChurnPattern** |

**Ba việc cần làm ngay sau khi chọn (Phase 4 sẽ bắt đầu bằng):**
1. **Tải thử dataset và đếm số dòng thật** — xác minh C4 trước khi cam kết
2. **Hỏi giảng viên** về phạm vi (đặc biệt nếu chọn cụm B — Sequential Pattern Mining chỉ được nêu tên)
3. Đăng ký tên đề tài với lớp để "giữ chỗ" trước khi nhóm khác đổi hướng

---

*Đầu ra Phase 3. Phase 4 (thiết kế kiến trúc giải pháp chi tiết) sẽ bắt đầu sau khi bạn chọn đề tài.*
