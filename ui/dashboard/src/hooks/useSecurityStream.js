// useSecurityStream.js
import { useEffect, useState } from "react";

export default function useSecurityStream() {
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);
  

  useEffect(() => {
    const source = new EventSource("http://localhost:8000/security/live");

    source.onopen = () => {
      console.log("[SSE] Security stream connected");
      setConnected(true);
    };

source.onmessage = (event) => {

  try {
    const data = JSON.parse(event.data);
    data.severity = String(data.severity || "LOW").toUpperCase();

    // ZORUNLU ALAN KONTROLÜ
    if (!data.anomaly_type || !data.cp_id || !data.severity) {
      return;
    }

setAlerts((prev) => {

  const exists = prev.some((a) => a.event_id === data.event_id);

   if (exists) {
     return prev;
   }

  // EN YENİ EN ÜSTE (max 20)
  return [data, ...prev.slice(0, 25)];
});

  } catch (err) {
    console.error("SSE parse error", err);
  }
};


    source.onerror = () => {
      console.error("[SSE] Security stream error");
      source.close();
      setConnected(false);
    };

    return () => source.close();
  }, []);

  return { alerts, connected };
}
