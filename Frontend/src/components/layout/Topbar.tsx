import React, { useState, useRef, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';
import { Search, LogOut, ChevronDown } from 'lucide-react';

export const Topbar: React.FC = () => {
  const user = useAuthStore(s => s.user);
  const logout = useAuthStore(s => s.logout);
  const navigate = useNavigate();
  const [showDropdown, setShowDropdown] = useState(false);
  const dropdownRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    function handleClickOutside(event: MouseEvent) {
      if (dropdownRef.current && !dropdownRef.current.contains(event.target as Node)) {
        setShowDropdown(false);
      }
    }
    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  const handleLogout = () => {
    logout();
    setShowDropdown(false);
    navigate('/login', { replace: true });
  };

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

      {/* User chip with dropdown */}
      <div className="flex items-center gap-2 relative" ref={dropdownRef}>
        <span className="text-[12.5px] text-text-dim">
          {user?.name || 'Guest'}
        </span>
        <span className="bg-panel-2 border border-border text-text-dim px-2.5 py-1 rounded-xl text-[11px]">
          {user?.role || 'Unknown'}
        </span>
        <div className="w-[26px] h-[26px] rounded-full bg-orange text-[#1a1000] flex items-center justify-center text-[11px] font-bold cursor-pointer"
             onClick={() => setShowDropdown(!showDropdown)}>
          {user?.initials || '??'}
          <ChevronDown size={10} className="ml-1" />
        </div>

        {showDropdown && (
          <div className="absolute right-0 top-full mt-2 w-40 bg-panel-2 border border-border rounded-md shadow-lg z-50 py-1">
            <button
              onClick={handleLogout}
              className="w-full text-left px-3 py-2 text-[12.5px] text-text hover:bg-panel hover:text-orange transition-colors flex items-center gap-2"
            >
              <LogOut size={14} />
              Log out
            </button>
          </div>
        )}
      </div>
    </div>
  );
};
