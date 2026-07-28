"""Phase 5 — Bước 4: Thực nghiệm E4 — kiểm chứng giả thuyết H1.

H1: với DGIM mở rộng cho tổng số nguyên (slide tr.66), phân bổ ngân sách bucket
KHÔNG ĐỀU giữa các luồng bit cho sai số thấp hơn phân bổ đều ở cùng ngân sách.

So sánh ba chiến lược ở CÙNG tổng ngân sách sum(r_i):
    A. uniform      — r bằng nhau cho mọi bit (mốc so sánh)
    B. high_bit     — r tăng dần theo vị trí bit (dạng ngây thơ của H1)
    C. sqrt_weighted— r_i ∝ sqrt(2^i * c_i)   (dạng suy ra từ lý thuyết)

Kết quả âm tính vẫn là kết quả hợp lệ.
"""

from __future__ import annotations

import json
import sys
from pathlib import Path

import numpy as np

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "src"))
from cityflow.ingest.replay import load_events  # noqa: E402
from cityflow.oracle.exact_window import ExactWindowSumOracle  # noqa: E402
from cityflow.sketches.dgim_integer import (  # noqa: E402
    DGIMInteger, compute_bit_counts, high_bit_allocation, predicted_error_weight,
    sqrt_weighted_allocation, uniform_allocation,
)

OUT = Path(__file__).resolve().parents[1] / "docs" / "e4_h1_results.json"

N_WINDOW = 1_000_000
M_BITS = 8
BUDGETS = [16, 32, 64, 128]
N_QUERY_POINTS = 150


def section(t: str) -> None:
    print(f"\n{'=' * 78}\n{t}\n{'=' * 78}")


def replay_and_measure(values: np.ndarray, oracle: ExactWindowSumOracle,
                       n_total: int, N: int, m: int, alloc: list[int]) -> dict:
    """Phát lại một lượt, truy vấn tại các mốc rải đều.

    Ngữ nghĩa luồng phải được tôn trọng: tại mốc t, sketch chỉ được thấy sự kiện tới t.
    """
    d = DGIMInteger(N=N, m=m, r_alloc=alloc)
    query_points = np.linspace(N, n_total, N_QUERY_POINTS, dtype=np.int64)

    idx = 0
    errors = []
    per_bit_abs_err = np.zeros(m, dtype=np.float64)
    n_measured = 0

    for t in query_points:
        t = int(t)
        while idx < t:
            v = int(values[idx])
            if v:
                d.record(idx + 1, v)
            idx += 1
        d.now = t

        exact = oracle.total(t, N)
        if exact == 0:
            continue
        est = d.query(k=N, t_now=t)
        errors.append(abs(est - exact) / exact)

        # Phân rã sai số theo vị trí bit: đóng góp của luồng bit i vào sai số tổng.
        est_bits = d.query_per_bit(k=N, t_now=t)
        for i in range(m):
            exact_bit = int(((values[max(0, t - N):t] >> i) & 1).sum())
            per_bit_abs_err[i] += abs(est_bits[i] - exact_bit) * (1 << i)
        n_measured += 1

    errors = np.array(errors)
    return {
        "alloc": list(alloc),
        "budget": int(sum(alloc)),
        "n_queries": len(errors),
        "mean_rel_error": float(errors.mean()),
        "median_rel_error": float(np.median(errors)),
        "max_rel_error": float(errors.max()),
        "memory_bytes": d.memory_bytes(),
        "n_clipped": d.n_clipped(),
        "per_bit_weighted_abs_error": (per_bit_abs_err / max(n_measured, 1)).tolist(),
    }


def main() -> int:
    print("Nạp luồng sự kiện...")
    ev = load_events("2024-01")
    values = ev.revenue_int.astype(np.int64)
    print(f"  {ev.n:,} sự kiện")

    oracle = ExactWindowSumOracle(values)
    bit_counts = compute_bit_counts(values, M_BITS)

    results: dict = {"n_events": ev.n, "N": N_WINDOW, "m": M_BITS,
                     "bit_counts": bit_counts.tolist(), "runs": {}}

    # =====================================================================
    section("PHÂN PHỐI BIT CỦA DOANH THU  (đầu vào của công thức phân bổ)")
    print(f"{'bit i':>6} {'giá trị 2^i':>12} {'c_i (số bit 1)':>16} {'tỷ lệ':>8} "
          f"{'2^i · c_i':>16} {'sqrt(2^i·c_i)':>15}")
    print("-" * 80)
    for i in range(M_BITS):
        w = (1 << i) * int(bit_counts[i])
        print(f"{i:>6} {1 << i:>12,} {int(bit_counts[i]):>16,} "
              f"{100 * bit_counts[i] / ev.n:>7.2f}% {w:>16,} {np.sqrt(w):>15,.0f}")

    peak = int(np.argmax([(1 << i) * bit_counts[i] for i in range(M_BITS)]))
    print(f"\n  Trọng số 2^i·c_i đạt cực đại tại bit {peak}, KHÔNG phải bit cao nhất ({M_BITS-1}).")
    print("  -> Trực giác 'ưu tiên bit cao' có thể sai. Đây là điều E4 phải kiểm chứng.")

    # =====================================================================
    section(f"E4 — SO SÁNH BA CHIẾN LƯỢC PHÂN BỔ  (N = {N_WINDOW:,}, m = {M_BITS})")

    for budget in BUDGETS:
        allocs = {
            "uniform": uniform_allocation(M_BITS, budget),
            "high_bit": high_bit_allocation(M_BITS, budget),
            "sqrt_weighted": sqrt_weighted_allocation(M_BITS, budget, bit_counts),
        }

        print(f"\n  Ngân sách sum(r_i) = {budget}")
        print(f"  {'Chiến lược':<16} {'Phân bổ r_i':<34} {'Ngân sách':>10} "
              f"{'Sai số TB':>11} {'Sai số max':>11} {'Bộ nhớ':>9} {'E dự đoán':>12}")
        print("  " + "-" * 108)

        run = {}
        for name, alloc in allocs.items():
            m_res = replay_and_measure(values, oracle, ev.n, N_WINDOW, M_BITS, alloc)
            m_res["predicted_error"] = predicted_error_weight(alloc, bit_counts, M_BITS)
            run[name] = m_res
            print(f"  {name:<16} {str(alloc):<34} {sum(alloc):>10} "
                  f"{m_res['mean_rel_error']:>10.3%} {m_res['max_rel_error']:>10.3%} "
                  f"{m_res['memory_bytes']:>9,} {m_res['predicted_error']:>12,.0f}")

        base = run["uniform"]["mean_rel_error"]
        for name in ("high_bit", "sqrt_weighted"):
            delta = (base - run[name]["mean_rel_error"]) / base
            verdict = "TỐT HƠN" if delta > 0 else "TỆ HƠN"
            print(f"    {name:<16} so với uniform: {delta:+.1%}  -> {verdict}")

        results["runs"][str(budget)] = run

    # =====================================================================
    section("PHÂN RÃ SAI SỐ THEO VỊ TRÍ BIT  (ngân sách 32, phân bổ đều)")
    ref = results["runs"]["32"]["uniform"]["per_bit_weighted_abs_error"]
    total = sum(ref) or 1.0
    print(f"{'bit i':>6} {'sai số tuyệt đối × 2^i':>26} {'tỷ trọng':>10}")
    print("-" * 46)
    for i, v in enumerate(ref):
        bar = "#" * int(40 * v / max(ref))
        print(f"{i:>6} {v:>26,.0f} {100 * v / total:>9.1f}%  {bar}")

    dominant = int(np.argmax(ref))
    print(f"\n  Luồng bit đóng góp nhiều sai số nhất: bit {dominant} "
          f"({100 * ref[dominant] / total:.1f}% tổng sai số)")

    OUT.write_text(json.dumps(results, indent=2, ensure_ascii=False), encoding="utf-8")
    print(f"\n\nKết quả đã lưu: {OUT}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
