import { useState } from "react";
import AlarmList from "../components/AlarmList";
import SeverityKPI from "../components/SeverityKPI";
import useSecurityStream from "../hooks/useSecurityStream";

export default function Dashboard({ onSelectAlert }) {

 const { alerts, connected } = useSecurityStream();

 //const [selectedAlert, setSelectedAlert] = useState(null);

//  const authBypassAlarms = alerts.filter(
//   (a) => a.anomaly_type === "AUTH_BYPASS"
// );
  
   return (
    <div
      style={{
        maxWidth: "980px",
        margin: "0 auto",
        padding: "32px 16px",
      }}
    >
      {/* HEADER */}
      <h1
        style={{
          fontSize: "34px",
          fontWeight: 800,
          marginBottom: "8px",
          letterSpacing: "-0.2px",
        }}
      >
        Charge-Shield Control Center
      </h1>

      <p style={{ opacity: 0.72, marginBottom: "18px", lineHeight: 1.4 }}>
        Real-time anomaly monitoring for OCPP 1.6 charge points
      </p>

      {/* CONNECTION BADGE */}
      <div style={{ marginBottom: "24px" }}>
        Security Stream:{" "}
        <b style={{ color: connected ? "#10b981" : "#ef4444" }}>
          {connected ? "CONNECTED" : "DISCONNECTED"}
        </b>
      </div>

      {/* KPI */}
      <SeverityKPI alarms={alerts} />

      {/* AUTH BYPASS ÖZEL PANEL
      {authBypassAlarms.length > 0 && (
        <div
          style={{
            marginTop: "24px",
            padding: "16px",
            borderRadius: "12px",
            border: "1px solid rgba(239,68,68,0.4)",
            background:
              "radial-gradient(1200px 300px at 10% 0%, rgba(239,68,68,0.12), transparent 60%), #020617",
          }}
        >
          <h3 style={{ color: "#ef4444", marginBottom: "12px" }}>
            🚨 Critical Attack: Authentication Bypass
          </h3>

          {authBypassAlarms.map((a, i) => (
            <div
              key={i}
              style={{
                padding: "10px",
                marginBottom: "8px",
                borderRadius: "8px",
                background: "#020617",
                borderLeft: "4px solid #ef4444",
                cursor: "pointer",
              }}
              onClick={() => onSelectAlert(a)}
            >
              <b>{a.cp_id}</b> —{" "}
              {a.details?.reason || "Authorize skipped"}
            </div>
          ))}
        </div>
      )} */}

      {/* TÜM ALARMLAR */}
      <AlarmList
        alarms={alerts}
        onSelectAlert={onSelectAlert}
      />
    </div>
  );
}

