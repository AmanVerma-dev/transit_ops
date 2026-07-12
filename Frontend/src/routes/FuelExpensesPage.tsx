import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useFinanceStore } from '../store/useFinanceStore';
import { useMaintenanceStore } from '../store/useMaintenanceStore';
import { useFleetStore } from '../store/useFleetStore';
import { useAuthStore } from '../store/useAuthStore';
import { StatusPill } from '../components/shared/StatusPill';
import { formatCurrency, totalOperationalCost } from '../lib/calculations';
import { X } from 'lucide-react';
import { getPermission } from '../lib/rbac';
import { fuelSchema, type FuelFormValues } from '../schemas/fuelSchema';
import { expenseSchema, type ExpenseFormValues } from '../schemas/expenseSchema';

export const FuelExpensesPage: React.FC = () => {
  const { fuelLogs, expenses, addFuelLog, addExpense } = useFinanceStore();
  const maintenanceLogs = useMaintenanceStore(s => s.logs);
  const vehicles = useFleetStore(s => s.vehicles);
  const userRole = useAuthStore(s => s.user?.role);
  const canManageFuel = userRole ? getPermission(userRole, 'fuelExp') === 'full' : false;

  const [showFuelDialog, setShowFuelDialog] = useState(false);
  const [showExpenseDialog, setShowExpenseDialog] = useState(false);

  const fuelForm = useForm<FuelFormValues>({
    resolver: zodResolver(fuelSchema),
    defaultValues: { vehicleId: '', date: '', liters: '', cost: '' },
  });
  const expenseForm = useForm<ExpenseFormValues>({
    resolver: zodResolver(expenseSchema),
    defaultValues: { tripId: '', vehicleId: '', toll: '', other: '' },
  });

  const opCost = totalOperationalCost(fuelLogs, maintenanceLogs);

  const onAddFuel = (values: FuelFormValues) => {
    const vehicle = vehicles.find(v => v.id === values.vehicleId);
    addFuelLog({
      id: `f${Date.now()}`,
      vehicleId: values.vehicleId,
      vehicleName: vehicle?.name || '',
      date: values.date,
      liters: Number(values.liters),
      cost: Number(values.cost),
    });
    fuelForm.reset();
    setShowFuelDialog(false);
  };

  const onAddExpense = (values: ExpenseFormValues) => {
    const vehicle = vehicles.find(v => v.id === values.vehicleId);
    addExpense({
      tripId: values.tripId,
      vehicleId: values.vehicleId,
      vehicleName: vehicle?.name || '',
      toll: Number(values.toll) || 0,
      other: Number(values.other) || 0,
      maintenanceLinked: 0,
      status: 'Available',
    });
    expenseForm.reset();
    setShowExpenseDialog(false);
  };

  const inputClass =
    'w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange';
  const labelClass = 'text-[10px] uppercase text-text-faint tracking-wider mb-1 block';
  const fieldErrorClass = 'text-red text-[11px] mt-1';

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Fuel &amp; Expense Management</h1>

      {/* Fuel Logs */}
      <div className="bg-panel-2 border border-border rounded-lg p-3.5 mb-4">
        <div className="flex items-center mb-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider font-bold">Fuel Logs</div>
          <div className="flex-1" />
          {canManageFuel && (
            <>
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
            </>
          )}
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
            <form onSubmit={fuelForm.handleSubmit(onAddFuel)}>
              <div className="flex flex-col gap-3">
                <div>
                  <label className={labelClass}>Vehicle</label>
                  <select {...fuelForm.register('vehicleId')} className={inputClass}>
                    <option value="">Select...</option>
                    {vehicles.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                  </select>
                  {fuelForm.formState.errors.vehicleId && <div className={fieldErrorClass}>{fuelForm.formState.errors.vehicleId.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Date</label>
                  <input {...fuelForm.register('date')} placeholder="DD Mon YYYY" className={inputClass} />
                  {fuelForm.formState.errors.date && <div className={fieldErrorClass}>{fuelForm.formState.errors.date.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Liters</label>
                  <input type="number" {...fuelForm.register('liters')} className={inputClass} />
                  {fuelForm.formState.errors.liters && <div className={fieldErrorClass}>{fuelForm.formState.errors.liters.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Cost</label>
                  <input type="number" {...fuelForm.register('cost')} className={inputClass} />
                  {fuelForm.formState.errors.cost && <div className={fieldErrorClass}>{fuelForm.formState.errors.cost.message}</div>}
                </div>
              </div>
              <div className="flex gap-2.5 mt-4">
                <button type="submit" className="bg-orange text-[#1a0f02] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors">Save</button>
                <button type="button" onClick={() => setShowFuelDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">Cancel</button>
              </div>
            </form>
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
            <form onSubmit={expenseForm.handleSubmit(onAddExpense)}>
              <div className="flex flex-col gap-3">
                <div>
                  <label className={labelClass}>Trip ID</label>
                  <input {...expenseForm.register('tripId')} className={inputClass} />
                  {expenseForm.formState.errors.tripId && <div className={fieldErrorClass}>{expenseForm.formState.errors.tripId.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Vehicle</label>
                  <select {...expenseForm.register('vehicleId')} className={inputClass}>
                    <option value="">Select...</option>
                    {vehicles.map(v => <option key={v.id} value={v.id}>{v.name}</option>)}
                  </select>
                  {expenseForm.formState.errors.vehicleId && <div className={fieldErrorClass}>{expenseForm.formState.errors.vehicleId.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Toll</label>
                  <input type="number" {...expenseForm.register('toll')} className={inputClass} />
                  {expenseForm.formState.errors.toll && <div className={fieldErrorClass}>{expenseForm.formState.errors.toll.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Other</label>
                  <input type="number" {...expenseForm.register('other')} className={inputClass} />
                  {expenseForm.formState.errors.other && <div className={fieldErrorClass}>{expenseForm.formState.errors.other.message}</div>}
                </div>
              </div>
              <div className="flex gap-2.5 mt-4">
                <button type="submit" className="bg-orange text-[#1a0f02] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors">Save</button>
                <button type="button" onClick={() => setShowExpenseDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">Cancel</button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
