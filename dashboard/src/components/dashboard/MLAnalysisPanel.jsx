import React from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { Brain, Cpu, FileText, CheckCircle2, Clock, Shield } from 'lucide-react';

export function MLAnalysisPanel({ selectedAlert }) {

    if (!selectedAlert) {
        return (
            <Card className="h-full flex items-center justify-center min-h-[200px]">
                <div className="text-center text-slate-500">
                    <Brain className="mx-auto mb-2 opacity-20" size={48} />
                    <p className="text-sm">Select an event group to view ML analysis</p>
                </div>
            </Card>
        );
    }

    const { ml, details, anomaly_type } = selectedAlert;
    // ... rest of the component logic using displayAlert
    const displayAlert = selectedAlert;


    const confidence = ml?.confidence ? Math.round(ml.confidence * 100) : 0;
    const score = ml?.score ? ml.score.toFixed(3) : "N/A";
    const model = ml?.model || "Unknown Model";

    // Determine visuals based on confidence
    const riskColor = confidence > 80 ? 'text-red-500' : confidence > 50 ? 'text-amber-500' : 'text-slate-400';
    const barColor = confidence > 80 ? 'bg-red-500' : confidence > 50 ? 'bg-amber-500' : 'bg-slate-500';

    return (
        <Card className="h-[600px] flex flex-col overflow-hidden">
            <CardHeader
                title="AI Model Interpretation"
                subtitle="Decision Logic"
                icon={Brain}
                className="py-1 px-3 text-[10px]"
            />
            <CardContent className="flex-1 overflow-y-auto custom-scrollbar p-2 space-y-2">
                {/* 1. MODEL & SCORE HEADER */}
                <div className="flex items-center justify-between">
                    <div className="flex items-center gap-2 text-slate-200 text-[10px] bg-white/5 px-2 py-0.5 rounded border border-white/5">
                        <Cpu size={12} className="text-indigo-400" />
                        {model}
                    </div>
                    <div className="text-right">
                        <span className="text-[9px] text-slate-500 font-mono mr-1">SCORE:</span>
                        <span className={`font-bold ${riskColor}`}>{score}</span>
                    </div>
                </div>

                {/* AGREEMENT */}
                <div className="flex items-center justify-between p-1.5 rounded bg-slate-800/40 border border-white/5 text-[9px]">
                    <div className="flex items-center gap-1.5 font-bold">
                        <span className="text-slate-400">CORRELATION:</span>
                        {displayAlert.severity === 'HIGH' && confidence > 60 ? (
                            <span className="text-emerald-400">✓ BOTH</span>
                        ) : displayAlert.severity === 'LOW' && confidence > 60 ? (
                            <span className="text-amber-400">⚠ ML ONLY</span>
                        ) : displayAlert.severity === 'HIGH' && confidence < 40 ? (
                            <span className="text-amber-400">⚠ RULE ONLY</span>
                        ) : (
                            <span className="text-slate-400">PARTIAL</span>
                        )}
                    </div>
                </div>

                {/* 2. CONFIDENCE */}
                <div className="space-y-1">
                    <div className="flex justify-between text-[10px]">
                        <span className="text-slate-400">AI Confidence</span>
                        <span className={`font-bold ${riskColor}`}>{confidence}%</span>
                    </div>
                    <div className="h-1 w-full bg-slate-800 rounded-full overflow-hidden">
                        <div
                            className={`h-full ${barColor} transition-all duration-1000 ease-out`}
                            style={{ width: `${confidence}%` }}
                        />
                    </div>
                </div>

                {/* 3. REASONING */}
                <div className="bg-slate-900/40 rounded p-2 border border-white/5">
                    <div className="flex items-center gap-1.5 mb-1 text-slate-500 uppercase text-[9px] font-bold">
                        <FileText size={10} />
                        Reasoning
                    </div>
                    <p className="text-[10px] text-slate-300 leading-tight">
                        {details?.reason || details?.message || "No detailed reasoning."}
                    </p>
                </div>

                {/* 4. DEFENSE MITIGATION (IPS) */}
                {displayAlert.mitigation && (
                    <div className="bg-blue-500/10 rounded p-2 border border-blue-500/30">
                        <div className="flex items-center justify-between mb-1.5">
                            <div className="flex items-center gap-1.5 text-blue-400 uppercase text-[9px] font-bold">
                                <Shield size={10} />
                                Active Defense (IPS)
                            </div>
                            <span className="text-[9px] bg-blue-500/20 text-blue-300 px-1.5 py-0.5 rounded font-mono">
                                {displayAlert.mitigation.status}
                            </span>
                        </div>
                        <div className="flex items-center gap-2">
                            <div className="w-1.5 h-1.5 rounded-full bg-blue-500 animate-pulse" />
                            <span className="text-sm font-bold text-white tracking-tight">
                                {displayAlert.mitigation.action}
                            </span>
                        </div>
                    </div>
                )}
            </CardContent>
        </Card>
    );
}
