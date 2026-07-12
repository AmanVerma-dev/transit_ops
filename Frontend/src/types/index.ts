// ── Role & Auth ──
export type Role = 'Fleet Manager' | 'Dispatcher' | 'Safety Officer' | 'Financial Analyst';

export interface User {
  name: string;
  email: string;
  role: Role;
  initials: string;
}

// ── Vehicle ──
export type VehicleStatus = 'Available' | 'On Trip' | 'In Shop' | 'Retired';
export type VehicleType = 'Van' | 'Truck' | 'Mini' | 'Bus';

export interface Vehicle {
  id: string;
  regNo: string;
  name: string;
  type: VehicleType;
  capacity: number;      // kg
  capacityLabel: string;  // e.g. "500 kg" or "5 Ton"
  odometer: number;
  acquisitionCost: number;
  status: VehicleStatus;
}

// ── Driver ──
export type DriverStatus = 'Available' | 'On Trip' | 'Off Duty' | 'Suspended';
export type LicenseCategory = 'LMV' | 'HMV';

export interface Driver {
  id: string;
  name: string;
  licenseNo: string;
  category: LicenseCategory;
  licenseExpiry: string;   // MM/YYYY
  contact: string;
  tripCompletion: number;  // percentage
  safetyScore: number;     // percentage
  status: DriverStatus;
}

// ── Trip ──
export type TripStatus = 'Draft' | 'Dispatched' | 'Completed' | 'Cancelled';

export interface Trip {
  id: string;
  source: string;
  destination: string;
  vehicleId: string | null;
  driverId: string | null;
  cargoWeight: number;     // kg
  plannedDistance: number;  // km
  actualDistance?: number;
  fuelConsumed?: number;
  status: TripStatus;
  eta?: string;
  createdAt: string;
}

// ── Maintenance ──
export type MaintenanceStatus = 'In Shop' | 'Completed';

export interface MaintenanceLog {
  id: string;
  vehicleId: string;
  vehicleName: string;
  serviceType: string;
  cost: number;
  date: string;
  status: MaintenanceStatus;
}

// ── Finance ──
export interface FuelLog {
  id: string;
  vehicleId: string;
  vehicleName: string;
  date: string;
  liters: number;
  cost: number;
}

export interface Expense {
  id: string;
  tripId: string;
  vehicleId: string;
  vehicleName: string;
  toll: number;
  other: number;
  maintenanceLinked: number;
  status: string;
}

// ── Settings ──
export interface Settings {
  depotName: string;
  currency: string;
  distanceUnit: string;
}

// ── RBAC Permission ──
export type PermissionLevel = 'full' | 'view' | 'none';

export interface RbacEntry {
  role: Role;
  fleet: PermissionLevel;
  drivers: PermissionLevel;
  trips: PermissionLevel;
  fuelExp: PermissionLevel;
  analytics: PermissionLevel;
}
