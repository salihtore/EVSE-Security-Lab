import React from 'react';
import { Card } from '../ui/Card';
import { Activity, ShieldAlert, Zap, Radio, Target, CheckCircle2, Shield } from 'lucide-react';

function StatCard({ title, value, icon: Icon, colorClass, label }) {
    // Extract base color (e.g., 'text-blue-400' -> 'blue-400') for border/bg usage
    const baseColor = colorClass.split('-')[1];

    return (
        <Card className="flex flex-col justify-between p-3 group hover:border-white/20 transition-all duration-300 bg-slate-900/40 backdrop-blur-md">
            <div className="flex justify-between items-start mb-4">
                <div className={`p-1.5 rounded-lg bg-slate-800/50 border border-white/5 group-hover:bg-slate-800/80 transition-colors`}>
                    <Icon className={colorClass} size={16} />
                </div>
            </div>

            <div>
                <div className="text-xl font-bold text-white tracking-tight leading-none mb-1">{value}</div>
                <div className="text-[9px] uppercase tracking-wider font-semibold text-slate-500 truncate">{title}</div>
            </div>

            {/* Decoration Bar */}
            <div className="mt-4 w-full bg-slate-800 h-1 rounded-full overflow-hidden">
                <div
                    className={`h-full rounded-full opacity-80 ${colorClass.replace('text-', 'bg-')}`}
                    style={{ width: `60%` }}
                />
            </div>
        </Card>
    );
}

export function StatGrid({ stats }) {
    return (
        <div className="grid grid-cols-2 md:grid-cols-3 lg:grid-cols-7 gap-4 mb-8">
            <StatCard
                title="Total Events"
                value={stats.totalEvents}
                icon={Activity}
                colorClass="text-blue-400"
            />
            <StatCard
                title="High Risk Threats"
                value={stats.highRisk}
                icon={ShieldAlert}
                colorClass="text-red-400"
            />
            <StatCard
                title="Active Monitors"
                value={stats.activeMonitors}
                icon={Radio}
                colorClass="text-emerald-400"
            />
            <StatCard
                title="Avg Risk Score"
                value={stats.avgRisk}
                icon={Zap}
                colorClass="text-purple-400"
            />
            <StatCard
                title="ML Accuracy"
                value={`${stats.truePositiveRate}%`}
                icon={Target}
                colorClass="text-cyan-400"
            />
            <StatCard
                title="Actions Taken"
                value={stats.actionsTaken}
                icon={Shield}
                colorClass="text-amber-400"
            />
            <StatCard
                title="Threats Blocked"
                value={stats.threatsMitigated}
                icon={CheckCircle2}
                colorClass="text-emerald-500"
            />
        </div>
    );
}
