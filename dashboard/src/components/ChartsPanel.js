import React, { useEffect, useState } from "react";
import { Bar, Pie } from "react-chartjs-2";
import {
  Chart as ChartJS,
  BarElement,
  CategoryScale,
  LinearScale,
  ArcElement,
} from "chart.js";

ChartJS.register(BarElement, CategoryScale, LinearScale, ArcElement);

export default function ChartsPanel() {
  const [counts, setCounts] = useState({ last_5_min: 0, total_events: 0 });
  const [severity, setSeverity] = useState({});
  const [cpActivity, setCp] = useState({});

  useEffect(() => {
    const load = async () => {
      const c = await (await fetch("http://localhost:8000/analytics/event_counts")).json();
      const s = await (await fetch("http://localhost:8000/analytics/severity_stats")).json();
      const cp = await (await fetch("http://localhost:8000/analytics/cp_activity")).json();

      setCounts(c);
      setSeverity(s);
      setCp(cp);
    };
    load();
    const t = setInterval(load, 2000);
    return () => clearInterval(t);
  }, []);

  return (
    <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 shadow-lg mt-8">
      <h2 className="text-xl font-semibold mb-4">📊 Analytics</h2>

      <div className="grid grid-cols-3 gap-6">
        
        {/* Event Count Chart */}
        <div className="bg-gray-700 p-4 rounded-lg">
          <h3 className="text-sm mb-2 font-bold">Events (Last 5 Minutes)</h3>
          <Bar
            data={{
              labels: ["Last 5 Min", "Total"],
              datasets: [
                {
                  label: "Events",
                  data: [counts.last_5_min, counts.total_events],
                  backgroundColor: ["#4ade80", "#60a5fa"],
                },
              ],
            }}
          />
        </div>

        {/* Severity Pie */}
        <div className="bg-gray-700 p-4 rounded-lg">
          <h3 className="text-sm mb-2 font-bold">Alert Severity</h3>
          <Pie
            data={{
              labels: ["High", "Medium", "Low"],
              datasets: [
                {
                  data: [
                    severity.high || 0,
                    severity.medium || 0,
                    severity.low || 0,
                  ],
                  backgroundColor: ["#ef4444", "#f97316", "#eab308"],
                },
              ],
            }}
          />
        </div>

        {/* CP Activity */}
        <div className="bg-gray-700 p-4 rounded-lg text-sm">
          <h3 className="text-sm mb-2 font-bold">Most Active CP</h3>
          <div className="space-y-2">
            {Object.entries(cpActivity).map(([cp, count]) => (
              <div key={cp} className="p-2 bg-gray-600 rounded flex justify-between">
                <span>{cp}</span>
                <span className="font-bold">{count}</span>
              </div>
            ))}
          </div>
        </div>

      </div>
    </div>
  );
}
