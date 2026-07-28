import { useEffect, useState } from "react";
import { fetchBench } from "../api/client";

export default function AccuracyLab() {
  const [e1e3, setE1e3] = useState<any>(null);
  const [e7, setE7] = useState<any>(null);

  useEffect(() => {
    fetchBench("E1_E3").then(setE1e3).catch(() => {});
    fetchBench("E7").then(setE7).catch(() => {});
  }, []);

  return (
    <div className="space-y-6">
      <div className="rounded-xl border border-slate-800 p-4">
        <h3 className="text-sm font-medium mb-3">E1 — Sai số theo khu vực và N (cận lý thuyết 50%)</h3>
        {e1e3?.E1 ? (
          <table className="w-full text-sm">
            <thead className="text-xs text-slate-400">
              <tr>
                <th className="text-left py-1">Khu vực</th>
                <th className="text-right">N</th>
                <th className="text-right">Sai số TB</th>
                <th className="text-right">Sai số max</th>
                <th className="text-right">Vi phạm 50%</th>
              </tr>
            </thead>
            <tbody>
              {Object.values(e1e3.E1 as Record<string, any>).map((d: any, i: number) => (
                <tr key={i} className="border-t border-slate-800">
                  <td className="py-1">{d.zone}</td>
                  <td className="text-right">{d.N.toLocaleString("vi-VN")}</td>
                  <td className="text-right">{(d.mean_rel_error * 100).toFixed(2)}%</td>
                  <td
                    className={`text-right ${d.max_rel_error > 0.5 ? "text-red-400" : "text-emerald-400"}`}
                  >
                    {(d.max_rel_error * 100).toFixed(2)}%
                  </td>
                  <td className="text-right">{d.violations_50pct}</td>
                </tr>
              ))}
            </tbody>
          </table>
        ) : (
          <p className="text-xs text-slate-500 py-8 text-center">Chưa có dữ liệu E1.</p>
        )}
      </div>

      <div className="rounded-xl border border-slate-800 p-4">
        <h3 className="text-sm font-medium mb-3">E7 — Thông lượng & bộ nhớ 535 luồng</h3>
        {e7?.E7a ? (
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 text-sm">
            <Metric label="Thông lượng" value={`${Math.round(e7.E7a.throughput).toLocaleString("vi-VN")}/s`} />
            <Metric label="Tổng bucket" value={e7.E7a.total_buckets.toLocaleString("vi-VN")} />
            <Metric
              label="Bộ nhớ (trừ mẫu)"
              value={`${(e7.E7a.memory.total_without_reservoir / 1e6).toFixed(2)} MB`}
            />
            <Metric label="Tiết kiệm vs cửa sổ đầy" value={`${e7.E7a.saving_ratio.toFixed(1)}×`} />
          </div>
        ) : (
          <p className="text-xs text-slate-500 py-8 text-center">Chưa có dữ liệu E7.</p>
        )}
      </div>
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div>
      <div className="text-xs text-slate-400">{label}</div>
      <div className="text-lg font-semibold">{value}</div>
    </div>
  );
}
