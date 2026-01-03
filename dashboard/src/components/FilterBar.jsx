import React from 'react';

const theme = {
    inputBg: "rgba(0, 0, 0, 0.3)",
    border: "rgba(255, 255, 255, 0.1)",
    text: "#f1f5f9",
    placeholder: "#64748b"
};

export const FilterBar = ({ onSearch, onTypeFilter, onSeverityFilter, filters }) => {
    return (
        <div style={{
            display: 'flex',
            gap: '10px',
            padding: '10px 15px',
            borderBottom: `1px solid ${theme.border}`,
            background: "rgba(30, 41, 59, 0.4)",
            flexWrap: 'wrap'
        }}>
            {/* Search Input */}
            <input
                type="text"
                placeholder="Search CP ID..."
                value={filters.search}
                onChange={(e) => onSearch(e.target.value)}
                style={{
                    padding: '6px 12px',
                    borderRadius: '4px',
                    border: `1px solid ${theme.border}`,
                    background: theme.inputBg,
                    color: theme.text,
                    outline: 'none',
                    fontSize: '11px',
                    minWidth: '120px'
                }}
            />

            {/* Severity Filter */}
            <select
                value={filters.severity}
                onChange={(e) => onSeverityFilter(e.target.value)}
                style={{
                    padding: '6px',
                    borderRadius: '4px',
                    border: `1px solid ${theme.border}`,
                    background: theme.inputBg,
                    color: theme.text,
                    outline: 'none',
                    fontSize: '11px',
                    cursor: 'pointer'
                }}
            >
                <option value="ALL">All Severities</option>
                <option value="HIGH">HIGH</option>
                <option value="MEDIUM">MEDIUM</option>
                <option value="LOW">LOW</option>
            </select>

            {/* Anomaly Type Filter - Genelde sunucudan gelir ama şimdilik statik yaygın tipler */}
            <select
                value={filters.type}
                onChange={(e) => onTypeFilter(e.target.value)}
                style={{
                    padding: '6px',
                    borderRadius: '4px',
                    border: `1px solid ${theme.border}`,
                    background: theme.inputBg,
                    color: theme.text,
                    outline: 'none',
                    fontSize: '11px',
                    cursor: 'pointer'
                }}
            >
                <option value="ALL">All Types</option>
                <option value="AUTH_FAILURE">Auth Failure</option>
                <option value="REPLAY_ATTACK">Replay Attack</option>
                <option value="ENERGY_SPIKE">Energy Spike</option>
                <option value="UNAUTHORIZED_ACCESS">Unauthorized</option>
            </select>
        </div>
    );
};
