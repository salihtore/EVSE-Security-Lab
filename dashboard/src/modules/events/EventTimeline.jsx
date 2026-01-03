// Dosya: src/modules/events/EventTimeline.jsx
import React, { useState, useMemo } from "react";
import { useSecurityStream } from "../../hooks/useSecurityStream";

export const EventTimeline = () => {
  const { alerts } = useSecurityStream();
  
  // 1. Filtreleme için State
  const [selectedCP, setSelectedCP] = useState("ALL");

  // 2. Mevcut alarmlardan benzersiz CP ID listesini oluştur (Dropdown için)
  const uniqueCPs = useMemo(() => {
    const cps = alerts.map(a => a.cp_id).filter(id => id);
    return ["ALL", ...new Set(cps)];
  }, [alerts]);

  // 3. Veriyi seçili CP'ye göre filtrele
  const filteredAlerts = useMemo(() => {
    if (selectedCP === "ALL") return alerts;
    return alerts.filter(alert => alert.cp_id === selectedCP);
  }, [alerts, selectedCP]);

  return (
    <div style={{ 
      background: "#161625", 
      borderRadius: "8px", 
      border: "1px solid #333", 
      display: "flex", 
      flexDirection: "column",
      height: "100%", 
      overflow: "hidden" 
    }}>
      {/* --- SABİT BAŞLIK VE AKTİF FİLTRE --- */}
      <div style={{ 
        padding: "12px 15px", 
        borderBottom: "1px solid #444", 
        background: "#1c1c2e",
        display: "flex",
        justifyContent: "space-between",
        alignItems: "center",
        flexShrink: 0 
      }}>
        <h3 style={{ margin: 0, fontSize: "14px", color: "#fff" }}>Event Timeline</h3>
        
        {/* AKTİF FİLTRE DROPDOWN */}
        <select 
          value={selectedCP}
          onChange={(e) => setSelectedCP(e.target.value)}
          style={{ 
            background: "#111", 
            color: "#38bdf8", // Filtre olduğunu belli etmek için accent rengi
            border: "1px solid #444", 
            padding: "2px 8px", 
            borderRadius: "4px", 
            fontSize: "11px", 
            outline: "none",
            cursor: "pointer",
            fontWeight: "bold"
          }}
        >
          {uniqueCPs.map(cp => (
            <option key={cp} value={cp} style={{ background: "#1c1c2e", color: "#fff" }}>
              {cp === "ALL" ? "FILTER: ALL CP" : `CP: ${cp}`}
            </option>
          ))}
        </select>
      </div>

      {/* --- KAYDIRILABİLİR TIMELINE ALANI --- */}
      <div style={{ 
        flex: 1, 
        overflowY: "auto", 
        padding: "20px",
        minHeight: 0,
        scrollbarWidth: "thin",
        scrollbarColor: "#444 #161625"
      }}>
         {filteredAlerts.length === 0 ? (
            <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', height: '100%', color: "#555" }}>
              <p>{selectedCP === "ALL" ? "Waiting for events..." : "No events for this CP."}</p>
            </div>
         ) : (
            <div style={{ position: "relative", paddingLeft: "10px" }}>
               {/* Dikey Çizgi */}
               <div style={{ position: "absolute", left: "19px", top: 0, bottom: 0, width: "2px", background: "#444" }}></div>

               {filteredAlerts.map((alert, index) => (
                 <div key={index} style={{ display: "flex", alignItems: "center", marginBottom: "15px", position: "relative" }}>
                    {/* Nokta (Dot) */}
                    <div style={{ 
                      width: "10px", 
                      height: "10px", 
                      borderRadius: "50%", 
                      background: alert.severity === "HIGH" ? "#f43f5e" : "#38bdf8", 
                      zIndex: 2,
                      border: "3px solid #161625", 
                      marginRight: "15px",
                      flexShrink: 0,
                      boxShadow: alert.severity === "HIGH" ? "0 0 8px #f43f5e88" : "none"
                    }}></div>

                    {/* İçerik */}
                    <div style={{ 
                      flex: 1, 
                      borderBottom: "1px solid rgba(255,255,255,0.05)", 
                      paddingBottom: "8px", 
                      display: "flex", 
                      flexDirection: "column",
                      gap: "2px"
                    }}>
                       <div style={{ display: "flex", justifyContent: "space-between", alignItems: "center" }}>
                          <span style={{ color: "#f1f5f9", fontWeight: "600", fontSize: "12px" }}>{alert.anomaly_type}</span>
                          <span style={{ color: "#64748b", fontSize: "10px", fontFamily: "monospace" }}>{new Date().toLocaleTimeString()}</span>
                       </div>
                       <div style={{ color: "#94a3b8", fontSize: "11px" }}>
                          Station: <span style={{ color: "#38bdf8" }}>{alert.cp_id}</span>
                       </div>
                    </div>
                 </div>
               ))}
            </div>
         )}
      </div>
    </div>
  );
};