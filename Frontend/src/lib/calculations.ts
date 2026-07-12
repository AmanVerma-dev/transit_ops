import type { FuelLog, MaintenanceLog } from '../types';

export function fuelEfficiency(distanceKm: number, liters: number): number {
  if (liters === 0) return 0;
  return Math.round((distanceKm / liters) * 10) / 10;
}

export function fleetUtilization(activeVehicles: number, totalVehicles: number): number {
  if (totalVehicles === 0) return 0;
  return Math.round((activeVehicles / totalVehicles) * 100);
}

export function vehicleROI(
  revenue: number,
  maintenanceCost: number,
  fuelCost: number,
  acquisitionCost: number
): number {
  if (acquisitionCost === 0) return 0;
  return Math.round(((revenue - (maintenanceCost + fuelCost)) / acquisitionCost) * 1000) / 10;
}

export function totalOperationalCost(
  fuelLogs: FuelLog[],
  maintenanceLogs: MaintenanceLog[]
): number {
  const fuelTotal = fuelLogs.reduce((sum, log) => sum + log.cost, 0);
  const maintenanceTotal = maintenanceLogs.reduce((sum, log) => sum + log.cost, 0);
  return fuelTotal + maintenanceTotal;
}

export function formatCurrency(value: number): string {
  return value.toLocaleString('en-IN');
}

export function isLicenseExpired(expiryStr: string): boolean {
  const [monthStr, yearStr] = expiryStr.split('/');
  const month = parseInt(monthStr, 10);
  const year = parseInt(yearStr, 10);
  const now = new Date();
  const expiryDate = new Date(year, month - 1, 1);
  return expiryDate < now;
}

export function padNumber(n: number): string {
  return n.toString().padStart(2, '0');
}
