import type { Driver, LicenseCategory, DriverStatus } from '../../types';

export interface BackendDriver {
  id: number;
  name: string;
  license_number: string;
  license_category: string;
  license_expiry_date: string; // ISO date YYYY-MM-DD
  contact_number: string | null;
  safety_score: number;
  status: string;
  user_id: number | null;
  created_at: string;
  updated_at: string;
}

const STATUS_MAP: Record<string, DriverStatus> = {
  AVAILABLE: 'Available',
  ON_TRIP: 'On Trip',
  OFF_DUTY: 'Off Duty',
  SUSPENDED: 'Suspended',
};

const STATUS_MAP_REVERSE: Record<DriverStatus, string> = {
  'Available': 'AVAILABLE',
  'On Trip': 'ON_TRIP',
  'Off Duty': 'OFF_DUTY',
  'Suspended': 'SUSPENDED',
};

/** Convert ISO date "YYYY-MM-DD" to display format "MM/YYYY" */
function isoToMmYyyy(isoDate: string): string {
  const [year, month] = isoDate.split('-');
  return `${month}/${year}`;
}

/** Convert "MM/YYYY" back to ISO date "YYYY-MM-01" for the backend */
export function mmYyyyToIso(mmYyyy: string): string {
  const [month, year] = mmYyyy.split('/');
  return `${year}-${month.padStart(2, '0')}-01`;
}

export function driverToFrontend(b: BackendDriver): Driver {
  return {
    id: String(b.id),
    name: b.name,
    licenseNo: b.license_number,
    category: b.license_category as LicenseCategory,
    licenseExpiry: isoToMmYyyy(b.license_expiry_date),
    contact: b.contact_number || '',
    tripCompletion: 0, // Computed client-side from trip data
    safetyScore: b.safety_score,
    status: STATUS_MAP[b.status] || 'Available',
  };
}

export function driverToBackend(f: Omit<Driver, 'id' | 'tripCompletion'>) {
  return {
    name: f.name,
    license_number: f.licenseNo,
    license_category: f.category,
    license_expiry_date: mmYyyyToIso(f.licenseExpiry),
    contact_number: f.contact || null,
    safety_score: f.safetyScore,
    status: STATUS_MAP_REVERSE[f.status] || 'AVAILABLE',
  };
}
