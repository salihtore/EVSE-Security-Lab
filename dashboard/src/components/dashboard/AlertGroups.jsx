import React, { useMemo, useState } from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { ShieldAlert, ChevronDown, ChevronRight, Clock, AlertTriangle, Shield } from 'lucide-react';

export function AlertGroups({ alerts, onSelectAlert }) {
    const [expandedGroups, setExpandedGroups] = useState(new Set());

    // Group alerts by CP_ID and anomaly_type
    const groupedData = useMemo(() => {
        const groups = {};
        alerts.forEach(alert => {
            const key = `${alert.cp_id}_${alert.anomaly_type}`;
            if (!groups[key]) {
                groups[key] = {
                    cp_id: alert.cp_id,
                    anomaly_type: alert.anomaly_type,
                    count: 0,
                    highestSeverity: 'LOW',
                    latestTimestamp: 0,
                    alerts: []
                };
            }
            const group = groups[key];
            group.count++;
            group.alerts.push(alert);
            if (alert.timestamp > group.latestTimestamp) group.latestTimestamp = alert.timestamp;

            if (alert.severity === 'HIGH') group.highestSeverity = 'HIGH';
            else if (alert.severity === 'MEDIUM' && group.highestSeverity !== 'HIGH') group.highestSeverity = 'MEDIUM';
        });

        return Object.values(groups).sort((a, b) => b.latestTimestamp - a.latestTimestamp);
    }, [alerts]);

    const toggleGroup = (key) => {
        const newExpanded = new Set(expandedGroups);
        if (newExpanded.has(key)) {
            newExpanded.delete(key);
        } else {
            newExpanded.add(key);
        }
        setExpandedGroups(newExpanded);
    };

    const getSeverityGradient = (severity) => {
        switch (severity) {
            case 'HIGH':
                return 'bg-gradient-to-br from-red-500/20 via-red-600/10 to-transparent';
            case 'MEDIUM':
                return 'bg-gradient-to-br from-amber-500/20 via-amber-600/10 to-transparent';
            default:
                return 'bg-gradient-to-br from-emerald-500/20 via-emerald-600/10 to-transparent';
        }
    };

    const getSeverityBorder = (severity) => {
        switch (severity) {
            case 'HIGH':
                return 'border-red-500/30 hover:border-red-500/50';
            case 'MEDIUM':
                return 'border-amber-500/30 hover:border-amber-500/50';
            default:
                return 'border-emerald-500/30 hover:border-emerald-500/50';
        }
    };

    return (
        <Card className="flex flex-col h-[1212px] overflow-hidden">
            {/* Custom Header matching WalrusPanel for Symmetry */}
            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5 relative z-10">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-red-900/20 border border-red-500/20 flex items-center justify-center">
                        <ShieldAlert size={16} className="text-red-400" />
                    </div>
                    <div>
                        <h3 className="text-slate-200 font-bold text-sm tracking-wide">Threat Campaigns</h3>
                        <div className="text-[10px] text-red-400 font-mono flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-red-500 animate-pulse" />
                            {groupedData.length} Active Targets
                        </div>
                    </div>
                </div>
                <div className="text-[10px] text-slate-500 font-black tracking-widest opacity-60">
                    LIVE FEED
                </div>
            </div>
            <CardContent className="flex-1 overflow-y-auto custom-scrollbar p-0">
                <div className="space-y-1 p-2 pt-0">
                    {groupedData.length === 0 ? (
                        <div className="text-center text-slate-500 py-8">No active threats</div>
                    ) : (
                        groupedData.map((group) => {
                            const groupKey = `${group.cp_id}_${group.anomaly_type}`;
                            const isExpanded = expandedGroups.has(groupKey);

                            return (
                                <div
                                    key={groupKey}
                                    className={`${getSeverityGradient(group.highestSeverity)} border ${getSeverityBorder(group.highestSeverity)} rounded-xl overflow-hidden transition-all duration-300`}
                                >
                                    {/* Header - Always Visible */}
                                    <div
                                        onClick={() => toggleGroup(groupKey)}
                                        className="p-4 cursor-pointer hover:bg-white/5 transition-colors"
                                    >
                                        <div className="flex items-start justify-between mb-3">
                                            <div className="flex items-center gap-3">
                                                <div className={`w-3 h-3 rounded-full ${group.highestSeverity === 'HIGH' ? 'bg-red-500 animate-pulse shadow-lg shadow-red-500/50' : group.highestSeverity === 'MEDIUM' ? 'bg-amber-500 shadow-lg shadow-amber-500/50' : 'bg-emerald-500'}`} />
                                                <div>
                                                    <div className="font-bold text-white text-base tracking-tight">{group.cp_id}</div>
                                                    <div className="text-xs text-slate-400 font-mono mt-0.5">{new Date(group.latestTimestamp * 1000).toLocaleString()}</div>
                                                </div>
                                            </div>
                                            {isExpanded ? <ChevronDown className="text-slate-400" size={20} /> : <ChevronRight className="text-slate-400" size={20} />}
                                        </div>

                                        <div className="flex items-center justify-between">
                                            <div className="flex items-center gap-2">
                                                <span className={`px-3 py-1 rounded-lg text-xs font-bold uppercase tracking-wider ${group.highestSeverity === 'HIGH' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                                                    group.highestSeverity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                                                        'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                                                    }`}>
                                                    {group.anomaly_type.replace(/_/g, ' ')}
                                                </span>
                                            </div>
                                            <span className="text-sm text-slate-300 font-semibold">{group.count} Events</span>
                                        </div>
                                    </div>

                                    {/* Expanded Details */}
                                    {isExpanded && (
                                        <div className="border-t border-white/10 bg-slate-900/20 p-2 space-y-1.5 text-[11px]">
                                            {group.alerts.map((alert, idx) => (
                                                <div
                                                    key={alert.event_id || idx}
                                                    onClick={(e) => {
                                                        e.stopPropagation();
                                                        onSelectAlert && onSelectAlert(alert);
                                                    }}
                                                    className="bg-slate-800/30 border border-white/5 rounded-lg p-2 hover:bg-slate-800/60 cursor-pointer transition-colors"
                                                >
                                                    <div className="flex items-center justify-between mb-2">
                                                        <span className="text-xs font-mono text-slate-400">Event #{alert.event_id?.slice(-6) || idx}</span>
                                                        <div className="flex items-center gap-2">

                                                            <span className={`text-xs px-2 py-0.5 rounded font-bold ${alert.severity === 'HIGH' ? 'bg-red-500/20 text-red-400' :
                                                                alert.severity === 'MEDIUM' ? 'bg-amber-500/20 text-amber-400' :
                                                                    'bg-emerald-500/20 text-emerald-400'
                                                                }`}>
                                                                {alert.severity}
                                                            </span>
                                                        </div>
                                                    </div>

                                                    <div className="flex items-center justify-between mb-2">
                                                        <div className="flex items-center gap-2 text-xs text-slate-300">
                                                            <Clock size={12} className="text-slate-500" />
                                                            <span>{alert.time || new Date(alert.timestamp * 1000).toLocaleTimeString()}</span>
                                                        </div>

                                                        <div className="flex items-center gap-2">
                                                            {/* 🛡️ Mitigation Badge */}
                                                            {alert.mitigation && alert.mitigation.action !== "MONITOR_ONLY" && (
                                                                <>
                                                                    {alert.mitigation.action === "AI_VETTING_PENDING" ? (
                                                                        <div className="flex items-center gap-1.5 bg-purple-500/10 border border-purple-500/30 rounded-lg px-2 py-1">
                                                                            <Shield size={10} className="text-purple-400" />
                                                                            <span className="text-[10px] text-purple-300 font-bold uppercase tracking-wider">AI VETTING</span>
                                                                        </div>
                                                                    ) : (
                                                                        <div className="flex items-center gap-1.5 bg-blue-500/10 border border-blue-500/30 rounded-lg px-2 py-1">
                                                                            <div className="w-2 h-2 rounded-full bg-blue-400 animate-pulse" />
                                                                            <span className="text-[10px] text-blue-300 font-bold uppercase tracking-wider">{alert.mitigation.action}</span>
                                                                        </div>
                                                                    )}
                                                                </>
                                                            )}

                                                            {/* ML Score Display */}
                                                            <div className="flex items-center gap-1.5 bg-indigo-500/10 border border-indigo-500/30 rounded-lg px-2 py-1">
                                                                <span className="text-[10px] text-indigo-300 font-semibold uppercase tracking-wider">ML Score:</span>
                                                                <span className="text-xs font-bold text-indigo-200">
                                                                    {alert.ml?.score !== undefined && alert.ml?.score !== null
                                                                        ? alert.ml.score.toFixed(3)
                                                                        : 'N/A'}
                                                                </span>
                                                            </div>
                                                        </div>
                                                    </div>
                                                    {alert.details?.message && (
                                                        <div className="mt-2 text-xs text-slate-400 italic truncate">
                                                            {alert.details.message}
                                                        </div>
                                                    )}
                                                </div>
                                            ))}
                                        </div>
                                    )}
                                </div>
                            );
                        })
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
