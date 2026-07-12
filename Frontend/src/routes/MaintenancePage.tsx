import React, { useState, useEffect } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMaintenanceStore } from '../store/useMaintenanceStore';
import { useFleetStore } from '../store/useFleetStore';
import { useAuthStore } from '../store/useAuthStore';
import { StatusPill } from '../components/shared/StatusPill';
import { formatCurrency } from '../lib/calculations';
import { getPermission } from '../lib/rbac';
import { serviceRecordSchema, MAINTENANCE_TYPES, type ServiceRecordFormValues } from '../schemas/serviceRecordSchema';
import type { MaintenanceType } from '../types';
import { X } from 'lucide-react';

export const MaintenancePage: React.FC = () => {
  const { logs, isLoading, fetchMaintenance, addRecord, startRecord, completeRecord } = useMaintenanceStore();
  const { vehicles, fetchVehicles } = useFleetStore();
  const userRole = useAuthStore(s => s.user?.role);
  // Maintenance inherits the fleet permission per getPermission() in rbac.ts.
  const canManageFleet = userRole ? getPermission(userRole, 'fleet') === 'full' : false;

  const [submitError, setSubmitError] = useState('');
  const [showCompleteDialog, setShowCompleteDialog] = useState(false);
  const [completingRecordId, setCompletingRecordId] = useState('');
  const [actualCost, setActualCost] = useState('');

  useEffect(() => {
    fetchVehicles();
    fetchMaintenance();
  }, [fetchVehicles, fetchMaintenance]);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ServiceRecordFormValues>({
    resolver: zodResolver(serviceRecordSchema),
    defaultValues: { vehicleId: '', maintenanceType: 'Preventive', serviceType: '', estimatedCost: '', technicianNotes: '' },
  });

  const onSubmit = async (values: ServiceRecordFormValues) => {
    setSubmitError('');
    try {
      await addRecord({
        vehicleId: values.vehicleId,
        maintenanceType: values.maintenanceType as MaintenanceType,
        serviceType: values.serviceType,
        estimatedCost: Number(values.estimatedCost),
        technicianNotes: values.technicianNotes,
      });
      reset();
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to schedule maintenance.');
    }
  };

  const handleStart = async (id: string) => {
    setSubmitError('');
    try {
      await startRecord(id);
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to start maintenance.');
    }
  };

  const handleComplete = (id: string) => {
    setCompletingRecordId(id);
    setActualCost('');
    setShowCompleteDialog(true);
  };

  const handleCompleteSubmit = async () => {
    if (!actualCost) return;
    setSubmitError('');
    try {
      await completeRecord(completingRecordId, Number(actualCost));
      setShowCompleteDialog(false);
    } catch (err: any) {
      setSubmitError(err.message || 'Failed to complete maintenance.');
      setShowCompleteDialog(false);
    }
  };

  const inputClass =
    'w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange';
  const labelClass = 'text-[10px] uppercase text-text-faint tracking-wider mb-1 block';
  const fieldErrorClass = 'text-red text-[11px] mt-1';

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Maintenance {isLoading && <span className="text-xs font-normal text-text-faint ml-2">(Loading...)</span>}</h1>

      {submitError && (
        <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3.5 py-3 text-xs mb-4 whitespace-pre-line">
          {submitError}
        </div>
      )}

      <div className="grid grid-cols-1 md:grid-cols-[1.6fr_1fr] gap-4">
        {/* Log Service Record */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Schedule Service Record</div>

          <form onSubmit={handleSubmit(onSubmit)}>
            <div className="flex flex-col gap-2.5">
              <div>
                <label className={labelClass}>Vehicle</label>
                <select
                  value={watch('vehicleId')}
                  onChange={e => setValue('vehicleId', e.target.value, { shouldValidate: true })}
                  className={inputClass}
                >
                  <option value="">Select vehicle...</option>
                  {vehicles.filter(v => v.status !== 'Retired').map(v => (
                    <option key={v.id} value={v.id}>{v.name}</option>
                  ))}
                </select>
                {errors.vehicleId && <div className={fieldErrorClass}>{errors.vehicleId.message}</div>}
              </div>
              <div>
                <label className={labelClass}>Maintenance Type</label>
                <select
                  value={watch('maintenanceType')}
                  onChange={e => setValue('maintenanceType', e.target.value as MaintenanceType, { shouldValidate: true })}
                  className={inputClass}
                >
                  {MAINTENANCE_TYPES.map(t => (
                    <option key={t} value={t}>{t}</option>
                  ))}
                </select>
                {errors.maintenanceType && <div className={fieldErrorClass}>{errors.maintenanceType.message}</div>}
              </div>
              <div>
                <label className={labelClass}>Service Type / Description</label>
                <input {...register('serviceType')} className={inputClass} />
                {errors.serviceType && <div className={fieldErrorClass}>{errors.serviceType.message}</div>}
              </div>
              <div>
                <label className={labelClass}>Estimated Cost</label>
                <input type="number" {...register('estimatedCost')} className={inputClass} />
                {errors.estimatedCost && <div className={fieldErrorClass}>{errors.estimatedCost.message}</div>}
              </div>
              <div>
                <label className={labelClass}>Technician Notes (Optional)</label>
                <textarea {...register('technicianNotes')} className={`${inputClass} min-h-[60px] resize-y`} />
              </div>
            </div>

            {canManageFleet && (
              <button
                type="submit"
                className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors mt-3.5"
              >
                Schedule Service
              </button>
            )}
          </form>

          {/* Status transitions */}
          <div className="mt-5">
            <div className="flex items-center gap-2 text-text-dim text-[11px]">
              Available <span className="text-text-faint">→</span> Scheduled
            </div>
            <div className="flex items-center gap-2 text-text-dim text-[11px] mt-1">
              Scheduled <span className="text-text-faint">→</span> In Progress (In Shop)
            </div>
            <div className="flex items-center gap-2 text-text-dim text-[11px] mt-1">
              In Progress <span className="text-text-faint">→</span> Completed (Available)
            </div>
          </div>
          <div className="text-text-faint text-[11px] mt-3">
            Note: In Shop vehicles are removed from the Dispatch pool
          </div>
        </div>

        {/* Service Log */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Service Log</div>
          <div className="overflow-x-auto">
            <table className="w-full border-collapse text-xs">
              <thead>
                <tr>
                  {['Date', 'Vehicle', 'Type', 'Cost', 'Status'].map(h => (
                    <th key={h} className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">{h}</th>
                  ))}
                </tr>
              </thead>
              <tbody>
                {logs.map(log => (
                  <tr key={log.id} className="hover:bg-white/[0.02]">
                    <td className="py-2.5 px-2 border-b border-border-soft">{log.date}</td>
                    <td className="py-2.5 px-2 border-b border-border-soft font-medium">{log.vehicleName}</td>
                    <td className="py-2.5 px-2 border-b border-border-soft">{log.maintenanceType}</td>
                    <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(log.cost)}</td>
                    <td className="py-2.5 px-2 border-b border-border-soft">
                      <div className="flex flex-col gap-1 items-start">
                        <StatusPill status={log.status} />
                        {canManageFleet && log.status === 'Scheduled' && (
                          <button
                            onClick={() => handleStart(log.id)}
                            className="bg-blue/20 text-blue border-none py-0.5 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-blue/30 w-full"
                          >
                            Start
                          </button>
                        )}
                        {canManageFleet && log.status === 'In Progress' && (
                          <button
                            onClick={() => handleComplete(log.id)}
                            className="bg-green/20 text-green border-none py-0.5 px-2 rounded text-[10px] font-bold cursor-pointer hover:bg-green/30 w-full"
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

      {/* Complete Maintenance Dialog */}
      {showCompleteDialog && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-panel border border-border rounded-lg p-6 w-[380px]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold">Complete Service Record</h2>
              <button onClick={() => setShowCompleteDialog(false)} className="text-text-faint hover:text-text cursor-pointer bg-transparent border-none">
                <X size={16} />
              </button>
            </div>
            <div className="flex flex-col gap-3">
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Actual Cost</label>
                <input type="number" value={actualCost} onChange={e => setActualCost(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
            </div>
            <div className="flex gap-2.5 mt-4">
              <button
                onClick={handleCompleteSubmit}
                disabled={!actualCost}
                className="bg-green text-[#0a1f10] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:opacity-90 transition-colors disabled:opacity-50"
              >
                Complete Service
              </button>
              <button onClick={() => setShowCompleteDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
