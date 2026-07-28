# CHECKLIST ĐỐI CHIẾU YÊU CẦU ĐỒ ÁN

*(Không có rubric chấm điểm chính thức được cung cấp — checklist này đối chiếu với yêu cầu chung của bài tập lớn và 8 tiêu chí đánh giá nhóm đã tự đặt ra khi chọn đề tài, xem Chương 3.)*

## A. Yêu cầu sản phẩm

| # | Yêu cầu | Trạng thái | Vị trí |
|:--:|---|:---:|---|
| 1 | Source Code | ✅ | `src/cityflow/` |
| 2 | Dataset | ✅ | NYC TLC FHVHV 2024-01, script tải tự động `scripts/download_data.py` |
| 3 | Notebook | ⚠️ Chưa | Script thực nghiệm (`scripts/0N_*.py`) đóng vai trò tương đương, chưa chuyển sang `.ipynb` |
| 4 | Trained Model | N/A | Bài toán khai phá mẫu + ước lượng luồng, không phải học có giám sát — giải thích ở §14.3 Phase 4 |
| 5 | REST API | ✅ | `src/cityflow/api/`, đã kiểm chứng end-to-end |
| 6 | Web Application | ✅ | `web/`, 4 màn hình, đã kiểm chứng render dữ liệu thật |
| 7 | Dashboard | ✅ | Tích hợp trong Web Application (Live Monitor, Accuracy Lab, Pattern Explorer, Benchmark) |
| 8 | Database | ✅ | PostgreSQL, 7 bảng, đã kiểm chứng ghi/đọc dữ liệu thật |
| 9 | Docker | ✅ | `docker compose up` chạy đủ 3 dịch vụ (`db` healthy, `api`, `web`); đã kiểm chứng end-to-end: `/api/status`, `/api/zones`, `/api/rules` (484 luật thật), `/api/bench` (5/5 bộ thực nghiệm), và dashboard tại `:3000` render đúng dữ liệu thật |
| 10 | README | ✅ | `README.md` |

## B. Yêu cầu quy trình khoa học (CRISP-DM)

| Pha | Đáp ứng | Vị trí |
|---|:---:|---|
| Business Understanding | ✅ | Chương 1, 3 báo cáo · Phase 4 §1 |
| Data Understanding | ✅ | Chương 3 báo cáo · `04_DATA_UNDERSTANDING.md` |
| Data Preparation | ✅ | `scripts/02_prepare_data.py`, xử lý 44,67% bản ghi lệch thời gian |
| Modeling | ✅ | Chương 4 báo cáo, 5 thuật toán from-scratch |
| Evaluation | ✅ | Chương 5 báo cáo, 12 thực nghiệm E1–E12 |
| Deployment | ✅ | API + CSDL + Web đã đóng gói Docker, kiểm chứng `docker compose up` chạy đủ và đúng dữ liệu thật |

## C. Yêu cầu Machine Learning

| Yêu cầu | Đáp ứng | Ghi chú |
|---|:---:|---|
| So sánh nhiều thuật toán | ✅ | FP-Growth vs Apriori (E9); 3 chiến lược tổng hợp Flajolet-Martin (E5); 3 chiến lược phân bổ DGIM-Integer (E4) |
| Cross Validation | ❌ N/A | Không áp dụng — không phải bài toán học có giám sát |
| Hyperparameter Tuning | ✅ | $r$, $m$, $g$, $k$, min_support đều được quét và chốt qua thực nghiệm |
| Feature Engineering | ✅ | Rời rạc hóa theo phân vị riêng từng khu vực (basket_builder.py) |
| Feature Selection | N/A | Không áp dụng |
| Explainability (SHAP/LIME) | ❌ N/A | Không áp dụng — luật kết hợp vốn đã tự giải thích được |
| Confusion Matrix / ROC / AUC | ❌ N/A | Không áp dụng — không phải bài toán phân loại |
| Precision / Recall / F1 | Thay thế | Sai số tương đối, độ chệch, hệ số biến thiên — đúng bộ độ đo cho bài toán ước lượng luồng |

**Giải thích việc không áp dụng nhóm ML cổ điển:** đề tài thuộc phạm trù *stream mining* và *frequent pattern mining* (MMDS), không phải học có giám sát. Áp đặt Cross-Validation/ROC/SHAP vào bài toán này sẽ gượng ép và sai bản chất — giới hạn này được nêu rõ và nhất quán xuyên suốt toàn bộ đồ án.

## D. Yêu cầu tài liệu luận văn

| Mục | Trạng thái | File |
|---|:---:|---|
| Abstract | ✅ | `bao_cao/00_TRANG_BIA_MUC_LUC.md` |
| Lời cảm ơn | ⚠️ Để trống | Cần nhóm tự viết theo trải nghiệm thật |
| Mục lục, danh mục hình/bảng | ✅ (khung) | Sinh tự động khi xuất PDF/DOCX |
| Chương 1: Giới thiệu | ✅ | `bao_cao/01_CHUONG1_GIOI_THIEU.md` |
| Chương 2: Cơ sở lý thuyết | ✅ | `bao_cao/02_CHUONG2_CO_SO_LY_THUYET.md` |
| Chương 3: Phân tích bài toán | ✅ | `bao_cao/03_CHUONG3_PHAN_TICH_BAI_TOAN.md` |
| Chương 4: Thiết kế hệ thống | ✅ | `bao_cao/04_CHUONG4_THIET_KE_HE_THONG.md` |
| Chương 5: Thực nghiệm | ✅ | `bao_cao/05_CHUONG5_THUC_NGHIEM.md` |
| Chương 6: Đánh giá | ✅ | `bao_cao/06_CHUONG6_DANH_GIA.md` |
| Chương 7: Kết luận | ✅ | `bao_cao/07_CHUONG7_KET_LUAN.md` |
| Phụ lục | ✅ | `bao_cao/08_PHU_LUC_VA_TAI_LIEU_THAM_KHAO.md` |
| Tài liệu tham khảo (IEEE) | ✅ | Cùng file phụ lục, 12 mục |
| Slide bảo vệ | ✅ | `slides/CityFlow_Slide_Bao_Ve.pptx`, 17 trang |
| Script demo | ✅ | `bao_cao/09_SCRIPT_DEMO.md` |

## E. Tám tiêu chí chọn đề tài — đối chiếu cuối kỳ

| Tiêu chí | Đạt | Bằng chứng |
|---|:---:|---|
| C1: lõi ≥2 thuật toán MMDS | ✅ | 5 thuật toán/cấu trúc + Apriori đối chứng |
| C2: không trùng 16 nhóm | ✅ | DGIM làm lõi — 0/16 nhóm khác dùng |
| C3: thuật toán khớp bản chất bài toán | ✅ | Cửa sổ trượt cho truy vấn thời gian thực; FP-Growth cho đồng xuất hiện |
| C4: dữ liệu đủ lớn | ✅ | 19.663.928 sự kiện thật |
| C5: ground truth định lượng | ✅✅ | Oracle chính xác độc lập cho mọi thực nghiệm |
| C6: đủ 6 pha CRISP-DM | ✅ | Chương 3–6 báo cáo |
| C7: khai thác ≥2 khoảng trống | ✅ | DGIM (G1), null-invariance (G6), phân bổ ngân sách (nghiên cứu độc lập) |
| C8: sản phẩm chạy được | ✅ | API + CSDL + Docker đã kiểm chứng chạy đầy đủ, một lệnh |

## F. Việc còn lại / khuyến nghị trước khi nộp

1. **Viết Lời cảm ơn** — phần duy nhất không thể tạo thay.
2. **Chuyển script thực nghiệm sang Jupyter Notebook** nếu định dạng nộp bài yêu cầu `.ipynb` tường minh (nội dung khoa học đã đầy đủ trong script `.py`).
3. **Render slide thành ảnh để xem trước** — môi trường phát triển hiện tại không có LibreOffice cài sẵn; đã QA thay thế bằng kiểm tra cấu trúc XML, nội dung văn bản, và tọa độ hình học (không vượt biên, không chồng lấn), nhưng nên xem trực tiếp bằng PowerPoint/LibreOffice trước khi trình bày chính thức.
4. **Cân nhắc xin xác nhận rubric chính thức từ giảng viên** nếu có, để đối chiếu chính xác hơn checklist tự suy luận này.
5. **(Tùy chọn) Mở rộng 12 tháng dữ liệu** — hiện đánh giá trên 1 tháng (19,66 triệu sự kiện), đã đủ lớn để thể hiện tính chất bất đối xứng logarit; mở rộng toàn bộ 12 tháng (~236 triệu bản ghi) sẽ tốn nhiều giờ tải + xử lý, đã liệt kê thành hướng phát triển ở Chương 7 thay vì thực hiện ngay.

### Đã xác minh — Docker chạy một lệnh thật (không phải tuyên bố suông)

```
docker compose up -d
```
→ 3 container `Up`: `db` (healthy), `api`, `web`. Đã kiểm chứng qua HTTP thật:
`/api/status`, `/api/zones` (265 khu vực), `/api/rules` (484 luật thật, khớp log thực nghiệm), `/api/bench` (5/5 bộ E1–E11), và dashboard tại `localhost:3000` render đúng dữ liệu — không có phần nào giả lập.

**Sự cố kỹ thuật đã gặp và khắc phục:** mạng egress của container trong môi trường build không ổn định với PyPI/Debian (xác nhận qua nhiều lần thử, có lần treo 24 phút rồi mới lộ lỗi thật). Giải pháp: tải sẵn wheel Python trên host (`scripts/download_docker_wheels.py`), cài offline trong image bằng `pip install --no-index`. npm/registry.npmjs.org không gặp vấn đề tương tự.
