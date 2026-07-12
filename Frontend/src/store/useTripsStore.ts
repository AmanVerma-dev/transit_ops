import { create } from 'zustand';
import type { Trip } from '../types';
import { apiGet, apiPost, apiPatch } from '../lib/apiClient';
import { tripToFrontend, tripCreateToBackend, tripCompleteToBackend, type BackendTrip } from '../lib/mappers/tripMapper';
import { useFleetStore } from './useFleetStore';
import { useDriversStore } from './useDriversStore';

interface TripListResponse {
  total: number;
  items: BackendTrip[];
}

interface TripsState {
  trips: Trip[];
  isLoading: boolean;
  fetchTrips: () => Promise<void>;
  createTrip: (trip: { source: string; destination: string; vehicleId: string; driverId: string; cargoWeight: number; plannedDistance: number; eta?: string }) => Promise<void>;
  dispatchTrip: (id: string) => Promise<void>;
  completeTrip: (id: string, finalOdometer: number, fuelConsumed: number) => Promise<void>;
  cancelTrip: (id: string) => Promise<void>;
}

export const useTripsStore = create<TripsState>((set, get) => ({
  trips: [],
  isLoading: false,

  fetchTrips: async () => {
    set({ isLoading: true });
    try {
      const data = await apiGet<TripListResponse>('/trips');
      set({ trips: data.items.map(tripToFrontend), isLoading: false });
    } catch {
      set({ isLoading: false });
    }
  },

  createTrip: async (tripData) => {
    // Only submit to backend when both vehicle and driver are chosen.
    // Unassigned drafts are intentionally not persisted — see prompt step 3 note.
    if (!tripData.vehicleId || !tripData.driverId) return;

    const payload = tripCreateToBackend(tripData);
    const created = await apiPost<BackendTrip>('/trips', payload);
    const mapped = tripToFrontend(created);
    set(state => ({ trips: [...state.trips, mapped] }));
  },

  dispatchTrip: async (id) => {
    const dispatched = await apiPatch<BackendTrip>(`/trips/${id}/dispatch`);
    const mapped = tripToFrontend(dispatched);
    set(state => ({
      trips: state.trips.map(t => t.id === id ? mapped : t),
    }));
    // Re-fetch vehicles and drivers to pick up status side-effects from backend
    useFleetStore.getState().fetchVehicles();
    useDriversStore.getState().fetchDrivers();
  },

  completeTrip: async (id, finalOdometer, fuelConsumed) => {
    const trip = get().trips.find(t => t.id === id);
    if (!trip) return;
    const payload = tripCompleteToBackend(finalOdometer, fuelConsumed, trip.cargoWeight);
    const completed = await apiPatch<BackendTrip>(`/trips/${id}/complete`, payload);
    const mapped = tripToFrontend(completed);
    set(state => ({
      trips: state.trips.map(t => t.id === id ? mapped : t),
    }));
    // Re-fetch vehicles and drivers to pick up status side-effects
    useFleetStore.getState().fetchVehicles();
    useDriversStore.getState().fetchDrivers();
  },

  cancelTrip: async (id) => {
    const cancelled = await apiPatch<BackendTrip>(`/trips/${id}/cancel`);
    const mapped = tripToFrontend(cancelled);
    set(state => ({
      trips: state.trips.map(t => t.id === id ? mapped : t),
    }));
    // Re-fetch vehicles and drivers to pick up status side-effects
    useFleetStore.getState().fetchVehicles();
    useDriversStore.getState().fetchDrivers();
  },
}));
