import React from 'react';
import { useAuthStore } from '../../store/useAuthStore';
import { Search } from 'lucide-react';

export const Topbar: React.FC = () => {
  const user = useAuthStore(s => s.user);

  return (
    <div className="h-[52px] border-b border-border-soft flex items-center justify-between px-5 bg-bg">
      {/* Search */}
      <div className="relative">
        <Search size={14} className="absolute left-3 top-1/2 -translate-y-1/2 text-text-faint" />
        <input
          type="text"
          placeholder="Search..."
          className="bg-panel-2 border border-border rounded-md py-[7px] pl-9 pr-3 text-text-dim text-[12.5px] w-[260px] outline-none focus:border-orange transition-colors"
        />
      </div>

      {/* User chip */}
      <div className="flex items-center gap-2">
        <span className="text-[12.5px] text-text-dim">
          {user?.name || 'Guest'}
        </span>
        <span className="bg-panel-2 border border-border text-text-dim px-2.5 py-1 rounded-xl text-[11px]">
          {user?.role || 'Unknown'}
        </span>
        <div className="w-[26px] h-[26px] rounded-full bg-orange text-[#1a1000] flex items-center justify-center text-[11px] font-bold">
          {user?.initials || '??'}
        </div>
      </div>
    </div>
  );
};
