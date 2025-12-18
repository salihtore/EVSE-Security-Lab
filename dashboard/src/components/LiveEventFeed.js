import React, { useEffect, useState } from "react";

export default function LiveEventFeed() {
  const [events, setEvents] = useState([]);

  useEffect(() => {
    const sse = new EventSource("http://localhost:8000/events/live");
    sse.onmessage = (e) => {
      const data = JSON.parse(e.data);
      setEvents((prev) => [data, ...prev.slice(0, 100)]);
    };
    return () => sse.close();
  }, []);

  return (
    <div className="bg-gray-800 p-4 rounded-xl border border-gray-700 shadow-lg">
      <h2 className="text-xl font-semibold mb-3">⚡ Event Stream</h2>

      <div className="max-h-80 overflow-y-auto space-y-2 text-sm">
        {events.map((ev, i) => (
          <div
            key={i}
            className="p-3 bg-gray-700 rounded-lg border border-gray-600"
          >
            <strong>{ev.cp_id}</strong>
            <span className="ml-2 text-blue-300">{ev.message_type}</span>
          </div>
        ))}
      </div>
    </div>
  );
}
