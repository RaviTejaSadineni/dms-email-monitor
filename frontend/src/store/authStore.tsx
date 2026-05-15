import { useCallback, useEffect, useMemo, useState } from 'react';
import type { PropsWithChildren } from 'react';
import { authApi, type AuthResponse, type AuthUser, type LoginPayload, type RegisterPayload } from '../api/auth';
import { AuthContext, type AuthContextValue } from './authContext';
import { AUTH_UNAUTHORIZED_EVENT, clearStoredAuthToken, getStoredAuthToken, setStoredAuthToken } from './authStorage';

function persistAuth(response: AuthResponse, setToken: (token: string | null) => void, setUser: (user: AuthUser | null) => void) {
  setStoredAuthToken(response.access_token);
  setToken(response.access_token);
  setUser(response.user);
}

export function AuthProvider({ children }: PropsWithChildren) {
  const initialToken = getStoredAuthToken();
  const [token, setToken] = useState<string | null>(initialToken);
  const [user, setUser] = useState<AuthUser | null>(null);
  const [isInitializing, setIsInitializing] = useState(Boolean(initialToken));

  const logout = useCallback(() => {
    clearStoredAuthToken();
    setToken(null);
    setUser(null);
  }, []);

  const login = useCallback(async (payload: LoginPayload) => {
    const response = await authApi.login(payload);
    persistAuth(response, setToken, setUser);
  }, []);

  const register = useCallback(async (payload: RegisterPayload) => {
    const response = await authApi.register(payload);
    persistAuth(response, setToken, setUser);
  }, []);

  useEffect(() => {
    if (!token) {
      return;
    }
    authApi.me()
      .then((currentUser) => setUser(currentUser))
      .catch(() => logout())
      .finally(() => setIsInitializing(false));
  }, [logout, token]);

  useEffect(() => {
    const handleUnauthorized = () => logout();
    window.addEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
    return () => window.removeEventListener(AUTH_UNAUTHORIZED_EVENT, handleUnauthorized);
  }, [logout]);

  const value = useMemo<AuthContextValue>(() => ({
    isAuthenticated: Boolean(token),
    isInitializing,
    token,
    user,
    login,
    register,
    logout,
  }), [isInitializing, login, logout, register, token, user]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}
