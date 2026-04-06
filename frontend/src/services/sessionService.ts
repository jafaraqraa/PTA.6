import type { SessionDTO } from '../types';
import { apiStartSession } from '../api/api';

// ─────────────────────────────────────────────────────────────
//  Session Service — business logic around session lifecycle
// ─────────────────────────────────────────────────────────────

export const SessionService = {
  /** Create a new session for a given user */
  async start(): Promise<SessionDTO> {
    return apiStartSession();
  },
};
