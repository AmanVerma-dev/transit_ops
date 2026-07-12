import React, { useState } from 'react';
import { useDriversStore } from '../store/useDriversStore';
import { StatusPill } from '../components/shared/StatusPill';
import { isLicenseExpired } from '../lib/calculations';
import type { LicenseCategory, DriverStatus } from '../types';
import { X } from 'lucide-react';

export const DriversPage: React.FC = () => {
  const { drivers, addDriver } = useDriversStore();
  const [searchQuery, setSearchQuery] = useState('');
  const [showDialog, setShowDialog] = useState(false);

  // Form state
  const [formName, setFormName] = useState('');
  const [formLicense, setFormLicense] = useState('');
  const [formCategory, setFormCategory] = useState<LicenseCategory>('LMV');
  const [formExpiry, setFormExpiry] = useState('');
  const [formContact, setFormContact] = useState('');
  const [formError, setFormError] = useState('');

  const filteredDrivers = drivers.filter(d => {
    if (searchQuery && !d.name.toLowerCase().includes(searchQuery.toLowerCase()) &&
        !d.licenseNo.toLowerCase().includes(searchQuery.toLowerCase())) return false;
    return true;
  });

  const handleAddDriver = () => {
    setFormError('');
    if (!formName || !formLicense || !formExpiry || !formContact) {
      setFormError('All fields are required.');
      return;
    }
    // Validate expiry format MM/YYYY
    if (!/^\d{2}\/\d{4}$/.test(formExpiry)) {
      setFormError('License expiry must be in MM/YYYY format.');
      return;
    }
    addDriver({
      name: formName,
      licenseNo: formLicense,
      category: formCategory,
      licenseExpiry: formExpiry,
      contact: formContact,
      tripCompletion: 0,
      safetyScore: 100,
      status: 'Available' as DriverStatus,
    });
    setShowDialog(false);
    setFormName(''); setFormLicense(''); setFormExpiry(''); setFormContact('');
  };

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
        <button
          onClick={() => setShowDialog(true)}
          className="bg-orange text-[#1a0f02] border-none py-2 px-3.5 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors"
        >
          + Add Driver
        </button>
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

            {formError && (
              <div className="border border-red bg-[rgba(226,88,92,0.14)] text-red rounded-lg px-3 py-2.5 text-xs mb-3">
                {formError}
              </div>
            )}

            <div className="flex flex-col gap-3">
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Name</label>
                <input value={formName} onChange={e => setFormName(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">License No.</label>
                <input value={formLicense} onChange={e => setFormLicense(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Category</label>
                <select value={formCategory} onChange={e => setFormCategory(e.target.value as LicenseCategory)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange">
                  <option>LMV</option>
                  <option>HMV</option>
                </select>
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">License Expiry (MM/YYYY)</label>
                <input value={formExpiry} onChange={e => setFormExpiry(e.target.value)} placeholder="MM/YYYY" className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
              <div>
                <label className="text-[10px] uppercase text-text-faint tracking-wider mb-1 block">Contact</label>
                <input value={formContact} onChange={e => setFormContact(e.target.value)} className="w-full bg-bg border border-border text-text py-2 px-2.5 rounded-md text-[12.5px] outline-none focus:border-orange" />
              </div>
            </div>

            <div className="flex gap-2.5 mt-4">
              <button onClick={handleAddDriver} className="bg-orange text-[#1a0f02] border-none py-2 px-4 rounded-md font-bold text-[12.5px] cursor-pointer hover:bg-orange-hover transition-colors">
                Save Driver
              </button>
              <button onClick={() => setShowDialog(false)} className="bg-panel-2 text-text-dim border border-border py-2 px-4 rounded-md text-[12.5px] cursor-pointer hover:text-text transition-colors">
                Cancel
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};
