import React, { useMemo } from 'react';
import { BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend, Cell } from 'recharts';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Clock } from 'lucide-react';

export function LiveTrendChart({ data }) {
    // Aggregate attacks by hour of day to show temporal patterns
    const chartData = useMemo(() => {
        if (!data || data.length === 0) return [];

        // Initialize 24-hour buckets
        const hourBuckets = Array.from({ length: 24 }, (_, i) => ({
            hour: i,
            hourLabel: `${String(i).padStart(2, '0')}:00`,
            count: 0,
            highSeverity: 0,
            mediumSeverity: 0,
            lowSeverity: 0
        }));

        // Aggregate anomalies by hour
        data.forEach(alert => {
            if (!alert.timestamp) return;

            const date = new Date(alert.timestamp * 1000);
            const hour = date.getHours();

            hourBuckets[hour].count++;

            // Track severity distribution
            if (alert.severity === 'HIGH') hourBuckets[hour].highSeverity++;
            else if (alert.severity === 'MEDIUM') hourBuckets[hour].mediumSeverity++;
            else hourBuckets[hour].lowSeverity++;
        });

        return hourBuckets;
    }, [data]);

    // Find peak attack hour for highlighting
    const peakHour = useMemo(() => {
        return chartData.reduce((max, curr) => curr.count > max.count ? curr : max, chartData[0]);
    }, [chartData]);

    const CustomTooltip = ({ active, payload }) => {
        if (active && payload && payload.length) {
            const data = payload[0].payload;
            return (
                <div className="bg-slate-900 border border-slate-700 p-3 rounded-lg shadow-xl text-xs">
                    <div className="font-bold text-slate-200 mb-2 border-b border-slate-700 pb-1">
                        {data.hourLabel} - {String((data.hour + 1) % 24).padStart(2, '0')}:00
                    </div>
                    <div className="space-y-1">
                        <div className="flex justify-between gap-4">
                            <span className="text-slate-400">Total Attacks:</span>
                            <span className="text-white font-bold">{data.count}</span>
                        </div>
                        {data.highSeverity > 0 && (
                            <div className="flex justify-between gap-4">
                                <span className="text-red-400">High Severity:</span>
                                <span className="text-red-400 font-bold">{data.highSeverity}</span>
                            </div>
                        )}
                        {data.mediumSeverity > 0 && (
                            <div className="flex justify-between gap-4">
                                <span className="text-amber-400">Medium Severity:</span>
                                <span className="text-amber-400 font-bold">{data.mediumSeverity}</span>
                            </div>
                        )}
                        {data.lowSeverity > 0 && (
                            <div className="flex justify-between gap-4">
                                <span className="text-emerald-400">Low Severity:</span>
                                <span className="text-emerald-400 font-bold">{data.lowSeverity}</span>
                            </div>
                        )}
                    </div>
                </div>
            );
        }
        return null;
    };

    return (
        <Card className="col-span-1 min-h-[400px]">
            <CardHeader
                title="Temporal Attack Pattern Analysis"
                subtitle="Attack frequency by hour - Identify vulnerable time windows"
                icon={Clock}
            />
            <CardContent className="h-[320px]">
                <ResponsiveContainer width="100%" height="100%">
                    <BarChart data={chartData} margin={{ top: 20, right: 20, bottom: 20, left: 10 }}>
                        <CartesianGrid strokeDasharray="3 3" stroke="#334155" opacity={0.3} vertical={false} />
                        <XAxis
                            dataKey="hourLabel"
                            stroke="#94a3b8"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            interval={1}
                            angle={-45}
                            textAnchor="end"
                            height={60}
                        />
                        <YAxis
                            stroke="#94a3b8"
                            fontSize={10}
                            tickLine={false}
                            axisLine={false}
                            label={{ value: 'Attack Count', angle: -90, position: 'insideLeft', fill: '#64748b', fontSize: 10 }}
                        />
                        <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
                        <Legend
                            iconType="circle"
                            wrapperStyle={{ fontSize: '11px', paddingTop: '10px' }}
                            payload={[
                                { value: 'Attack Frequency', type: 'circle', color: '#22d3ee' },
                                { value: `Peak: ${peakHour?.hourLabel} (${peakHour?.count} attacks)`, type: 'circle', color: '#f59e0b' }
                            ]}
                        />

                        <Bar
                            dataKey="count"
                            name="Attacks"
                            radius={[4, 4, 0, 0]}
                        >
                            {chartData.map((entry, index) => (
                                <Cell
                                    key={`cell-${index}`}
                                    fill={entry.hour === peakHour?.hour ? '#f59e0b' : '#22d3ee'}
                                    opacity={entry.count === 0 ? 0.2 : 0.8}
                                />
                            ))}
                        </Bar>
                    </BarChart>
                </ResponsiveContainer>
            </CardContent>
        </Card>
    );
}
