// ui/dashboard/src/components/AlarmList.jsx
export default function AlarmList({ alarms, onSelectAlert }) {

  if (!alarms || alarms.length === 0) {
    return <div style={{ opacity: 0.6 }}>No active alarms</div>;
  }

  // 1️⃣ CP bazlı grupla
  const groupedByCp = alarms.reduce((acc, alarm) => {
    const cp = alarm.cp_id || "UNKNOWN_CP";
    if (!acc[cp]) acc[cp] = [];
    acc[cp].push(alarm);
    return acc;
  }, {});

  return (
    <div>
<h3>Active Alarms by Charge Point</h3>

<div
  style={{
    display: "grid",
    gridTemplateColumns: "repeat(auto-fit, minmax(360px, 1fr))",
    gap: "16px",
    marginTop: "12px",
  }}
>
  {Object.entries(groupedByCp).map(([cpId, cpAlarms]) => (
    <div
      key={cpId}
      style={{
        padding: "12px",
        border: "1px solid #1f2937",
        borderRadius: "10px",
        background: "rgba(2, 6, 23, 0.6)",
        boxShadow: "0 0 0 1px rgba(255,255,255,0.04)",
      }}
    >
      {/* CP HEADER */}
      <div
        style={{
          fontWeight: 700,
          marginBottom: "10px",
          color: "#60a5fa",
          display: "flex",
          justifyContent: "space-between",
          alignItems: "center",
        }}
      >
        <span>🔌 {cpId}</span>
        <span style={{ fontSize: "12px", opacity: 0.8 }}>
          {cpAlarms.length} alarm(s)
        </span>
      </div>

      {/* ALARMS */}
      <ul style={{ listStyle: "none", paddingLeft: 0, margin: 0 }}>
        {cpAlarms.map((alarm, i) => (
          <li
            key={`${alarm.cp_id}-${alarm.anomaly_type}-${i}`}
            onClick={() => onSelectAlert(alarm)}
            style={{
            marginBottom: "8px",
            padding: "8px",
            borderRadius: "8px",
            cursor: "pointer",
            borderLeft: "4px solid",
            borderLeftColor:
              alarm.severity === "HIGH"
              ? "#ef4444"
              : alarm.severity === "MEDIUM"
              ? "#f59e0b"
              : "#10b981",
            background: "rgba(2, 6, 23, 0.9)",
          }}
          >
            <div style={{ fontWeight: 700, fontSize: "13px" }}>
              {alarm.anomaly_type}
            </div>
            <div style={{ fontSize: "12px", opacity: 0.75 }}>
              Severity: {alarm.severity}
            </div>
          </li>
        ))}
      </ul>
    </div>
  ))}
</div>
    </div>
  );
}
