import axios from "axios";

export const api = axios.create({ baseURL: "/api" });

export interface Status {
  ready: boolean;
  loading: boolean;
  error: string | null;
  n_loaded: number;
  n_total: number;
  progress: number;
  elapsed_s: number;
  throughput: number;
  now: number;
  n_streams: number;
}

export interface Zone {
  location_id: number;
  zone_name: string;
  borough: string;
  is_airport: boolean;
}

export interface HeatmapEntry {
  location_id: number;
  zone_name: string;
  count: number;
}

export interface WindowCountResult {
  zone: number;
  zone_name: string;
  direction: string;
  k: number;
  estimated: number;
  theoretical_bound: number;
  params: { N: number; r: number };
  memory_bytes: number;
}

export interface RuleMeasures {
  support: number;
  confidence: number;
  lift: number;
  chi_square: number;
  all_confidence: number;
  coherence: number;
  cosine: number;
  kulczynski: number;
  max_confidence: number;
  imbalance_ratio: number;
}

export interface Rule {
  antecedent: number[];
  antecedent_names: string[];
  consequent: number[];
  consequent_names: string[];
  measures: RuleMeasures;
  stats: { n: number; sup_a: number; sup_b: number; sup_ab: number };
}

export interface RulesResponse {
  ready: boolean;
  measure: string;
  n_total_rules: number;
  n_baskets: number;
  min_support: number;
  percentile: number;
  rules: Rule[];
}

export const fetchStatus = () => api.get<Status>("/status").then((r) => r.data);
export const fetchZones = () => api.get<Zone[]>("/zones").then((r) => r.data);
export const fetchHeatmap = (k?: number) =>
  api.get<{ k: number; now: number; zones: HeatmapEntry[] }>("/heatmap", { params: { k } })
    .then((r) => r.data);
export const fetchWindowCount = (zone: number, k?: number) =>
  api.get<WindowCountResult>("/window/count", { params: { zone, k } }).then((r) => r.data);
export const fetchWindowSum = (k?: number) =>
  api.get("/window/sum", { params: { k } }).then((r) => r.data);
export const fetchDistinctRoutes = () => api.get("/distinct/routes").then((r) => r.data);
export const fetchSurprise = () => api.get("/surprise").then((r) => r.data);
export const fetchRules = (measure: string, top_k = 20) =>
  api.get<RulesResponse>("/rules", { params: { measure, top_k } }).then((r) => r.data);
export const fetchRulesCompare = () => api.get("/rules/compare").then((r) => r.data);
export const fetchBench = (experiment: string) =>
  api.get(`/bench/${experiment}`).then((r) => r.data);
export const fetchBenchList = () => api.get("/bench").then((r) => r.data);
