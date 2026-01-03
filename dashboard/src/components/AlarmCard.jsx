export default function AlarmCard({ alarm, onClick }) {
  const levelColors = {
    HIGH: "#ef4444",
    MEDIUM: "#f97316",
    LOW: "#eab308",
  };

  const mitigation = alarm.mitigation || null;

  return (
    <div
      onClick={() => onClick && onClick(alarm)}
      style={{
        cursor: "pointer",
        borderLeft: `4px solid ${levelColors[alarm.severity] || levelColors.LOW}`,
        background: "#020617",
        padding: "10px 12px",
        marginBottom: "8px",
        borderRadius: "4px",
        fontSize: "13px",
        position: "relative"
      }}
    >
      <div style={{ display: "flex", justifyContent: "space-between", alignItems: "flex-start", marginBottom: "4px" }}>
        <div style={{ fontWeight: "bold" }}>
          {alarm.anomaly_type}
        </div>
        {mitigation && mitigation.action !== "MONITOR_ONLY" && (
          <span style={{
            fontSize: "10px",
            background: "#1e293b",
            color: "#60a5fa",
            padding: "2px 6px",
            borderRadius: "10px",
            display: "flex",
            alignItems: "center",
            gap: "4px",
            border: "1px solid #3b82f6"
          }}>
            🛡️ {mitigation.action}
          </span>
        )}
      </div>

      <div style={{ opacity: 0.8 }}>{alarm.details?.reason || alarm.details?.message || "Güvenlik olayı tespit edildi"}</div>

      <div
        style={{
          marginTop: "6px",
          fontSize: "11px",
          opacity: 0.6,
        }}
      >
        CP: {alarm.cp_id} · {alarm.time}
      </div>
    </div>
  );
}
