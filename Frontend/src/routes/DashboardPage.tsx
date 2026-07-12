import React, { useMemo, useState } from 'react';
import { useFleetStore } from '../store/useFleetStore';
import { useTripsStore } from '../store/useTripsStore';
import { useDriversStore } from '../store/useDriversStore';
import { KpiCard } from '../components/shared/KpiCard';
import { StatusPill } from '../components/shared/StatusPill';
import { padNumber } from '../lib/calculations';

export const DashboardPage: React.FC = () => {
  const vehicles = useFleetStore(s => s.vehicles);
  const trips = useTripsStore(s => s.trips);
  const drivers = useDriversStore(s => s.drivers);

  const [typeFilter, setTypeFilter] = useState('All');
  const [statusFilter, setStatusFilter] = useState('All');
  const [regionFilter, setRegionFilter] = useState('All');

  // KPI computations
  const activeVehicles = vehicles.filter(v => v.status !== 'Retired').length;
  const availableVehicles = vehicles.filter(v => v.status === 'Available').length;
  const inMaintenance = vehicles.filter(v => v.status === 'In Shop').length;
  const activeTrips = trips.filter(t => t.status === 'Dispatched').length;
  const pendingTrips = trips.filter(t => t.status === 'Draft').length;
  const driversOnDuty = drivers.filter(d => d.status === 'On Trip').length;
  const utilization = activeVehicles > 0 ? Math.round(((activeVehicles - availableVehicles) / activeVehicles) * 100) : 0;

  // Filtered trips for table
  const filteredTrips = useMemo(() => {
    return trips.filter(t => {
      if (statusFilter !== 'All' && t.status !== statusFilter) return false;
      return true;
    });
  }, [trips, typeFilter, statusFilter, regionFilter]);

  // Vehicle status percentages
  const total = vehicles.length;
  const statusBars = [
    { label: 'Available', count: availableVehicles, color: 'bg-green', pct: Math.round((availableVehicles / total) * 100) },
    { label: 'On Trip', count: vehicles.filter(v => v.status === 'On Trip').length, color: 'bg-blue', pct: Math.round((vehicles.filter(v => v.status === 'On Trip').length / total) * 100) },
    { label: 'In Shop', count: inMaintenance, color: 'bg-amber', pct: Math.round((inMaintenance / total) * 100) },
    { label: 'Retired', count: vehicles.filter(v => v.status === 'Retired').length, color: 'bg-red', pct: Math.round((vehicles.filter(v => v.status === 'Retired').length / total) * 100) },
  ];

  const getVehicleName = (vehicleId: string | null) => {
    if (!vehicleId) return '—';
    const v = vehicles.find(v => v.id === vehicleId);
    return v?.name || '—';
  };

  const getDriverName = (driverId: string | null) => {
    if (!driverId) return '—';
    const d = drivers.find(d => d.id === driverId);
    return d?.name || '—';
  };

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Dashboard</h1>

      {/* Filters */}
      <div className="flex gap-2.5 mb-4 flex-wrap items-center">
        <select
          value={typeFilter}
          onChange={e => setTypeFilter(e.target.value)}
          className="bg-panel-2 border border-border text-text-dim py-[7px] px-2.5 rounded-md text-xs outline-none"
        >
          <option value="All">Vehicle Type: All</option>
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
          <option value="Draft">Draft</option>
          <option value="Dispatched">Dispatched</option>
          <option value="Completed">Completed</option>
          <option value="Cancelled">Cancelled</option>
        </select>
        <select
          value={regionFilter}
          onChange={e => setRegionFilter(e.target.value)}
          className="bg-panel-2 border border-border text-text-dim py-[7px] px-2.5 rounded-md text-xs outline-none"
        >
          <option value="All">Region: All</option>
        </select>
      </div>

      {/* KPI Row */}
      <div className="grid grid-cols-2 md:grid-cols-4 xl:grid-cols-7 gap-2.5 mb-4">
        <KpiCard label="Active Vehicles" value={padNumber(activeVehicles)} />
        <KpiCard label="Available Vehicles" value={padNumber(availableVehicles)} />
        <KpiCard label="Vehicles in Maintenance" value={padNumber(inMaintenance)} color="amber" />
        <KpiCard label="Active Trips" value={padNumber(activeTrips)} color="blue" />
        <KpiCard label="Pending Trips" value={padNumber(pendingTrips)} />
        <KpiCard label="Drivers On Duty" value={padNumber(driversOnDuty)} />
        <KpiCard label="Fleet Utilization" value={`${utilization}%`} color="green" />
      </div>

      {/* Grid: Recent Trips + Vehicle Status */}
      <div className="grid grid-cols-1 md:grid-cols-[1.6fr_1fr] gap-4">
        {/* Recent Trips */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">
            Recent Trips
          </div>
          <table className="w-full border-collapse text-xs">
            <thead>
              <tr>
                <th className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Trip</th>
                <th className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Vehicle</th>
                <th className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Driver</th>
                <th className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">Status</th>
                <th className="text-left text-text-faint font-semibold uppercase text-[10px] tracking-wider py-2 px-2 border-b border-border">ETA</th>
              </tr>
            </thead>
            <tbody>
              {filteredTrips.slice(0, 6).map(trip => (
                <tr key={trip.id} className="hover:bg-white/[0.02]">
                  <td className="py-2 px-2 border-b border-border-soft">{trip.id}</td>
                  <td className="py-2 px-2 border-b border-border-soft">{getVehicleName(trip.vehicleId)}</td>
                  <td className="py-2 px-2 border-b border-border-soft">{getDriverName(trip.driverId)}</td>
                  <td className="py-2 px-2 border-b border-border-soft"><StatusPill status={trip.status} /></td>
                  <td className="py-2 px-2 border-b border-border-soft text-text-dim">{trip.eta || '—'}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Vehicle Status */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">
            Vehicle Status
          </div>
          {statusBars.map(bar => (
            <div key={bar.label} className="flex items-center gap-2 mb-2.5 text-[11px] text-text-dim">
              <span className="w-[70px]">{bar.label}</span>
              <div className="flex-1 h-[7px] rounded bg-border-soft overflow-hidden">
                <div
                  className={`h-full ${bar.color}`}
                  style={{ width: `${bar.pct}%` }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
