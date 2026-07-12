import type { Vehicle, VehicleType, VehicleStatus } from '../../types';

// Backend response shape from GET /vehicles
export interface BackendVehicle {
  id: number;
  registration_number: string;
  name_model: string;
  type: string;
  max_load_capacity_kg: number;
  odometer_km: number;
  acquisition_cost: number;
  status: string;
  region?: string | null;
  created_at: string;
  updated_at: string;
}

const STATUS_MAP: Record<string, VehicleStatus> = {
  AVAILABLE: 'Available',
  ON_TRIP: 'On Trip',
  IN_SHOP: 'In Shop',
  RETIRED: 'Retired',
};

const STATUS_MAP_REVERSE: Record<VehicleStatus, string> = {
  'Available': 'AVAILABLE',
  'On Trip': 'ON_TRIP',
  'In Shop': 'IN_SHOP',
  'Retired': 'RETIRED',
};

function deriveCapacityLabel(kg: number): string {
  return kg >= 1000 ? `${kg / 1000} Ton` : `${kg} kg`;
}

export function vehicleToFrontend(b: BackendVehicle): Vehicle {
  return {
    id: String(b.id),
    regNo: b.registration_number,
    name: b.name_model,
    type: b.type as VehicleType,
    capacity: b.max_load_capacity_kg,
    capacityLabel: deriveCapacityLabel(b.max_load_capacity_kg),
    odometer: b.odometer_km,
    acquisitionCost: b.acquisition_cost,
    status: STATUS_MAP[b.status] || 'Available',
    region: b.region ?? undefined,
  };
}

export function vehicleToBackend(f: Omit<Vehicle, 'id' | 'capacityLabel'>) {
  return {
    registration_number: f.regNo,
    name_model: f.name,
    type: f.type,
    max_load_capacity_kg: f.capacity,
    odometer_km: f.odometer,
    acquisition_cost: f.acquisitionCost,
    status: STATUS_MAP_REVERSE[f.status] || 'AVAILABLE',
    region: f.region ?? null,
  };
}
