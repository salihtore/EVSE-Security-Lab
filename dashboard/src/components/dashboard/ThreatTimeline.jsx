import React, { useMemo } from 'react';
import { LineChart, Line, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, ReferenceDot } from 'recharts';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { TrendingUp, ShieldAlert, CheckCircle } from 'lucide-react';

export function ThreatTimeline({ alerts }) {
    // Transform alerts into a time-series of risk scores for the most active CPs
    const timelineData = useMemo(() => {
        if (!alerts || alerts.length === 0) return [];

        // Sort by time
        const sorted = [...alerts].sort((a, b) => a.timestamp - b.timestamp);

        // We'll show the aggregate risk level over time (rolling window-ish)
        // or just individual events mapped to time
        const dataMap = sorted.map(alert => {
            const riskValue = alert.severity === 'HIGH' ? 90 : alert.severity === 'MEDIUM' ? 60 : 30;
            const mlBoost = alert.ml?.confidence ? (alert.ml.confidence * 10) : 0;
            const jitter = (alert.timestamp % 10) - 5; // ±5 jitter

            return {
                time: new Date(alert.timestamp * 1000).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' }),
                timestamp: alert.timestamp,
                risk: Math.max(10, riskValue + mlBoost + jitter),
                cp_id: alert.cp_id,
                action: alert.severity === 'HIGH' ? 'AI Intervened' : null
            };
        });

        return dataMap;
    }, [alerts]);

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-slate-900/90 border border-slate-700 p-2 rounded text-[10px] backdrop-blur-md">
                    <div className="text-white font-bold mb-1">{data.cp_id}</div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-400">Time:</span>
                        <span className="text-slate-200">{data.time}</span>
                    </div>
                    <div className="flex justify-between gap-4">
                        <span className="text-slate-400">Risk Level:</span>
                        <span className="text-red-400 font-bold">{Math.round(data.risk)}</span>
                    </div>
                    {data.action && (
                        <div className="mt-1 text-emerald-400 font-bold uppercase tracking-wider">
                            🛡️ {data.action}
                        </div>
                    )}
                </div>
            );
        }
        return null;
    };

    return (
        <Card className="h-[600px] flex flex-col overflow-hidden">
            <CardHeader
                title="Threat Evolution & Defense"
                subtitle="Real-time threat level vs. AI intervention points"
                icon={TrendingUp}
                className="py-1.5 px-3"
            />
            <CardContent className="flex-1 min-h-0 p-2">
                <ResponsiveContainer width="100%" height="100%">
                    <LineChart data={timelineData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" vertical={false} opacity={0.3} />
                        <XAxis
                            dataKey="time"
                            stroke="#64748b"
                            fontSize={9}
                            tickLine={false}
                            axisLine={false}
                            interval="preserveStartEnd"
                        />
                        <YAxis
                            stroke="#64748b"
                            fontSize={9}
                            tickLine={false}
                            axisLine={false}
                            domain={[0, 110]}
                        />
                        <Tooltip content={<CustomTooltip />} />
                        <Legend iconType="circle" wrapperStyle={{ fontSize: '9px', paddingBottom: '10px' }} />

                        <Line
                            type="monotone"
                            dataKey="risk"
                            name="Threat Intensity"
                            stroke="#f43f5e"
                            strokeWidth={2}
                            dot={{ r: 3, fill: '#f43f5e', strokeWidth: 0 }}
                            activeDot={{ r: 5, strokeWidth: 0 }}
                        />

                        {/* Intervention Markers */}
                        {timelineData.filter(d => d.action).map((d, i) => (
                            <ReferenceDot
                                key={i}
                                x={d.time}
                                y={d.risk}
                                r={6}
                                fill="#10b981"
                                stroke="none"
                                className="animate-pulse"
                            />
                        ))}
                    </LineChart>
                </ResponsiveContainer>
                <div className="mt-2 flex items-center gap-4 text-[9px] uppercase tracking-widest text-slate-500 font-bold px-2">
                    <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-rose-500" /> Threat Peak</div>
                    <div className="flex items-center gap-1"><div className="w-2 h-2 rounded-full bg-emerald-500" /> AI Response</div>
                </div>
            </CardContent>
        </Card>
    );
}
