import type {
  AttemptCreateDTO,
  CreateStoredThresholdDTO,
  EndSessionDTO,
  SessionDTO,
  SessionEvaluationDTO,
  StoredThreshold,
} from '../types';

const BASE_URL = 'http://localhost:8000';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || BASE_URL;

async function throwApiError(res: Response): Promise<never> {
  const text = await res.text();
  try {
    const data = JSON.parse(text);
    if (typeof data?.detail === 'string') {
      throw new Error(data.detail);
    }
  } catch {
    // Fall through to plain-text error below.
  }
  throw new Error(text || `Request failed with status ${res.status}`);
}

// ─────────────────────────────────────────────────────────────
//  Raw HTTP calls — no business logic here
// ─────────────────────────────────────────────────────────────

export async function apiStartSession(userId: number): Promise<SessionDTO> {
  const res = await fetch(`${API_BASE_URL}/sessions/startSession?user_id=${userId}`, {
    method: 'POST',
  });
  if (!res.ok) await throwApiError(res);
  return res.json();
}

export async function apiPlayTone(
  dto: AttemptCreateDTO
): Promise<{ response: 'heard' | 'not_heard'; attempt: import('../types').AttemptDTO }> {
  const res = await fetch(`${API_BASE_URL}/sessions/playTone`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dto),
  });
  if (!res.ok) await throwApiError(res);
  return res.json();
}

export async function apiStoreTone(
  dto: CreateStoredThresholdDTO
): Promise<{ confirmation: string; data: StoredThreshold }> {
  const res = await fetch(`${API_BASE_URL}/sessions/storeTone`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dto),
  });
  if (!res.ok) await throwApiError(res);
  return res.json();
}

export async function apiEndSession(
  dto: EndSessionDTO
): Promise<SessionEvaluationDTO> {
  const res = await fetch(`${API_BASE_URL}/sessions/endSession`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(dto),
  });
  if (!res.ok) await throwApiError(res);
  return res.json();
}
