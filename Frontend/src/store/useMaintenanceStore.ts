import { create } from 'zustand';
import type { MaintenanceLog, MaintenanceStatus } from '../types';
import { seedMaintenance } from '../mock-data/maintenance';
import { useFleetStore } from './useFleetStore';

interface MaintenanceState {
  logs: MaintenanceLog[];
  addRecord: (log: Omit<MaintenanceLog, 'id'>) => void;
  completeRecord: (id: string) => void;
}

let nextId = seedMaintenance.length + 1;

export const useMaintenanceStore = create<MaintenanceState>((set, get) => ({
  logs: [...seedMaintenance],

  addRecord: (log) => {
    const id = `m${nextId++}`;
    // Set vehicle to "In Shop"
    useFleetStore.getState().updateVehicleStatus(log.vehicleId, 'In Shop');
    set(state => ({
      logs: [...state.logs, { ...log, id, status: 'In Shop' as MaintenanceStatus }],
    }));
  },

  completeRecord: (id) => {
    const record = get().logs.find(l => l.id === id);
    if (!record) return;

    // Return vehicle to "Available" unless it's Retired
    const vehicle = useFleetStore.getState().getVehicleById(record.vehicleId);
    if (vehicle && vehicle.status !== 'Retired') {
      useFleetStore.getState().updateVehicleStatus(record.vehicleId, 'Available');
    }

    set(state => ({
      logs: state.logs.map(l =>
        l.id === id ? { ...l, status: 'Completed' as MaintenanceStatus } : l
      ),
    }));
  },
}));
