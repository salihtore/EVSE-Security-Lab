import React, { useState } from "react";
import { ConnectButton, useCurrentAccount, useDisconnectWallet, useResolveSuiNSName } from "@mysten/dapp-kit";
import { formatAddress } from "@mysten/sui/utils";
import { LogOut, Copy, Check, ChevronDown } from "lucide-react";

const SlushIcon = ({ className }) => (
    <svg viewBox="0 0 24 24" fill="none" className={className} xmlns="http://www.w3.org/2000/svg">
        <path d="M12 22C17.5228 22 22 17.5228 22 12C22 6.47715 17.5228 2 12 2C6.47715 2 2 6.47715 2 12C2 17.5228 6.47715 22 12 22Z" fill="url(#paint0_radial)" fillOpacity="0.2" />
        <path d="M12.0001 5.5C10.2001 8.5 8.50009 10 7.50009 12C6.50009 14 7.50009 16.5 9.50009 17.5C11.5001 18.5 14.0001 18 15.5001 16.5C17.0001 15 17.5001 12.5 15.5001 10.5C13.5001 8.5 13.0001 6.5 12.0001 5.5Z" fill="url(#paint1_linear)" stroke="white" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round" />
        <defs>
            <radialGradient id="paint0_radial" cx="0" cy="0" r="1" gradientUnits="userSpaceOnUse" gradientTransform="translate(12 12) rotate(90) scale(10)">
                <stop stopColor="#3B82F6" />
                <stop offset="1" stopColor="#3B82F6" stopOpacity="0" />
            </radialGradient>
            <linearGradient id="paint1_linear" x1="12" y1="5.5" x2="12" y2="18" gradientUnits="userSpaceOnUse">
                <stop stopColor="#60A5FA" />
                <stop offset="1" stopColor="#2563EB" />
            </linearGradient>
        </defs>
    </svg>
);

export const CustomConnectButton = () => {
    const currentAccount = useCurrentAccount();
    const { mutate: disconnect } = useDisconnectWallet();
    const { data: suinsName } = useResolveSuiNSName({ address: currentAccount?.address });
    const [isOpen, setIsOpen] = useState(false);
    const [copied, setCopied] = useState(false);

    const handleCopy = (e) => {
        e.stopPropagation();
        if (currentAccount?.address) {
            navigator.clipboard.writeText(currentAccount.address);
            setCopied(true);
            setTimeout(() => setCopied(false), 2000);
        }
    };

    if (!currentAccount) {
        return (
            <div className="custom-connect-wrapper">
                <ConnectButton
                    className="!bg-indigo-600/20 !hover:bg-indigo-600/30 !text-indigo-300 !border !border-indigo-500/30 !rounded-lg !font-bold !text-xs !py-2 !px-4 !transition-all !tracking-wide hover:!shadow-[0_0_15px_rgba(99,102,241,0.3)] flex items-center gap-2"
                    connectText={
                        <div className="flex items-center gap-2">
                            <SlushIcon className="w-5 h-5 animate-pulse" />
                            <span>CONNECT WALLET</span>
                        </div>
                    }
                />
                {/* CSS Hack to override ConnectButton internal styles if className isn't enough */}
                <style>{`
          .custom-connect-wrapper button {
             background: rgba(79, 70, 229, 0.1) !important;
             border: 1px solid rgba(99, 102, 241, 0.3) !important;
             color: #a5b4fc !important;
             border-radius: 0.5rem !important;
             font-family: inherit !important;
             font-weight: 700 !important;
             font-size: 0.75rem !important;
             letter-spacing: 0.05em !important;
             transition: all 0.2s !important;
             height: 38px !important;
             display: flex !important;
             align-items: center !important;
             justify-content: center !important;
          }
          .custom-connect-wrapper button:hover {
             background: rgba(79, 70, 229, 0.25) !important;
             box-shadow: 0 0 15px rgba(99,102,241,0.2) !important;
             transform: translateY(-1px);
          }
        `}</style>
            </div>
        );
    }

    // Connected State
    return (
        <div className="relative font-mono">
            <button
                onClick={() => setIsOpen(!isOpen)}
                className="flex items-center gap-3 bg-[#1e2028] hover:bg-[#252832] border border-white/10 hover:border-indigo-500/30 rounded-lg py-1.5 px-3 transition-all duration-200 group"
            >
                <div className="relative">
                    <SlushIcon className="w-8 h-8 drop-shadow-[0_0_8px_rgba(59,130,246,0.3)]" />
                    <div className="absolute -bottom-0.5 -right-0.5 w-2.5 h-2.5 bg-emerald-500 border-2 border-[#1e2028] rounded-full animate-pulse" />
                </div>

                <div className="flex flex-col items-start gap-0.5 text-left">
                    <span className="text-[10px] text-slate-400 font-bold uppercase tracking-wider">Connected</span>
                    <div className="flex items-center gap-2">
                        <span className="text-sm font-bold text-slate-200 group-hover:text-white transition-colors">
                            {suinsName || formatAddress(currentAccount.address)}
                        </span>
                        <ChevronDown size={12} className={`text-slate-500 transition-transform ${isOpen ? 'rotate-180' : ''}`} />
                    </div>
                </div>
            </button>

            {/* Dropdown Menu */}
            {isOpen && (
                <>
                    <div className="fixed inset-0 z-40" onClick={() => setIsOpen(false)} />
                    <div className="absolute right-0 top-full mt-2 w-56 bg-[#161820] border border-white/10 rounded-xl shadow-2xl p-1 z-50 backdrop-blur-xl animate-in fade-in zoom-in-95 duration-200">
                        <div className="px-3 py-2 border-b border-white/5 mb-1">
                            <div className="text-[10px] text-slate-500 font-black uppercase tracking-wider mb-1">Active Account</div>
                            <div className="text-xs text-white break-all font-mono opacity-80">
                                {currentAccount.address.slice(0, 20)}...
                            </div>
                        </div>

                        <button
                            onClick={handleCopy}
                            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold text-slate-400 hover:text-white hover:bg-white/5 rounded-lg transition-colors group"
                        >
                            {copied ? <Check size={14} className="text-emerald-500" /> : <Copy size={14} className="group-hover:text-indigo-400" />}
                            {copied ? "Copied Address" : "Copy Address"}
                        </button>

                        <button
                            onClick={() => { disconnect(); setIsOpen(false); }}
                            className="w-full flex items-center gap-2 px-3 py-2 text-xs font-semibold text-red-400 hover:text-red-300 hover:bg-red-500/10 rounded-lg transition-colors mt-1"
                        >
                            <LogOut size={14} />
                            Disconnect Wallet
                        </button>
                    </div>
                </>
            )}
        </div>
    );
};
