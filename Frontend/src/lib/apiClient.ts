import type { User, Role } from '../types';

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000/api/v1';

export interface TokenResponse {
  access_token: string;
  token_type: string;
}

export interface BackendUser {
  name: string;
  email: string;
  role: string;
}

function mapBackendRole(backendRole: string): Role {
  const normalized = backendRole.trim().toLowerCase();
  switch (normalized) {
    case 'fleet manager':
    case 'fleet_manager':
      return 'Fleet Manager';
    case 'dispatcher':
      return 'Dispatcher';
    // Backend seeds the driver role as "Driver"; the frontend Role union uses
    // "Dispatcher". Reconcile explicitly rather than relying on the default.
    case 'driver':
      return 'Dispatcher';
    case 'safety officer':
    case 'safety_officer':
      return 'Safety Officer';
    case 'financial analyst':
    case 'financial_analyst':
      return 'Financial Analyst';
    default:
      // Default fallback - will be caught by backend validation anyway
      return 'Dispatcher';
  }
}

// The backend puts the role name in the JWT claim (not in /auth/me, which only
// returns role_id). Decode the payload to recover the role without touching the
// backend.
function decodeJwtRole(token: string): string | null {
  try {
    const payload = token.split('.')[1];
    if (!payload) return null;
    const base64 = payload.replace(/-/g, '+').replace(/_/g, '/');
    const json = JSON.parse(window.atob(base64)) as { role?: unknown };
    return typeof json.role === 'string' ? json.role : null;
  } catch {
    return null;
  }
}

export function getStoredToken(): string | null {
  return localStorage.getItem('transitops_token');
}

export function setStoredToken(token: string): void {
  localStorage.setItem('transitops_token', token);
}

export function clearStoredToken(): void {
  localStorage.removeItem('transitops_token');
}

// ── Generic request helpers ──

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  const token = getStoredToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearStoredToken();
      window.location.href = '/login';
    }
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.message || `Request failed: ${response.status}`;
    throw new Error(message);
  }

  return response.json();
}

/** Fire a DELETE and return nothing (expects 204). */
async function requestNoContent(path: string, options: RequestInit = {}): Promise<void> {
  const token = getStoredToken();
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options.headers,
  };
  if (token) {
    (headers as Record<string, string>)['Authorization'] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_BASE_URL}${path}`, {
    ...options,
    headers,
  });

  if (!response.ok) {
    if (response.status === 401) {
      clearStoredToken();
      window.location.href = '/login';
    }
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.message || `Request failed: ${response.status}`;
    throw new Error(message);
  }
}

export function apiGet<T>(path: string): Promise<T> {
  return request<T>(path);
}

export function apiPost<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: 'POST', body: JSON.stringify(body) });
}

export function apiPut<T>(path: string, body: unknown): Promise<T> {
  return request<T>(path, { method: 'PUT', body: JSON.stringify(body) });
}

export function apiPatch<T>(path: string, body?: unknown): Promise<T> {
  return request<T>(path, {
    method: 'PATCH',
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });
}

export function apiDelete(path: string): Promise<void> {
  return requestNoContent(path, { method: 'DELETE' });
}

// ── Auth-specific helpers ──

export async function login(email: string, password: string): Promise<TokenResponse> {
  const formData = new URLSearchParams();
  formData.append('username', email);
  formData.append('password', password);

  const response = await fetch(`${API_BASE_URL}/auth/login`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/x-www-form-urlencoded',
    },
    body: formData.toString(),
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const message = errorData.detail || errorData.message || 'Invalid credentials. Please check your email and password, or contact your admin if your account is locked.';
    throw new Error(message);
  }

  return response.json();
}

export async function fetchMe(): Promise<User> {
  const token = getStoredToken();
  const backendUser = await request<{ name: string; email: string }>('/auth/me');
  // Role comes from the JWT claim (backend /auth/me only exposes role_id).
  const rawRole = token ? decodeJwtRole(token) : undefined;
  const role = mapBackendRole(rawRole ?? '');

  // Generate initials from name
  const nameParts = backendUser.name.split(' ');
  const initials = nameParts.length >= 2
    ? (nameParts[0][0] + nameParts[1][0]).toUpperCase()
    : backendUser.name.substring(0, 2).toUpperCase();

  return {
    name: backendUser.name,
    email: backendUser.email,
    role,
    initials,
  };
}