import React, { useEffect } from "react";
import { Routes, Route } from "react-router-dom";
import MainLayout from "./layout/MainLayout";
import { useEventStore } from "./store/eventStore";

export default function App() {
  const addEvent = useEventStore((state) => state.addEvent);

  useEffect(() => {
    // Backend'in tek kapısı
    const url = 'http://127.0.0.1:8000/security/live';
    console.log("🔌 Bağlantı kuruluyor:", url);

    const eventSource = new EventSource(url);

    eventSource.onmessage = (event) => {
      try {
        const data = JSON.parse(event.data);

        // --- DEDEKTİF MODU BAŞLANGIÇ ---
        // Gelen her veriyi konsola yazdırıyoruz
        console.log("📦 GELEN HAM VERİ:", data);

        // Eğer verinin içinde 'risk_level' varsa o bir Alarmdır.
        if (data.risk_level) {
          console.log("🔴 Bu bir ALARM (Event değil)");
        }
        // Eğer 'risk_level' yoksa, onu Olay (Event) kabul edip ekleyelim
        else {
          console.log("🟢 Bu bir OLAY! Listeye ekleniyor...");
          addEvent(data);
        }
        // --- DEDEKTİF MODU BİTİŞ ---

      } catch (err) {
        console.error("Veri okuma hatası:", err);
      }
    };

    eventSource.onerror = (err) => {
      // Bağlantı koparsa veya hata olursa
      console.error("Bağlantı Hatası:", err);
      eventSource.close();
    };

    return () => {
      eventSource.close();
    };
  }, []);

  return (
    <Routes>
      <Route path="/*" element={<MainLayout />} />
    </Routes>
  );
}