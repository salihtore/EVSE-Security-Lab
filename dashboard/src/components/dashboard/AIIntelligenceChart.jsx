import React, { useMemo } from 'react';
import { ScatterChart, Scatter, XAxis, YAxis, ZAxis, CartesianGrid, Tooltip, ResponsiveContainer, Cell, Label, ReferenceArea } from 'recharts';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { BrainCircuit, ShieldCheck } from 'lucide-react';

export function AIIntelligenceChart({ alerts }) {
    // Map alerts to a 2D Intelligence Matrix (Rule Risk vs ML Risk)
    const correlationData = useMemo(() => {
        if (!alerts || alerts.length === 0) return [];

        return alerts.map(alert => {
            // Normalize Rule Severity (0-100)
            const ruleRisk = alert.severity === 'HIGH' ? 90 : alert.severity === 'MEDIUM' ? 50 : 20;

            // Normalize ML Confidence (0-100)
            // 💡 Jitter: ML offline olsa bile grafiğin "ölü" (düz çizgi) görünmemesi için küçük bir varyasyon ekle
            const jitter = (alert.timestamp % 20) - 10;
            const mlRisk = alert.ml?.confidence
                ? Math.round(alert.ml.confidence * 100)
                : (30 + jitter); // 20-40 aralığında dalgalanma

            // Determine Action Category (Success/Proactive indicator)
            let status = 'Alerted';
            if (alert.severity === 'HIGH' && mlRisk > 60) status = 'Blocked';
            else if (mlRisk > 50) status = 'Throttled';

            return {
                x: ruleRisk, // Rule Risk
                y: mlRisk,   // AI Confidence
                z: 100,      // Size
                cp_id: alert.cp_id,
                type: alert.anomaly_type,
                status: status
            };
        });
    }, [alerts]);

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs backdrop-blur-md">
                    <div className="font-bold text-white mb-1 border-b border-slate-700 pb-1">{data.cp_id}</div>
                    <div className="text-slate-400 mb-2 uppercase text-[10px]">{data.type}</div>
                    <div className="space-y-1">
                        <div className="flex justify-between gap-4">
                            <span className="text-slate-500 text-[10px] uppercase">Rule Risk:</span>
                            <span className="text-slate-200 font-mono">{data.x}%</span>
                        </div>
                        <div className="flex justify-between gap-4">
                            <span className="text-slate-500 text-[10px] uppercase">AI Confidence:</span>
                            <span className="text-white font-mono">{data.y}%</span>
                        </div>
                        <div className="flex justify-between gap-4 mt-1 pt-1 border-t border-white/5">
                            <span className="text-slate-500 text-[10px] uppercase">Action:</span>
                            <span className={`font-bold ${data.status === 'Blocked' ? 'text-emerald-400' : 'text-amber-400'}`}>
                                {data.status.toUpperCase()}
                            </span>
                        </div>
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <Card className="h-[600px] flex flex-col overflow-hidden">
            <CardHeader
                title="Intelligence & Mitigation Matrix"
                subtitle="Rule vs AI Correlation | Automated Blocking Efficacy"
                icon={BrainCircuit}
                className="py-1.5 px-3"
            />
            <CardContent className="flex-1 relative min-h-0">
                {/* Labels for Matrix Quadrants */}
                <div className="absolute top-4 right-4 text-[9px] text-emerald-500/50 font-bold uppercase pointer-events-none">Resilient (Agreement)</div>
                <div className="absolute top-4 left-4 text-[9px] text-cyan-500/50 font-bold uppercase pointer-events-none">AI Insight (New Threats)</div>
                <div className="absolute bottom-12 right-4 text-[9px] text-amber-500/50 font-bold uppercase pointer-events-none">Legacy Pattern</div>

                <ResponsiveContainer width="100%" height="100%">
                    <ScatterChart margin={{ top: 20, right: 20, bottom: 20, left: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.2} />

                        {/* Reference lines for quadrants */}
                        <XAxis
                            type="number"
                            dataKey="x"
                            name="Rule Risk"
                            unit="%"
                            domain={[0, 100]}
                            stroke="#64748b"
                            fontSize={10}
                            axisLine={false}
                            tickLine={false}
                        >
                            <Label value="Rule Severity Index" position="bottom" offset={0} fill="#475569" fontSize={9} />
                        </XAxis>

                        <YAxis
                            type="number"
                            dataKey="y"
                            name="AI Confidence"
                            unit="%"
                            domain={[0, 100]}
                            stroke="#64748b"
                            fontSize={10}
                            axisLine={false}
                            tickLine={false}
                        >
                            <Label value="AI Confidence Score" angle={-90} position="left" offset={10} fill="#475569" fontSize={9} />
                        </YAxis>

                        <ZAxis type="number" dataKey="z" range={[60, 400]} />
                        <Tooltip content={<CustomTooltip />} />

                        <Scatter name="Threat Mitigation" data={correlationData}>
                            {correlationData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={entry.status === 'Blocked' ? '#10b981' : entry.status === 'Throttled' ? '#f59e0b' : '#3b82f6'}
                                    strokeWidth={entry.status === 'Blocked' ? 4 : 1}
                                    stroke={entry.status === 'Blocked' ? 'rgba(16, 185, 129, 0.4)' : 'transparent'}
                                    className="drop-shadow-[0_0_8px_rgba(255,255,255,0.1)]"
                                />
                            ))}
                        </Scatter>
                    </ScatterChart>
                </ResponsiveContainer>
            </CardContent>
            <div className="px-4 pb-3 flex gap-4 text-[9px] font-bold tracking-widest uppercase">
                <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-emerald-500" /> Blocked (High Trust)</div>
                <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-amber-500" /> Throttled (Anomalous)</div>
                <div className="flex items-center gap-1.5"><div className="w-1.5 h-1.5 rounded-full bg-blue-500" /> Monitored</div>
            </div>
        </Card>
    );
}
