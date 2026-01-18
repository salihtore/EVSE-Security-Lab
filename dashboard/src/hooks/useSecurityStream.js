// Dosya: src/hooks/useSecurityStream.jsx
import { useEffect, useState } from "react";



export function useSecurityStream() {
  const [alerts, setAlerts] = useState([]);
  const [connected, setConnected] = useState(false);

  useEffect(() => {
    const url = "http://localhost:8000/security/live";
    const source = new EventSource(url);

    source.onopen = () => {
      console.log("[SSE] Security stream connected:", url);
      setConnected(true);
    };

    source.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // Beklenen temel alanlar ve Normalizasyon
        data.severity = String(data.severity || "LOW").toUpperCase();
        data.event_id = data.event_id || data.id || String(Date.now());
        data.details = data.details || {};

        // Frontend UI'ın beklediği ek alanlar (Eski JSONL mantığına uyumluluk için)
        data.time = data.timestamp
          ? new Date(data.timestamp * 1000).toLocaleTimeString()
          : new Date().toLocaleTimeString();

        // ML bilgisini normalize et (new_ui mantığı)
        const mlFromDetails = data.details.ml ?? null;
        const mlScoreLegacy = data.details.ml_score ?? null;
        data.ml = mlFromDetails;
        data.ml_score =
          (mlFromDetails && typeof mlFromDetails.score === "number")
            ? mlFromDetails.score
            : (typeof mlScoreLegacy === "number" ? mlScoreLegacy : null);

        // 🛡️ Müdahale (Mitigation) bilgisini ayıkla
        data.mitigation = data.details.mitigation ?? null;
        if (data.mitigation) {
          console.log("🛡️ [STREAM] Mitigation found for " + data.anomaly_type, data.mitigation);
        } else {
          console.log("⚠️ [STREAM] No mitigation in alert:", data.event_id);
        }

        // Zorunlu alan kontrolü
        if (!data.anomaly_type || !data.cp_id) return;

        setAlerts((prev) => {
          // event_id bazlı dedup (mükerrer kayıt engelleme)
          const exists = prev.some((a) => a.event_id === data.event_id);
          if (exists) return prev;

          // En yeni en üstte olacak şekilde ekle, limit 500
          const updated = [data, ...prev];
          return updated.slice(0, 500);
        });
      } catch (err) {
        console.error("[SSE] parse error", err);
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