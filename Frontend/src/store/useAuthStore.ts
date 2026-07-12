import { create } from 'zustand';
import { persist, createJSONStorage } from 'zustand/middleware';
import type { User } from '../types';
import { login as apiLogin, fetchMe, getStoredToken, setStoredToken, clearStoredToken } from '../lib/apiClient';

interface AuthState {
  user: User | null;
  isAuthenticated: boolean;
  isLoading: boolean;
  login: (email: string, password: string) => Promise<{ success: boolean; error?: string }>;
  logout: () => void;
  rehydrate: () => Promise<void>;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set) => ({
      user: null,
      isAuthenticated: false,
      isLoading: false,

      login: async (email: string, password: string) => {
        set({ isLoading: true });
        try {
          const { access_token } = await apiLogin(email, password);
          setStoredToken(access_token);
          const user = await fetchMe();
          set({ user, isAuthenticated: true, isLoading: false });
          return { success: true };
        } catch (error) {
          const errorMessage = error instanceof Error ? error.message : 'Invalid credentials. Please check your email and password, or contact your admin if your account is locked.';
          set({ isLoading: false });
          return { success: false, error: errorMessage };
        }
      },

      logout: () => {
        clearStoredToken();
        set({ user: null, isAuthenticated: false });
      },

      rehydrate: async () => {
        const token = getStoredToken();
        if (!token) {
          set({ isAuthenticated: false, user: null });
          return;
        }
        try {
          const user = await fetchMe();
          set({ user, isAuthenticated: true });
        } catch {
          clearStoredToken();
          set({ user: null, isAuthenticated: false });
        }
      },
    }),
    {
      name: 'transitops-auth',
      storage: createJSONStorage(() => localStorage),
      partialize: (state) => ({
        user: state.user,
        isAuthenticated: state.isAuthenticated,
      }),
    }
  )
);