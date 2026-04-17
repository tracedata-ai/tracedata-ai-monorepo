"use client";

import { createContext, useContext, useState, useCallback, type ReactNode } from "react";

export type UserRole = "fleet-manager" | "driver" | "admin" | null;

type RoleContextType = {
  role: UserRole;
  setRole: (role: UserRole) => void;
  hasRole: (allowed: UserRole | UserRole[]) => boolean;
};

const RoleContext = createContext<RoleContextType | null>(null);

export function RoleProvider({ children }: { children: ReactNode }) {
  const [role, setRole] = useState<UserRole>(null);

  const hasRole = useCallback(
    (allowed: UserRole | UserRole[]) => {
      const allowedRoles = Array.isArray(allowed) ? allowed : [allowed];
      return allowedRoles.includes(role);
    },
    [role],
  );

  return (
    <RoleContext.Provider value={{ role, setRole, hasRole }}>
      {children}
    </RoleContext.Provider>
  );
}

export function useRole() {
  const context = useContext(RoleContext);
  if (!context) {
    throw new Error("useRole must be used within a RoleProvider");
  }
  return context;
}
