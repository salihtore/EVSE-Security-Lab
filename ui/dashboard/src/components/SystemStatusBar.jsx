export default function SystemStatusBar() {
  // ŞU AN: mock data
  const systemStatus = {
    engine: "ONLINE", // ONLINE | OFFLINE
    lastHeartbeat: "3s ago",
    activeCpCount: 4,
    activeAlarmCount: 1,
  };

  const engineColor =
    systemStatus.engine === "ONLINE" ? "#22c55e" : "#ef4444";

  return (
    <div
      style={{
        height: "40px",
        background: "#020617",
        borderBottom: "1px solid #1e293b",
        display: "flex",
        alignItems: "center",
        gap: "24px",
        padding: "0 16px",
        fontSize: "13px",
        color: "#e5e7eb",
      }}
    >
      <span>
        <strong>Engine:</strong>{" "}
        <span style={{ color: engineColor }}>
          {systemStatus.engine}
        </span>
      </span>

      <span>
        <strong>Last Data:</strong> {systemStatus.lastHeartbeat}
      </span>

      <span>
        <strong>Active CPs:</strong> {systemStatus.activeCpCount}
      </span>

      <span>
        <strong>Active Alarms:</strong>{" "}
        <span
          style={{
            color:
              systemStatus.activeAlarmCount > 0
                ? "#f97316"
                : "#22c55e",
          }}
        >
          {systemStatus.activeAlarmCount}
        </span>
      </span>
    </div>
  );
}
