import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';

interface SettingsState {
  depotName: string;
  currency: string;
  distanceUnit: string;
  setDepotName: (v: string) => void;
  setCurrency: (v: string) => void;
  setDistanceUnit: (v: string) => void;
}

// Seeded with the current default values used by SettingsPage. Persisted to
// localStorage so the General form survives a refresh / navigation.
export const useSettingsStore = create<SettingsState>()(
  persist(
    (set) => ({
      depotName: 'Gandhinagar Depot ADV',
      currency: 'INR (₹)',
      distanceUnit: 'Kilometers',
      setDepotName: (v) => set({ depotName: v }),
      setCurrency: (v) => set({ currency: v }),
      setDistanceUnit: (v) => set({ distanceUnit: v }),
    }),
    {
      name: 'transitops-settings',
      storage: createJSONStorage(() => localStorage),
    }
  )
);
