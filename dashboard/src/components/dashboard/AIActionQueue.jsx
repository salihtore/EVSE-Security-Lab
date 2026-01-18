import React from 'react';
import { Card, CardHeader, CardContent } from '../ui/Card';
import { UserCheck, Check, X, ShieldAlert } from 'lucide-react';

export function AIActionQueue() {
    // Mock recommendations awaiting approval
    const pendingActions = [
        { id: 1, cp_id: 'CP_HASAN_VICTIM', action: 'Isolate Session', reason: 'High likelihood of account takeover', risk: 'High' },
        { id: 2, cp_id: 'CP_EMIN', action: 'Refresh Credentials', reason: 'Sequence of Auth Bypass attempts', risk: 'Medium' }
    ];

    return (
        <Card className="h-[132px] flex flex-col overflow-hidden">
            <CardHeader
                title="AI Recommendation Hub"
                subtitle="Actions requiring human verification"
                icon={UserCheck}
                className="py-1 px-3 text-[10px]"
            />
            <CardContent className="flex-1 overflow-y-auto custom-scrollbar p-1 space-y-1">
                {pendingActions.map(action => (
                    <div key={action.id} className="bg-white/5 border border-white/10 rounded-lg p-2 flex items-center justify-between">
                        <div className="flex-1 min-w-0">
                            <div className="flex items-center gap-2 mb-1">
                                <span className="font-bold text-[11px] text-white underline">{action.cp_id}</span>
                                <span className={`text-[8px] px-1 rounded font-bold ${action.risk === 'High' ? 'bg-red-500/20 text-red-300' : 'bg-amber-500/20 text-amber-300'}`}>
                                    {action.risk} RISK
                                </span>
                            </div>
                            <div className="text-[10px] text-slate-200 font-semibold">{action.action}</div>
                            <div className="text-[9px] text-slate-500 truncate">{action.reason}</div>
                        </div>
                        <div className="flex gap-1 ml-2">
                            <button className="p-1 hover:bg-emerald-500/20 text-emerald-500 rounded transition-colors">
                                <Check size={14} />
                            </button>
                            <button className="p-1 hover:bg-rose-500/20 text-rose-500 rounded transition-colors">
                                <X size={14} />
                            </button>
                        </div>
                    </div>
                ))}
            </CardContent>
        </Card>
    );
}
