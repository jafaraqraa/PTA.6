import { create } from 'zustand';
import { persist } from 'zustand/middleware';
import type { User, University } from '../types';

interface AuthState {
  token: string | null;
  user: User | null;
  university: University | null;
  domain: string | null;

  setAuth: (token: string, user: User, university: University) => void;
  setDomain: (domain: string) => void;
  logout: () => void;
  isAuthenticated: () => boolean;
}

export const useAuthStore = create<AuthState>()(
  persist(
    (set, get) => ({
      token: null,
      user: null,
      university: null,
      domain: null,

      setAuth: (token, user, university) => set({ token, user, university }),
      setDomain: (domain) => set({ domain }),
      logout: () => set({ token: null, user: null, university: null }),
      isAuthenticated: () => !!get().token,
    }),
    {
      name: 'pta-auth-storage',
    }
  )
);
