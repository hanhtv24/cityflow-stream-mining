# CityFlow

### Hệ giám sát giao thông đô thị dựa trên truy vấn cửa sổ trượt và khai phá mẫu đồng ùn tắc trên luồng dữ liệu quy mô lớn

**Bài tập lớn môn Khai phá dữ liệu** — Lớp Hệ thống Thông tin 02, khóa 2025–2027, Học viện Công nghệ Bưu chính Viễn thông
**Nhóm 15:** Nguyễn Thuý Anh (B25CHHT076) · Trần Thị Thảo (B25CHHT113) · Trần Văn Hanh (B25CHHT092)

---

## 1. Bài toán

Trung tâm điều hành giao thông nhận luồng sự kiện chuyến đi liên tục và cần trả lời các truy vấn cửa sổ trượt trên **hàng trăm luồng song song** — mỗi khu vực địa lý là một luồng.

> Slide chương Data Streaming, tr.53: *"N có thể rất lớn (hàng triệu phần tử). Có thể có nhiều luồng đồng thời — **không thể giữ nhiều cửa sổ**."*

Với 265 khu vực taxi của New York, giữ cửa sổ đầy đủ $N = 10^6$ cho mỗi luồng đòi hỏi bộ nhớ tăng tuyến tính theo số luồng × số loại truy vấn. CityFlow dùng các cấu trúc sketch xấp xỉ để đạt bộ nhớ dưới tuyến tính với sai số có kiểm soát, đồng thời khai phá **mẫu đồng ùn tắc** giữa các khu vực.

## 2. Sáu câu hỏi hệ thống trả lời

| | Câu hỏi | Thuật toán | Sai số đo được |
|---|---|---|---:|
| **Q1** | Trong $N$ chuyến gần nhất, bao nhiêu chuyến xuất phát từ khu vực $z$? | DGIM | 2,43% |
| **Q2** | Tổng doanh thu của $N$ chuyến gần nhất? | DGIM mở rộng cho số nguyên | 0,82% |
| **Q3** | Bao nhiêu tuyến đường phân biệt đang hoạt động? | Flajolet-Martin | 6,4% |
| **Q4** | Nhu cầu có đang tập trung bất thường không? | AMS — số bất ngờ | 7,1% |
| **Q5** | Giữ mẫu đại diện nào để phân tích sâu? | Reservoir Sampling | chính xác |
| **Q6** | **Những khu vực nào thường xuyên ùn tắc CÙNG NHAU?** | **FP-Growth + 10 độ đo** | — |

## 3. Dữ liệu

**NYC TLC Trip Record Data** (High Volume For-Hire Vehicles — Uber/Lyft), công khai.

| | |
|---|---|
| Quy mô | **19.663.928** sự kiện/tháng · 12 tháng ≈ 236 triệu |
| Khu vực | 265 (`taxi_zone_lookup.csv`) |
| Chất lượng | **0 giá trị thiếu** trên toàn bộ 11 cột sử dụng |
| Đặc điểm | 44,67% bản ghi lệch thứ tự thời gian → **bắt buộc sắp lại** trước khi xử lý |

Chi tiết: [`docs/04_DATA_UNDERSTANDING.md`](docs/04_DATA_UNDERSTANDING.md)

## 4. Cài đặt

```bash
# 1. Môi trường (Python 3.12 — 3.14 chưa đủ wheel cho stack data science)
python3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install duckdb pandas pyarrow numpy requests matplotlib mlxtend pytest

# 2. Tải dữ liệu (~524 MB, lưu ngoài thư mục dự án)
.venv/Scripts/python.exe scripts/download_data.py

# 3. Chuẩn bị luồng sự kiện (lọc, tính cột dẫn xuất, SẮP THEO THỜI GIAN)
.venv/Scripts/python.exe scripts/02_prepare_data.py --month 2024-01
```

> ⚠️ Console Windows dùng bảng mã cp1252. Luôn đặt `PYTHONIOENCODING=utf-8` khi chạy script, nếu không sẽ lỗi ở dòng in tiếng Việt.

## 4b. Triển khai bằng Docker

```bash
# Tải sẵn wheel Python trên host (mạng egress của container build không ổn định
# với PyPI/Debian trong một số môi trường — xem scripts/download_docker_wheels.py)
.venv/Scripts/python.exe scripts/download_docker_wheels.py

docker compose up -d
python scripts/08_load_zones.py
```

## 5. Chạy thực nghiệm

```bash
export PYTHONIOENCODING=utf-8

.venv/Scripts/python.exe scripts/01_data_understanding.py   # xác minh dữ liệu
.venv/Scripts/python.exe scripts/03_validate_dgim.py        # E1, E2, E3
.venv/Scripts/python.exe scripts/04_experiment_h1.py        # E4 — giả thuyết H1
.venv/Scripts/python.exe scripts/05_experiment_fm_ams.py    # E5, E6
.venv/Scripts/python.exe scripts/06_experiment_registry.py  # E7
.venv/Scripts/python.exe scripts/07_experiment_mining.py    # E9, E10, E11

.venv/Scripts/python.exe -m pytest tests/                   # E12 + toàn bộ kiểm định
```

## 6. Cấu trúc mã nguồn

```
btl/
├── src/cityflow/
│   ├── sketches/            ⭐ FROM SCRATCH
│   │   ├── dgim.py                  DGIM — đếm bit 1 trong cửa sổ trượt
│   │   ├── dgim_integer.py          DGIM mở rộng cho tổng số nguyên (tr.66)
│   │   ├── flajolet_martin.py       Đếm phần tử phân biệt + vector hóa numpy
│   │   ├── ams.py                   Ước lượng mô-men / số bất ngờ
│   │   ├── reservoir.py             Lấy mẫu hồ chứa + lấy mẫu theo khóa
│   │   └── registry.py              Quản lý 535 luồng, lazy expiration
│   ├── mining/              ⭐ FROM SCRATCH
│   │   ├── fptree.py                Cây FP + bảng header
│   │   ├── fpgrowth.py              FP-Growth, mẫu đóng, mẫu cực đại
│   │   ├── apriori.py               Apriori đối chứng + số liệu 3 điểm nghẽn
│   │   ├── basket_builder.py        Rời rạc hóa theo phân vị TỪNG khu vực
│   │   ├── interestingness.py       10 độ đo, 6 bất biến với giao dịch rỗng
│   │   └── rules.py                 Sinh luật, xếp hạng, tương quan hạng
│   ├── ingest/replay.py             Nạp và phát lại luồng
│   ├── oracle/exact_window.py       Oracle chính xác (đường đi ĐỘC LẬP)
│   └── config.py                    Tham số — mọi giá trị cấu hình được
├── scripts/                         Tải dữ liệu + 7 script thực nghiệm
├── tests/                           158 kiểm định
└── docs/                            Tài liệu 8 pha
```

## 7. Nguyên tắc thiết kế

| | |
|---|---|
| **P1** | **Một lượt, không quay lại.** Tầng sketch chỉ thấy mỗi sự kiện một lần và không lưu nó |
| **P2** | **Bộ nhớ đo thật.** Mọi sketch có `memory_bytes()` đo thực tế, không ước lượng bằng công thức |
| **P3** | **Oracle tách biệt.** Giá trị chính xác tính bằng đường đi riêng, không chung một dòng mã với sketch |
| **P4** | **From scratch trước, thư viện sau.** Thư viện chỉ dùng để kiểm định chéo |
| **P5** | **Tham số là biến thực nghiệm.** $N, r, m, g, k, \text{min\_sup}$ đều cấu hình được |

## 8. Kết quả chính

### Cận lý thuyết được xác nhận trên dữ liệu thật

| Thực nghiệm | Cận trên slide | Đo thật |
|---|---|---|
| **E1** | Sai số DGIM ≤ 50% (tr.64) | **0/3.178** truy vấn vi phạm |
| **E2** | Sai số $\propto O(1/r)$ (tr.64) | Tích `sai số × r` ≈ hằng số qua 8× thay đổi $r$ |
| **E3** | Bộ nhớ $O(\log^2 N)$ (tr.58) | $N$ tăng 500× → bộ nhớ tăng 1,46× |
| **E7** | — | **87.933 sự kiện/giây**, 5,66 MB cho 535 luồng |
| **E12** | — | FP-Growth from scratch **khớp tuyệt đối** mlxtend |

### Hai đóng góp vượt ra ngoài slide

**① Giả thuyết H1 — phân bổ ngân sách trong DGIM mở rộng cho số nguyên.**
Slide tr.66 nêu cách mở rộng rồi dừng, không nói gì về phân bổ bộ nhớ giữa $m$ luồng bit. Suy dẫn bằng nhân tử Lagrange cho $r_i \propto \sqrt{2^i c_i}$ — công thức này **bác bỏ** trực giác "ưu tiên bit cao". Thực nghiệm xác nhận: phân bổ theo lý thuyết tốt hơn phân bổ đều **23,8%**, trong khi phân bổ theo trực giác **tệ hơn** phân bổ đều 12,2%. Bit gây sai số nhiều nhất là **bit 4** (29,8%), không phải bit 7 (4,5%).
→ [`docs/06_KET_QUA_E4_GIA_THUYET_H1.md`](docs/06_KET_QUA_E4_GIA_THUYET_H1.md)

**② Hiệu chuẩn độ chệch của Flajolet-Martin.**
Sơ đồ tổng hợp mà slide tr.40 khuyến nghị chệch lên có hệ thống **2,3 lần**, và hằng số $\varphi = 0{,}77351$ kinh điển **làm tệ thêm** vì nó dành cho một biến thể khác. Sau khi hiệu chuẩn riêng theo $m$, sai số vượt được cận 11,2% của ước lượng $2^R$ đơn tại $m \ge 128$.
→ [`docs/07_KET_QUA_E5_E6.md`](docs/07_KET_QUA_E5_E6.md)

## 9. Tài liệu

| Tài liệu | Nội dung |
|---|---|
| [`00_KNOWLEDGE_BASE.md`](docs/00_KNOWLEDGE_BASE.md) | Kiến thức môn học, thuật toán, tín hiệu chấm điểm |
| [`01_PHAN_TICH_DE_TAI_CAC_NHOM.md`](docs/01_PHAN_TICH_DE_TAI_CAC_NHOM.md) | Phân tích 16 đề tài, khoảng trống nghiên cứu |
| [`02_DE_XUAT_DE_TAI.md`](docs/02_DE_XUAT_DE_TAI.md) | 16 đề xuất, chấm theo 8 tiêu chí |
| [`03_THIET_KE_KIEN_TRUC.md`](docs/03_THIET_KE_KIEN_TRUC.md) | Kiến trúc 7 tầng, CRISP-DM, ma trận thực nghiệm |
| [`04_DATA_UNDERSTANDING.md`](docs/04_DATA_UNDERSTANDING.md) | Xác minh dữ liệu, 3 giả định sai đã sửa |
| [`05_KET_QUA_E1_E3.md`](docs/05_KET_QUA_E1_E3.md) | DGIM — cận 50%, quan hệ $O(1/r)$, bộ nhớ |
| [`06_KET_QUA_E4_GIA_THUYET_H1.md`](docs/06_KET_QUA_E4_GIA_THUYET_H1.md) | Giả thuyết H1 |
| [`07_KET_QUA_E5_E6.md`](docs/07_KET_QUA_E5_E6.md) | Flajolet-Martin, AMS |
| [`08_KET_QUA_E7.md`](docs/08_KET_QUA_E7.md) | Thông lượng 535 luồng |

## 10. Tài liệu tham khảo

1. Leskovec, J., Rajaraman, A., & Ullman, J. D. (2020). *Mining of Massive Datasets* (3rd ed.). Cambridge University Press. http://www.mmds.org
2. Datar, M., Gionis, A., Indyk, P., & Motwani, R. (2002). Maintaining stream statistics over sliding windows. *SIAM Journal on Computing*, 31(6), 1794–1813.
3. Flajolet, P., & Martin, G. N. (1985). Probabilistic counting algorithms for data base applications. *Journal of Computer and System Sciences*, 31(2), 182–209.
4. Alon, N., Matias, Y., & Szegedy, M. (1996). The space complexity of approximating the frequency moments. *STOC '96*.
5. Han, J., Pei, J., & Yin, Y. (2000). Mining frequent patterns without candidate generation. *SIGMOD '00*.
6. Agrawal, R., & Srikant, R. (1994). Fast algorithms for mining association rules. *VLDB '94*.
7. Tan, P.-N., Kumar, V., & Srivastava, J. (2002). Selecting the right interestingness measure for association patterns. *KDD '02*.
8. Wu, T., Chen, Y., & Han, J. (2010). Re-examination of interestingness measures in pattern mining. *Data Mining and Knowledge Discovery*, 21(3), 371–397.
9. Durand, M., & Flajolet, P. (2003). Loglog counting of large cardinalities. *ESA '03*.
10. NYC Taxi & Limousine Commission. TLC Trip Record Data. https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page
