import type { FuelLog, Expense } from '../types';

export const seedFuelLogs: FuelLog[] = [
  {
    id: 'f1',
    vehicleId: 'v1',
    vehicleName: 'VAN-05',
    date: '05 Jul 2026',
    liters: 42,
    cost: 3150,
  },
  {
    id: 'f2',
    vehicleId: 'v2',
    vehicleName: 'TRUCK-11',
    date: '06 Jul 2026',
    liters: 110,
    cost: 8400,
  },
  {
    id: 'f3',
    vehicleId: 'v5',
    vehicleName: 'MINI-08',
    date: '06 Jul 2026',
    liters: 28,
    cost: 2050,
  },
];

export const seedExpenses: Expense[] = [
  {
    id: 'e1',
    tripId: 'TR001',
    vehicleId: 'v1',
    vehicleName: 'VAN-05',
    toll: 120,
    other: 0,
    maintenanceLinked: 0,
    status: 'Available',
  },
  {
    id: 'e2',
    tripId: 'TR002',
    vehicleId: 'v2',
    vehicleName: 'TRK-12',
    toll: 340,
    other: 150,
    maintenanceLinked: 18000,
    status: 'Completed',
  },
];

export const seedMonthlyRevenue = [
  { month: 'Jan', revenue: 220000 },
  { month: 'Feb', revenue: 248000 },
  { month: 'Mar', revenue: 232000 },
  { month: 'Apr', revenue: 280000 },
  { month: 'May', revenue: 264000 },
  { month: 'Jun', revenue: 320000 },
  { month: 'Jul', revenue: 296000 },
];
