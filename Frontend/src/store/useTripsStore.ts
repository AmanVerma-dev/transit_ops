import { create } from 'zustand';
import type { Trip, TripStatus } from '../types';
import { seedTrips } from '../mock-data/trips';
import { useFleetStore } from './useFleetStore';
import { useDriversStore } from './useDriversStore';
import { useFinanceStore } from './useFinanceStore';

interface TripsState {
  trips: Trip[];
  createTrip: (trip: Omit<Trip, 'id' | 'status' | 'createdAt'>) => void;
  dispatchTrip: (id: string) => void;
  completeTrip: (id: string, finalOdometer: number, fuelConsumed: number) => void;
  cancelTrip: (id: string) => void;
}

let nextNum = 7;

export const useTripsStore = create<TripsState>((set, get) => ({
  trips: [...seedTrips],

  createTrip: (tripData) => {
    const id = `TR${String(nextNum++).padStart(3, '0')}`;
    const trip: Trip = {
      ...tripData,
      id,
      status: 'Draft' as TripStatus,
      createdAt: new Date().toISOString().split('T')[0],
    };
    set(state => ({ trips: [...state.trips, trip] }));
  },

  dispatchTrip: (id) => {
    const trip = get().trips.find(t => t.id === id);
    if (!trip || trip.status !== 'Draft') return;

    // Set vehicle + driver to "On Trip"
    if (trip.vehicleId) {
      useFleetStore.getState().updateVehicleStatus(trip.vehicleId, 'On Trip');
    }
    if (trip.driverId) {
      useDriversStore.getState().updateDriverStatus(trip.driverId, 'On Trip');
    }

    set(state => ({
      trips: state.trips.map(t =>
        t.id === id ? { ...t, status: 'Dispatched' as TripStatus } : t
      ),
    }));
  },

  completeTrip: (id, finalOdometer, fuelConsumed) => {
    const trip = get().trips.find(t => t.id === id);
    if (!trip || trip.status !== 'Dispatched') return;

    // Restore vehicle + driver to "Available"
    if (trip.vehicleId) {
      useFleetStore.getState().updateVehicleStatus(trip.vehicleId, 'Available');
      useFleetStore.getState().updateVehicleOdometer(trip.vehicleId, finalOdometer);
    }
    if (trip.driverId) {
      useDriversStore.getState().updateDriverStatus(trip.driverId, 'Available');
    }

    // Write fuel log
    const vehicle = trip.vehicleId
      ? useFleetStore.getState().getVehicleById(trip.vehicleId)
      : null;
    useFinanceStore.getState().addFuelLog({
      id: `f${Date.now()}`,
      vehicleId: trip.vehicleId || '',
      vehicleName: vehicle?.name || 'Unknown',
      date: new Date().toLocaleDateString('en-GB', { day: '2-digit', month: 'short', year: 'numeric' }),
      liters: fuelConsumed,
      cost: Math.round(fuelConsumed * 75), // ~₹75/liter estimate
    });

    set(state => ({
      trips: state.trips.map(t =>
        t.id === id
          ? { ...t, status: 'Completed' as TripStatus, actualDistance: trip.plannedDistance, fuelConsumed }
          : t
      ),
    }));
  },

  cancelTrip: (id) => {
    const trip = get().trips.find(t => t.id === id);
    if (!trip) return;

    // Restore vehicle + driver to "Available" if dispatched
    if (trip.status === 'Dispatched') {
      if (trip.vehicleId) {
        useFleetStore.getState().updateVehicleStatus(trip.vehicleId, 'Available');
      }
      if (trip.driverId) {
        useDriversStore.getState().updateDriverStatus(trip.driverId, 'Available');
      }
    }

    set(state => ({
      trips: state.trips.map(t =>
        t.id === id ? { ...t, status: 'Cancelled' as TripStatus } : t
      ),
    }));
  },
}));
