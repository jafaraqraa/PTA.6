import { create } from 'zustand';
import type {
  AttemptDTO,
  SessionDTO,
  StoredThreshold,
  SessionEvaluationDTO,
} from '../types';

interface SessionState {
  // auth (mock)
  userId: number;
  userName: string;

  // current session
  session: SessionDTO | null;
  attempts: AttemptDTO[];
  storedThresholds: StoredThreshold[];
  lastAttemptId: number | null;
  lastResponse: 'heard' | 'not_heard' | null;
  evaluation: SessionEvaluationDTO | null;
  isLoading: boolean;
  error: string | null;

  // actions
  setSession: (s: SessionDTO) => void;
  addAttempt: (a: AttemptDTO) => void;
  setLastAttemptId: (id: number | null) => void;
  setLastResponse: (r: 'heard' | 'not_heard' | null) => void;
  addStoredThreshold: (t: StoredThreshold) => void;
  setEvaluation: (e: SessionEvaluationDTO) => void;
  setLoading: (v: boolean) => void;
  setError: (msg: string | null) => void;
  resetSession: () => void;
}

export const useSessionStore = create<SessionState>((set) => ({
  userId: 1,
  userName: 'Student User',

  session: null,
  attempts: [],
  storedThresholds: [],
  lastAttemptId: null,
  lastResponse: null,
  evaluation: null,
  isLoading: false,
  error: null,

  setSession: (s) => set({ session: s, attempts: [], storedThresholds: [], lastResponse: null }),
  addAttempt: (a) => set((st) => ({ attempts: [...st.attempts, a] })),
  setLastAttemptId: (id) => set({ lastAttemptId: id }),
  setLastResponse: (r) => set({ lastResponse: r }),
  addStoredThreshold: (t) => set((st) => ({
    storedThresholds: [
      ...st.storedThresholds.map((existing) =>
        existing.session_id === t.session_id &&
        existing.ear_side === t.ear_side &&
        existing.test_type === t.test_type &&
        existing.frequency === t.frequency
          ? { ...existing, is_final: false }
          : existing
      ),
      t,
    ],
  })),
  setEvaluation: (e) => set({ evaluation: e }),
  setLoading: (v) => set({ isLoading: v }),
  setError: (msg) => set({ error: msg }),
  resetSession: () =>
    set({
      session: null,
      attempts: [],
      storedThresholds: [],
      lastAttemptId: null,
      lastResponse: null,
      evaluation: null,
      error: null,
    }),
}));
