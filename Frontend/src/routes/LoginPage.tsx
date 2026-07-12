import React, { useState, useEffect } from 'react';
import { useNavigate } from 'react-router-dom';
import { useAuthStore } from '../store/useAuthStore';
import { getDefaultRoute } from '../lib/rbac';
import type { Role } from '../types';

export const LoginPage: React.FC = () => {
  const navigate = useNavigate();
  const { isAuthenticated, login } = useAuthStore();

  // Redirect authenticated users away from login
  useEffect(() => {
    if (isAuthenticated) {
      navigate(getDefaultRoute('Dispatcher'), { replace: true });
    }
  }, [isAuthenticated, navigate]);

  const [email, setEmail] = useState('');
  const [password, setPassword] = useState('');
  const [role, setRole] = useState<Role>('Dispatcher');
  const [showError, setShowError] = useState(false);
  const [errorMessage, setErrorMessage] = useState('');
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!email || !password) {
      setErrorMessage('Please enter both email and password.');
      setShowError(true);
      return;
    }
    setShowError(false);
    setIsLoading(true);
    const result = await login(email, password);
    setIsLoading(false);
    if (result.success) {
      navigate('/dashboard');
    } else {
      setErrorMessage(result.error || 'Invalid credentials. Please check your email and password, or contact your admin if your account is locked.');
      setShowError(true);
    }
  };

  return (
    <div className="flex min-h-screen">
      {/* Left cream panel */}
      <div className="flex-1 bg-cream hidden md:flex items-center justify-center">
        <div className="text-center">
          <div className="w-16 h-16 rounded-xl bg-gradient-to-br from-orange to-[#c96a2c] mx-auto mb-4" />
          <div className="text-[#1a1000] text-2xl font-bold">TransitOps</div>
          <div className="text-[#6c6b62] text-sm mt-1">Smart Fleet Management</div>
        </div>
      </div>

      {/* Right dark panel */}
      <div className="w-full md:w-[480px] flex flex-col justify-center px-8 md:px-[60px] bg-bg">
        <div className="flex items-center gap-2.5 mb-1.5">
          <div className="w-[26px] h-[26px] rounded-md bg-gradient-to-br from-orange to-[#c96a2c]" />
          <div className="font-[800] text-xl">TransitOps</div>
        </div>
        <div className="text-text-faint text-xs mb-7">Smart Transport Operations Platform</div>

        <div className="text-lg font-bold mb-1">Sign in to your account</div>
        <div className="text-text-faint text-xs mb-3">Enter your credentials to continue</div>

        {showError && (
          <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3.5 py-3 text-xs mb-4">
            {errorMessage}
          </div>
        )}

        <form onSubmit={handleSubmit}>
          <label className="text-[11px] text-text-faint uppercase tracking-wider block mt-3.5 mb-1.5">
            Email
          </label>
          <input
            type="text"
            placeholder="Ravan.k@transitops.io"
            value={email}
            onChange={e => setEmail(e.target.value)}
            className="w-full bg-panel-2 border border-border text-text py-2.5 px-3 rounded-md text-[13px] outline-none focus:border-orange transition-colors"
          />

          <label className="text-[11px] text-text-faint uppercase tracking-wider block mt-3.5 mb-1.5">
            Password
          </label>
          <input
            type="password"
            placeholder="••••••••"
            value={password}
            onChange={e => setPassword(e.target.value)}
            className="w-full bg-panel-2 border border-border text-text py-2.5 px-3 rounded-md text-[13px] outline-none focus:border-orange transition-colors"
          />

          <label className="text-[11px] text-text-faint uppercase tracking-wider block mt-3.5 mb-1.5">
            Role (RBAC)
          </label>
          <select
            value={role}
            onChange={e => setRole(e.target.value as Role)}
            className="w-full bg-panel-2 border border-border text-text py-2.5 px-3 rounded-md text-[13px] outline-none focus:border-orange transition-colors"
          >
            <option>Dispatcher</option>
            <option>Fleet Manager</option>
            <option>Safety Officer</option>
            <option>Financial Analyst</option>
          </select>

          <div className="flex justify-between items-center my-4 text-xs text-text-dim">
            <label className="flex items-center gap-1.5 cursor-pointer">
              <input
                type="checkbox"
                checked={rememberMe}
                onChange={e => setRememberMe(e.target.checked)}
                className="accent-orange"
              />
              Remember me
            </label>
            <a href="#" className="text-text-faint hover:text-text transition-colors">
              Forgot password?
            </a>
          </div>

          <button
            type="submit"
            disabled={isLoading}
            className="w-full bg-orange text-[#1a0f02] border-none py-3 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {isLoading ? 'Signing in...' : 'Sign In'}
          </button>
        </form>

        <div className="text-xs text-text-dim mt-5 leading-relaxed">
          <div className="font-bold mb-1">One login, four roles:</div>
          <div><span className="text-orange mr-1.5">•</span>Fleet Manager</div>
          <div><span className="text-orange mr-1.5">•</span>Dispatcher</div>
          <div><span className="text-orange mr-1.5">•</span>Safety Officer</div>
          <div><span className="text-orange mr-1.5">•</span>Financial Analyst</div>
        </div>

        <div className="text-text-faint text-[11px] mt-5 leading-[1.8]">
          Access is scoped by role after login:<br />
          • Fleet Manager → Fleet, Maintenance<br />
          • Dispatcher → Dashboard, Trips<br />
          • Safety Officer → Drivers, Compliance<br />
          • Financial Analyst → Fuel &amp; Expenses, Analytics
        </div>

        <div className="text-text-faint text-[10px] mt-10">TRANSITOPS © 2026 · RBAC ENABLED</div>
      </div>
    </div>
  );
};
