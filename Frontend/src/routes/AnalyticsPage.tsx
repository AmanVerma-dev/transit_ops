import React from 'react';
import { useFleetStore } from '../store/useFleetStore';
import { useTripsStore } from '../store/useTripsStore';
import { useFinanceStore } from '../store/useFinanceStore';
import { useMaintenanceStore } from '../store/useMaintenanceStore';
import { KpiCard } from '../components/shared/KpiCard';
import {
  fuelEfficiency,
  fleetUtilization,
  vehicleROI,
  totalOperationalCost,
  formatCurrency,
} from '../lib/calculations';
import { exportToCsv } from '../lib/csvExport';
import { seedMonthlyRevenue } from '../mock-data/finance';
import {
  BarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
} from 'recharts';
import { Download } from 'lucide-react';

export const AnalyticsPage: React.FC = () => {
  const vehicles = useFleetStore(s => s.vehicles);
  const trips = useTripsStore(s => s.trips);
  const fuelLogs = useFinanceStore(s => s.fuelLogs);
  const maintenanceLogs = useMaintenanceStore(s => s.logs);

  // Calculations
  const totalDistance = trips
    .filter(t => t.status === 'Completed')
    .reduce((sum, t) => sum + (t.actualDistance || t.plannedDistance), 0);
  const totalLiters = fuelLogs.reduce((sum, f) => sum + f.liters, 0);
  const efficiency = fuelEfficiency(totalDistance, totalLiters);

  const activeVehicles = vehicles.filter(v => v.status !== 'Retired').length;
  const utilization = fleetUtilization(
    vehicles.filter(v => v.status !== 'Retired' && v.status !== 'Available').length,
    activeVehicles
  );

  const opCost = totalOperationalCost(fuelLogs, maintenanceLogs);

  const totalRevenue = seedMonthlyRevenue.reduce((s, m) => s + m.revenue, 0);
  const totalAcqCost = vehicles.reduce((s, v) => s + v.acquisitionCost, 0);
  const fuelCostTotal = fuelLogs.reduce((s, f) => s + f.cost, 0);
  const maintCostTotal = maintenanceLogs.reduce((s, m) => s + m.cost, 0);
  const roi = vehicleROI(totalRevenue, maintCostTotal, fuelCostTotal, totalAcqCost);

  // Top costliest vehicles
  const vehicleCosts = vehicles.map(v => {
    const fuel = fuelLogs.filter(f => f.vehicleId === v.id).reduce((s, f) => s + f.cost, 0);
    const maint = maintenanceLogs.filter(m => m.vehicleId === v.id).reduce((s, m) => s + m.cost, 0);
    return { name: v.name, cost: fuel + maint };
  }).sort((a, b) => b.cost - a.cost).slice(0, 3);

  const maxCost = vehicleCosts[0]?.cost || 1;
  const barColors = ['#e2585c', '#e0a53c', '#4d90e2'];

  const handleExport = () => {
    const reportData = trips.map(t => ({
      TripID: t.id,
      Source: t.source,
      Destination: t.destination,
      Status: t.status,
      PlannedDistance: t.plannedDistance,
      CargoWeight: t.cargoWeight,
    }));
    exportToCsv('transitops-report', reportData);
  };

  return (
    <div>
      <h1 className="text-base font-bold mb-4">Reports &amp; Analytics</h1>

      {/* KPI Row */}
      <div className="grid grid-cols-4 gap-2.5 mb-1">
        <KpiCard label="Fuel Efficiency" value={`${efficiency} km/l`} color="blue" />
        <KpiCard label="Fleet Utilization" value={`${utilization}%`} color="green" />
        <KpiCard label="Operational Cost" value={formatCurrency(opCost)} color="amber" />
        <KpiCard label="Vehicle ROI" value={`${roi}%`} />
      </div>
      <div className="text-[10.5px] text-text-faint mb-3.5 ml-0.5">
        ROI = (Revenue − (Maintenance + Fuel)) / Acquisition Cost
      </div>

      <div className="grid grid-cols-[1.6fr_1fr] gap-4">
        {/* Monthly Revenue Chart */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="flex justify-between items-center mb-3">
            <div className="text-xs text-text-dim uppercase tracking-wider font-bold">Monthly Revenue</div>
            <button
              onClick={handleExport}
              className="flex items-center gap-1.5 bg-panel-2 text-text-dim border border-border py-1.5 px-3 rounded-md text-[11px] cursor-pointer hover:text-text transition-colors"
            >
              <Download size={12} /> Export CSV
            </button>
          </div>
          <ResponsiveContainer width="100%" height={160}>
            <BarChart data={seedMonthlyRevenue}>
              <CartesianGrid strokeDasharray="3 3" stroke="#26262b" />
              <XAxis
                dataKey="month"
                tick={{ fill: '#6c6b72', fontSize: 10 }}
                axisLine={{ stroke: '#26262b' }}
              />
              <YAxis
                tick={{ fill: '#6c6b72', fontSize: 10 }}
                axisLine={{ stroke: '#26262b' }}
                tickFormatter={(v: number) => `${v / 1000}k`}
              />
              <Tooltip
                contentStyle={{
                  background: '#17171b',
                  border: '1px solid #26262b',
                  borderRadius: 6,
                  fontSize: 12,
                  color: '#e9e8e6',
                }}
              />
              <Bar
                dataKey="revenue"
                fill="url(#blueGrad)"
                radius={[4, 4, 0, 0]}
              />
              <defs>
                <linearGradient id="blueGrad" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="0%" stopColor="#5b9de0" />
                  <stop offset="100%" stopColor="#4d90e2" />
                </linearGradient>
              </defs>
            </BarChart>
          </ResponsiveContainer>
        </div>

        {/* Top Costliest Vehicles */}
        <div className="bg-panel-2 border border-border rounded-lg p-3.5">
          <div className="text-xs text-text-dim uppercase tracking-wider mb-3 font-bold">Top Costliest Vehicles</div>
          {vehicleCosts.map((vc, i) => (
            <div key={vc.name} className="flex items-center gap-2 mb-2.5 text-[11px] text-text-dim">
              <div className="w-16 flex-none">{vc.name}</div>
              <div className="flex-1 h-3.5 bg-border-soft rounded overflow-hidden">
                <div
                  className="h-full"
                  style={{
                    width: `${(vc.cost / maxCost) * 100}%`,
                    backgroundColor: barColors[i] || '#4d90e2',
                  }}
                />
              </div>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
};
