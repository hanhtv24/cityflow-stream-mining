import { useEffect, useMemo, useState } from "react";
import { MapContainer, TileLayer, CircleMarker, Tooltip } from "react-leaflet";
import "leaflet/dist/leaflet.css";
import { fetchHeatmap, fetchDistinctRoutes, fetchSurprise, fetchWindowSum } from "../api/client";
import type { HeatmapEntry } from "../api/client";
import zoneCentroids from "../../public/zone_centroids.json";

const centroids = zoneCentroids as unknown as Record<string, [number, number]>;

function colorFor(count: number, max: number): string {
  if (max === 0) return "#334155";
  const t = Math.min(count / max, 1);
  // xanh dương nhạt (thấp) -> vàng -> đỏ (cao)
  const hue = (1 - t) * 220; // 220 = xanh, 0 = đỏ
  return `hsl(${hue}, 85%, 55%)`;
}

export default function LiveMonitor() {
  const [k, setK] = useState(1_000_000);
  const [zones, setZones] = useState<HeatmapEntry[]>([]);
  const [routes, setRoutes] = useState<number | null>(null);
  const [surprise, setSurprise] = useState<number | null>(null);
  const [revenue, setRevenue] = useState<number | null>(null);
  const [now, setNow] = useState(0);

  useEffect(() => {
    let cancelled = false;
    const tick = async () => {
      try {
        const [hm, dr, sp, rv] = await Promise.all([
          fetchHeatmap(k), fetchDistinctRoutes(), fetchSurprise(), fetchWindowSum(k),
        ]);
        if (cancelled) return;
        setZones(hm.zones);
        setNow(hm.now);
        setRoutes(dr.estimated);
        setSurprise(sp.estimated);
        setRevenue(rv.estimated_usd);
      } catch {
        /* API chưa sẵn sàng — thử lại ở tick sau */
      }
    };
    tick();
    const id = setInterval(tick, 3000);
    return () => {
      cancelled = true;
      clearInterval(id);
    };
  }, [k]);

  const maxCount = useMemo(() => Math.max(1, ...zones.map((z) => z.count)), [zones]);

  return (
    <div className="grid grid-cols-1 lg:grid-cols-4 gap-4">
      <div className="lg:col-span-3 rounded-xl overflow-hidden border border-slate-800 h-[600px]">
        <MapContainer center={[40.73, -73.94]} zoom={11} className="h-full w-full">
          <TileLayer
            url="https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png"
            attribution='&copy; OpenStreetMap &copy; CARTO'
          />
          {zones.map((z) => {
            const c = centroids[String(z.location_id)];
            if (!c) return null;
            return (
              <CircleMarker
                key={z.location_id}
                center={c}
                radius={4 + 10 * (z.count / maxCount)}
                pathOptions={{ color: colorFor(z.count, maxCount), fillOpacity: 0.75, weight: 1 }}
              >
                <Tooltip>
                  <b>{z.zone_name}</b>
                  <br />~{z.count.toLocaleString("vi-VN")} chuyến / cửa sổ
                </Tooltip>
              </CircleMarker>
            );
          })}
        </MapContainer>
      </div>

      <div className="space-y-4">
        <div className="rounded-xl border border-slate-800 p-4">
          <label className="text-xs text-slate-400 block mb-2">
            Độ rộng cửa sổ N = {k.toLocaleString("vi-VN")} sự kiện
          </label>
          <input
            type="range" min={10_000} max={5_000_000} step={10_000}
            value={k} onChange={(e) => setK(Number(e.target.value))}
            className="w-full accent-sky-500"
          />
          <p className="text-[11px] text-slate-500 mt-1">
            Kéo để thay đổi cửa sổ trượt — bản đồ cập nhật ngay (DGIM, r=8)
          </p>
        </div>

        <Stat label="Vị trí trong luồng" value={now.toLocaleString("vi-VN")} />
        <Stat
          label="Số tuyến phân biệt (FM, m=256)"
          value={routes !== null ? Math.round(routes).toLocaleString("vi-VN") : "…"}
          hint="sai số trung vị 6,4%"
        />
        <Stat
          label="Doanh thu ước lượng (DGIM-Integer)"
          value={revenue !== null ? `$${revenue.toLocaleString("vi-VN")}` : "…"}
          hint="sai số 0,82% (E7c)"
        />
        <Stat
          label="Số bất ngờ (AMS, k=100)"
          value={surprise !== null ? surprise.toExponential(3) : "…"}
          hint="tín hiệu yếu ở phạm vi toàn cục — xem Pattern Explorer"
        />
      </div>
    </div>
  );
}

function Stat({ label, value, hint }: { label: string; value: string; hint?: string }) {
  return (
    <div className="rounded-xl border border-slate-800 p-4">
      <div className="text-xs text-slate-400">{label}</div>
      <div className="text-xl font-semibold mt-1">{value}</div>
      {hint && <div className="text-[11px] text-slate-500 mt-1">{hint}</div>}
    </div>
  );
}
