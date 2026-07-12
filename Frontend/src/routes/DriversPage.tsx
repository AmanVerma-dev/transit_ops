import React, { useState } from 'react';
import { useForm } from 'react-hook-form';
import { zodResolver } from '@hookform/resolvers/zod';
import { useDriversStore } from '../store/useDriversStore';
import { useAuthStore } from '../store/useAuthStore';
import { StatusPill } from '../components/shared/StatusPill';
import { isLicenseExpired } from '../lib/calculations';
import type { LicenseCategory, DriverStatus } from '../types';
import { X } from 'lucide-react';
import { getPermission } from '../lib/rbac';
import { driverSchema, LICENSE_CATEGORIES, type DriverFormValues } from '../schemas/driverSchema';

export const DriversPage: React.FC = () => {
  const { drivers, addDriver } = useDriversStore();
  const userRole = useAuthStore(s => s.user?.role);
  const canManageDrivers = userRole ? getPermission(userRole, 'drivers') === 'full' : false;
  const [searchQuery, setSearchQuery] = useState('');
  const [showDialog, setShowDialog] = useState(false);

  const {
    register,
    handleSubmit,
    reset,
    setValue,
    watch,
    formState: { errors },
  } = useForm<DriverFormValues>({
    resolver: zodResolver(driverSchema),
    defaultValues: { name: '', licenseNo: '', category: 'LMV', licenseExpiry: '', contact: '' },
  });

  const filteredDrivers = drivers.filter(d => {
    if (searchQuery && !d.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !d.licenseNo.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const onSubmit = (values: DriverFormValues) => {
    addDriver({
      name: values.name,
      licenseNo: values.licenseNo,
      category: values.category as LicenseCategory,
      licenseExpiry: values.licenseExpiry,
      contact: values.contact,
      tripCompletion: 0,
      safetyScore: 100,
      status: 'Available' as DriverStatus,
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
      <h1 className="text-base font-bold mb-4">Drivers &amp; Safety Profiles</h1>

      {/* Filters */}
      <div className="flex gap-2.5 mb-4 flex-wrap items-center">
        <input
          placeholder="Search..."
          value={searchQuery}
          onChange={e => setSearchQuery(e.target.value)}
          className="bg-panel-2 border border-border text-text-dim py-[7px] px-2.5 rounded-md text-xs outline-none"
        />
        <div className="flex-1" />
        {canManageDrivers && (
          <button
            onClick={() => setShowDialog(true)}
            className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors"
          >
            + Add Driver
          </button>
        )}
      </div>

      {/* Table */}
      <div className="bg-panel-2 border border-border rounded-lg p-3.5">
        <table className="w-full border-collapse text-xs">
          <thead>
            <tr>
              {['Driver', 'License No.', 'Category', 'Expiry', 'Contact', 'Trip Compl.', 'Safety', 'Status'].map(h => (
                <th key={h} className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">{h}</th>
              ))}
            </tr>
          </thead>
          <tbody>
            {filteredDrivers.map(d => {
              const expired = isLicenseExpired(d.licenseExpiry);
              return (
                <tr key={d.id} className="hover:bg-white/[0.02]">
                  <td className="py-2.5 px-2 border-b border-border-soft">{d.name}</td>
                  <td className="py-2.5 px-2 border-b border-border-soft">{d.licenseNo}</td>
                  <td className="py-2.5 px-2 border-b border-border-soft">{d.category}</td>
                  <td className={`py-2.5 px-2 border-b border-border-soft ${expired ? 'text-red' : ''}`}>
                    {d.licenseExpiry}{expired ? ' EXPIRED' : ''}
                  </td>
                  <td className="py-2.5 px-2 border-b border-border-soft">{d.contact}</td>
                  <td className="py-2.5 px-2 border-b border-border-soft">{d.tripCompletion}%</td>
                  <td className="py-2.5 px-2 border-b border-border-soft">{d.safetyScore}%</td>
                  <td className="py-2.5 px-2 border-b border-border-soft"><StatusPill status={d.status} /></td>
                </tr>
              );
            })}
          </tbody>
        </table>

        {/* Status legend */}
        <div className="mt-3.5 flex gap-2">
          <StatusPill status="Available" />
          <StatusPill status="On Trip" />
          <StatusPill status="Off Duty" />
          <StatusPill status="Suspended" />
        </div>
        <div className="text-red text-[11px] mt-2.5">
          Rule: Expired license or Suspended status → blocked from trip assignment
        </div>
      </div>

      {/* Add Driver Dialog */}
      {showDialog && (
        <div className="fixed inset-0 bg-black/60 flex items-center justify-center z-50">
          <div className="bg-panel border border-border rounded-lg p-6 w-[420px]">
            <div className="flex justify-between items-center mb-4">
              <h2 className="text-sm font-bold">Add Driver</h2>
              <button onClick={() => setShowDialog(false)} className="text-text-faint hover:text-text cursor-pointer bg-transparent border-none">
                <X size={16} />
              </button>
            </div>

            <form onSubmit={handleSubmit(onSubmit)}>
              <div className="flex flex-col gap-3">
                <div>
                  <label className={labelClass}>Name</label>
                  <input {...register('name')} className={inputClass} />
                  {errors.name && <div className={fieldErrorClass}>{errors.name.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>License No.</label>
                  <input {...register('licenseNo')} className={inputClass} />
                  {errors.licenseNo && <div className={fieldErrorClass}>{errors.licenseNo.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Category</label>
                  <select
                    value={watch('category')}
                    onChange={e => setValue('category', e.target.value as LicenseCategory, { shouldValidate: true })}
                    className={inputClass}
                  >
                    {LICENSE_CATEGORIES.map(c => (
                      <option key={c} value={c}>{c}</option>
                    ))}
                  </select>
                  {errors.category && <div className={fieldErrorClass}>{errors.category.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>License Expiry (MM/YYYY)</label>
                  <input {...register('licenseExpiry')} placeholder="MM/YYYY" className={inputClass} />
                  {errors.licenseExpiry && <div className={fieldErrorClass}>{errors.licenseExpiry.message}</div>}
                </div>
                <div>
                  <label className={labelClass}>Contact</label>
                  <input {...register('contact')} className={inputClass} />
                  {errors.contact && <div className={fieldErrorClass}>{errors.contact.message}</div>}
                </div>
              </div>

              <div className="flex gap-2.5 mt-4">
                <button type="submit" className="bg-orange text-[#1a0f02] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors">
                  Save Driver
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
