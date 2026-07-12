import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useFleetStore } from '../store/useFleetStore';
import { useAuthStore } from '../store/useAuthStore';
import { StatusPill } from '../components/shared/StatusPill';
import { formatCurrency } from '../lib/calculations';
import type { VehicleType, VehicleStatus } from '../types';
import { X } from 'lucide-react';
import { getPermission } from '../lib/rbac';
import { vehicleSchema, VEHICLE_TYPES, type VehicleFormValues } from '../schemas/vehicleSchema';

export const FleetPage: React.FC = () => {
  const { vehicles, addVehicle, isRegNoUnique } = useFleetStore();
  const userRole = useAuthStore(s => s.user?.role);
  const canManageFleet = userRole ? getPermission(userRole, 'fleet') === 'full' : false;
  const [typeFilter, setTypeFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [searchQuery, setSearchQuery] = useState('');
  const [showDialog, setShowDialog] = useState(false);
  const [submitError, setSubmitError] = useState('');

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<VehicleFormValues>({
    resolver: zodResolver(vehicleSchema),
    defaultValues: { regNo: '', name: '', type: 'Van', capacity: '', odometer: '', acquisitionCost: '' },
  });

  const filteredVehicles = vehicles.filter(v => {
    if (typeFilter !== 'All' && v.type !== typeFilter) return false;
    if (statusFilter !== 'All' && v.status !== statusFilter) return false;
    if (searchQuery && !v.regNo.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const onSubmit = (values: VehicleFormValues) => {
    setSubmitError('');
    if (!isRegNoUnique(values.regNo)) {
      setSubmitError('Registration number must be unique.');
      return;
    }
    const cap = Number(values.capacity);
    addVehicle({
      regNo: values.regNo,
      name: values.name,
      type: values.type as VehicleType,
      capacity: cap,
      capacityLabel: cap >= 1000 ? `${cap / 1000} Ton` : `${cap} kg`,
      odometer: Number(values.odometer),
      acquisitionCost: Number(values.acquisitionCost),
      status: 'Available' as VehicleStatus,
    });
    reset();
    setShowDialog(false);
  };

  const inputClass =
    'w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange';
  const labelClass = 'text-[10px] uppercase text-text-faint tracking-wider mb-1 block';
  const fieldErrorClass = 'text-red text-[11px] mt-1';

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Vehicle Registry</h1>

      {/* Filters */}
      <div className="flex gap-2.5 mb-4 flex-wrap items-center">
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          className="bg-panel-2 border border-border text-text-dim py-[7px] px-2.5 rounded-md text-xs outline-none"
        >
          <option value="All">Type: All</option>
          <option value="Van">Van</option>
          <option value="Truck">Truck</option>
          <option value="Mini">Mini</option>
        </select>
        <select
          value={statusFilter}
          onChange={e => setStatusFilter(e.target.value)}
          className="bg-panel-2 border border-border text-text-dim py-[7px] px-2.5 rounded-md text-xs outline-none"
        >
          <option value="All">Status: All</option>
          <option value="Available">Available</option>
          <option value="On Trip">On Trip</option>
          <option value="In Shop">In Shop</option>
          <option value="Retired">Retired</option>
        </select>
        <input
          placeholder="Search reg. no..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="bg-panel-2 border border-border text-text-dim py-[7px] px-2.5 rounded-md text-xs outline-none"
        />
        <div className="flex-1" />
        {canManageFleet && (
          <button
            onClick={() => setShowDialog(true)}
            className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors"
          >
            + Add Vehicle
          </button>
        )}
      </div>

      {/* Table */}
      <div className="bg-panel-2 border border-border rounded-lg p-3.5">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr>
              {['Reg. No. (unique)', 'Name/Model', 'Type', 'Capacity', 'Odometer', 'Acq. Cost', 'Status'].map(h => (
                <th key={h} className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredVehicles.map(v => (
              <tr key={v.id} className="hover:bg-white/[0.02]">
                <td className="py-2.5 px-2 border-b border-border-soft">{v.regNo}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{v.name}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{v.type}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{v.capacityLabel}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(v.odometer)}</td>
                <td className="py-2.5 px-2 border-b border-border-soft">{formatCurrency(v.acquisitionCost)}</td>
                <td className="py-2.5 px-2 border-b border-border-soft"><StatusPill status={v.status} /></td>
              </tr>
            ))}
          </tbody>
        </table>
        <div className="text-red text-[11px] mt-2.5">
          Rule: Registration No. must be unique · Retired/In Shop vehicles are hidden from Trip Dispatcher
        </div>
      </div>

      {/* Add Vehicle Dialog */}
      {canManageFleet && showDialog && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-panel border border-border rounded-lg p-6 w-[420px] max-h-[90vh] overflow-auto">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold">Add Vehicle</h2>
              <button onClick={() => setShowDialog(false)} className="text-text-faint hover:text-text cursor-pointer bg-transparent border-none">
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)}>
              {submitError && (
                <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3 py-2.5 text-xs mb-3">
                  {submitError}
                </div>
              )}

              <div className="flex flex-col gap-3">
                <div>
                  <label className={labelClass}>Registration No.</label>
                  <input {...register('regNo')} className={inputClass} />
                  {errors.regNo && <div className={fieldErrorClass}>{errors.regNo.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Name/Model</label>
                  <input {...register('name')} className={inputClass} />
                  {errors.name && <div className={fieldErrorClass}>{errors.name.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Type</label>
                  <select
                    value={watch('type')}
                    onChange={e => setValue('type', e.target.value as VehicleType, { shouldValidate: true })}
                    className={inputClass}
                  >
                    {VEHICLE_TYPES.map(t => (
                      <option key={t} value={t}>{t}</option>
                    ))}
                  </select>
                  {errors.type && <div className={fieldErrorClass}>{errors.type.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Capacity (kg)</label>
                  <input type="number" {...register('capacity')} className={inputClass} />
                  {errors.capacity && <div className={fieldErrorClass}>{errors.capacity.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Odometer</label>
                  <input type="number" {...register('odometer')} className={inputClass} />
                  {errors.odometer && <div className={fieldErrorClass}>{errors.odometer.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Acquisition Cost</label>
                  <input type="number" {...register('acquisitionCost')} className={inputClass} />
                  {errors.acquisitionCost && <div className={fieldErrorClass}>{errors.acquisitionCost.message}</div>}
                </div>
              </div>

              <div className="flex gap-2.5 mt-4">
                <button type="submit" className="bg-orange text-[#1a0f02] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors">
                  Save Vehicle
                </button>
                <button type="button" onClick={() => setShowDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">
                  Cancel
                </button>
              </div>
            </form>
          </div>
        </div>
      )}
    </div>
  );
};
