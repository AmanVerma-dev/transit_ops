import { create } from 'zustand';
import type { Driver, DriverStatus } from '../types';
import { seedDrivers } from '../mock-data/drivers';
import { isLicenseExpired } from '../lib/calculations';

interface DriversState {
  drivers: Driver[];
  addDriver: (driver: Omit<Driver, 'id'>) => void;
  updateDriverStatus: (id: string, status: DriverStatus) => void;
  getAvailableDrivers: () => Driver[];
  getDriverById: (id: string) => Driver | undefined;
}

let nextId = seedDrivers.length + 1;

export const useDriversStore = create<DriversState>((set, get) => ({
  drivers: [...seedDrivers],
  addDriver: (driver) => {
    const id = `d${nextId++}`;
    set(state => ({
      drivers: [...state.drivers, { ...driver, id }],
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
