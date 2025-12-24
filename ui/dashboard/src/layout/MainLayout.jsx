import { Outlet, useLocation } from "react-router-dom";
import { Routes, Route } from "react-router-dom";
import { useState } from "react";
import Header from "./Header";
import SystemStatusBar from "../components/SystemStatusBar";
import AlertDetailPanel from "../components/AlertDetailPanel";
import Dashboard from "../pages/Dashboard";
import LiveAlertsPage from "../pages/LiveAlertsPage";
import Analytics from "../pages/Analytics";


export default function MainLayout() {
  const location = useLocation();
  const [selectedAlert, setSelectedAlert] = useState(null);

  // /alerts sayfasında sağ paneli kapat
  const isAlertsPage = location.pathname === "/alerts";


  return (
  <div
    style={{
      minHeight: "100vh",
      display: "flex",
      justifyContent: "center",
      alignItems: "flex-start",
      paddingTop: "48px",
    }}
  >
    <main
      style={{
        width: "100%",
        maxWidth: "1200px",
        padding: "32px",
      }}
    >
<Routes>
  <Route
    path="/"
    element={
      <Dashboard onSelectAlert={setSelectedAlert} />
    }
  />
  <Route
    path="/alerts"
    element={
      <LiveAlertsPage onSelectAlert={setSelectedAlert} />
    }
  />
  <Route path="/analytics" element={<Analytics />} />
</Routes>

    </main>

    <AlertDetailPanel
      alert={selectedAlert}
      onClose={() => setSelectedAlert(null)}
    />
  </div>
);
}