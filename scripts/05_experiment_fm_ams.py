"""Phase 5 — Bước 5: Thực nghiệm E5 (Flajolet-Martin) và E6 (AMS).

E5: đếm số TUYẾN phân biệt (cặp đón-trả).
    Ground truth cả tháng = 58.911 tuyến (docs/04_DATA_UNDERSTANDING §7).
    Câu hỏi: chiến lược tổng hợp nào của slide tr.40 đạt độ chính xác nào, và có
    vượt được cận 11,2% của ước lượng 2^R đơn lẻ không?

E6: số bất ngờ (mô-men bậc 2) trên cửa sổ 15 phút.
    Đã đẩy lên sớm theo khuyến nghị docs/04_DATA_UNDERSTANDING §5: phân phối khu
    vực đều hơn dự kiến (top 10 chỉ 13,3%) nên số bất ngờ ở phạm vi toàn cục có
    thể mất hiệu lực. Cần kiểm chứng trên cửa sổ ngắn.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
from collections import defaultdict
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.config import PROCESSED_DIR  # noqa: E402
from cityflow.sketches.ams import AMS, exact_moment  # noqa: E402
from cityflow.sketches.flajolet_martin import FlajoletMartin  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "docs" / "e5_e6_results.json"
WINDOW_MINUTES = 15


def section(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def fm_over_distinct(distinct_items: np.ndarray, m: int, g: int, seed: int) -> FlajoletMartin:
    """Nạp Flajolet-Martin bằng TẬP PHÂN BIỆT thay vì toàn bộ luồng.

    Kết quả HOÀN TOÀN GIỐNG việc nạp cả luồng: trạng thái của FM chỉ là
    R_j = max trên các phần tử, và max là phép lũy đẳng — nạp lại phần tử đã thấy
    không đổi gì (đã có unit test test_duplicates_do_not_change_estimate).

    Đây là tối ưu hóa cho HARNESS ĐO ĐẠC, không phải cho hệ thống luồng: hệ thống
    thật vẫn phải xử lý từng sự kiện vì nó không biết trước tập phân biệt.
    Nếu không tối ưu, E5 phải chạy 19,7 triệu x 64 = 1,26 tỷ phép băm.
    """
    fm = FlajoletMartin(m=m, g=g, seed=seed)
    for it in distinct_items:
        fm.update(int(it))
    return fm


def main() -> int:
    print("Nạp dữ liệu...")
    t0 = time.perf_counter()
    table = pq.read_table(PROCESSED_DIR / "events_2024-01.parquet",
                          columns=["pickup_datetime", "pu_zone", "do_zone"])
    pu = table["pu_zone"].to_numpy(zero_copy_only=False).astype(np.int64)
    do = table["do_zone"].to_numpy(zero_copy_only=False).astype(np.int64)
    ts = table["pickup_datetime"].to_numpy(zero_copy_only=False).astype("datetime64[s]")
    route = pu * 1000 + do
    n = len(pu)
    print(f"  {n:,} sự kiện  ({time.perf_counter() - t0:.1f}s)")

    results: dict = {"n_events": n, "E5": {}, "E6": {}}

    # =====================================================================
    section("E5a — SỐ TUYẾN PHÂN BIỆT CẢ THÁNG  (ground truth = số đếm chính xác)")

    truth = int(len(np.unique(route)))
    distinct = np.unique(route)
    print(f"  Ground truth: {truth:,} tuyến phân biệt (tối đa lý thuyết 265^2 = 70.225)\n")

    print("  Cận lý thuyết của ước lượng 2^R đơn lẻ (luôn là lũy thừa của 2):")
    lo, hi = 2 ** int(np.floor(np.log2(truth))), 2 ** int(np.ceil(np.log2(truth)))
    print(f"      2^{int(np.log2(lo))} = {lo:,}  ->  sai số {abs(lo - truth) / truth:+.1%}")
    print(f"      2^{int(np.log2(hi))} = {hi:,}  ->  sai số {abs(hi - truth) / truth:+.1%}")
    print(f"      => KHÔNG ước lượng 2^R đơn nào tốt hơn {min(abs(lo-truth), abs(hi-truth))/truth:.1%}\n")

    SEEDS = 20
    strategies: dict[str, list[float]] = defaultdict(list)
    for seed in range(SEEDS):
        for k, v in fm_over_distinct(distinct, m=64, g=8, seed=seed).all_estimates().items():
            strategies[k].append(v)

    print(f"  Chiến lược tổng hợp (m=64, g=8, {SEEDS} hạt giống):\n")
    print(f"  {'Chiến lược':<26} {'Ước lượng TV':>14} {'Sai số TV':>11} "
          f"{'Sai số p90':>11} {'Hệ số biến thiên':>18}")
    print("  " + "-" * 84)
    for name, vals in strategies.items():
        errs = [abs(v - truth) / truth for v in vals]
        cv = statistics.pstdev(vals) / statistics.fmean(vals)
        results["E5"][name] = {"median_estimate": statistics.median(vals),
                               "median_rel_error": statistics.median(errs),
                               "p90_rel_error": float(np.percentile(errs, 90)), "cv": cv}
        print(f"  {name:<26} {statistics.median(vals):>14,.0f} "
              f"{statistics.median(errs):>10.1%} {np.percentile(errs, 90):>10.1%} {cv:>17.1%}")

    best = min(results["E5"].items(), key=lambda kv: kv[1]["median_rel_error"])
    floor = min(abs(lo - truth), abs(hi - truth)) / truth
    print(f"\n  Tốt nhất: {best[0]} — sai số trung vị {best[1]['median_rel_error']:.1%}")
    print(f"  Cận của 2^R đơn: {floor:.1%}  ->  "
          f"{'ĐÃ VƯỢT' if best[1]['median_rel_error'] < floor else 'CHƯA VƯỢT'}")

    # =====================================================================
    section("E5b — ẢNH HƯỞNG CỦA m VÀ g")
    print(f"  {'m':>5} {'g':>4} {'Sai số TV':>11} {'Hệ số biến thiên':>18} {'Bộ nhớ (B)':>12}")
    print("  " + "-" * 54)
    results["E5_mg"] = {}
    for m, g in [(8, 1), (16, 4), (32, 4), (64, 8), (128, 8), (256, 16)]:
        vals = [fm_over_distinct(distinct, m, g, s).estimate_loglog() for s in range(12)]
        errs = [abs(v - truth) / truth for v in vals]
        mem = fm_over_distinct(distinct, m, g, 0).memory_bytes()
        cv = statistics.pstdev(vals) / statistics.fmean(vals)
        results["E5_mg"][f"m{m}_g{g}"] = {"m": m, "g": g,
                                          "median_rel_error": statistics.median(errs),
                                          "cv": cv, "memory_bytes": mem}
        print(f"  {m:>5} {g:>4} {statistics.median(errs):>10.1%} {cv:>17.1%} {mem:>12,}")

    # =====================================================================
    section(f"E6 — SỐ BẤT NGỜ TRÊN CỬA SỔ {WINDOW_MINUTES} PHÚT")

    t0 = time.perf_counter()
    origin = ts[0].astype("datetime64[s]").astype(np.int64)
    win_id = ((ts.astype(np.int64) - origin) // (WINDOW_MINUTES * 60)).astype(np.int64)
    bounds = np.searchsorted(win_id, np.arange(win_id[-1] + 2))
    n_windows = len(bounds) - 1
    print(f"  {n_windows:,} cửa sổ {WINDOW_MINUTES} phút  ({time.perf_counter() - t0:.1f}s)")

    exact_vals, sizes = [], []
    for w in range(n_windows):
        seg = pu[bounds[w]:bounds[w + 1]]
        if len(seg) < 100:
            continue
        counts = np.bincount(seg)
        exact_vals.append(int((counts.astype(np.int64) ** 2).sum()))
        sizes.append(len(seg))

    exact_vals = np.array(exact_vals, dtype=np.float64)
    sizes = np.array(sizes)
    print(f"  {len(exact_vals):,} cửa sổ có >= 100 sự kiện\n")

    print("  Phân bố số bất ngờ CHÍNH XÁC theo cửa sổ:")
    print(f"      min    = {exact_vals.min():>14,.0f}")
    print(f"      p25    = {np.percentile(exact_vals, 25):>14,.0f}")
    print(f"      trung vị= {np.median(exact_vals):>13,.0f}")
    print(f"      p75    = {np.percentile(exact_vals, 75):>14,.0f}")
    print(f"      max    = {exact_vals.max():>14,.0f}")
    print(f"      max/trung vị = {exact_vals.max() / np.median(exact_vals):.1f}x")

    # Chuẩn hóa theo kích thước cửa sổ: mô-men bậc 2 tăng theo bình phương số sự kiện,
    # nên so sánh thô giữa giờ cao điểm và giờ thấp điểm là vô nghĩa.
    normalized = exact_vals / (sizes.astype(np.float64) ** 2)
    print(f"\n  Sau khi chuẩn hóa theo n^2 (loại bỏ ảnh hưởng kích thước cửa sổ):")
    print(f"      trung vị = {np.median(normalized):.5f}")
    print(f"      max      = {normalized.max():.5f}   ->  {normalized.max()/np.median(normalized):.1f}x trung vị")
    print(f"      min      = {normalized.min():.5f}")

    results["E6"]["exact"] = {
        "n_windows": int(len(exact_vals)),
        "median": float(np.median(exact_vals)), "max": float(exact_vals.max()),
        "max_over_median": float(exact_vals.max() / np.median(exact_vals)),
        "normalized_median": float(np.median(normalized)),
        "normalized_max_over_median": float(normalized.max() / np.median(normalized)),
    }

    # --- Độ chính xác của AMS theo k -------------------------------------
    print(f"\n  Độ chính xác AMS theo số biến k (200 cửa sổ mẫu):")
    print(f"  {'k':>6} {'Sai số TV':>11} {'Sai số p90':>11} {'Bộ nhớ (B)':>12}")
    print("  " + "-" * 44)

    sample_windows = np.linspace(0, n_windows - 1, 200, dtype=int)
    results["E6"]["ams"] = {}
    for k in (10, 50, 100, 500):
        errs = []
        mem = 0
        for w in sample_windows:
            seg = pu[bounds[w]:bounds[w + 1]]
            if len(seg) < 100:
                continue
            truth_w = exact_moment(seg.tolist(), 2)
            ams = AMS(k=k, seed=int(w))
            for it in seg:
                ams.update(int(it))
            mem = ams.memory_bytes()
            errs.append(abs(ams.surprise_number() - truth_w) / truth_w)
        results["E6"]["ams"][f"k{k}"] = {
            "k": k, "median_rel_error": statistics.median(errs),
            "p90_rel_error": float(np.percentile(errs, 90)), "memory_bytes": mem}
        print(f"  {k:>6} {statistics.median(errs):>10.1%} "
              f"{np.percentile(errs, 90):>10.1%} {mem:>12,}")

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n\nKết quả đã lưu: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
