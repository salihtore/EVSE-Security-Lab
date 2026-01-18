import React from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { List, AlertTriangle, CheckCircle, Clock } from 'lucide-react';

const SeverityBadge = ({ level }) => {
    // Dark Mode colors
    const styles = {
        HIGH: "bg-red-500/10 text-red-500 border-red-500/20",
        MEDIUM: "bg-amber-500/10 text-amber-500 border-amber-500/20",
        LOW: "bg-emerald-500/10 text-emerald-500 border-emerald-500/20",
        DEFAULT: "bg-slate-500/10 text-slate-500 border-slate-500/20",
    };

    return (
        <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${styles[level] || styles.DEFAULT} tracking-wide uppercase`}>
            {level}
        </span>
    );
};

export function ActivityFeed({ alerts }) {
    return (
        <Card className="col-span-1 lg:col-span-1 h-[400px] flex flex-col">
            <CardHeader
                title="Recent Alerts"
                subtitle="Live event log"
                icon={List}
                action={<span className="text-xs text-blue-400 font-mono animate-pulse">LIVE</span>}
            />
            <CardContent className="flex-1 overflow-y-auto pr-2 space-y-3 custom-scrollbar">
                {alerts.length === 0 ? (
                    <div className="flex flex-col items-center justify-center h-full text-slate-500">
                        <CheckCircle size={32} className="mb-2 opacity-20" />
                        <p className="text-sm">No active threats</p>
                    </div>
                ) : (
                    alerts.map((alert) => (
                        <div key={alert.event_id} className="group flex items-start gap-3 p-3 rounded-lg bg-white/5 border border-white/5 hover:bg-white/10 transition-colors">
                            <div className={`mt-1 h-2 w-2 rounded-full ${alert.severity === 'HIGH' ? 'bg-red-500 shadow-[0_0_8px_rgba(239,68,68,0.6)]' : 'bg-slate-500'}`} />

                            <div className="flex-1 min-w-0">
                                <div className="flex items-center justify-between mb-1">
                                    <span className="text-sm font-medium text-slate-200 truncate">{alert.anomaly_type}</span>
                                    <SeverityBadge level={alert.severity} />
                                </div>

                                <div className="flex items-center justify-between text-xs text-slate-400">
                                    <span className="font-mono text-slate-500">{alert.cp_id}</span>
                                    <div className="flex items-center gap-1">
                                        <Clock size={10} />
                                        <span>{alert.time}</span>
                                    </div>
                                </div>
                            </div>
                        </div>
                    ))
                )}
            </CardContent>
        </Card>
    );
}
