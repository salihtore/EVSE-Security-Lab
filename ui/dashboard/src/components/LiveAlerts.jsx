import AlarmCard from "./AlarmCard";
import useSecurityStream from "../hooks/useSecurityStream";

export default function LiveAlerts({ onSelectAlert }) {
  const { alerts, connected } = useSecurityStream();

  return (
    <div
      style={{
        width: "360px",
        background: "#020617",
        borderLeft: "1px solid #1e293b",
        padding: "12px",
        overflowY: "auto",
      }}
    >
      <div
        style={{
          fontWeight: "bold",
          marginBottom: "10px",
          fontSize: "14px",
          color: connected ? "#22c55e" : "#ef4444",
        }}
      >
        🚨 Live Alerts {connected ? "(LIVE)" : "(DISCONNECTED)"}
      </div>

      {alerts.length === 0 && (
        <div style={{ fontSize: "12px", opacity: 0.6 }}>
          No alerts yet
        </div>
      )}

      {alerts.map((alarm) => (
        <AlarmCard
          key={alarm.id}
          alarm={alarm}
          onClick={onSelectAlert}
        />
      ))}
    </div>
  );
}
