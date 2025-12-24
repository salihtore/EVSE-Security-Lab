// ui/dashboard/src/components/AlertDetailPanel.jsx
export default function AlertDetailPanel({ alert, onClose }) {
  if (!alert) return null;

  return (
    <div
      style={{
        position: "fixed",
        top: 0,
        right: 0,
        width: "360px",
        height: "100vh",
        background: "#020617",
        borderLeft: "1px solid #1e293b",
        padding: "16px",
        zIndex: 50,
      }}
    >
      <button
        onClick={onClose}
        style={{
          background: "transparent",
          color: "#e5e7eb",
          border: "none",
          fontSize: "14px",
          cursor: "pointer",
          marginBottom: "12px",
        }}
      >
        ← Close
      </button>

      <h3 style={{ marginBottom: "12px", color: "#f87171" }}>
      🚨 {alert.anomaly_type}
      </h3>


      <pre
        style={{
          fontSize: "12px",
          background: "#020617",
          border: "1px solid #1e293b",
          padding: "10px",
          borderRadius: "6px",
          overflowX: "auto",
        }}
      >
        {JSON.stringify(alert, null, 2)}
      </pre>
    </div>
  );
}
