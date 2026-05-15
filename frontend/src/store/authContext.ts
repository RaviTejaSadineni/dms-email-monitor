import { createContext } from 'react';
import type { AuthUser, LoginPayload, RegisterPayload } from '../api/auth';

export type AuthContextValue = {
  isAuthenticated: boolean;
  isInitializing: boolean;
  token: string | null;
  user: AuthUser | null;
  login: (payload: LoginPayload) => Promise<void>;
  register: (payload: RegisterPayload) => Promise<void>;
  logout: () => void;
};

export const AuthContext = createContext<AuthContextValue | undefined>(undefined);
