import React, { createContext, useContext, useState, useCallback, useEffect } from "react";
import { apiClient } from "../services/api/client";

interface User {
  id: string;
  email: string;
  first_name: string;
  last_name: string;
  full_name: string;
  role: "admin" | "analyst" | "viewer";
  organization: string | null;
  organization_name: string | null;
}

interface AuthState {
  user: User | null;
  accessToken: string | null;
  refreshToken: string | null;
  isAuthenticated: boolean;
}

interface AuthContextValue extends AuthState {
  login: (access: string, refresh: string, user: User) => void;
  logout: () => void;
  setUser: (user: User) => void;
}

const AuthContext = createContext<AuthContextValue | null>(null);

const STORAGE_KEY = "esg_auth";

function loadFromStorage(): AuthState {
  try {
    const raw = localStorage.getItem(STORAGE_KEY);
    if (raw) return JSON.parse(raw);
  } catch {}
  return { user: null, accessToken: null, refreshToken: null, isAuthenticated: false };
}

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [state, setState] = useState<AuthState>(loadFromStorage);

  useEffect(() => {
    localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state]);

  const login = useCallback((access: string, refresh: string, user: User) => {
    setState({ user, accessToken: access, refreshToken: refresh, isAuthenticated: true });
  }, []);

  const logout = useCallback(() => {
    setState({ user: null, accessToken: null, refreshToken: null, isAuthenticated: false });
    localStorage.removeItem(STORAGE_KEY);
  }, []);

  const setUser = useCallback((user: User) => {
    setState(s => ({ ...s, user }));
  }, []);

  return (
    <AuthContext.Provider value={{ ...state, login, logout, setUser }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within AuthProvider");
  return ctx;
}
