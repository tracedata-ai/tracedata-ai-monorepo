"use client";

import { AppShell } from "@/components/app-shell";
import { ReactNode } from "react";

export default function DriverLayout({ children }: { children: ReactNode }) {
  return <AppShell>{children}</AppShell>;
}
