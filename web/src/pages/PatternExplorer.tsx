import { useEffect, useState } from "react";
import { fetchRules, fetchRulesCompare, type Rule } from "../api/client";

const MEASURES = [
  { key: "support", label: "Support", invariant: false },
  { key: "confidence", label: "Confidence", invariant: false },
  { key: "lift", label: "Lift", invariant: false },
  { key: "chi_square", label: "Chi-bình phương", invariant: false },
  { key: "all_confidence", label: "All-Confidence", invariant: true },
  { key: "coherence", label: "Coherence (Jaccard)", invariant: true },
  { key: "cosine", label: "Cosine", invariant: true },
  { key: "kulczynski", label: "Kulczynski", invariant: true },
  { key: "max_confidence", label: "Max-Confidence", invariant: true },
  { key: "imbalance_ratio", label: "Imbalance Ratio", invariant: true },
];

export default function PatternExplorer() {
  const [measure, setMeasure] = useState("kulczynski");
  const [rules, setRules] = useState<Rule[]>([]);
  const [meta, setMeta] = useState<{ n_total_rules: number; n_baskets: number } | null>(null);
  const [correlations, setCorrelations] = useState<
    { measure_a: string; measure_b: string; spearman_rho: number }[]
  >([]);
  const [prevOrder, setPrevOrder] = useState<string[]>([]);

  useEffect(() => {
    fetchRules(measure, 20).then((r) => {
      setPrevOrder(rules.map(ruleKey));
      setRules(r.rules);
      setMeta({ n_total_rules: r.n_total_rules, n_baskets: r.n_baskets });
    });
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, [measure]);

  useEffect(() => {
    fetchRulesCompare().then((d) => d.ready && setCorrelations(d.correlations));
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center gap-3 flex-wrap">
        <span className="text-sm text-slate-400">Xếp hạng theo:</span>
        {MEASURES.map((m) => (
          <button
            key={m.key}
            onClick={() => setMeasure(m.key)}
            className={`px-3 py-1.5 rounded-md text-sm border transition ${
              measure === m.key
                ? "bg-sky-600 border-sky-500 text-white"
                : "border-slate-700 text-slate-300 hover:bg-slate-800"
            }`}
            title={m.invariant ? "Bất biến với giao dịch rỗng" : "KHÔNG bất biến"}
          >
            {m.label} {m.invariant ? "🟢" : "🔴"}
          </button>
        ))}
      </div>

      {meta && (
        <p className="text-xs text-slate-500">
          {meta.n_total_rules.toLocaleString("vi-VN")} luật tổng cộng, trên{" "}
          {meta.n_baskets.toLocaleString("vi-VN")} giỏ hàng (cửa sổ 15 phút). 🟢 = bất biến với
          giao dịch rỗng, 🔴 = không bất biến (xem docs/09_KET_QUA_MINING.md §5).
        </p>
      )}

      <div className="rounded-xl border border-slate-800 overflow-hidden">
        <table className="w-full text-sm">
          <thead className="bg-slate-900 text-slate-400 text-xs">
            <tr>
              <th className="text-left px-3 py-2">#</th>
              <th className="text-left px-3 py-2">Tiền đề</th>
              <th className="text-left px-3 py-2">Hệ quả</th>
              <th className="text-right px-3 py-2">Sup</th>
              <th className="text-right px-3 py-2">Conf</th>
              <th className="text-right px-3 py-2">Lift</th>
              <th className="text-right px-3 py-2 text-sky-400">
                {MEASURES.find((m) => m.key === measure)?.label}
              </th>
            </tr>
          </thead>
          <tbody>
            {rules.map((r, i) => {
              const key = ruleKey(r);
              const moved = prevOrder.length > 0 && prevOrder.indexOf(key) !== i;
              return (
                <tr
                  key={key}
                  className={`border-t border-slate-800 ${moved ? "bg-sky-950/40" : ""}`}
                >
                  <td className="px-3 py-2 text-slate-500">{i + 1}</td>
                  <td className="px-3 py-2">{r.antecedent_names.join(" + ")}</td>
                  <td className="px-3 py-2">{r.consequent_names.join(" + ")}</td>
                  <td className="px-3 py-2 text-right">{r.measures.support.toFixed(3)}</td>
                  <td className="px-3 py-2 text-right">{r.measures.confidence.toFixed(3)}</td>
                  <td className="px-3 py-2 text-right">{r.measures.lift.toFixed(2)}</td>
                  <td className="px-3 py-2 text-right font-semibold text-sky-300">
                    {(r.measures as any)[measure].toFixed(4)}
                  </td>
                </tr>
              );
            })}
            {rules.length === 0 && (
              <tr>
                <td colSpan={7} className="px-3 py-6 text-center text-slate-500">
                  Đang khai phá mẫu từ dữ liệu tháng… (chạy một lần khi khởi động)
                </td>
              </tr>
            )}
          </tbody>
        </table>
      </div>

      {correlations.length > 0 && (
        <div className="rounded-xl border border-slate-800 p-4">
          <h3 className="text-sm font-medium mb-3">
            Tương quan hạng Spearman — mức đảo lộn thứ hạng giữa các độ đo
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
            {correlations.map((c) => (
              <div key={`${c.measure_a}-${c.measure_b}`} className="text-xs">
                <div className="text-slate-400">
                  {c.measure_a} vs {c.measure_b}
                </div>
                <div
                  className={`text-lg font-semibold ${
                    c.spearman_rho > 0.8 ? "text-emerald-400" : "text-amber-400"
                  }`}
                >
                  ρ = {c.spearman_rho.toFixed(3)}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );
}

function ruleKey(r: Rule): string {
  return `${r.antecedent.join(",")}=>${r.consequent.join(",")}`;
}
