import React, { useState } from "react";
import Dashboard from "../pages/Dashboard";
import { Toast } from "../components/Toast";
import { useSecurityStream } from "../hooks/useSecurityStream";

export default function MainLayout() {
  const { connected, alerts } = useSecurityStream();
  const [toast, setToast] = useState(null);

  // Toast logic removed for stability
  // React.useEffect(() => {}, [alerts]);

  return (
    <div className="h-screen w-full overflow-hidden bg-slate-950 relative">
      <div className="absolute top-4 right-4 z-50">

      </div>
      {/* MAIN CONTENT Area - Renders the Dashboard which handles its own layout */}
      <main className="h-full relative overflow-hidden">
        <Dashboard />
      </main>

      {toast && <Toast message={toast} onClose={() => setToast(null)} />}
    </div>
  );
}