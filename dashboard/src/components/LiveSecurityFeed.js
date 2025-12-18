import React, { useEffect, useState } from "react";

export default function LiveSecurityFeed() {
  const [items, setItems] = useState([]);
  const [filter, setFilter] = useState("all");

  useEffect(() => {
    const sse = new EventSource("http://localhost:8000/security/live");
    sse.onmessage = (e) => {
      const d = JSON.parse(e.data);
      setItems((prev) => [d, ...prev.slice(0, 50)]);
    };
    return () => sse.close();
  }, []);

  const filtered = items.filter((ev) => {
    if (filter === "all") return true;
    return ev.severity === filter;
  });

  // Severity -> renk eşleştirme
  const getSeverityColor = (sev) => {
    switch (sev) {
      case "high":
        return "bg-red-500 text-white";
      case "medium":
        return "bg-orange-400 text-black";
      case "low":
        return "bg-yellow-300 text-black";
      default:
        return "bg-gray-600 text-white";
    }
  };

  return (
    <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 shadow-lg">
      <div className="flex items-center justify-between mb-4">
        <h2 className="text-xl font-semibold flex items-center gap-2">
          🔥 Security Events
        </h2>

        <span className="text-sm opacity-70">
          {filtered.length} alerts shown
        </span>
      </div>

      {/* Filtre butonları */}
      <div className="flex gap-2 mb-4">
        {["all", "high", "medium", "low"].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-3 py-1 rounded text-sm border ${
              filter === f
                ? "bg-blue-500 border-blue-400"
                : "bg-gray-700 border-gray-600 hover:bg-gray-600"
            }`}
          >
            {f.toUpperCase()}
          </button>
        ))}
      </div>

      {/* Event List */}
      <div className="max-h-72 overflow-y-auto space-y-3 text-sm">
        {filtered.map((ev, i) => (
          <div
            key={i}
            className="p-3 bg-gray-700 rounded-lg border border-gray-600"
          >
            <div className="flex items-center justify-between">
              <strong>{ev.anomaly_type}</strong>

              <span
                className={`text-xs px-2 py-1 rounded ${getSeverityColor(
                  ev.severity
                )}`}
              >
                {ev.severity.toUpperCase()}
              </span>
            </div>

            <div className="text-gray-300">{ev.cp_id}</div>
            <div className="text-xs opacity-70">{ev.details?.reason}</div>
          </div>
        ))}
      </div>
    </div>
  );
}
