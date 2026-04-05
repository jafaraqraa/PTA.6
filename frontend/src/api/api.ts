import type {
  AttemptCreateDTO,
  CreateStoredThresholdDTO,
  EndSessionDTO,
  SessionDTO,
  SessionEvaluationDTO,
  StoredThreshold,
  LoginRequest,
  Token,
} from '../types';
import { useAuthStore } from '../store/authStore';
import { detectDomain } from '../utils/domain';

const BASE_URL = 'http://localhost:8000';
const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || BASE_URL;

async function request(path: string, options: RequestInit = {}): Promise<Response> {
  const { token, domain: storedDomain } = useAuthStore.getState();
  const detectedDomain = detectDomain();
  // Ensure we don't send "localhost" or empty domains
  const domain = (detectedDomain && !detectedDomain.includes('localhost')) ? detectedDomain : storedDomain;

  const url = new URL(`${API_BASE_URL}${path}`);
  if (domain) {
    url.searchParams.append('domain', domain);
  }

  const headers = new Headers(options.headers || {});
  if (domain) {
    headers.set('X-University-Domain', domain);
  }
  if (token) {
    headers.set('Authorization', `Bearer ${token}`);
  }
  if (!headers.has('Content-Type') && options.body) {
    headers.set('Content-Type', 'application/json');
  }

  const response = await fetch(url.toString(), {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      // Unauthorized - clear auth state
      useAuthStore.getState().logout();
      if (!window.location.pathname.includes('/login')) {
        window.location.href = '/login';
      }
    }
    if (response.status === 403) {
      const text = await response.clone().text();
      if (text.toLowerCase().includes('subscription')) {
        window.location.href = '/subscription-expired';
      }
    }
    await throwApiError(response);
  }

  return response;
}

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
//  Authentication API
// ─────────────────────────────────────────────────────────────

export async function apiLogin(dto: LoginRequest): Promise<Token> {
  const res = await request('/auth/login', {
    method: 'POST',
    body: JSON.stringify(dto),
  });
  return res.json();
}

// ─────────────────────────────────────────────────────────────
//  Session API
// ─────────────────────────────────────────────────────────────

export async function apiStartSession(userId: number): Promise<SessionDTO> {
  const res = await request('/sessions/startSession', {
    method: 'POST',
  });
  return res.json();
}

export async function apiPlayTone(
  dto: AttemptCreateDTO
): Promise<{ response: 'heard' | 'not_heard'; attempt: import('../types').AttemptDTO }> {
  const res = await request('/sessions/playTone', {
    method: 'POST',
    body: JSON.stringify(dto),
  });
  return res.json();
}

export async function apiStoreTone(
  dto: CreateStoredThresholdDTO
): Promise<{ confirmation: string; data: StoredThreshold }> {
  const res = await request('/sessions/storeTone', {
    method: 'POST',
    body: JSON.stringify(dto),
  });
  return res.json();
}

export async function apiEndSession(
  dto: EndSessionDTO
): Promise<SessionEvaluationDTO> {
  const res = await request('/sessions/endSession', {
    method: 'POST',
    body: JSON.stringify(dto),
  });
  return res.json();
}
