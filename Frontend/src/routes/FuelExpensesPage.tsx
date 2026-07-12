import React, { useState } from 'react';
import { useFinanceStore } from '../store/useFinanceStore';
import { useMaintenanceStore } from '../store/useMaintenanceStore';
import { useFleetStore } from '../store/useFleetStore';
import { StatusPill } from '../components/shared/StatusPill';
import { formatCurrency, totalOperationalCost } from '../lib/calculations';
import { X } from 'lucide-react';

export const FuelExpensesPage: React.FC = () => {
  const { fuelLogs, expenses, addFuelLog, addExpense } = useFinanceStore();
  const maintenanceLogs = useMaintenanceStore(s => s.logs);
  const vehicles = useFleetStore(s => s.vehicles);

  const [showFuelDialog, setShowFuelDialog] = useState(false);
  const [showExpenseDialog, setShowExpenseDialog] = useState(false);

  // Fuel form
  const [fVehicleId, setFVehicleId] = useState('');
  const [fDate, setFDate] = useState('');
  const [fLiters, setFLiters] = useState('');
  const [fCost, setFCost] = useState('');
  const [fError, setFError] = useState('');

  // Expense form
  const [eTripId, setETripId] = useState('');
  const [eVehicleId, setEVehicleId] = useState('');
  const [eToll, setEToll] = useState('');
  const [eOther, setEOther] = useState('');
  const [eError, setEError] = useState('');

  const opCost = totalOperationalCost(fuelLogs, maintenanceLogs);

  const handleAddFuel = () => {
    setFError('');
    if (!fVehicleId || !fDate || !fLiters || !fCost) { setFError('All fields are required.'); return; }
    const vehicle = vehicles.find(v => v.id === fVehicleId);
    addFuelLog({
      id: `f${Date.now()}`,
      vehicleId: fVehicleId,
      vehicleName: vehicle?.name || '',
      date: fDate,
      liters: parseFloat(fLiters),
      cost: parseInt(fCost),
    });
    setShowFuelDialog(false);
    setFVehicleId(''); setFDate(''); setFLiters(''); setFCost('');
  };

  const handleAddExpense = () => {
    setEError('');
    if (!eTripId || !eVehicleId) { setEError('Trip and Vehicle are required.'); return; }
    const vehicle = vehicles.find(v => v.id === eVehicleId);
    addExpense({
      tripId: eTripId,
      vehicleId: eVehicleId,
      vehicleName: vehicle?.name || '',
      toll: parseInt(eToll) || 0,
      other: parseInt(eOther) || 0,
      maintenanceLinked: 0,
      status: 'Available',
    });
    setShowExpenseDialog(false);
    setETripId(''); setEVehicleId(''); setEToll(''); setEOther('');
  };

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Fuel &amp; Expense Management</h1>

      {/* Fuel Logs */}
      <div className="bg-panel-2 border border-border rounded-lg p-3.5 mb-4">
        <div className="flex items-center mb-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider font-bold">Fuel Logs</div>
          <div className="flex-1" />
          <button
            onClick={() => setShowFuelDialog(true)}
            className="bg-panel-2 text-text-dim border border-border py-2 px-3 rounded-md font-bold text-[12.5px] cursor-pointer hover:text-text transition-colors mr-2"
          >
            + Log Fuel
          </button>
          <button
            onClick={() => setShowExpenseDialog(true)}
            className="bg-orange text-[#1a0f02] border-none py-2 px-3 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors"
          >
            + Add Expense
          </button>
        </div>
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr>
              {['Vehicle', 'Date', 'Liters', 'Cost'].map(h => (
                <th key={h} className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {fuelLogs.map(log => (
              <tr key={log.id} className="hover:bg-white/[0.02]">
                <td className="py-2.5 px-2 border-b border-border-soft">{log.vehicleName}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{log.date}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{log.liters} L</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(log.cost)}</td>
              </tr>
            ))}
          </tbody>
        </table>
      </div>

      {/* Other Expenses */}
      <div className="bg-panel-2 border border-border rounded-lg p-3.5">
        <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Other Expenses (Toll / Misc)</div>
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr>
              {['Trip', 'Vehicle', 'Toll', 'Other', 'Maint. Linked', 'Status'].map(h => (
                <th key={h} className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {expenses.map(exp => (
              <tr key={exp.id} className="hover:bg-white/[0.02]">
                <td className="py-2.5 px-2 border-b border-border-soft">{exp.tripId}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{exp.vehicleName}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(exp.toll)}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(exp.other)}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(exp.maintenanceLinked)}</td>
                <td className="py-2.5 px-2 border-b border-border-soft"><StatusPill status={exp.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>

        {/* Total Operational Cost */}
        <div className="text-right mt-3">
          <span className="text-text-dim text-[13px]">TOTAL OPERATIONAL COST (AUTO) = FUEL + MAINTENANCE</span>
          <b className="text-orange ml-2.5 text-base">{formatCurrency(opCost)}</b>
        </div>
      </div>

      {/* Fuel Dialog */}
      {showFuelDialog && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-panel border border-border rounded-lg p-6 w-[380px]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold">Log Fuel</h2>
              <button onClick={() => setShowFuelDialog(false)} className="text-text-faint hover:text-text cursor-pointer bg-transparent border-none"><X size={16} /></button>
            </div>
            {fError && <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3 py-2.5 text-xs mb-3">{fError}</div>}
            <div className="flex flex-col gap-3">
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Vehicle</label>
                <select value={fVehicleId} onChange={e => setFVehicleId(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange">
                  <option value="">Select...</option>
                  {vehicles.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                </select>
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Date</label>
                <input value={fDate} onChange={e => setFDate(e.target.value)} placeholder="DD Mon YYYY" className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Liters</label>
                <input type="number" value={fLiters} onChange={e => setFLiters(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Cost</label>
                <input type="number" value={fCost} onChange={e => setFCost(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
            </div>
            <div className="flex gap-2.5 mt-4">
              <button onClick={handleAddFuel} className="bg-orange text-[#1a0f02] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors">Save</button>
              <button onClick={() => setShowFuelDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">Cancel</button>
            </div>
          </div>
        </div>
      )}

      {/* Expense Dialog */}
      {showExpenseDialog && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-panel border border-border rounded-lg p-6 w-[380px]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold">Add Expense</h2>
              <button onClick={() => setShowExpenseDialog(false)} className="text-text-faint hover:text-text cursor-pointer bg-transparent border-none"><X size={16} /></button>
            </div>
            {eError && <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3 py-2.5 text-xs mb-3">{eError}</div>}
            <div className="flex flex-col gap-3">
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Trip ID</label>
                <input value={eTripId} onChange={e => setETripId(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Vehicle</label>
                <select value={eVehicleId} onChange={e => setEVehicleId(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange">
                  <option value="">Select...</option>
                  {vehicles.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                </select>
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Toll</label>
                <input type="number" value={eToll} onChange={e => setEToll(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Other</label>
                <input type="number" value={eOther} onChange={e => setEOther(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
            </div>
            <div className="flex gap-2.5 mt-4">
              <button onClick={handleAddExpense} className="bg-orange text-[#1a0f02] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors">Save</button>
              <button onClick={() => setShowExpenseDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">Cancel</button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
