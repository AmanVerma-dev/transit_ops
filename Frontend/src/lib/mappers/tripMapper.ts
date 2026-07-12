import type { Trip, TripStatus } from '../../types';

export interface BackendTrip {
  id: number;
  source: string;
  destination: string;
  vehicle_id: number;
  driver_id: number;
  cargo_weight_kg: number;
  planned_distance_km: number;
  status: string;
  dispatched_at: string | null;
  completed_at: string | null;
  cancelled_at: string | null;
  final_odometer: number | null;
  fuel_consumed_liters: number | null;
  revenue: number | null;
  created_by: number;
  created_at: string;
  updated_at: string;
}

const STATUS_MAP: Record<string, TripStatus> = {
  DRAFT: 'Draft',
  DISPATCHED: 'Dispatched',
  COMPLETED: 'Completed',
  CANCELLED: 'Cancelled',
};

export function tripToFrontend(b: BackendTrip): Trip {
  return {
    id: String(b.id),
    source: b.source,
    destination: b.destination,
    vehicleId: String(b.vehicle_id),
    driverId: String(b.driver_id),
    cargoWeight: b.cargo_weight_kg,
    plannedDistance: b.planned_distance_km,
    actualDistance: b.final_odometer != null ? b.planned_distance_km : undefined,
    fuelConsumed: b.fuel_consumed_liters ?? undefined,
    revenue: b.revenue ?? undefined,
    status: STATUS_MAP[b.status] || 'Draft',
    createdAt: b.created_at.split('T')[0],
  };
}

export function tripCreateToBackend(f: {
  source: string;
  destination: string;
  vehicleId: string;
  driverId: string;
  cargoWeight: number;
  plannedDistance: number;
}) {
  return {
    source: f.source,
    destination: f.destination,
    vehicle_id: parseInt(f.vehicleId, 10),
    driver_id: parseInt(f.driverId, 10),
    cargo_weight_kg: f.cargoWeight,
    planned_distance_km: f.plannedDistance,
  };
}

export function tripCompleteToBackend(finalOdometer: number, fuelConsumed: number, cargoWeight: number) {
  // Revenue estimated at ₹2/kg as a simple proxy until real pricing is built.
  return {
    final_odometer: finalOdometer,
    fuel_consumed_liters: fuelConsumed,
    revenue: cargoWeight * 2,
  };
}
