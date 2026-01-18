import React from 'react';
import { clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs) {
    return twMerge(clsx(inputs));
}

export function Card({ children, className, ...props }) {
    return (
        <div
            className={cn(
                "relative overflow-hidden rounded-xl border border-white/20 bg-slate-900/60 backdrop-blur-md transition-all duration-300",
                "shadow-2xl shadow-black/80 hover:border-white/30 hover:bg-slate-900/80",
                className
            )}
            {...props}
        >
            <div className="absolute inset-0 bg-gradient-to-br from-cyan-500/5 to-transparent opacity-0 pointer-events-none transition-opacity duration-300 hover:opacity-100" />
            {children}
        </div>
    );
}

export function CardHeader({ title, subtitle, icon: Icon, action }) {
    return (
        <div className="flex items-center justify-between border-b border-white/5 px-6 py-4">
            <div className="flex items-center gap-3">
                {Icon && (
                    <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-cyan-500/20 text-cyan-400 ring-1 ring-cyan-500/30">
                        <Icon size={18} />
                    </div>
                )}
                <div>
                    <h3 className="font-semibold text-slate-100 leading-none">{title}</h3>
                    {subtitle && <p className="mt-1 text-xs text-slate-400">{subtitle}</p>}
                </div>
            </div>
            {action && <div>{action}</div>}
        </div>
    );
}

export function CardContent({ children, className }) {
    return (
        <div className={cn("p-6", className)}>
            {children}
        </div>
    );
}
