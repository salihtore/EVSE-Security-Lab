export default function AlarmCard({ alarm, onClick }) {
  const levelColors = {
    HIGH: "#ef4444",
    MEDIUM: "#f97316",
    LOW: "#eab308",
  };

  return (
    <div
      onClick={() => onClick && onClick(alarm)}
      style={{
        cursor: "pointer",
        borderLeft: `4px solid ${levelColors[alarm.level]}`,
        background: "#020617",
        padding: "10px 12px",
        marginBottom: "8px",
        borderRadius: "4px",
        fontSize: "13px",
      }}
    >
      <div style={{ fontWeight: "bold", marginBottom: "4px" }}>
        {alarm.type}
      </div>

      <div style={{ opacity: 0.8 }}>{alarm.message}</div>

      <div
        style={{
          marginTop: "6px",
          fontSize: "11px",
          opacity: 0.6,
        }}
      >
        CP: {alarm.cpId} · {alarm.time}
      </div>
    </div>
  );
}
