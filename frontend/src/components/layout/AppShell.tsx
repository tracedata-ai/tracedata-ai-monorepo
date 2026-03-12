"use client";

import React from "react";
import { SidebarProvider, SidebarInset } from "@/components/ui/sidebar";
import { Sidebar } from "@/components/dashboard/Sidebar";
import { Header } from "@/components/dashboard/Header";

interface AppShellProps {
  children: React.ReactNode;
}

export function AppShell({ children }: AppShellProps) {
  return (
    <SidebarProvider>
      <div className="flex h-screen w-full bg-muted/20 overflow-hidden font-sans">
        <Sidebar aria-label="Main Navigation" />
        <SidebarInset className="flex-1 flex flex-col overflow-hidden relative bg-transparent border-0 shadow-none m-0 ml-0 mr-0 peer-data-[variant=inset]:ml-0 peer-data-[variant=inset]:mr-0 peer-data-[variant=inset]:rounded-none">
          <Header />
          <div className="flex-1 overflow-hidden relative flex flex-col">
            {children}
          </div>
        </SidebarInset>
      </div>
    </SidebarProvider>
  );
}
