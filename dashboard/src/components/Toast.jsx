import React, { useEffect } from 'react';

const theme = {
    danger: "#f43f5e",
    text: "#f1f5f9",
    bg: "#1e293b",
    border: "rgba(255, 255, 255, 0.1)"
};

export const Toast = ({ message, onClose }) => {
    useEffect(() => {
        const timer = setTimeout(() => {
            onClose();
        }, 5000);
        return () => clearTimeout(timer);
    }, [onClose]);

    return (
        <div style={{
            position: 'fixed',
            bottom: '20px',
            right: '20px',
            background: theme.bg,
            borderLeft: `4px solid ${theme.danger}`,
            borderTop: `1px solid ${theme.border}`,
            borderRight: `1px solid ${theme.border}`,
            borderBottom: `1px solid ${theme.border}`,
            padding: '15px 20px',
            borderRadius: '4px',
            boxShadow: '0 4px 12px rgba(0,0,0,0.5)',
            zIndex: 9999,
            display: 'flex',
            alignItems: 'center',
            gap: '15px',
            animation: 'slideIn 0.3s ease-out'
        }}>
            <div style={{ fontSize: '20px' }}>🚨</div>
            <div>
                <h4 style={{ margin: 0, color: theme.danger, fontSize: '14px', marginBottom: '4px' }}>SECURITY ALERT</h4>
                <p style={{ margin: 0, color: theme.text, fontSize: '12px' }}>{message}</p>
            </div>
            <button
                onClick={onClose}
                style={{
                    background: 'transparent',
                    border: 'none',
                    color: '#888',
                    fontSize: '16px',
                    cursor: 'pointer',
                    marginLeft: '10px'
                }}
            >
                ✕
            </button>
            <style>{`
                @keyframes slideIn {
                    from { transform: translateX(100%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
            `}</style>
        </div>
    );
};
