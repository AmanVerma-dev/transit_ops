import { create } from 'zustand';
import type { MaintenanceLog, MaintenanceType } from '../types';
import { apiGet, apiPost, apiPatch } from '../lib/apiClient';
import { maintenanceToFrontend, maintenanceCreateToBackend, type BackendMaintenance } from '../lib/mappers/maintenanceMapper';
import { useFleetStore } from './useFleetStore';

interface MaintenanceListResponse {
  total: number;
  items: BackendMaintenance[];
}

interface MaintenanceState {
  logs: MaintenanceLog[];
  isLoading: boolean;
  fetchMaintenance: () => Promise<void>;
  addRecord: (log: { vehicleId: string; maintenanceType: MaintenanceType; serviceType: string; estimatedCost: number; technicianNotes?: string }) => Promise<void>;
  startRecord: (id: string) => Promise<void>;
  completeRecord: (id: string, actualCost: number) => Promise<void>;
}

export const useMaintenanceStore = create<MaintenanceState>((set, get) => ({
  logs: [],
  isLoading: false,

  fetchMaintenance: async () => {
    set({ isLoading: true });
    try {
      const data = await apiGet<MaintenanceListResponse>('/maintenance');
      // We need vehicle names for the frontend model, so we grab them from FleetStore.
      const vehicles = useFleetStore.getState().vehicles;
      const getVehicleName = (id: number) => vehicles.find(v => v.id === String(id))?.name || 'Unknown';
      
      const mapped = data.items.map(b => maintenanceToFrontend(b, getVehicleName(b.vehicle_id)));
      set({ logs: mapped, isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  addRecord: async (log) => {
    const payload = maintenanceCreateToBackend({
      vehicleId: log.vehicleId,
      maintenanceType: log.maintenanceType,
      description: log.serviceType,
      estimatedCost: log.estimatedCost,
      technicianNotes: log.technicianNotes,
    });
    const created = await apiPost<BackendMaintenance>('/maintenance', payload);
    const vehicle = useFleetStore.getState().getVehicleById(log.vehicleId);
    const mapped = maintenanceToFrontend(created, vehicle?.name || 'Unknown');
    set(state => ({ logs: [...state.logs, mapped] }));
    useFleetStore.getState().fetchVehicles();
  },

  startRecord: async (id) => {
    const started = await apiPatch<BackendMaintenance>(`/maintenance/${id}/start`);
    const vehicle = useFleetStore.getState().getVehicleById(String(started.vehicle_id));
    const mapped = maintenanceToFrontend(started, vehicle?.name || 'Unknown');
    set(state => ({
      logs: state.logs.map(l => l.id === id ? mapped : l),
    }));
    useFleetStore.getState().fetchVehicles();
  },

  completeRecord: async (id, actualCost) => {
    const completed = await apiPatch<BackendMaintenance>(`/maintenance/${id}/complete`, { actual_cost: actualCost });
    const vehicle = useFleetStore.getState().getVehicleById(String(completed.vehicle_id));
    const mapped = maintenanceToFrontend(completed, vehicle?.name || 'Unknown');
    set(state => ({
      logs: state.logs.map(l => l.id === id ? mapped : l),
    }));
    useFleetStore.getState().fetchVehicles();
  },
}));
