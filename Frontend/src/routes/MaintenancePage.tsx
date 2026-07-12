import React, { useState } from 'react';
import { useMaintenanceStore } from '../store/useMaintenanceStore';
import { useFleetStore } from '../store/useFleetStore';
import { StatusPill } from '../components/shared/StatusPill';
import { formatCurrency } from '../lib/calculations';

export const MaintenancePage: React.FC = () => {
  const { logs, addRecord, completeRecord } = useMaintenanceStore();
  const vehicles = useFleetStore(s => s.vehicles);

  const [formVehicleId, setFormVehicleId] = useState('');
  const [formServiceType, setFormServiceType] = useState('');
  const [formCost, setFormCost] = useState('');
  const [formDate, setFormDate] = useState('');
  const [formError, setFormError] = useState('');

  const handleSave = () => {
    setFormError('');
    if (!formVehicleId || !formServiceType || !formCost || !formDate) {
      setFormError('All fields are required.');
      return;
    }
    const vehicle = vehicles.find(v => v.id === formVehicleId);
    addRecord({
      vehicleId: formVehicleId,
      vehicleName: vehicle?.name || '',
      serviceType: formServiceType,
      cost: parseInt(formCost),
      date: formDate,
      status: 'In Shop',
    });
    setFormVehicleId(''); setFormServiceType(''); setFormCost(''); setFormDate('');
  };

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Maintenance</h1>

      <div className="grid grid-cols-[1.6fr_1fr] gap-4">
        {/* Log Service Record */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Log Service Record</div>

          {formError && (
            <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3 py-2.5 text-xs mb-3">
              {formError}
            </div>
          )}

          <div className="flex flex-col gap-2.5">
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Vehicle</label>
              <select value={formVehicleId} onChange={e => setFormVehicleId(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange">
                <option value="">Select vehicle...</option>
                {vehicles.filter(v => v.status !== 'Retired').map(v => (
                  <option key={v.id} value={v.id}>{v.name}</option>
                ))}
              </select>
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Service Type</label>
              <input value={formServiceType} onChange={e => setFormServiceType(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Cost</label>
              <input type="number" value={formCost} onChange={e => setFormCost(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
            <div>
              <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Date</label>
              <input value={formDate} onChange={e => setFormDate(e.target.value)} placeholder="MM/DD/YYYY" className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
            </div>
          </div>

          <button
            onClick={handleSave}
            className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors mt-3.5"
          >
            Save
          </button>

          {/* Status transitions */}
          <div className="mt-5">
            <div className="flex items-center gap-2 text-text-dim text-[11px]">
              Available <span className="text-text-faint">→</span> In Shop
            </div>
            <div className="flex items-center gap-2 text-text-dim text-[11px] mt-1">
              In Shop <span className="text-text-faint">→</span> Available
            </div>
          </div>
          <div className="text-text-faint text-[11px] mt-3">
            Note: In Shop vehicles are removed from the Dispatch pool
          </div>
        </div>

        {/* Service Log */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Service Log</div>
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr>
                {['Vehicle', 'Service', 'Cost', 'Status'].map(h => (
                  <th key={h} className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">{h}</th>
                ))}
              </tr>
            </thead>
            <tbody>
              {logs.map(log => (
                <tr key={log.id} className="hover:bg-white/[0.02]">
                  <td className="py-2.5 px-2 border-b border-border-soft">{log.vehicleName}</td>
                  <td className="py-2.5 px-2 border-b border-border-soft">{log.serviceType}</td>
                  <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(log.cost)}</td>
                  <td className="py-2.5 px-2 border-b border-border-soft">
                    <div className="flex items-center gap-2">
                      <StatusPill status={log.status} />
                      {log.status === 'In Shop' && (
                        <button
                          onClick={() => completeRecord(log.id)}
                          className="bg-green/20 text-green border-none py-0.5 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-green/30"
                        >
                          Complete
                        </button>
                      )}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};
