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
  "/": "Dashboard",
  "/routes": "Routes",
  "/trips": "Trips",
  "/drivers": "Drivers",
  "/issues": "Issues",
  "/telemetry-simulator": "Telemetry Simulator",
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
          <header className="glass sticky top-0 z-20 mx-2 mt-2 flex h-14 items-center gap-3 rounded-xl px-4">
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
