import { create } from 'zustand';
import type { Vehicle, VehicleStatus } from '../types';
import { apiGet, apiPost, apiPut } from '../lib/apiClient';
import { vehicleToFrontend, vehicleToBackend, type BackendVehicle } from '../lib/mappers/vehicleMapper';

interface VehicleListResponse {
  total: number;
  items: BackendVehicle[];
}

interface FleetState {
  vehicles: Vehicle[];
  isLoading: boolean;
  fetchVehicles: () => Promise<void>;
  addVehicle: (vehicle: Omit<Vehicle, 'id' | 'capacityLabel'>) => Promise<void>;
  updateVehicleStatus: (id: string, status: VehicleStatus) => void;
  updateVehicleOdometer: (id: string, odometer: number) => void;
  getAvailableVehicles: () => Vehicle[];
  getVehicleById: (id: string) => Vehicle | undefined;
  isRegNoUnique: (regNo: string) => boolean;
}

export const useFleetStore = create<FleetState>((set, get) => ({
  vehicles: [],
  isLoading: false,

  fetchVehicles: async () => {
    set({ isLoading: true });
    try {
      const data = await apiGet<VehicleListResponse>('/vehicles');
      set({ vehicles: data.items.map(vehicleToFrontend), isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  addVehicle: async (vehicle) => {
    const payload = vehicleToBackend(vehicle);
    const created = await apiPost<BackendVehicle>('/vehicles', payload);
    const mapped = vehicleToFrontend(created);
    set(state => ({
      vehicles: [...state.vehicles, mapped],
    }));
  },

  updateVehicleStatus: (id, status) => {
    // Optimistic local update — backend handles status side-effects on trips/maintenance
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
