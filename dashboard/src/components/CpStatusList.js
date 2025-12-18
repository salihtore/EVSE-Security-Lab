import React, { useEffect, useState } from "react";

export default function CpStatusList() {
  const [status, setStatus] = useState({});

  useEffect(() => {
    const load = async () => {
      try {
        const res = await fetch("http://localhost:8000/cp/status");
        const data = await res.json();
        setStatus(data);
      } catch (err) {
        console.error("Failed to fetch CP status");
      }
    };

    load();
    const t = setInterval(load, 3000);
    return () => clearInterval(t);
  }, []);

  const getColor = (s) => {
    if (s === "Charging") return "text-green-400";
    if (s === "Available") return "text-blue-300";
    if (s === "Finishing") return "text-yellow-300";
    return "text-gray-300";
  };

  return (
    <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 shadow-lg">
      <h2 className="text-xl font-semibold mb-3">
        📡 Charge Point Status
      </h2>

      <div className="space-y-2 text-sm">
        {Object.entries(status).map(([cp, st]) => (
          <div
            key={cp}
            className="p-3 bg-gray-700 rounded-lg border border-gray-600"
          >
            <strong>{cp}</strong>
            <span className={`ml-3 ${getColor(st.status)}`}>
              {st.status}
            </span>
          </div>
        ))}
      </div>
    </div>
  );
}
