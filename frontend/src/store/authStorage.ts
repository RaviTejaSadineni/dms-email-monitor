export const AUTH_TOKEN_KEY = 'auth_token';
export const AUTH_UNAUTHORIZED_EVENT = 'auth:unauthorized';

export function getStoredAuthToken() {
  return window.localStorage.getItem(AUTH_TOKEN_KEY);
}

export function setStoredAuthToken(token: string) {
  window.localStorage.setItem(AUTH_TOKEN_KEY, token);
}

export function clearStoredAuthToken() {
  window.localStorage.removeItem(AUTH_TOKEN_KEY);
}
