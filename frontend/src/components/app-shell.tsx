"use client";

import { useMemo } from "react";
import { usePathname } from "next/navigation";

import { AppSidebar } from "@/components/app-sidebar";
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
          <header className="sticky top-0 z-20 flex h-14 items-center gap-3 border-b bg-background/95 px-4 backdrop-blur supports-[backdrop-filter]:bg-background/70">
            <SidebarTrigger />
            <div>
              <p className="text-xs text-muted-foreground">Operations</p>
              <h1 className="text-sm font-semibold tracking-wide">
                {currentTitle}
              </h1>
            </div>
          </header>
          <div className="flex-1 p-4 md:p-6">{children}</div>
        </SidebarInset>
      </SidebarProvider>
    </TooltipProvider>
  );
}
