import React, { useState } from 'react';
import { useLocation, useNavigate } from 'react-router-dom';
import { useAuthStore } from '../../store/useAuthStore';
import { getAccessibleNavItems } from '../../lib/rbac';
import {
  LayoutDashboard,
  Truck,
  Users,
  Route,
  Wrench,
  Fuel,
  BarChart3,
  Settings,
  ChevronLeft,
  ChevronRight,
} from 'lucide-react';

const ICON_MAP: Record<string, React.FC<{ size?: number }>> = {
  LayoutDashboard,
  Truck,
  Users,
  Route,
  Wrench,
  Fuel,
  BarChart3,
  Settings,
};

export const Sidebar: React.FC = () => {
  const location = useLocation();
  const navigate = useNavigate();
  const user = useAuthStore(s => s.user);
  const [collapsed, setCollapsed] = useState(false);

  const navItems = user ? getAccessibleNavItems(user.role) : [];

  return (
    <nav
      className={`${
        collapsed ? 'w-[60px]' : 'w-[212px]'
      } flex-none bg-panel border-r border-border-soft flex flex-col transition-all duration-200 relative`}
    >
      {/* Brand */}
      <div className={`flex items-center gap-2.5 mb-6 ${collapsed ? 'px-3 pt-5' : 'px-4 pt-5'}`}>
        <div className="w-[26px] h-[26px] rounded-md bg-gradient-to-br from-orange to-[#c96a2c] flex-none" />
        {!collapsed && (
          <span className="font-bold text-[15px] tracking-wide">TransitOps</span>
        )}
      </div>

      {/* Nav List */}
      <ul className="list-none m-0 p-0 flex flex-col gap-0.5 px-2">
        {navItems.map(item => {
          const isActive = location.pathname === item.path;
          const Icon = ICON_MAP[item.icon];
          return (
            <li
              key={item.path}
              onClick={() => navigate(item.path)}
              className={`flex items-center gap-3 py-2.5 px-3 rounded-md cursor-pointer text-[13px] border-l-2 transition-colors ${
                isActive
                  ? 'bg-panel-2 text-text border-l-orange font-semibold'
                  : 'text-text-dim border-l-transparent hover:text-text'
              }`}
            >
              {Icon && <Icon size={16} />}
              {!collapsed && <span>{item.label}</span>}
            </li>
          );
        })}
      </ul>

      {/* Collapse toggle */}
      <button
        onClick={() => setCollapsed(!collapsed)}
        className="absolute -right-3 top-20 w-6 h-6 rounded-full bg-panel-2 border border-border flex items-center justify-center cursor-pointer text-text-dim hover:text-text z-10"
      >
        {collapsed ? <ChevronRight size={12} /> : <ChevronLeft size={12} />}
      </button>
    </nav>
  );
};
