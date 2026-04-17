"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";

import { AppSidebar } from "@/components/app-sidebar";
import { BrandMark } from "@/components/shared/BrandMark";
import { TooltipProvider } from "@/components/ui/tooltip";
import {
  SidebarInset,
  SidebarProvider,
  SidebarTrigger,
} from "@/components/ui/sidebar";

const pageTitles: Record<string, string> = {
  "/fleet-manager": "Fleet Dashboard",
  "/fleet-manager/routes": "Routes",
  "/fleet-manager/trips": "Trips",
  "/fleet-manager/drivers": "Drivers",
  "/fleet-manager/issues": "Issues & Incidents",
  "/fleet-manager/telemetry-simulator": "Telemetry Simulator",
  "/driver": "Driver Portal",
  "/driver/trips": "My Trips",
};

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  const currentTitle = useMemo(() => {
    if (pageTitles[pathname]) {
      return pageTitles[pathname];
    }

    const matchingEntry = Object.entries(pageTitles).find(
      ([route]) => pathname.startsWith(route) && route !== "/",
    );

    return matchingEntry?.[1] ?? "TraceData";
  }, [pathname]);

  return (
    <TooltipProvider>
      <SidebarProvider>
        <AppSidebar />
        <SidebarInset>
          <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b border-border bg-card px-4">
            <SidebarTrigger />
            <BrandMark size={24} className="rounded-sm" />
            <div>
              <p className="text-xs font-medium text-muted-foreground">
                Operations
              </p>
              <h1 className="text-sm font-bold uppercase tracking-tight">
                {currentTitle}
              </h1>
            </div>
          </header>
          <div className="flex-1 p-2 md:p-3">{children}</div>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}
