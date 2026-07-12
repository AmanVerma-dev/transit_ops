import { create } from 'zustand';
import type { Vehicle, VehicleStatus } from '../types';
import { seedVehicles } from '../mock-data/vehicles';

interface FleetState {
  vehicles: Vehicle[];
  addVehicle: (vehicle: Omit<Vehicle, 'id'>) => void;
  updateVehicleStatus: (id: string, status: VehicleStatus) => void;
  updateVehicleOdometer: (id: string, odometer: number) => void;
  getAvailableVehicles: () => Vehicle[];
  getVehicleById: (id: string) => Vehicle | undefined;
  isRegNoUnique: (regNo: string) => boolean;
}

let nextId = seedVehicles.length + 1;

export const useFleetStore = create<FleetState>((set, get) => ({
  vehicles: [...seedVehicles],
  addVehicle: (vehicle) => {
    const id = `v${nextId++}`;
    set(state => ({
      vehicles: [...state.vehicles, { ...vehicle, id }],
    }));
  },
  updateVehicleStatus: (id, status) => {
    set(state => ({
      vehicles: state.vehicles.map(v =>
        v.id === id ? { ...v, status } : v
      ),
    }));
  },
  updateVehicleOdometer: (id, odometer) => {
    set(state => ({
      vehicles: state.vehicles.map(v =>
        v.id === id ? { ...v, odometer } : v
      ),
    }));
  },
  getAvailableVehicles: () => {
    return get().vehicles.filter(v => v.status === 'Available');
  },
  getVehicleById: (id) => {
    return get().vehicles.find(v => v.id === id);
  },
  isRegNoUnique: (regNo) => {
    return !get().vehicles.some(v => v.regNo.toLowerCase() === regNo.toLowerCase());
  },
}));
