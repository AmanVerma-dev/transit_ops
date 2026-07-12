import React, { useState } from 'react';
import { RBAC_MATRIX } from '../lib/rbac';
import { useSettingsStore } from '../store/useSettingsStore';

export const SettingsPage: React.FC = () => {
  const { depotName, currency, distanceUnit, setDepotName, setCurrency, setDistanceUnit } = useSettingsStore();
  const [saved, setSaved] = useState(false);

  const handleSave = () => {
    setSaved(true);
    setTimeout(() => setSaved(false), 2000);
  };

  const renderPermission = (level: string) => {
    if (level === 'full') return <span className="text-green font-[800]">✓</span>;
    if (level === 'view') return <span className="text-amber text-[10.5px]">view</span>;
    return <span className="text-text-faint">–</span>;
  };

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Settings &amp; RBAC</h1>

      <div className="grid grid-cols-1 md:grid-cols-[1.6fr_1fr] gap-4">
        {/* General Settings */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">General</div>
          <div className="flex flex-col gap-2.5">
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Depot Name</label>
              <input value={depotName} onChange={e => setDepotName(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Currency</label>
              <input value={currency} onChange={e => setCurrency(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Distance Unit</label>
              <input value={distanceUnit} onChange={e => setDistanceUnit(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
          </div>
          <button
            onClick={handleSave}
            className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors mt-3.5"
          >
            {saved ? '✓ Saved!' : 'Save changes'}
          </button>
        </div>

        {/* RBAC Table */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Role-Based Access (RBAC)</div>
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr>
                <th className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Role</th>
                <th className="text-center text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Fleet</th>
                <th className="text-center text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Drivers</th>
                <th className="text-center text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Trips</th>
                <th className="text-center text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Fuel/Exp</th>
                <th className="text-center text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Analytics</th>
              </tr>
            </thead>
            <tbody>
              {RBAC_MATRIX.map(entry => (
                <tr key={entry.role} className="hover:bg-white/[0.02]">
                  <td className="text-left py-2.5 px-2 border-b border-border-soft">{entry.role}</td>
                  <td className="text-center py-2.5 px-2 border-b border-border-soft">{renderPermission(entry.fleet)}</td>
                  <td className="text-center py-2.5 px-2 border-b border-border-soft">{renderPermission(entry.drivers)}</td>
                  <td className="text-center py-2.5 px-2 border-b border-border-soft">{renderPermission(entry.trips)}</td>
                  <td className="text-center py-2.5 px-2 border-b border-border-soft">{renderPermission(entry.fuelExp)}</td>
                  <td className="text-center py-2.5 px-2 border-b border-border-soft">{renderPermission(entry.analytics)}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
