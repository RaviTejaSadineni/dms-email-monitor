import { AUTH_UNAUTHORIZED_EVENT, clearStoredAuthToken, getStoredAuthToken } from '../store/authStorage';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8888/api';

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  auth?: boolean;
};

async function requestJson<T>(path: string, options: RequestOptions = {}): Promise<T> {
  const { method = 'GET', body, auth = true } = options;
  const token = auth ? getStoredAuthToken() : null;
  const response = await fetch(`${API_BASE}${path}`, {
    method,
    headers: {
      'Content-Type': 'application/json',
      ...(token ? { Authorization: `Bearer ${token}` } : {}),
    },
    ...(body === undefined ? {} : { body: JSON.stringify(body) }),
  });

  if (response.status === 401) {
    clearStoredAuthToken();
    window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT));
  }

  if (!response.ok) {
    const payload = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(payload?.detail ?? `Request failed with status ${response.status}`);
  }

  return response.json() as Promise<T>;
}

export function getJson<T>(path: string, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
  return requestJson<T>(path, options);
}

export function postJson<T>(path: string, body: unknown, options?: Omit<RequestOptions, 'method' | 'body'>): Promise<T> {
  return requestJson<T>(path, { ...options, method: 'POST', body });
}

export { API_BASE };
