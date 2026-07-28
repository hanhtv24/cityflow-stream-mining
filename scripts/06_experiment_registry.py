"""Phase 5 — Bước 6: Thực nghiệm E7 — thông lượng và bộ nhớ của 535 luồng.

Kiểm chứng lập luận nền tảng của đề tài (Phase 4 §1.2): với nhiều luồng đồng thời,
giữ cửa sổ đầy đủ cho mỗi luồng là bất khả thi, còn sketch thì khả thi.

Đồng thời đo cái giá của tối ưu hóa lazy expiration: so sánh thông lượng khi chỉ
chạm luồng nhận bit 1 với cách ngây thơ lặp qua mọi luồng.
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.config import N_ZONES  # noqa: E402
from cityflow.ingest.replay import PREDICATE_COLUMNS, load_events  # noqa: E402
from cityflow.oracle.exact_window import ExactWindowOracle  # noqa: E402
from cityflow.sketches.dgim import DGIM  # noqa: E402
from cityflow.sketches.registry import RegistryConfig, SketchRegistry  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "docs" / "e7_results.json"
LIMIT = 3_000_000  # đủ để đo ổn định mà không phải chờ cả tháng


def section(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def main() -> int:
    print("Nạp luồng sự kiện...")
    ev = load_events("2024-01", limit=LIMIT)
    n = ev.n
    print(f"  {n:,} sự kiện")

    results: dict = {"n_events": n, "N_window": RegistryConfig().N}

    # =====================================================================
    section("E7a — THÔNG LƯỢNG VÀ BỘ NHỚ CỦA REGISTRY ĐẦY ĐỦ")

    reg = SketchRegistry()
    print(f"  {reg.n_streams} luồng DGIM + DGIM-Integer + FM + AMS + Reservoir")

    pu, do, rev = ev.pu_zone, ev.do_zone, ev.revenue_int
    preds = [ev.predicates[p] for p in PREDICATE_COLUMNS]

    BATCH = 65_536
    t0 = time.perf_counter()
    for start in range(0, n, BATCH):
        stop = min(start + BATCH, n)
        reg.update_batch(
            pu[start:stop], do[start:stop], rev[start:stop],
            {name: ev.predicates[name][start:stop] for name in PREDICATE_COLUMNS},
        )
    elapsed = time.perf_counter() - t0

    thr = n / elapsed
    mem = reg.memory_bytes()
    print(f"\n  Thời gian     : {elapsed:.1f}s")
    print(f"  Thông lượng   : {thr:,.0f} sự kiện/giây")
    print(f"  Tổng bucket   : {reg.total_buckets():,}")
    print(f"\n  Bộ nhớ theo nhóm:")
    for k, v in mem.items():
        if k.startswith("total"):
            continue
        print(f"      {k:<14} {v:>12,} B  ({v / 1e6:6.2f} MB)")
    print(f"      {'-' * 40}")
    print(f"      {'TỔNG':<14} {mem['total']:>12,} B  ({mem['total'] / 1e6:6.2f} MB)")
    print(f"      {'(trừ mẫu)':<14} {mem['total_without_reservoir']:>12,} B  "
          f"({mem['total_without_reservoir'] / 1e6:6.2f} MB)")

    results["E7a"] = {"elapsed_s": elapsed, "throughput": thr,
                      "total_buckets": reg.total_buckets(), "memory": mem}

    # --- So sánh với giữ cửa sổ đầy đủ -----------------------------------
    N = reg.cfg.N
    full_window_bytes = reg.n_streams * N / 8  # 1 bit/phần tử/luồng
    sketch_bytes = mem["total_without_reservoir"]
    print(f"\n  Nếu giữ cửa sổ đầy đủ N={N:,} cho cả {reg.n_streams} luồng:")
    print(f"      mảng bit  : {full_window_bytes:>14,.0f} B  ({full_window_bytes / 1e6:.1f} MB)")
    print(f"      sketch    : {sketch_bytes:>14,.0f} B  ({sketch_bytes / 1e6:.1f} MB)")
    print(f"      tiết kiệm : {full_window_bytes / sketch_bytes:>14.1f}x")
    results["E7a"]["full_window_bytes"] = full_window_bytes
    results["E7a"]["saving_ratio"] = full_window_bytes / sketch_bytes

    # =====================================================================
    section("E7b — GIÁ TRỊ CỦA LAZY EXPIRATION")
    print("  So sánh trên 200.000 sự kiện đầu:\n")

    SUB = 200_000
    cfg = RegistryConfig()

    # Cách tối ưu: chỉ chạm luồng nhận bit 1.
    streams_a = {z: DGIM(cfg.N, cfg.dgim_r) for z in range(1, N_ZONES + 1)}
    t0 = time.perf_counter()
    for i in range(SUB):
        streams_a[int(pu[i])].record(i + 1)
    t_lazy = time.perf_counter() - t0

    # Cách ngây thơ: gọi update(bit) cho MỌI luồng, kể cả bit 0.
    streams_b = {z: DGIM(cfg.N, cfg.dgim_r) for z in range(1, N_ZONES + 1)}
    NAIVE_SUB = 20_000  # ít hơn 10 lần vì quá chậm; ngoại suy tuyến tính
    t0 = time.perf_counter()
    for i in range(NAIVE_SUB):
        z = int(pu[i])
        for zz, s in streams_b.items():
            s.update(1 if zz == z else 0)
    t_naive_measured = time.perf_counter() - t0
    t_naive = t_naive_measured * (SUB / NAIVE_SUB)

    print(f"  {'Cách làm':<38} {'Thời gian':>12} {'Thông lượng':>16}")
    print("  " + "-" * 68)
    print(f"  {'Lazy (chỉ chạm luồng nhận bit 1)':<38} {t_lazy:>11.2f}s "
          f"{SUB / t_lazy:>15,.0f}/s")
    print(f"  {'Ngây thơ (lặp cả 265 luồng)':<38} {t_naive:>11.2f}s "
          f"{SUB / t_naive:>15,.0f}/s   (ngoại suy từ {NAIVE_SUB:,})")
    print(f"\n  Tăng tốc: {t_naive / t_lazy:.0f}x")
    print(f"  Ngoại suy cho cả tháng 19,7 triệu sự kiện:")
    print(f"      lazy    : {19_663_928 / (SUB / t_lazy) / 60:>8.1f} phút")
    print(f"      ngây thơ: {19_663_928 / (SUB / t_naive) / 3600:>8.1f} giờ")

    results["E7b"] = {"lazy_s": t_lazy, "naive_s_extrapolated": t_naive,
                      "speedup": t_naive / t_lazy}

    # =====================================================================
    section("E7c — KIỂM CHỨNG ĐỘ CHÍNH XÁC QUA REGISTRY")
    print("  Đối chiếu ước lượng của registry với oracle chính xác\n")
    print(f"  {'Khu vực':<32} {'Ước lượng':>12} {'Chính xác':>12} {'Sai số':>10}")
    print("  " + "-" * 68)

    zones = [132, 161, 61, 237, 5]
    errs = []
    for z in zones:
        oracle = ExactWindowOracle(ev.pu_zone == z)
        exact = oracle.count(n, N)
        est = reg.count_pickups(z, N)
        if exact == 0:
            continue
        e = abs(est - exact) / exact
        errs.append(e)
        print(f"  zone {z:<27} {est:>12,} {exact:>12,} {e:>9.2%}")

    print(f"\n  Sai số trung bình: {np.mean(errs):.2%}  |  lớn nhất: {np.max(errs):.2%}")
    results["E7c"] = {"mean_rel_error": float(np.mean(errs)),
                      "max_rel_error": float(np.max(errs))}

    # Tổng doanh thu (Q2)
    from cityflow.oracle.exact_window import ExactWindowSumOracle
    rev_oracle = ExactWindowSumOracle(ev.revenue_int.astype(np.int64))
    exact_rev = rev_oracle.total(n, N)
    est_rev = reg.total_revenue(N)
    print(f"\n  Tổng doanh thu (Q2): ước lượng {est_rev:,} vs chính xác {exact_rev:,} "
          f"-> sai số {abs(est_rev - exact_rev) / exact_rev:.2%}")
    results["E7c"]["revenue_rel_error"] = abs(est_rev - exact_rev) / exact_rev

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n\nKết quả đã lưu: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
