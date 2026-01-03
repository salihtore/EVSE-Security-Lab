export default function Header() {
  return (
    <header
      style={{
        height: "48px",
        background: "#020617",
        color: "#e5e7eb",
        display: "flex",
        alignItems: "center",
        padding: "0 16px",
        borderBottom: "1px solid #1e293b",
      }}
    >
      <strong>CHARGE-SHIELD AI</strong>
      <span style={{ marginLeft: "12px", opacity: 0.7 }}>
        | Security Dashboard
      </span>
    </header>
  );
}
