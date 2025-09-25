import type { ReactNode } from "react";
import { createContext, useContext, useState, useMemo } from "react";
import { useNavigate } from "react-router-dom";
import { api } from "../api/client";

type AuthContextType = {
  token: string | null;
  login: (username: string, password: string) => Promise<void>;
  logout: () => void;
};

const AuthContext = createContext<AuthContextType | undefined>(undefined);

export function AuthProvider({ children }: { children: ReactNode }) {
  const navigate = useNavigate();
  const [token, setToken] = useState<string | null>(() => {
    return localStorage.getItem("admin_token");
  });

  const login = async (username: string, password: string) => {
    const response = await api.post("/auth/login", new URLSearchParams({
      username,
      password,
    }));
    const accessToken = response.data.access_token;
    setToken(accessToken);
    localStorage.setItem("admin_token", accessToken);
    navigate("/");
  };

  const logout = () => {
    setToken(null);
    localStorage.removeItem("admin_token");
    navigate("/login");
  };

  const value = useMemo(() => ({ token, login, logout }), [token]);

  return <AuthContext.Provider value={value}>{children}</AuthContext.Provider>;
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (!context) {
    throw new Error("useAuth должен использоваться внутри AuthProvider");
  }
  return context;
}
