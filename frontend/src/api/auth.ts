import { getJson, postJson } from './client';

export type AuthUser = {
  id: number;
  email: string;
  full_name: string;
  role: string;
  is_active: boolean;
};

export type AuthResponse = {
  access_token: string;
  token_type: string;
  user: AuthUser;
};

export type LoginPayload = {
  email: string;
  password: string;
};

export type RegisterPayload = LoginPayload & {
  full_name: string;
};

export const authApi = {
  login: (payload: LoginPayload) => postJson<AuthResponse>('/auth/login', payload, { auth: false }),
  register: (payload: RegisterPayload) => postJson<AuthResponse>('/auth/register', payload, { auth: false }),
  me: () => getJson<AuthUser>('/auth/me'),
};
