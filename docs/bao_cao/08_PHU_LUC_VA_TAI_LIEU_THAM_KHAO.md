# PHỤ LỤC

## Phụ lục A. Cấu trúc mã nguồn

```
btl/
├── src/cityflow/
│   ├── sketches/            FROM SCRATCH: dgim.py, dgim_integer.py,
│   │                        flajolet_martin.py, ams.py, reservoir.py, registry.py
│   ├── mining/               FROM SCRATCH: fptree.py, fpgrowth.py, apriori.py,
│   │                        basket_builder.py, interestingness.py, rules.py, persist.py
│   ├── ingest/replay.py      Nạp và phát lại luồng
│   ├── oracle/exact_window.py  Oracle chính xác (đường đi độc lập)
│   ├── api/                  FastAPI: main.py, state.py, routers/
│   ├── db/                   SQLAlchemy: models.py, session.py
│   └── config.py             Tham số hệ thống
├── scripts/                  Tải dữ liệu + 9 script thực nghiệm
├── tests/                    158 kiểm định đơn vị
├── web/                      Dashboard React + Vite + Tailwind
├── sql/init.sql              Lược đồ PostgreSQL
├── docker-compose.yml        Triển khai 3 dịch vụ: db, api, web
└── docs/                     Toàn bộ tài liệu Phase 1–8
```

## Phụ lục B. Bảng tra cứu tham số đã chốt qua thực nghiệm

| Tham số | Ký hiệu | Giá trị | Căn cứ |
|---|---|---:|---|
| Độ rộng cửa sổ | $N$ | $10^6$ | Cấu hình vận hành thiết kế |
| Số bucket mỗi kích thước (DGIM) | $r$ | 8 | E2: sai số 2,43%, bộ nhớ gần như không đổi so với $r=2$ |
| Số bit doanh thu | $m$ | 8 | Data Understanding: phân vị 99,9 = 227,42 USD |
| Phân bổ ngân sách DGIM-Integer | $r_i$ | $[3,5,7,10,13,12,9,5]$ | E4: `sqrt_weighted` ngân sách 64 |
| Số hàm băm Flajolet-Martin | $m$ | 256 | E5: sai số trung vị 6,4%, dưới cận 11,2% |
| Số biến AMS | $k$ | 100 | E6: sai số 7,1% |
| Kích thước mẫu Reservoir | $s$ | 100.000 | Thiết kế Phase 4 |
| Độ dài cửa sổ khai phá mẫu | — | 15 phút | Thiết kế Phase 4 |
| Ngưỡng phân vị rời rạc hóa | $q$ | 90% | E9: điều chỉnh từ 80% do CSDL quá dày |

## Phụ lục C. Ví dụ số đã tái hiện làm kiểm định đơn vị

| Ví dụ | Nguồn | Kết quả kỳ vọng | File kiểm định |
|---|---|---|---|
| DGIM: bucket 1,1,2,4 | Slide tr.65 | Ước lượng = 6 | `test_dgim.py` |
| DGIM: bucket 1,1,2,4,8 | Slide tr.61 | Ước lượng = 12 | `test_dgim.py` |
| DGIM: gộp bucket | Slide tr.63 | 1,1,2,4 → 1,2,2,4 | `test_dgim.py` |
| Flajolet-Martin: trailing zeros | Slide tr.37 | $r(12)=2$ | `test_sketches.py` |
| AMS: luồng 15 phần tử | Slide tr.48 | Ước lượng = 55 | `test_sketches.py` |
| AMS: bài tập mô-men bậc 3 | Slide tr.50 | Bậc 2 = 21, bậc 3 = 51 | `test_sketches.py` |
| FP-Growth: f-list | Slide tr.22 | f,c,a,b,m,p đều thường xuyên | `test_mining.py` |
| Basketball/Cereal | Slide tr.36 | Confidence gây hiểu lầm | `test_mining.py` |

## Phụ lục D. Lệnh tái lập kết quả

```bash
# Môi trường
python3.12 -m venv .venv
.venv/Scripts/python.exe -m pip install -e ".[dev]"

# Dữ liệu
.venv/Scripts/python.exe scripts/download_data.py
.venv/Scripts/python.exe scripts/02_prepare_data.py --month 2024-01

# Thực nghiệm (PYTHONIOENCODING=utf-8 bắt buộc trên Windows)
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/01_data_understanding.py
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/03_validate_dgim.py
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/04_experiment_h1.py
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/05_experiment_fm_ams.py
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/06_experiment_registry.py
PYTHONIOENCODING=utf-8 .venv/Scripts/python.exe scripts/07_experiment_mining.py

# Kiểm định
.venv/Scripts/python.exe -m pytest tests/ -v

# Triển khai
docker compose up -d
```

---

# TÀI LIỆU THAM KHẢO

*(Định dạng IEEE)*

[1] J. Leskovec, A. Rajaraman, and J. D. Ullman, *Mining of Massive Datasets*, 3rd ed. Cambridge, U.K.: Cambridge University Press, 2020. [Online]. Available: http://www.mmds.org

[2] M. Datar, A. Gionis, P. Indyk, and R. Motwani, "Maintaining stream statistics over sliding windows," *SIAM Journal on Computing*, vol. 31, no. 6, pp. 1794–1813, 2002.

[3] P. Flajolet and G. N. Martin, "Probabilistic counting algorithms for data base applications," *Journal of Computer and System Sciences*, vol. 31, no. 2, pp. 182–209, 1985.

[4] N. Alon, Y. Matias, and M. Szegedy, "The space complexity of approximating the frequency moments," in *Proc. 28th Annu. ACM Symp. Theory of Computing (STOC)*, 1996, pp. 20–29.

[5] J. Han, J. Pei, and Y. Yin, "Mining frequent patterns without candidate generation," in *Proc. ACM SIGMOD Int. Conf. Management of Data*, 2000, pp. 1–12.

[6] R. Agrawal and R. Srikant, "Fast algorithms for mining association rules," in *Proc. 20th Int. Conf. Very Large Data Bases (VLDB)*, 1994, pp. 487–499.

[7] P.-N. Tan, V. Kumar, and J. Srivastava, "Selecting the right interestingness measure for association patterns," in *Proc. 8th ACM SIGKDD Int. Conf. Knowledge Discovery and Data Mining*, 2002, pp. 32–41.

[8] T. Wu, Y. Chen, and J. Han, "Re-examination of interestingness measures in pattern mining: A unified framework," *Data Mining and Knowledge Discovery*, vol. 21, no. 3, pp. 371–397, 2010.

[9] M. Durand and P. Flajolet, "Loglog counting of large cardinalities," in *Proc. 11th Annu. European Symp. Algorithms (ESA)*, 2003, pp. 605–617.

[10] New York City Taxi & Limousine Commission, "TLC Trip Record Data." [Online]. Available: https://www.nyc.gov/site/tlc/about/tlc-trip-record-data.page

[11] R. Agarwal, C. Aggarwal, and V. Prasad, "A tree projection algorithm for generation of frequent item sets," *Journal of Parallel and Distributed Computing*, vol. 61, no. 3, pp. 350–371, 2001.

[12] Thanh-Hà Đỗ, "Advanced Data Mining: Mining Frequent Pattern, Association and Correlations" and "Finding Similar Items" and "Thuật toán cho Khoa học Dữ liệu: Luồng dữ liệu," Bài giảng môn Khai phá dữ liệu, Học viện Công nghệ Bưu chính Viễn thông, 2026.
