import { AUTH_UNAUTHORIZED_EVENT, clearStoredAuthToken, getStoredAuthToken } from '../store/authStorage';

const API_BASE = import.meta.env.VITE_API_BASE_URL ?? 'http://localhost:8888/api';

type RequestOptions = {
  method?: 'GET' | 'POST' | 'PUT' | 'PATCH' | 'DELETE';
  body?: unknown;
  auth?: boolean;
};

type FormDataRequestOptions = {
  auth?: boolean;
  onUploadProgress?: (percent: number) => void;
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

export function postFormData<T>(path: string, formData: FormData, options: FormDataRequestOptions = {}): Promise<T> {
  const { auth = true, onUploadProgress } = options;
  const token = auth ? getStoredAuthToken() : null;

  return new Promise<T>((resolve, reject) => {
    const xhr = new XMLHttpRequest();
    xhr.open('POST', `${API_BASE}${path}`);
    if (token) {
      xhr.setRequestHeader('Authorization', `Bearer ${token}`);
    }

    xhr.upload.onprogress = (event) => {
      if (!onUploadProgress || !event.lengthComputable) return;
      onUploadProgress(Math.min(100, Math.round((event.loaded / event.total) * 100)));
    };

    xhr.onload = () => {
      if (xhr.status === 401) {
        clearStoredAuthToken();
        window.dispatchEvent(new Event(AUTH_UNAUTHORIZED_EVENT));
      }

      if (xhr.status >= 200 && xhr.status < 300) {
        resolve(JSON.parse(xhr.responseText) as T);
        return;
      }

      try {
        const payload = JSON.parse(xhr.responseText) as { detail?: string };
        reject(new Error(payload.detail ?? `Request failed with status ${xhr.status}`));
      } catch {
        reject(new Error(`Request failed with status ${xhr.status}`));
      }
    };

    xhr.onerror = () => reject(new Error('Network error'));
    xhr.send(formData);
  });
}

export { API_BASE };
