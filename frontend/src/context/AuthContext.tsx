"use client";

import React, { createContext, useContext, useState, useEffect } from "react";
import { useRouter, usePathname } from "next/navigation";

export type UserRole = "Manager" | "Driver" | null;

interface AuthState {
  isAuthenticated: boolean;
  role: UserRole;
  tenantId: string | null;
  login: (tenantId: string, role: UserRole) => void;
  logout: () => void;
  isLoading: boolean;
}

const AuthContext = createContext<AuthState | undefined>(undefined);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [isAuthenticated, setIsAuthenticated] = useState(false);
  const [role, setRole] = useState<UserRole>(null);
  const [tenantId, setTenantId] = useState<string | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const router = useRouter();
  const pathname = usePathname();

  useEffect(() => {
    // Check localStorage on mount
    const storedAuth = localStorage.getItem("tracedata_auth");
    // Defer state updates to avoid synchronous cascading renders
    Promise.resolve().then(() => {
      if (storedAuth) {
        const parsed = JSON.parse(storedAuth);
        setIsAuthenticated(parsed.isAuthenticated);
        setRole(parsed.role);
        setTenantId(parsed.tenantId);
      }
      setIsLoading(false);
    });
  }, []);

  useEffect(() => {
    // Route protection logic
    if (!isLoading) {
      if (!isAuthenticated && pathname?.startsWith("/fleet-manager")) {
        router.push("/login");
      } else if (isAuthenticated && pathname === "/login") {
        router.push("/fleet-manager");
      }
    }
  }, [isLoading, isAuthenticated, pathname, router]);

  const login = (newTenantId: string, newRole: UserRole) => {
    setIsAuthenticated(true);
    setRole(newRole);
    setTenantId(newTenantId);
    localStorage.setItem(
      "tracedata_auth",
      JSON.stringify({ isAuthenticated: true, role: newRole, tenantId: newTenantId })
    );
    router.push("/fleet-manager");
  };

  const logout = () => {
    setIsAuthenticated(false);
    setRole(null);
    setTenantId(null);
    localStorage.removeItem("tracedata_auth");
    router.push("/login");
  };

  return (
    <AuthContext.Provider value={{ isAuthenticated, role, tenantId, login, logout, isLoading }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const context = useContext(AuthContext);
  if (context === undefined) {
    throw new Error("useAuth must be used within an AuthProvider");
  }
  return context;
}
