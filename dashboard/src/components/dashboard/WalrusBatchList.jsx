import React, { useState, useEffect } from "react";
import { Database, Lock, Clock, CheckCircle, ExternalLink, HardDrive, Waves } from "lucide-react";

export const WalrusBatchList = () => {
    const [batches, setBatches] = useState([]);
    const [loading, setLoading] = useState(true);

    const fetchHistory = async () => {
        try {
            const res = await fetch("http://localhost:8000/walrus/history");
            if (res.ok) {
                const data = await res.json();
                setBatches(data);
            }
        } catch (err) {
            console.error("Failed to fetch Walrus history:", err);
        } finally {
            setLoading(false);
        }
    };

    useEffect(() => {
        fetchHistory();
        // Poll every 10 seconds to respond quickly during tests
        const interval = setInterval(fetchHistory, 10000);
        return () => clearInterval(interval);
    }, []);

    const formatTime = (ts) => {
        const date = new Date(ts * 1000);
        return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
    };

    const formatSize = (kb) => {
        return kb ? `${kb} KB` : "0 KB";
    };

    return (
        <div className="h-[1212px] flex flex-col bg-[#0f172a]/40 backdrop-blur-md rounded-xl border border-white/5 shadow-xl relative overflow-hidden group">
            {/* Decorative Gradient Line (Top) */}
            <div className="absolute top-0 inset-x-0 h-[1px] bg-gradient-to-r from-transparent via-cyan-500/50 to-transparent opacity-50" />

            {/* Header */}
            <div className="p-4 border-b border-white/5 flex items-center justify-between bg-white/5 relative z-10">
                <div className="flex items-center gap-2">
                    <div className="w-8 h-8 rounded-lg bg-cyan-900/20 border border-cyan-500/20 flex items-center justify-center">
                        <Waves size={16} className="text-cyan-400" />
                    </div>
                    <div>
                        <h3 className="text-slate-200 font-bold text-sm tracking-wide">Walrus Archives</h3>
                        <div className="text-[10px] text-cyan-400 font-mono flex items-center gap-1">
                            <span className="w-1.5 h-1.5 rounded-full bg-cyan-500 animate-pulse" />
                            Testnet Synced
                        </div>
                    </div>
                </div>
                <div className="text-[10px] text-slate-500 font-black tracking-widest opacity-60">
                    IMMUTABLE
                </div>
            </div>

            {/* Content */}
            <div className="flex-1 overflow-y-auto custom-scrollbar p-0 space-y-[1px]">
                {loading && batches.length === 0 ? (
                    <div className="p-8 text-center space-y-3">
                        <div className="w-8 h-8 border-2 border-cyan-500/30 border-t-cyan-500 rounded-full animate-spin mx-auto" />
                        <div className="text-slate-500 text-xs">Syncing Chain Data...</div>
                    </div>
                ) : batches.length === 0 ? (
                    <div className="p-8 text-center">
                        <div className="w-12 h-12 bg-slate-800/50 rounded-full flex items-center justify-center mx-auto mb-3">
                            <HardDrive size={20} className="text-slate-600" />
                        </div>
                        <p className="text-slate-400 text-xs">No archives found yet.</p>
                        <p className="text-slate-600 text-[10px] mt-1">Batches are created every 30 mins.</p>
                    </div>
                ) : (
                    batches.map((batch, idx) => (
                        <div
                            key={batch.id || idx}
                            className="group/item relative p-3 hover:bg-white/5 transition-all duration-300 border-l-2 border-transparent hover:border-cyan-500"
                        >
                            <div className="flex items-start justify-between mb-1">
                                <div className="flex items-center gap-2">
                                    <span className="text-xs font-mono text-cyan-300">{formatTime(batch.timestamp)}</span>
                                    <span className="px-1.5 py-0.5 rounded text-[9px] font-bold bg-cyan-500/10 text-cyan-400 border border-cyan-500/20">
                                        TRAINING_DATA
                                    </span>
                                </div>
                                <div className="flex items-center text-emerald-400 text-[10px] gap-1 font-bold">
                                    <CheckCircle size={10} />
                                    STORED
                                </div>
                            </div>

                            <div className="grid grid-cols-2 gap-2 mt-2">
                                <div className="bg-slate-950/30 rounded p-1.5 border border-white/5">
                                    <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-0.5">Records</div>
                                    <div className="text-xs text-slate-300 font-mono">{batch.record_count} items</div>
                                </div>
                                <div className="bg-slate-950/30 rounded p-1.5 border border-white/5">
                                    <div className="text-[9px] text-slate-500 uppercase tracking-wider mb-0.5">Size</div>
                                    <div className="text-xs text-slate-300 font-mono">{formatSize(batch.size_kb)}</div>
                                </div>
                            </div>

                            <div className="mt-2 flex items-center gap-2 p-1.5 rounded border border-indigo-500/10 bg-indigo-500/5 group-hover/item:border-indigo-500/20 transition-colors">
                                <Lock size={10} className="text-indigo-400" />
                                <div className="text-[10px] font-mono text-indigo-300 truncate w-full" title={batch.blob_id}>
                                    {batch.blob_id}
                                </div>
                                <a href={`https://walrusscan.com/testnet/blob/${batch.blob_id}`} target="_blank" rel="noopener noreferrer" className="ml-auto text-indigo-400 hover:text-indigo-200">
                                    <ExternalLink size={10} />
                                </a>
                            </div>
                        </div>
                    ))
                )}
            </div>

            {/* Footer Stat */}
            <div className="p-3 border-t border-white/5 bg-slate-950/50 text-[10px] text-slate-500 flex justify-between items-center">
                <span className="flex items-center gap-1">
                    <Clock size={10} />
                    Next Batch: ~10 min
                </span>
                <span>Total: {batches.length}</span>
            </div>
        </div>
    );
};
