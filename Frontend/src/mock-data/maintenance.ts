import type { MaintenanceLog } from '../types';

export const seedMaintenance: MaintenanceLog[] = [
  {
    id: 'm1',
    vehicleId: 'v1',
    vehicleName: 'VAN-05',
    serviceType: 'Oil Change',
    cost: 2500,
    date: '07/01/2026',
    status: 'In Shop',
  },
  {
    id: 'm2',
    vehicleId: 'v2',
    vehicleName: 'TRUCK-11',
    serviceType: 'Engine Repair',
    cost: 18000,
    date: '06/25/2026',
    status: 'Completed',
  },
  {
    id: 'm3',
    vehicleId: 'v3',
    vehicleName: 'MINI-03',
    serviceType: 'Tyre Replace',
    cost: 6200,
    date: '07/03/2026',
    status: 'In Shop',
  },
];
