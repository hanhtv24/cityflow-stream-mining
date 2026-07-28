"""Phase 5 — Bước 3: Kiểm chứng DGIM trên dữ liệu thật (thực nghiệm E1, E2, E3).

Chạy DGIM trên toàn bộ 19,7 triệu sự kiện thật của tháng 01/2024 và đối chiếu với
oracle chính xác. Đây là lần đầu tiên các cận lý thuyết trên slide được kiểm chứng
bằng dữ liệu thật thay vì luồng ngẫu nhiên tổng hợp.

E1: sai số theo độ rộng cửa sổ N          -> cận 50% (slide tr.64)
E2: sai số theo số bucket mỗi cỡ r        -> quan hệ O(1/r) (slide tr.64)
E3: bộ nhớ theo N                          -> cận O(log^2 N) (slide tr.58)
"""

from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.ingest.replay import load_events  # noqa: E402
from cityflow.oracle.exact_window import ExactWindowOracle  # noqa: E402
from cityflow.sketches.dgim import DGIM  # noqa: E402

OUT = Path(__file__).resolve().parents[1] / "docs" / "e1_e3_results.json"

# Khu vực đại diện, chọn theo mật độ sự kiện khác nhau để phủ nhiều chế độ.
ZONES = {
    132: "JFK Airport (đông nhất)",
    161: "Midtown Center (đông)",
    61: "Crown Heights North (trung bình)",
    5: "Arden Heights (thưa)",
}

N_VALUES = [10_000, 100_000, 1_000_000, 5_000_000]
R_VALUES = [2, 4, 8, 16]
N_QUERY_POINTS = 200


def section(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def replay_and_measure(
    positions: np.ndarray,
    oracle: ExactWindowOracle,
    n_total: int,
    N: int,
    r: int,
) -> tuple[dict, DGIM]:
    """Phát lại luồng MỘT LƯỢT, truy vấn tại các mốc rải đều.

    Điểm then chốt về tính đúng đắn: tại mỗi mốc truy vấn t, sketch phải đã thấy
    ĐÚNG các sự kiện tới t và không thấy gì sau đó.

    Nạp toàn bộ luồng rồi mới truy vấn tại một mốc quá khứ là SAI, kể cả khi lọc
    bỏ bucket ở tương lai lúc truy vấn: lịch sử GỘP bucket cũng bị dữ liệu tương lai
    làm sai lệch, nên cấu trúc thu được không phải trạng thái mà thuật toán thực sự
    có tại thời điểm t. Sai lầm này từng cho sai số 129.311% trong lần chạy đầu.
    """
    d = DGIM(N=N, r=r)
    query_points = np.linspace(N, n_total, N_QUERY_POINTS, dtype=np.int64)

    errors, exacts = [], []
    idx = 0
    n_pos = len(positions)

    for t in query_points:
        t = int(t)
        # Nạp mọi bit 1 xảy ra tới thời điểm t — không sớm hơn, không muộn hơn.
        while idx < n_pos and positions[idx] <= t:
            d.record(int(positions[idx]))
            idx += 1
        d.now = t  # đồng hồ toàn cục tiến kể cả khi luồng không có bit 1 nào

        exact = oracle.count(t, N)
        if exact == 0:
            continue
        est = d.query(k=N, t_now=t)
        errors.append(abs(est - exact) / exact)
        exacts.append(exact)

    if not errors:
        return {}, d

    errors = np.array(errors)
    return {
        "n_queries": len(errors),
        "mean_rel_error": float(errors.mean()),
        "median_rel_error": float(np.median(errors)),
        "max_rel_error": float(errors.max()),
        "p95_rel_error": float(np.percentile(errors, 95)),
        "violations_50pct": int((errors > 0.5).sum()),
        "mean_exact": float(np.mean(exacts)),
    }, d


def main() -> int:
    print("Nạp luồng sự kiện...")
    t0 = time.perf_counter()
    ev = load_events("2024-01")
    print(f"  {ev.n:,} sự kiện  ({time.perf_counter() - t0:.1f}s)")

    results: dict = {"n_events": ev.n, "E1": {}, "E2": {}, "E3": {}}

    # =====================================================================
    section("E1 — SAI SỐ THEO ĐỘ RỘNG CỬA SỔ N  (r = 2, cận lý thuyết 50%)")
    print(f"{'Khu vực':<34} {'N':>10} {'TB thực':>10} {'Sai số TB':>10} "
          f"{'Sai số max':>11} {'Vi phạm':>8}")
    print("-" * 90)

    for zone, label in ZONES.items():
        mask = ev.pu_zone == zone
        oracle = ExactWindowOracle(mask)
        positions = ev.ones_positions(mask)

        for N in N_VALUES:
            m, _ = replay_and_measure(positions, oracle, ev.n, N, r=2)
            if not m:
                continue
            key = f"zone{zone}_N{N}"
            results["E1"][key] = {"zone": zone, "N": N, "r": 2, **m}
            flag = "" if m["violations_50pct"] == 0 else "  <-- VI PHẠM"
            print(f"{label:<34} {N:>10,} {m['mean_exact']:>10,.0f} "
                  f"{m['mean_rel_error']:>9.2%} {m['max_rel_error']:>10.2%} "
                  f"{m['violations_50pct']:>8}{flag}")

    total_violations = sum(v["violations_50pct"] for v in results["E1"].values())
    total_queries = sum(v["n_queries"] for v in results["E1"].values())
    print(f"\n  TỔNG: {total_queries:,} phép truy vấn, {total_violations} vi phạm cận 50%")

    # =====================================================================
    section("E2 — SAI SỐ THEO r  (kiểm chứng quan hệ O(1/r), slide tr.64)")
    zone = 161  # Midtown Center
    mask = ev.pu_zone == zone
    oracle = ExactWindowOracle(mask)
    positions = ev.ones_positions(mask)
    N = 1_000_000

    print(f"  Khu vực {zone} ({ZONES[zone]}), N = {N:,}\n")
    print(f"{'r':>4} {'Sai số TB':>11} {'Sai số max':>11} {'#bucket':>9} "
          f"{'Bộ nhớ (B)':>11} {'Sai số × r':>11}")
    print("-" * 62)

    base_err = None
    for r in R_VALUES:
        m, d = replay_and_measure(positions, oracle, ev.n, N, r=r)
        mem = d.memory_bytes()
        results["E2"][f"r{r}"] = {"r": r, "N": N, "zone": zone,
                                  "n_buckets": d.n_buckets(), "memory_bytes": mem, **m}
        if base_err is None:
            base_err = m["mean_rel_error"] * 2  # chuẩn hóa: err*r tại r=2
        print(f"{r:>4} {m['mean_rel_error']:>10.3%} {m['max_rel_error']:>10.3%} "
              f"{d.n_buckets():>9,} {mem:>11,} {m['mean_rel_error'] * r:>10.4%}")

    print(f"\n  Nếu quan hệ O(1/r) đúng, cột 'Sai số × r' phải xấp xỉ HẰNG SỐ.")

    # =====================================================================
    section("E3 — BỘ NHỚ THEO N  (kiểm chứng cận O(log^2 N), slide tr.58)")
    zone = 161
    mask = ev.pu_zone == zone
    positions = ev.ones_positions(mask)

    print(f"{'N':>10} {'#bucket':>9} {'Python (B)':>12} {'Lý thuyết (B)':>14} "
          f"{'Cửa sổ đầy (B)':>16} {'Tiết kiệm':>10}")
    print("-" * 76)

    oracle161 = ExactWindowOracle(mask)
    for N in N_VALUES:
        _, d = replay_and_measure(positions, oracle161, ev.n, N, r=2)
        mem = d.memory_bytes()
        theo = d.theoretical_bits() / 8
        full = N / 8
        results["E3"][f"N{N}"] = {"N": N, "n_buckets": d.n_buckets(),
                                  "memory_bytes": mem, "theoretical_bytes": theo,
                                  "full_window_bytes": full}
        print(f"{N:>10,} {d.n_buckets():>9} {mem:>12,} {theo:>14,.0f} "
              f"{full:>16,.0f} {full / mem:>9.1f}x")

    n0, n1 = N_VALUES[0], N_VALUES[-1]
    growth_mem = results["E3"][f"N{n1}"]["memory_bytes"] / results["E3"][f"N{n0}"]["memory_bytes"]
    growth_n = n1 / n0
    growth_log2 = (np.log2(n1) ** 2) / (np.log2(n0) ** 2)
    print(f"\n  N tăng {growth_n:,.0f}x  ->  bộ nhớ tăng {growth_mem:.2f}x")
    print(f"  Dự đoán theo cận log^2(N): {growth_log2:.2f}x")
    print(f"  Nếu bộ nhớ tăng tuyến tính theo N thì phải là {growth_n:,.0f}x")

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n\nKết quả đã lưu: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
