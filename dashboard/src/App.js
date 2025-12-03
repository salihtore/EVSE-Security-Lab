import React from "react";
import LiveSecurityFeed from "./components/LiveSecurityFeed";
import LiveEventFeed from "./components/LiveEventFeed";
import CpStatusList from "./components/CpStatusList";
import ChartsPanel from "./components/ChartsPanel";

export default function App() {
  return (
    <div className="p-6 bg-gray-900 min-h-screen text-white">
    <h1 className="text-3xl font-bold mb-6">EVSE Security Lab Dashboard</h1>

    <div className="grid grid-cols-2 gap-6">
        <LiveSecurityFeed />
        <CpStatusList />
    </div>

    <LiveEventFeed />

    <ChartsPanel />
</div>

  );
}
