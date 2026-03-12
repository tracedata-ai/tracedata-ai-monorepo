"use client";

import * as React from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  MapIcon, 
  TruckIcon, 
  UsersIcon, 
  AlertCircleIcon, 
  LayoutDashboardIcon,
  SettingsIcon,
  ChevronRight
} from "lucide-react";
import { cn } from "@/lib/utils";
import {
  Sidebar as ShadcnSidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
  SidebarRail,
} from "@/components/ui/sidebar";

const navigation = [
  { name: "Dashboard", href: "/", icon: LayoutDashboardIcon },
  { name: "Routes", href: "/routes", icon: MapIcon },
  { name: "Trips", href: "/trips", icon: TruckIcon },
  { name: "Drivers", href: "/drivers", icon: UsersIcon },
  { name: "Issues", href: "/issues", icon: AlertCircleIcon },
];

export function Sidebar() {
  const pathname = usePathname();

  return (
    <ShadcnSidebar collapsible="icon" className="border-r bg-white/50 backdrop-blur-md">
      <SidebarHeader className="p-6">
        <div className="flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-br from-brand-blue to-brand-teal flex items-center justify-center text-white font-bold shadow-lg shadow-brand-blue/20 shrink-0">
            T
          </div>
          <div className="flex flex-col group-data-[collapsible=icon]:hidden">
            <h1 className="text-xl font-bold bg-gradient-to-r from-brand-blue to-brand-teal bg-clip-text text-transparent fragmented-header leading-tight">
              TraceData
            </h1>
            <span className="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold">AI Orchestrator</span>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="group-data-[collapsible=icon]:hidden text-xs uppercase tracking-wider font-bold text-muted-foreground/50 mb-2">Platform</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navigation.map((item) => {
                const isActive = pathname === item.href;
                return (
                  <SidebarMenuItem key={item.name}>
                    <SidebarMenuButton
                      render={<Link href={item.href} />}
                      isActive={isActive}
                      tooltip={item.name}
                      className={cn(
                        "transition-all duration-300 h-11 px-4 mb-1",
                        isActive 
                          ? "bg-brand-blue text-white shadow-md shadow-brand-blue/20 hover:bg-brand-blue/90 hover:text-white" 
                          : "hover:bg-brand-blue/5 text-muted-foreground hover:text-brand-blue"
                      )}
                    >
                      <item.icon className={cn(
                        "w-5 h-5 transition-transform duration-300 group-hover:scale-110",
                        isActive ? "text-white" : "text-muted-foreground group-hover:text-brand-blue"
                      )} />
                      <span className="font-semibold tracking-tight">{item.name}</span>
                      {isActive && !process.env.NEXT_PUBLIC_DISABLE_ANIMATIONS && (
                          <ChevronRight className="ml-auto w-4 h-4 animate-in slide-in-from-left-2" />
                      )}
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="p-4 border-t border-border/50 bg-muted/30">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton tooltip="Settings" className="hover:bg-brand-blue/5 text-muted-foreground hover:text-brand-blue h-11 px-4 transition-all duration-300">
              <SettingsIcon className="w-5 h-5" />
              <span className="font-semibold tracking-tight">Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </ShadcnSidebar>
  );
}
