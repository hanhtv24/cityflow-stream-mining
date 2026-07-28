"""Phase 5 — Bước 7: Thực nghiệm E9, E10, E11 — tầng khai phá mẫu (Q6).

E9  : FP-Growth vs Apriori — thời gian, bộ nhớ, số ứng viên (3 điểm nghẽn tr.19)
E10 : Độ nhạy với giao dịch rỗng — chứng minh null-invariance trên DỮ LIỆU THẬT
E11 : Nén mẫu — closed / maximal so với toàn bộ tập thường xuyên (tr.13)

Đây là tầng mang thông tin chính của CityFlow, không phải phần bổ sung — xem
docs/07_KET_QUA_E5_E6.md §10.
"""

from __future__ import annotations

import json
import statistics
import sys
import time
import tracemalloc
from pathlib import Path

import numpy as np
import pyarrow.parquet as pq

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.config import N_ZONES, PROCESSED_DIR  # noqa: E402
from cityflow.mining.apriori import apriori  # noqa: E402
from cityflow.mining.basket_builder import build_baskets  # noqa: E402
from cityflow.mining.fpgrowth import (  # noqa: E402
    closed_itemsets, fpgrowth, maximal_itemsets, reconstruct_from_closed,
)
from cityflow.mining.interestingness import (  # noqa: E402
    ALL_MEASURES, NOT_NULL_INVARIANT, NULL_INVARIANT, add_null_transactions,
)
from cityflow.mining.rules import generate_rules, rank_by, rank_correlation  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "docs" / "e9_e11_results.json"
ZONE_NAMES: dict[int, str] = {}


def section(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def zname(z: int) -> str:
    return ZONE_NAMES.get(z, f"zone {z}")[:26]


def main() -> int:
    import csv
    from cityflow.config import REFERENCE_DIR
    with open(REFERENCE_DIR / "taxi_zone_lookup.csv", encoding="utf-8") as f:
        for row in csv.DictReader(f):
            ZONE_NAMES[int(row["LocationID"])] = row["Zone"]

    print("Nạp dữ liệu...")
    table = pq.read_table(PROCESSED_DIR / "events_2024-01.parquet",
                          columns=["pickup_datetime", "pu_zone"])
    ts = table["pickup_datetime"].to_numpy(zero_copy_only=False).astype("datetime64[s]")
    pu = table["pu_zone"].to_numpy(zero_copy_only=False).astype(np.int64)
    print(f"  {len(pu):,} sự kiện")

    results: dict = {"n_events": int(len(pu))}

    # =====================================================================
    section("RỜI RẠC HÓA — ẢNH HƯỞNG CỦA NGƯỠNG PHÂN VỊ")
    print(f"  {'Phân vị':>8} {'#giỏ':>7} {'Cỡ giỏ TB':>11} {'Cỡ giỏ max':>12} "
          f"{'#item':>7} {'Giỏ rỗng':>10}")
    print("  " + "-" * 62)

    basket_sets = {}
    for q in (70.0, 80.0, 90.0, 95.0):
        bs = build_baskets(ts, pu, n_zones=N_ZONES, window_minutes=15, percentile=q)
        basket_sets[q] = bs
        st = bs.stats()
        print(f"  {q:>7.0f}% {st['n_baskets']:>7,} {st['mean_basket_size']:>11.1f} "
              f"{st['max_basket_size']:>12} {st['n_distinct_items']:>7} "
              f"{st['empty_baskets']:>10}")
    results["discretization"] = {str(q): bs.stats() for q, bs in basket_sets.items()}

    # QUYẾT ĐỊNH THỰC NGHIỆM: phân vị 80 (Phase 4 mặc định) cho giỏ hàng quá DÀY —
    # đo được cỡ giỏ TRUNG BÌNH = 44,4 item trên 257 item khả dĩ (tức mỗi cửa sổ có
    # ~17% khu vực "hot" đồng thời). Đây là CSDL trù mật (dense), đúng kịch bản
    # slide tr.13 cảnh báo: {a1..a100} sinh 2^100-1 tập con. Ở phân vị 80, min_sup=5%
    # không hội tụ trong thời gian hợp lý (đã kiểm chứng, xem docs/09).
    #
    # Phân vị 90 cho cỡ giỏ TRUNG BÌNH = 22,1 (trung vị chỉ 8) — thưa hơn nhiều vì
    # ngưỡng "hot" khắt khe hơn (mỗi khu vực chỉ hot ở đúng 10% cửa sổ hoạt động
    # của chính nó). Đây là mức thấp nhất mà FP-Growth hội tụ ổn định tới min_sup=5%.
    baskets = basket_sets[90.0].baskets
    n_txn = len(baskets)
    print(f"\n  ⚠️  Đổi từ phân vị 80 (Phase 4) sang phân vị 90 cho thực nghiệm sau.")
    print(f"  Lý do: ở phân vị 80, cỡ giỏ TB=44,4/257 item -> CSDL quá trù mật,")
    print(f"  FP-Growth không hội tụ ở min_sup thấp (xem docs/09_KET_QUA_MINING.md §1).")
    print(f"  Phân vị 90: {n_txn:,} giỏ hàng, cỡ giỏ TB={basket_sets[90.0].stats()['mean_basket_size']:.1f}")

    # =====================================================================
    section("E9 — FP-GROWTH vs APRIORI  (3 điểm nghẽn slide tr.19)")
    print(f"  {'min_sup':>9} {'#mẫu':>8} {'FP-Growth':>12} {'Apriori':>12} "
          f"{'Tăng tốc':>10} {'#ứng viên':>12} {'#quét CSDL':>11}")
    print("  " + "-" * 80)

    results["E9"] = {}
    for ratio in (0.20, 0.15, 0.10, 0.07, 0.05):
        min_sup = max(2, int(ratio * n_txn))

        tracemalloc.start()
        t0 = time.perf_counter()
        freq_fp = fpgrowth(baskets, min_sup)
        t_fp = time.perf_counter() - t0
        _, peak_fp = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        tracemalloc.start()
        t0 = time.perf_counter()
        freq_ap, stats = apriori(baskets, min_sup)
        t_ap = time.perf_counter() - t0
        _, peak_ap = tracemalloc.get_traced_memory()
        tracemalloc.stop()

        assert freq_fp == freq_ap, f"HAI THUẬT TOÁN LỆCH NHAU tại min_sup={min_sup}"

        results["E9"][f"{ratio:.2f}"] = {
            "min_support_ratio": ratio, "min_support_count": min_sup,
            "n_patterns": len(freq_fp), "fpgrowth_s": t_fp, "apriori_s": t_ap,
            "speedup": t_ap / t_fp if t_fp else 0,
            "fpgrowth_peak_bytes": peak_fp, "apriori_peak_bytes": peak_ap,
            "candidates": stats.candidates_generated, "db_scans": stats.db_scans,
            "support_checks": stats.support_checks,
        }
        print(f"  {ratio:>8.0%} {len(freq_fp):>8,} {t_fp:>11.3f}s {t_ap:>11.3f}s "
              f"{t_ap / t_fp:>9.1f}x {stats.candidates_generated:>12,} "
              f"{stats.db_scans:>11}")

    print("\n  (khẳng định: cả hai thuật toán cho kết quả GIỐNG HỆT ở mọi mức)")

    r = results["E9"]["0.05"]
    print(f"\n  Tại min_sup=5%: Apriori sinh {r['candidates']:,} ứng viên cho "
          f"{r['n_patterns']:,} mẫu thật")
    print(f"                  ({r['candidates'] / r['n_patterns']:.1f} ứng viên/mẫu — điểm nghẽn 2)")
    print(f"                  {r['support_checks']:,} phép kiểm tra hỗ trợ — điểm nghẽn 3")
    print(f"                  bộ nhớ đỉnh: FP-Growth {r['fpgrowth_peak_bytes']/1e6:.1f} MB "
          f"vs Apriori {r['apriori_peak_bytes']/1e6:.1f} MB")

    # =====================================================================
    section("E11 — NÉN MẪU  (closed / maximal, slide tr.13)")
    print(f"  {'min_sup':>9} {'#tất cả':>10} {'#đóng':>9} {'#cực đại':>10} "
          f"{'tỷ lệ đóng':>12} {'tỷ lệ cực đại':>15} {'không mất mát':>15}")
    print("  " + "-" * 84)

    results["E11"] = {}
    for ratio in (0.15, 0.10, 0.07, 0.05):
        min_sup = max(2, int(ratio * n_txn))
        freq = fpgrowth(baskets, min_sup)
        if not freq:
            print(f"  {ratio:>8.0%} {'(không có mẫu thường xuyên ở mức này)':>50}")
            results["E11"][f"{ratio:.2f}"] = {"n_all": 0}
            continue

        closed = closed_itemsets(freq)
        maximal = maximal_itemsets(freq)

        recovered = {k: v for k, v in reconstruct_from_closed(closed).items()
                     if v >= min_sup}
        lossless = recovered == freq

        results["E11"][f"{ratio:.2f}"] = {
            "n_all": len(freq), "n_closed": len(closed), "n_maximal": len(maximal),
            "closed_ratio": len(closed) / len(freq), "maximal_ratio": len(maximal) / len(freq),
            "lossless": lossless,
        }
        print(f"  {ratio:>8.0%} {len(freq):>10,} {len(closed):>9,} {len(maximal):>10,} "
              f"{len(closed)/len(freq):>11.1%} {len(maximal)/len(freq):>14.1%} "
              f"{'ĐẠT' if lossless else 'HỎNG':>15}")

    # =====================================================================
    section("SINH LUẬT VÀ XẾP HẠNG")
    min_sup = max(2, int(0.07 * n_txn))
    freq = fpgrowth(baskets, min_sup)
    rules = generate_rules(freq, n_txn, min_confidence=0.5)
    print(f"  min_sup=7% ({min_sup} giỏ), min_conf=50%  ->  {len(rules):,} luật\n")

    print("  10 luật hàng đầu theo KULCZYNSKI:")
    for rk in rank_by(rules, "kulczynski", 10):
        a = " + ".join(zname(z) for z in sorted(rk.antecedent))
        c = " + ".join(zname(z) for z in sorted(rk.consequent))
        m = rk.measures
        print(f"      {a}  =>  {c}")
        print(f"          sup={m['support']:.3f} conf={m['confidence']:.3f} "
              f"lift={m['lift']:.2f} kulc={m['kulczynski']:.3f} IR={m['imbalance_ratio']:.3f}")

    results["n_rules"] = len(rules)

    # =====================================================================
    section("⭐ E10 — ĐỘ NHẠY VỚI GIAO DỊCH RỖNG TRÊN DỮ LIỆU THẬT")
    print("  Thêm dần giao dịch rỗng (cửa sổ không có khu vực nào trong luật hot)")
    print("  và quan sát giá trị các độ đo.\n")

    probe = rank_by(rules, "kulczynski", 1)[0]
    a = " + ".join(zname(z) for z in sorted(probe.antecedent))
    c = " + ".join(zname(z) for z in sorted(probe.consequent))
    print(f"  Luật khảo sát: {a}  =>  {c}")
    print(f"  n={probe.stats.n:,}  sup_A={probe.stats.sup_a:,}  "
          f"sup_B={probe.stats.sup_b:,}  sup_AB={probe.stats.sup_ab:,}")
    print(f"  Giao dịch rỗng sẵn có: {probe.stats.n_null:,}\n")

    additions = [0, n_txn, 10 * n_txn, 100 * n_txn]
    names = list(ALL_MEASURES)
    print(f"  {'Độ đo':<18} " + " ".join(f"{'+' + str(k):>13}" for k in additions)
          + f" {'Biến thiên':>12}")
    print("  " + "-" * 88)

    results["E10"] = {}
    for name in names:
        fn = ALL_MEASURES[name]
        vals = [fn(add_null_transactions(probe.stats, k)) for k in additions]
        drift = abs(vals[-1] - vals[0]) / abs(vals[0]) if vals[0] else 0.0
        tag = "BẤT BIẾN" if name in NULL_INVARIANT else "TRÔI"
        results["E10"][name] = {"values": vals, "drift": drift,
                                "null_invariant": name in NULL_INVARIANT}
        print(f"  {name:<18} " + " ".join(f"{v:>13.4f}" for v in vals)
              + f" {drift:>11.1%}  {tag}")

    inv_drift = max(results["E10"][n]["drift"] for n in NULL_INVARIANT)
    var_drift = max(results["E10"][n]["drift"] for n in NOT_NULL_INVARIANT)
    print(f"\n  Biến thiên lớn nhất trong nhóm BẤT BIẾN     : {inv_drift:.2e}")
    print(f"  Biến thiên lớn nhất trong nhóm KHÔNG bất biến: {var_drift:.1%}")

    # --- Xếp hạng có đảo lộn không? ---
    print("\n  Tương quan hạng Spearman giữa các độ đo (trên toàn bộ tập luật):")
    pairs = [("lift", "kulczynski"), ("confidence", "kulczynski"),
             ("lift", "cosine"), ("kulczynski", "cosine"),
             ("support", "kulczynski"), ("chi_square", "kulczynski")]
    results["E10_rank_corr"] = {}
    for m1, m2 in pairs:
        rho = rank_correlation(rules, m1, m2)
        results["E10_rank_corr"][f"{m1}__{m2}"] = rho
        print(f"      {m1:<12} vs {m2:<12} rho = {rho:+.3f}")

    print("\n  10 luật hàng đầu theo LIFT (so với bảng Kulczynski ở trên):")
    for rk in rank_by(rules, "lift", 10)[:5]:
        a = " + ".join(zname(z) for z in sorted(rk.antecedent))
        c = " + ".join(zname(z) for z in sorted(rk.consequent))
        print(f"      lift={rk.measures['lift']:.2f} kulc={rk.measures['kulczynski']:.3f}"
              f"  {a} => {c}")

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False, default=str),
                   encoding="utf-8")
    print(f"\n\nKết quả đã lưu: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
