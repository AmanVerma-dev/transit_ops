import React from 'react';

type PillColor = 'green' | 'blue' | 'amber' | 'red';

const STATUS_COLOR_MAP: Record<string, PillColor> = {
  // Green
  'Available': 'green',
  'Completed': 'green',
  'Active': 'green',
  // Blue
  'On Trip': 'blue',
  'Dispatched': 'blue',
  'In Progress': 'blue',
  // Amber
  'In Shop': 'amber',
  'Suspended': 'amber',
  'Draft': 'amber',
  'Off Duty': 'amber',
  'Scheduled': 'amber',
  // Red
  'Retired': 'red',
  'Cancelled': 'red',
  'Expired': 'red',
};

const PILL_STYLES: Record<PillColor, string> = {
  green: 'bg-[rgba(63,191,114,0.14)] text-green',
  blue: 'bg-[rgba(77,144,226,0.16)] text-blue',
  amber: 'bg-[rgba(224,165,60,0.16)] text-amber',
  red: 'bg-[rgba(226,88,92,0.14)] text-red',
};

interface StatusPillProps {
  status: string;
  className?: string;
}

export const StatusPill: React.FC<StatusPillProps> = ({ status, className = '' }) => {
  const color = STATUS_COLOR_MAP[status] || 'amber';
  return (
    <span
      className={`inline-block px-2.5 py-[3px] rounded-xl text-[11px] font-bold ${PILL_STYLES[color]} ${className}`}
    >
      {status}
    </span>
  );
};
