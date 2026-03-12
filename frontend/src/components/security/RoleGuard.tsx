"use client";

import React from "react";
import { useAuth } from "@/context/AuthContext";
import { useRouter } from "next/navigation";

interface RoleGuardProps {
  allowedRoles: string[];
  fallback?: React.ReactNode;
  children: React.ReactNode;
}

/**
 * RoleGuard prevents unauthorized access to pages/components.
 * RUBRIC: Cybersecurity—RBAC enforcement at component level.
 */
export function RoleGuard({
  allowedRoles,
  fallback = <div className="p-8 text-red-800">Access denied.</div>,
  children,
}: RoleGuardProps) {
  const { role, isLoading } = useAuth();

  if (isLoading) {
    return <div className="p-8">Loading...</div>;
  }

  if (!role || !allowedRoles.includes(role)) {
    return <>{fallback}</>;
  }

  return <>{children}</>;
}

/**
 * ManagerOnly - Restrict to Manager role
 */
export function ManagerOnly({
  children,
  fallback,
}: {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  return (
    <RoleGuard
      allowedRoles={["Manager"]}
      fallback={
        fallback || <div className="p-8 text-red-800">Managers only.</div>
      }
    >
      {children}
    </RoleGuard>
  );
}

/**
 * DriverOnly - Restrict to Driver role
 */
export function DriverOnly({
  children,
  fallback,
}: {
  children: React.ReactNode;
  fallback?: React.ReactNode;
}) {
  return (
    <RoleGuard
      allowedRoles={["Driver"]}
      fallback={
        fallback || <div className="p-8 text-red-800">Drivers only.</div>
      }
    >
      {children}
    </RoleGuard>
  );
}
