import { NavLink, Outlet } from "react-router-dom";
import { useEffect, useState } from "react";
import { fetchStatus, type Status } from "../api/client";

const tabs = [
  { to: "/", label: "Live Monitor" },
  { to: "/accuracy", label: "Accuracy Lab" },
  { to: "/patterns", label: "Pattern Explorer" },
  { to: "/benchmark", label: "Benchmark" },
];

export default function Layout() {
  const [status, setStatus] = useState<Status | null>(null);

  useEffect(() => {
    const tick = () => fetchStatus().then(setStatus).catch(() => {});
    tick();
    const id = setInterval(tick, 2000);
    return () => clearInterval(id);
  }, []);

  return (
    <div className="min-h-screen bg-slate-950 text-slate-100">
      <header className="border-b border-slate-800 px-6 py-3 flex items-center justify-between">
        <div>
          <h1 className="text-lg font-semibold tracking-tight">CityFlow</h1>
          <p className="text-xs text-slate-400">
            Giám sát giao thông đô thị · cửa sổ trượt & khai phá mẫu đồng ùn tắc
          </p>
        </div>
        <nav className="flex gap-1">
          {tabs.map((t) => (
            <NavLink
              key={t.to}
              to={t.to}
              className={({ isActive }) =>
                `px-3 py-1.5 rounded-md text-sm transition ${
                  isActive ? "bg-sky-600 text-white" : "text-slate-300 hover:bg-slate-800"
                }`
              }
            >
              {t.label}
            </NavLink>
          ))}
        </nav>
        <div className="text-xs text-right">
          {status ? (
            status.ready ? (
              <span className="text-emerald-400">
                ● {status.now.toLocaleString("vi-VN")} sự kiện đã nạp
              </span>
            ) : (
              <span className="text-amber-400">
                ⟳ Đang nạp {(status.progress * 100).toFixed(1)}%
                {" · "}
                {status.throughput.toLocaleString("vi-VN", { maximumFractionDigits: 0 })}/s
              </span>
            )
          ) : (
            <span className="text-slate-500">Đang kết nối API…</span>
          )}
        </div>
      </header>
      <main className="p-6">
        <Outlet context={{ status }} />
      </main>
    </div>
  );
}
