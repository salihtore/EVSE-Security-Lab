import useSecurityStream from "../hooks/useSecurityStream";
import AlarmCard from "../components/AlarmCard";

export default function LiveAlerts() {
  const { alerts, connected } = useSecurityStream();

  return (
    <aside style={{ width: 320, padding: 12 }}>
      <h3>
        🚨 Live Alerts {connected ? "(LIVE)" : "(DISCONNECTED)"}
      </h3>

      {alerts.length === 0 && <p>No alerts yet</p>}

      {alerts.map(alert => (
        <AlarmCard key={alert.id} alert={alert} />
      ))}
    </aside>
  );
}
