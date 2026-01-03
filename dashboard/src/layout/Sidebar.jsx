import { NavLink } from "react-router-dom";

const linkStyle = ({ isActive }) => ({
  display: "block",
  padding: "6px 8px",
  borderRadius: "4px",
  color: isActive ? "#22c55e" : "#cbd5f5",
  background: isActive ? "#022c22" : "transparent",
  textDecoration: "none",
  marginBottom: "4px",
});

export default function Sidebar() {
  return (
    <aside
      style={{
        width: "220px",
        background: "#020617",
        borderRight: "1px solid #1e293b",
        padding: "12px",
        color: "#cbd5f5",
      }}
    >
      <div style={{ marginBottom: "12px", fontWeight: "bold" }}>
        Navigation
      </div>

      <NavLink to="/" style={linkStyle}>
        Dashboard
      </NavLink>

      <NavLink to="/alerts" style={linkStyle}>
        Live Alerts
      </NavLink>

      <NavLink to="/analytics" style={linkStyle}>
        Analytics
      </NavLink>
    </aside>
  );
}
