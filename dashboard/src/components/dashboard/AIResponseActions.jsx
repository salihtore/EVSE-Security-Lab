import React, { useMemo } from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Shield, Ban, Gauge, Bell, Eye, CheckCircle, XCircle } from 'lucide-react';

const ACTION_TYPES = {
    BLOCK: { icon: Ban, color: 'text-red-400', bg: 'bg-red-500/10', border: 'border-red-500/30', label: 'BLOCKED' },
    THROTTLE: { icon: Gauge, color: 'text-amber-400', bg: 'bg-amber-500/10', border: 'border-amber-500/30', label: 'THROTTLED' },
    ALERT: { icon: Bell, color: 'text-blue-400', bg: 'bg-blue-500/10', border: 'border-blue-500/30', label: 'ALERTED' },
    MONITOR: { icon: Eye, color: 'text-emerald-400', bg: 'bg-emerald-500/10', border: 'border-emerald-500/30', label: 'MONITORING' }
};

export function AIResponseActions({ alerts }) {
    // Generate automated actions based on alerts
    const aiActions = useMemo(() => {
        if (!alerts || alerts.length === 0) return [];

        const actions = [];
        const processedCPs = new Set();

        alerts.forEach(alert => {
            // Skip if we already processed this CP
            if (processedCPs.has(alert.cp_id)) return;
            processedCPs.add(alert.cp_id);

            // Determine action based on severity and ML confidence
            let actionType = 'MONITOR';
            let reason = 'Low risk anomaly detected';
            let success = true;

            if (alert.severity === 'HIGH') {
                if (alert.ml?.confidence > 0.7) {
                    actionType = 'BLOCK';
                    reason = `High confidence threat (${Math.round(alert.ml.confidence * 100)}%)`;
                } else {
                    actionType = 'THROTTLE';
                    reason = 'High severity, moderate confidence';
                }
            } else if (alert.severity === 'MEDIUM') {
                if (alert.ml?.confidence > 0.6) {
                    actionType = 'THROTTLE';
                    reason = 'Suspicious pattern detected';
                } else {
                    actionType = 'ALERT';
                    reason = 'Potential anomaly flagged';
                }
            } else {
                actionType = 'MONITOR';
                reason = 'Low severity, monitoring only';
            }

            actions.push({
                id: `action_${alert.event_id}`,
                cp_id: alert.cp_id,
                actionType,
                reason,
                timestamp: alert.timestamp,
                anomalyType: alert.anomaly_type,
                success,
                mlScore: alert.ml?.score,
                confidence: alert.ml?.confidence
            });
        });

        return actions.slice(0, 6); // Show latest 6 actions
    }, [alerts]);

    return (
        <Card className="h-[136px] flex flex-col overflow-hidden">
            <CardHeader
                title="AI Automated Responses"
                subtitle={`${aiActions.length} actions`}
                icon={Shield}
                className="py-1 px-3 text-[10px]"
            />
            <CardContent className="flex-1 overflow-y-auto custom-scrollbar p-1">
                <div className="space-y-1">
                    {aiActions.length === 0 ? (
                        <div className="text-center text-slate-500 py-4 text-sm">No automated actions yet</div>
                    ) : (
                        aiActions.map((action) => {
                            const ActionConfig = ACTION_TYPES[action.actionType];
                            const Icon = ActionConfig.icon;

                            return (
                                <div
                                    key={action.id}
                                    className={`flex items-center justify-between p-1.5 rounded border ${ActionConfig.border} ${ActionConfig.bg} hover:bg-white/5 transition-colors`}
                                >
                                    <div className="flex items-center gap-2 flex-1">
                                        <div className={`p-1 rounded bg-slate-800/50 ${ActionConfig.color}`}>
                                            <Icon size={12} />
                                        </div>

                                        <div className="flex-1 min-w-0">
                                            <div className="flex items-center gap-1 mb-0.5">
                                                <span className="font-bold text-white text-[10px]">{action.cp_id}</span>
                                                <span className={`px-1 py-0.2 rounded text-[8px] font-bold uppercase tracking-wider ${ActionConfig.color} ${ActionConfig.bg} border ${ActionConfig.border}`}>
                                                    {ActionConfig.label}
                                                </span>
                                            </div>
                                            <div className="text-[9px] text-slate-400 truncate">{action.reason}</div>
                                        </div>
                                    </div>

                                    <div className="flex items-center gap-2 ml-2">
                                        <div className="text-right">
                                            <div className="text-[8px] text-slate-500 font-mono">
                                                {new Date(action.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                                            </div>
                                        </div>
                                        {action.success ? (
                                            <CheckCircle className="text-emerald-500" size={12} />
                                        ) : (
                                            <XCircle className="text-red-500" size={12} />
                                        )}
                                    </div>
                                </div>
                            );
                        })
                    )}
                </div>
            </CardContent>
        </Card>
    );
}
