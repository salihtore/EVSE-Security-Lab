export default function SeverityKPI({ alarms }) {
  const counts = alarms.reduce(
    (acc, alarm) => {
      const sev = alarm.severity || "UNKNOWN";
      acc[sev] = (acc[sev] || 0) + 1;
      return acc;
    },
    { HIGH: 0, MEDIUM: 0, LOW: 0 }
  );

  const boxStyle = (color) => ({
    flex: 1,
    padding: "12px",
    borderRadius: "6px",
    background: "#020617",
    border: `1px solid ${color}`,
    textAlign: "center",
  });

  return (
    <div style={{ display: "flex", gap: "12px", marginBottom: "16px" }}>
      <div style={boxStyle("#ef4444")}>
        <div style={{ fontSize: "12px", opacity: 0.7 }}>HIGH</div>
        <div style={{ fontSize: "24px", fontWeight: "bold", color: "#ef4444" }}>
          {counts.HIGH}
        </div>
      </div>

      <div style={boxStyle("#f59e0b")}>
        <div style={{ fontSize: "12px", opacity: 0.7 }}>MEDIUM</div>
        <div style={{ fontSize: "24px", fontWeight: "bold", color: "#f59e0b" }}>
          {counts.MEDIUM}
        </div>
      </div>

      <div style={boxStyle("#10b981")}>
        <div style={{ fontSize: "12px", opacity: 0.7 }}>LOW</div>
        <div style={{ fontSize: "24px", fontWeight: "bold", color: "#10b981" }}>
          {counts.LOW}
        </div>
      </div>
    </div>
  );
}
