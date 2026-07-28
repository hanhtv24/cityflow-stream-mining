import { BrowserRouter, Routes, Route } from "react-router-dom";
import Layout from "./components/Layout";
import LiveMonitor from "./pages/LiveMonitor";
import AccuracyLab from "./pages/AccuracyLab";
import PatternExplorer from "./pages/PatternExplorer";
import Benchmark from "./pages/Benchmark";

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<LiveMonitor />} />
          <Route path="/accuracy" element={<AccuracyLab />} />
          <Route path="/patterns" element={<PatternExplorer />} />
          <Route path="/benchmark" element={<Benchmark />} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}
