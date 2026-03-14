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
  NetworkIcon,
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
  { name: "Fleet", href: "/fleet", icon: TruckIcon },
  { name: "Routes", href: "/routes", icon: MapIcon },
  { name: "Drivers", href: "/drivers", icon: UsersIcon },
  { name: "Trips", href: "/trips", icon: TruckIcon },
  { name: "Incidents", icon: AlertCircleIcon, href: "/issues" },
  { name: "System Map", href: "/system-map", icon: NetworkIcon },
];

/**
 * Global Sidebar Navigation
 *
 * Provides top-level navigation for the TraceData management platform.
 * Features a collapsible structure, active route highlighting, and
 * high-level branding.
 */
export function Sidebar() {
  const pathname = usePathname();

  return (
    <ShadcnSidebar collapsible="icon" className="border-r bg-slate-50/50">
      {/* Sidebar Branding / Logo Header */}
      <SidebarHeader className="p-4">
        <div className="flex items-center gap-2">
          <div className="w-8 h-8 rounded bg-slate-900 flex items-center justify-center text-white font-bold shrink-0">
            T
          </div>
          <div className="flex flex-col group-data-[collapsible=icon]:hidden">
            <h1 className="text-lg font-bold text-slate-900 leading-none">
              TraceData
            </h1>
            <span className="text-[10px] uppercase font-medium text-slate-400">
              Intelligence OS
            </span>
          </div>
        </div>
      </SidebarHeader>

      {/* Primary Navigation Links */}
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="group-data-[collapsible=icon]:hidden text-[10px] uppercase font-bold text-slate-400 mb-2">
            Navigation
          </SidebarGroupLabel>
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
                        "h-9 px-3 mb-1",
                        isActive
                          ? "bg-slate-200 text-slate-900 font-semibold"
                          : "text-slate-500 hover:bg-slate-100 hover:text-slate-900",
                      )}
                    >
                      <item.icon
                        className={cn(
                          "w-4 h-4",
                          isActive ? "text-slate-900" : "text-slate-500",
                        )}
                      />
                      <span className="text-sm">{item.name}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      {/* Sidebar Action Footer */}
      <SidebarFooter className="p-4 border-t">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              tooltip="Settings"
              className="text-slate-500 hover:bg-slate-100 hover:text-slate-900 h-9 px-3"
            >
              <SettingsIcon className="w-4 h-4" />
              <span className="text-sm">Settings</span>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
      <SidebarRail />
    </ShadcnSidebar>
  );
}
