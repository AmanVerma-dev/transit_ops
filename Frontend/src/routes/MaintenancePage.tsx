import React from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useMaintenanceStore } from '../store/useMaintenanceStore';
import { useFleetStore } from '../store/useFleetStore';
import { useAuthStore } from '../store/useAuthStore';
import { StatusPill } from '../components/shared/StatusPill';
import { formatCurrency } from '../lib/calculations';
import { getPermission } from '../lib/rbac';
import { serviceRecordSchema, type ServiceRecordFormValues } from '../schemas/serviceRecordSchema';

export const MaintenancePage: React.FC = () => {
  const { logs, addRecord, completeRecord } = useMaintenanceStore();
  const vehicles = useFleetStore(s => s.vehicles);
  const userRole = useAuthStore(s => s.user?.role);
  // Maintenance inherits the fleet permission per getPermission() in rbac.ts.
  const canManageFleet = userRole ? getPermission(userRole, 'fleet') === 'full' : false;

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<ServiceRecordFormValues>({
    resolver: zodResolver(serviceRecordSchema),
    defaultValues: { vehicleId: '', serviceType: '', cost: '', date: '' },
  });

  const onSubmit = (values: ServiceRecordFormValues) => {
    const vehicle = vehicles.find(v => v.id === values.vehicleId);
    addRecord({
      vehicleId: values.vehicleId,
      vehicleName: vehicle?.name || '',
      serviceType: values.serviceType,
      cost: Number(values.cost),
      date: values.date,
      status: 'In Shop',
    });
    reset();
  };

  const inputClass =
    'w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange';
  const labelClass = 'text-[10px] uppercase text-text-faint tracking-wider mb-1 block';
  const fieldErrorClass = 'text-red text-[11px] mt-1';

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Maintenance</h1>

      <div className="grid grid-cols-1 md:grid-cols-[1.6fr_1fr] gap-4">
        {/* Log Service Record */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Log Service Record</div>

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
                <label className={labelClass}>Service Type</label>
                <input {...register('serviceType')} className={inputClass} />
                {errors.serviceType && <div className={fieldErrorClass}>{errors.serviceType.message}</div>}
              </div>
              <div>
                <label className={labelClass}>Cost</label>
                <input type="number" {...register('cost')} className={inputClass} />
                {errors.cost && <div className={fieldErrorClass}>{errors.cost.message}</div>}
              </div>
              <div>
                <label className={labelClass}>Date</label>
                <input {...register('date')} placeholder="MM/DD/YYYY" className={inputClass} />
                {errors.date && <div className={fieldErrorClass}>{errors.date.message}</div>}
              </div>
            </div>

            {canManageFleet && (
              <button
                type="submit"
                className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors mt-3.5"
              >
                Save
              </button>
            )}
          </form>

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
                      {canManageFleet && log.status === 'In Shop' && (
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
