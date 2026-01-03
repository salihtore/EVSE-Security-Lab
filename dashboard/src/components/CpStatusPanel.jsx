import useCpStream from "../hooks/useCpStream";


export default function CpStatusPanel() {
  const cps = useCpStream();

  if (cps.length === 0) {
    return <div style={{ opacity: 0.6 }}>No CP data</div>;
  }

  const stateColor = (cp) => {
    if (!cp.online) return "#475569"; // offline
    if (cp.state === "CHARGING") return "#22c55e";
    if (cp.state === "IDLE") return "#38bdf8";
    if (cp.state === "FAULTED") return "#ef4444";
    return "#64748b";
  };

  return (
    <div>
      <h2 style={{ marginBottom: "12px" }}>Charge Points</h2>

      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(auto-fill, minmax(220px, 1fr))",
          gap: "12px",
        }}
      >
        {cps.map((cp) => (
          <div
            key={cp.id}
            style={{
              background: "#020617",
              border: "1px solid #1e293b",
              borderLeft: `4px solid ${stateColor(cp)}`,
              padding: "12px",
              borderRadius: "6px",
              fontSize: "13px",
            }}
          >
            <div style={{ fontWeight: "bold", marginBottom: "6px" }}>
              {cp.id}
            </div>

            <div>
              <strong>Status:</strong>{" "}
              <span
                style={{
                  color: cp.online ? "#22c55e" : "#94a3b8",
                }}
              >
                {cp.online ? "ONLINE" : "OFFLINE"}
              </span>
            </div>

            <div>
              <strong>State:</strong>{" "}
              <span style={{ color: stateColor(cp) }}>
                {cp.state}
              </span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
