import { useEffect, useState } from "react";
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, Legend,
  BarChart, Bar,
} from "recharts";
import { fetchBench } from "../api/client";

export default function Benchmark() {
  const [e1e3, setE1e3] = useState<any>(null);
  const [e4, setE4] = useState<any>(null);
  const [e5e6, setE5e6] = useState<any>(null);
  const [e9e11, setE9e11] = useState<any>(null);

  useEffect(() => {
    fetchBench("E1_E3").then(setE1e3).catch(() => {});
    fetchBench("E4").then(setE4).catch(() => {});
    fetchBench("E5_E6").then(setE5e6).catch(() => {});
    fetchBench("E9_E11").then(setE9e11).catch(() => {});
  }, []);

  const e2Data = e1e3
    ? Object.values(e1e3.E2 as Record<string, any>).map((d: any) => ({
        r: d.r, sai_so: d.mean_rel_error * 100, sai_so_x_r: d.mean_rel_error * d.r * 100,
      }))
    : [];

  const e3Data = e1e3
    ? Object.values(e1e3.E3 as Record<string, any>).map((d: any) => ({
        N: d.N, python: d.memory_bytes, ly_thuyet: d.theoretical_bytes * 50, // scale để cùng thấy
      }))
    : [];

  const e9Data = e9e11
    ? Object.entries(e9e11.E9 as Record<string, any>).map(([, d]: [string, any]) => ({
        min_sup: `${(d.min_support_ratio * 100).toFixed(0)}%`,
        fpgrowth_s: d.fpgrowth_s, apriori_s: d.apriori_s,
      }))
    : [];

  return (
    <div className="space-y-6">
      <Section title="E2 — Sai số DGIM theo r (kiểm chứng O(1/r))">
        {e2Data.length > 0 ? (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={e2Data}>
              <CartesianGrid stroke="#1e293b" />
              <XAxis dataKey="r" stroke="#94a3b8" label={{ value: "r", position: "insideBottom", offset: -5 }} />
              <YAxis stroke="#94a3b8" label={{ value: "%", angle: -90 }} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Legend />
              <Line type="monotone" dataKey="sai_so" name="Sai số TB (%)" stroke="#38bdf8" strokeWidth={2} />
              <Line type="monotone" dataKey="sai_so_x_r" name="Sai số × r (phải ≈ hằng số)" stroke="#f472b6" strokeWidth={2} strokeDasharray="4 4" />
            </LineChart>
          </ResponsiveContainer>
        ) : <Placeholder />}
      </Section>

      <Section title="E3 — Bộ nhớ DGIM theo N">
        {e3Data.length > 0 ? (
          <ResponsiveContainer width="100%" height={260}>
            <LineChart data={e3Data}>
              <CartesianGrid stroke="#1e293b" />
              <XAxis dataKey="N" stroke="#94a3b8" scale="log" domain={["auto", "auto"]} />
              <YAxis stroke="#94a3b8" />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Legend />
              <Line type="monotone" dataKey="python" name="Bộ nhớ Python (byte)" stroke="#38bdf8" strokeWidth={2} />
            </LineChart>
          </ResponsiveContainer>
        ) : <Placeholder />}
      </Section>

      <Section title="E9 — FP-Growth vs Apriori (giây, thang log)">
        {e9Data.length > 0 ? (
          <ResponsiveContainer width="100%" height={260}>
            <BarChart data={e9Data}>
              <CartesianGrid stroke="#1e293b" />
              <XAxis dataKey="min_sup" stroke="#94a3b8" />
              <YAxis stroke="#94a3b8" scale="log" domain={[0.001, "auto"]} />
              <Tooltip contentStyle={{ background: "#0f172a", border: "1px solid #334155" }} />
              <Legend />
              <Bar dataKey="fpgrowth_s" name="FP-Growth (s)" fill="#38bdf8" />
              <Bar dataKey="apriori_s" name="Apriori (s)" fill="#f87171" />
            </BarChart>
          </ResponsiveContainer>
        ) : <Placeholder />}
      </Section>

      <Section title="E4 — Giả thuyết H1: phân bổ ngân sách DGIM-Integer">
        {e4 ? <H1Table data={e4} /> : <Placeholder />}
      </Section>

      <Section title="E5 — Flajolet-Martin theo m">
        {e5e6 ? <FMTable data={e5e6} /> : <Placeholder />}
      </Section>
    </div>
  );
}

function Section({ title, children }: { title: string; children: React.ReactNode }) {
  return (
    <div className="rounded-xl border border-slate-800 p-4">
      <h3 className="text-sm font-medium mb-3">{title}</h3>
      {children}
    </div>
  );
}

function Placeholder() {
  return (
    <p className="text-xs text-slate-500 py-8 text-center">
      Chưa có dữ liệu — chạy script thực nghiệm tương ứng trong scripts/ trước.
    </p>
  );
}

function H1Table({ data }: { data: any }) {
  const run32 = data.runs?.["32"];
  if (!run32) return <Placeholder />;
  return (
    <table className="w-full text-sm">
      <thead className="text-xs text-slate-400">
        <tr>
          <th className="text-left py-1">Chiến lược</th>
          <th className="text-right">Sai số TB</th>
          <th className="text-right">Bộ nhớ (B)</th>
        </tr>
      </thead>
      <tbody>
        {Object.entries(run32).map(([name, d]: [string, any]) => (
          <tr key={name} className="border-t border-slate-800">
            <td className="py-1">{name}</td>
            <td className="text-right">{(d.mean_rel_error * 100).toFixed(3)}%</td>
            <td className="text-right">{d.memory_bytes.toLocaleString("vi-VN")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}

function FMTable({ data }: { data: any }) {
  const mg = data.E5_mg;
  if (!mg) return <Placeholder />;
  return (
    <table className="w-full text-sm">
      <thead className="text-xs text-slate-400">
        <tr>
          <th className="text-left py-1">m</th>
          <th className="text-right">Sai số TV</th>
          <th className="text-right">Hệ số biến thiên</th>
          <th className="text-right">Bộ nhớ (B)</th>
        </tr>
      </thead>
      <tbody>
        {Object.values(mg).map((d: any) => (
          <tr key={d.m} className="border-t border-slate-800">
            <td className="py-1">{d.m}</td>
            <td className="text-right">{(d.median_rel_error * 100).toFixed(1)}%</td>
            <td className="text-right">{(d.cv * 100).toFixed(1)}%</td>
            <td className="text-right">{d.memory_bytes.toLocaleString("vi-VN")}</td>
          </tr>
        ))}
      </tbody>
    </table>
  );
}
