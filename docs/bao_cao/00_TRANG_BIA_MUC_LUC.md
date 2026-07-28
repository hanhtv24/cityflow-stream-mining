# HỌC VIỆN CÔNG NGHỆ BƯU CHÍNH VIỄN THÔNG {.unnumbered .unlisted}
## KHOA ĐÀO TẠO SAU ĐẠI HỌC {.unnumbered .unlisted}

---

# BÀI TẬP LỚN MÔN KHAI PHÁ DỮ LIỆU {.unnumbered .unlisted}

# CITYFLOW {.unnumbered .unlisted}
## Hệ giám sát giao thông đô thị dựa trên truy vấn cửa sổ trượt và khai phá mẫu đồng ùn tắc trên luồng dữ liệu chuyến đi quy mô lớn {.unnumbered .unlisted}

---

**Lớp:** Hệ thống Thông tin 02, khóa 2025–2027
**Nhóm thực hiện:** Nhóm 15
**Thành viên:**

| Họ tên | Mã học viên |
|---|---|
| Nguyễn Thuý Anh | B25CHHT076 |
| Trần Thị Thảo | B25CHHT113 |
| Trần Văn Hanh | B25CHHT092 |

**Giảng viên hướng dẫn:** Thanh-Hà Đỗ

---

*Hà Nội, 2026*

---
---

# LỜI CẢM ƠN

*(Phần này do nhóm tự viết theo trải nghiệm thực tế trong quá trình thực hiện đồ án — không thể tạo thay bằng nội dung tổng hợp.)*

---

# TÓM TẮT (ABSTRACT)

Hệ thống giám sát giao thông đô thị truyền thống đối mặt với một mâu thuẫn cơ bản: dữ liệu chuyến đi phát sinh ở tốc độ hàng triệu bản ghi mỗi giờ, trong khi cơ sở hạ tầng tính toán chỉ có bộ nhớ giới hạn để duy trì trạng thái cho hàng trăm khu vực địa lý song song. Đồ án này trình bày **CityFlow**, một hệ thống kết hợp bốn cấu trúc dữ liệu xấp xỉ xử lý luồng — DGIM, DGIM mở rộng cho tổng số nguyên, Flajolet-Martin và AMS (Alon-Matias-Szegedy) — với một tầng khai phá mẫu FP-Growth để đồng thời (a) trả lời các truy vấn cửa sổ trượt với bộ nhớ dưới tuyến tính và sai số có kiểm soát, và (b) phát hiện các nhóm khu vực có xu hướng ùn tắc đồng thời.

Toàn bộ năm thuật toán lõi được cài đặt **from scratch** bằng Python, đối chiếu tính đúng đắn với thư viện tham chiếu (`mlxtend`) và kiểm chứng bằng 158 kiểm định đơn vị tái hiện trực tiếp các ví dụ số trong tài liệu giảng dạy. Hệ thống được đánh giá trên **19.663.928 bản ghi** chuyến đi thật của New York City TLC (tháng 01/2024), qua mười hai thực nghiệm (E1–E12) đối chiếu từng cận sai số lý thuyết với số liệu đo thật.

Ba đóng góp chính của đồ án: **(1)** xác nhận thực nghiệm đầy đủ các cận lý thuyết của DGIM (sai số ≤ 50%, quan hệ $O(1/r)$, bộ nhớ $O(\log^2 N)$) trên dữ liệu quy mô lớn; **(2)** một giả thuyết nghiên cứu độc lập về phân bổ ngân sách bộ nhớ tối ưu trong DGIM mở rộng, được suy dẫn bằng nhân tử Lagrange và kiểm chứng thực nghiệm cho kết quả bác bỏ trực giác thông thường; **(3)** bằng chứng thực nghiệm hoàn hảo (biến thiên đúng 0,0% so với 10.259% của Lift) cho tính chất bất biến với giao dịch rỗng của năm độ đo tương quan, thay thế lời phê phán lý thuyết bằng số liệu thật.

**Từ khóa:** khai phá dữ liệu luồng, cửa sổ trượt, DGIM, Flajolet-Martin, AMS, FP-Growth, độ đo tương quan, null-invariance, giao thông đô thị.

---

# MỤC LỤC {.unnumbered .unlisted}

*(Mục lục được sinh tự động ở trang sau bởi Word/pandoc dựa trên các tiêu đề chương — không liệt kê thủ công tại đây để tránh trùng lặp.)*

# DANH MỤC TỪ VIẾT TẮT

| Viết tắt | Tiếng Anh | Giải thích |
|---|---|---|
| DGIM | Datar-Gionis-Indyk-Motwani | Thuật toán đếm bit 1 trong cửa sổ trượt |
| AMS | Alon-Matias-Szegedy | Thuật toán ước lượng mô-men của luồng |
| FM | Flajolet-Martin | Thuật toán đếm phần tử phân biệt |
| FP-Growth | Frequent Pattern Growth | Thuật toán khai phá tập mục thường xuyên |
| CRISP-DM | Cross-Industry Standard Process for Data Mining | Quy trình chuẩn khai phá dữ liệu |
| TLC | Taxi & Limousine Commission | Ủy ban Taxi & Limousine New York |
| FHVHV | High Volume For-Hire Vehicle | Xe hợp đồng khối lượng lớn (Uber/Lyft) |
| API | Application Programming Interface | Giao diện lập trình ứng dụng |
| DDL | Data Definition Language | Ngôn ngữ định nghĩa dữ liệu |

*(Danh mục hình và danh mục bảng sinh tự động từ số thứ tự hình/bảng khi xuất bản — không liệt kê thủ công trong bản thảo Markdown để tránh sai lệch khi chỉnh sửa nội dung.)*
