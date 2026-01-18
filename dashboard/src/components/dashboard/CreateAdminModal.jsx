import React, { useState } from "react";
import { useAdmin } from "../../hooks/useAdmin";

export const CreateAdminModal = ({ isOpen, onClose }) => {
    const [recipient, setRecipient] = useState("");
    const { createAdmin } = useAdmin();
    const [isLoading, setIsLoading] = useState(false);

    if (!isOpen) return null;

    const handleSubmit = (e) => {
        e.preventDefault();
        setIsLoading(true);
        createAdmin(
            recipient,
            () => {
                setIsLoading(false);
                setRecipient("");
                onClose();
                alert("New admin created successfully!");
            },
            (error) => {
                setIsLoading(false);
                alert("Failed to create admin. See console for details.");
            }
        );
    };

    return (
        <div className="fixed inset-0 z-50 flex items-center justify-center bg-black/80 backdrop-blur-sm">
            <div className="bg-[#1e2028] border border-white/10 rounded-lg p-6 w-full max-w-md shadow-xl relative">
                <button
                    onClick={onClose}
                    className="absolute top-4 right-4 text-slate-400 hover:text-white"
                >
                    ✕
                </button>

                <h2 className="text-xl font-bold text-white mb-4">Create New Admin</h2>

                <form onSubmit={handleSubmit} className="space-y-4">
                    <div>
                        <label className="block text-xs font-semibold text-slate-400 mb-1 uppercase tracking-wider">
                            Recipient Address
                        </label>
                        <input
                            type="text"
                            value={recipient}
                            onChange={(e) => setRecipient(e.target.value)}
                            placeholder="0x..."
                            className="w-full bg-slate-900 border border-white/10 rounded px-3 py-2 text-white focus:outline-none focus:border-indigo-500 font-mono text-sm"
                            required
                        />
                    </div>

                    <button
                        type="submit"
                        disabled={isLoading}
                        className="w-full bg-indigo-600 hover:bg-indigo-500 text-white font-bold py-2 px-4 rounded transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
                    >
                        {isLoading ? "Processing..." : "Create Admin"}
                    </button>
                </form>
            </div>
        </div>
    );
};
