import { create } from 'zustand';
import type { Driver, DriverStatus } from '../types';
import { apiGet, apiPost } from '../lib/apiClient';
import { driverToFrontend, driverToBackend, type BackendDriver } from '../lib/mappers/driverMapper';
import { isLicenseExpired } from '../lib/calculations';
import { useTripsStore } from './useTripsStore';

interface DriverListResponse {
  total: number;
  items: BackendDriver[];
}

interface DriversState {
  drivers: Driver[];
  isLoading: boolean;
  fetchDrivers: () => Promise<void>;
  addDriver: (driver: Omit<Driver, 'id' | 'tripCompletion'>) => Promise<void>;
  updateDriverStatus: (id: string, status: DriverStatus) => void;
  getAvailableDrivers: () => Driver[];
  getDriverById: (id: string) => Driver | undefined;
}

export const useDriversStore = create<DriversState>((set, get) => ({
  drivers: [],
  isLoading: false,

  fetchDrivers: async () => {
    set({ isLoading: true });
    try {
      const data = await apiGet<DriverListResponse>('/drivers');
      const mapped = data.items.map(driverToFrontend);
      
      // Calculate trip completion based on trips
      const trips = useTripsStore.getState().trips;
      const driversWithCompletion = mapped.map(d => {
        const driverTrips = trips.filter(t => t.driverId === d.id);
        const completedTrips = driverTrips.filter(t => t.status === 'Completed').length;
        const tripCompletion = driverTrips.length > 0 ? Math.round((completedTrips / driverTrips.length) * 100) : 0;
        return { ...d, tripCompletion };
      });
      
      set({ drivers: driversWithCompletion, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  addDriver: async (driver) => {
    const payload = driverToBackend(driver);
    const created = await apiPost<BackendDriver>('/drivers', payload);
    const mapped = driverToFrontend(created);
    set(state => ({
      drivers: [...state.drivers, mapped],
    }));
  },

  updateDriverStatus: (id, status) => {
    set(state => ({
      drivers: state.drivers.map(d =>
        d.id === id ? { ...d, status } : d
      ),
    }));
  },

  getAvailableDrivers: () => {
    return get().drivers.filter(d =>
      d.status === 'Available' && !isLicenseExpired(d.licenseExpiry)
    );
  },

  getDriverById: (id) => {
    return get().drivers.find(d => d.id === id);
  },
}));
