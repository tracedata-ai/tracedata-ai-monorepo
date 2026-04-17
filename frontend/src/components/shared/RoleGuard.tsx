"use client";

import type { ReactNode } from "react";
import { useRole, type UserRole } from "@/lib/role-context";

type Props = {
  allowed: UserRole | UserRole[];
  fallback?: ReactNode;
  children: ReactNode;
};

/**
 * Renders children only when the current user's role matches `allowed`.
 * Renders `fallback` (or nothing) otherwise.
 */
export function RoleGuard({ allowed, fallback = null, children }: Props) {
  const { role } = useRole();
  const allowedRoles = Array.isArray(allowed) ? allowed : [allowed];

  if (!allowedRoles.includes(role)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}
