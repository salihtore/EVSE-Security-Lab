import React, { useState, useEffect, useMemo } from "react";
import { ConnectButton, useCurrentAccount } from "@mysten/dapp-kit";
import { CreateAdminModal } from "../components/dashboard/CreateAdminModal";
import { CustomConnectButton } from "../components/dashboard/CustomConnectButton";
import { useSecurityStream } from "../hooks/useSecurityStream";
import { useAdmin } from "../hooks/useAdmin";
import { StatGrid } from "../components/dashboard/StatGrid";
import { AIIntelligenceChart } from "../components/dashboard/AIIntelligenceChart";
import { AlertGroups } from "../components/dashboard/AlertGroups";
import { MLAnalysisPanel } from "../components/dashboard/MLAnalysisPanel";
import { ThreatTimeline } from "../components/dashboard/ThreatTimeline";
import { WalrusBatchList } from "../components/dashboard/WalrusBatchList";
import { Shield } from "lucide-react";

export default function Dashboard() {
  const { alerts, connected } = useSecurityStream();
  const [selectedAlert, setSelectedAlert] = useState(null);
  const [isCreateAdminOpen, setIsCreateAdminOpen] = useState(false);
  const currentAccount = useCurrentAccount();
  const { checkIsAdmin } = useAdmin();
  const [isAdmin, setIsAdmin] = useState(false);
  const [checkingAdmin, setCheckingAdmin] = useState(false);
  const [verificationError, setVerificationError] = useState(null);

  useEffect(() => {
    const verifyAdmin = async () => {
      if (currentAccount?.address) {
        setCheckingAdmin(true);
        setVerificationError(null);
        try {
          const isUserAdmin = await checkIsAdmin(currentAccount.address);
          setIsAdmin(isUserAdmin);
        } catch (err) {
          console.error("Admin verification failed:", err);
          setIsAdmin(false);
          setVerificationError("Connection to Sui Network failed. Please check your internet or try again later.");
        } finally {
          setCheckingAdmin(false);
        }
      } else {
        setIsAdmin(false);
        setCheckingAdmin(false);
        setVerificationError(null);
      }
    };

    verifyAdmin();
  }, [currentAccount, checkIsAdmin]);

  // Auto-select latest if nothing selected
  React.useEffect(() => {
    if (!selectedAlert && alerts.length > 0 && isAdmin) {
      setSelectedAlert(alerts[0]);
    }
  }, [alerts, selectedAlert, isAdmin]);

  // --- STATS CALCULATION ---
  const stats = useMemo(() => {
    const totalEvents = alerts.length;
    const highRisk = alerts.filter(a => a.severity === "HIGH").length;
    const activeMonitors = new Set(alerts.map(a => a.cp_id)).size;
    const totalScore = alerts.reduce((acc, curr) => acc + (curr.ml?.score || 0), 0);
    const avgRisk = totalEvents > 0 ? (totalScore / totalEvents).toFixed(2) : "0.00";

    // Model Performance Metrics
    const alertsWithML = alerts.filter(a => a.ml?.confidence !== undefined);
    const truePositives = alertsWithML.filter(a => a.ml.confidence > 0.6 && a.severity !== 'LOW').length;
    const falsePositives = alertsWithML.filter(a => a.ml.confidence < 0.4 && a.severity === 'HIGH').length;
    const truePositiveRate = alertsWithML.length > 0 ? Math.round((truePositives / alertsWithML.length) * 100) : 0;

    // Actions Taken (HIGH severity or high ML confidence)
    const actionsTaken = alerts.filter(a =>
      a.severity === 'HIGH' || (a.ml?.confidence && a.ml.confidence > 0.7)
    ).length;

    // Threats Mitigated (unique CPs with HIGH severity)
    const threatsMitigated = new Set(
      alerts.filter(a => a.severity === 'HIGH').map(a => a.cp_id)
    ).size;

    return {
      totalEvents,
      highRisk,
      activeMonitors,
      avgRisk,
      truePositiveRate,
      actionsTaken,
      threatsMitigated
    };
  }, [alerts]);

  // --- LOADING STATE ---
  if (checkingAdmin) {
    return (
      <div className="h-screen w-full bg-[#020617] flex items-center justify-center relative overflow-hidden">
        {/* Simple Loading Animation */}
        <div className="relative flex flex-col items-center gap-4">
          {/* Spinner */}
          <div className="w-12 h-12 border-4 border-indigo-500/30 border-t-indigo-500 rounded-full animate-spin shadow-[0_0_15px_rgba(99,102,241,0.3)]" />

          {/* Text */}
          <div className="text-center space-y-1">
            <div className="text-indigo-400 text-xs font-bold tracking-[0.2em] uppercase animate-pulse">
              Verifying Credentials
            </div>
            <div className="text-slate-500 text-[10px] font-mono">
              Connecting to Sui Testnet...
            </div>
          </div>
        </div>
      </div>
    );
  }

  // --- ACCESS CONTROL RENDER ---
  if (!currentAccount || (!isAdmin && !checkingAdmin)) {
    return (
      <div className="h-screen w-full bg-[#020617] flex flex-col items-center justify-center relative overflow-hidden">
        {/* Background Effects */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_50%_50%,rgba(99,102,241,0.05),transparent_50%)]" />
        <div className="absolute top-[-10%] left-[-10%] w-[40%] h-[40%] rounded-full bg-indigo-500/5 blur-[120px]" />

        <div className="relative z-10 flex flex-col items-center text-center space-y-6 p-8 border border-white/5 rounded-2xl bg-white/5 backdrop-blur-sm max-w-md w-full mx-4">
          <div className="w-16 h-16 rounded-full bg-slate-900 border border-white/10 flex items-center justify-center mb-2 shadow-2xl shadow-indigo-500/10">
            <Shield size={32} className="text-indigo-500" />
          </div>

          <div className="space-y-2">
            <h1 className="text-2xl font-bold text-white tracking-tight">Access Restricted</h1>
            <p className="text-slate-400 text-sm leading-relaxed">
              {verificationError ? (
                <span className="text-red-400 block mb-2 font-semibold">
                  {verificationError}
                </span>
              ) : null}
              {currentAccount
                ? "This wallet does not have Admin privileges. Please switch to an authorized account."
                : "Secure dashboard access requires an authorized wallet connection."}
            </p>
          </div>

          <div className="pt-2 w-full flex justify-center">
            <CustomConnectButton />
          </div>

          <div className="text-[10px] text-slate-600 font-mono pt-4 border-t border-white/5 w-full">
            SECURE SYSTEM ENCLAVE v2.0
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="h-full overflow-y-auto custom-scrollbar bg-slate-950 relative">
      {/* Enhanced Multi-color Background Transitions */}
      <div className="fixed inset-0 pointer-events-none z-0 overflow-hidden">
        {/* Navy/Deep Blue Foundation */}
        <div className="absolute inset-0 bg-[#020617]" />

        {/* Red Glow (Top Left) */}
        <div className="absolute top-[-15%] left-[-10%] w-[50%] h-[50%] rounded-full bg-red-600/15 blur-[140px]" />

        {/* White/Light Blue Highlight (Center Top) */}
        <div className="absolute top-[-10%] left-1/2 -translate-x-1/2 w-[60%] h-[40%] rounded-full bg-slate-100/10 blur-[120px]" />

        {/* Blue/Cyan Glow (Bottom Right) */}
        <div className="absolute bottom-[-10%] right-[-10%] w-[50%] h-[50%] rounded-full bg-blue-500/15 blur-[140px]" />

        {/* Professional Mesh Gradient Overlay */}
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_20%_30%,rgba(59,130,246,0.1),transparent_50%),radial-gradient(circle_at_80%_70%,rgba(220,38,38,0.08),transparent_50%)]" />
      </div>

      <div className="max-w-[1700px] mx-auto px-8 py-10 space-y-8 relative z-10">
        {/* 1. HEADER - IMAGE REPLICA GRADIENT BAR */}
        <div className="flex items-center justify-between px-6 py-2 border-b border-t border-white/5 bg-[#1e2028] bg-gradient-to-r from-slate-900 via-[#1e2028] to-slate-900 rounded-sm mb-2 shadow-lg">
          <div className="flex items-center gap-4">
            <div className="flex items-center gap-2">
              <Shield size={16} className="text-indigo-500 fill-indigo-500/10" />
              <span className="text-indigo-400 font-bold text-[13px] tracking-wide">Security Panel</span>
            </div>

            <div className="h-4 w-[1.5px] bg-white/20" />

            <div className="flex items-center gap-2">
              <div className={`w-1.5 h-1.5 rounded-full ${connected ? 'bg-emerald-500 shadow-[0_0_8px_#10b981]' : 'bg-red-500'}`} />
              <span className={`text-[10px] font-black tracking-widest ${connected ? 'text-emerald-500' : 'text-red-500'}`}>
                ENGINE : {connected ? 'ONLINE' : 'OFFLINE'}
              </span>
            </div>
          </div>

          <div className="flex items-center gap-4">
            <div className="text-slate-500 text-[9px] font-black tracking-[0.25em] uppercase opacity-60">
              ACTIVE MONITORING SESSION
            </div>

            {isAdmin && (
              <button
                onClick={() => setIsCreateAdminOpen(true)}
                className="bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-400 text-xs font-bold py-1.5 px-3 rounded border border-indigo-500/30 transition-colors uppercase tracking-wider"
              >
                + New Admin
              </button>
            )}

            <CustomConnectButton />
          </div>

          <CreateAdminModal
            isOpen={isCreateAdminOpen}
            onClose={() => setIsCreateAdminOpen(false)}
          />
        </div>

        {/* 2. KPI GRID (TOP) */}
        <StatGrid stats={stats} />

        {/* 3. MAIN INTERFACE GRID */}
        <div className="grid grid-cols-1 lg:grid-cols-4 gap-3 h-[calc(100vh-220px)] min-h-[600px]">

          {/* Pillar 1: Targeted Campaigns (Left Sidebar) */}
          <div className="lg:col-span-1 h-full overflow-hidden">
            <AlertGroups alerts={alerts} onSelectAlert={setSelectedAlert} />
          </div>

          {/* Pillar 2: AI Analysis & Evolution Stack (Center) */}
          <div className="lg:col-span-2 h-full flex flex-col gap-3 overflow-y-auto custom-scrollbar pr-1">
            {/* Top Row: Analysis Core */}
            <div className="grid grid-cols-1 xl:grid-cols-2 gap-3">
              <MLAnalysisPanel selectedAlert={selectedAlert} />
              <AIIntelligenceChart alerts={alerts} />
            </div>

            {/* Middle Row: Evolution Timeline */}
            <div className="flex-1 min-h-[300px]">
              <ThreatTimeline alerts={alerts} />
            </div>
          </div>

          {/* Pillar 3: Walrus Archives (Right Sidebar) */}
          <div className="lg:col-span-1 h-full overflow-hidden">
            <WalrusBatchList />
          </div>
        </div>
      </div>
    </div>
  );
}