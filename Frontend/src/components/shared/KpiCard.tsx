import React from 'react';

interface KpiCardProps {
  label: string;
  value: string | number;
  color?: 'green' | 'blue' | 'amber' | 'red' | 'default';
}

const COLOR_MAP = {
  green: 'text-green',
  blue: 'text-blue',
  amber: 'text-amber',
  red: 'text-red',
  default: 'text-text',
};

export const KpiCard: React.FC<KpiCardProps> = ({ label, value, color = 'default' }) => {
  return (
    <div className="bg-panel-2 border border-border rounded-lg p-3 min-w-0">
      <div className="text-[10px] text-text-faint uppercase tracking-wider mb-1.5">
        {label}
      </div>
      <div className={`text-[22px] font-[800] ${COLOR_MAP[color]}`}>
        {value}
      </div>
    </div>
  );
};
