"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  AlertTriangle,
  LayoutDashboard,
  Route,
  CarFront,
  Users,
  Radar,
} from "lucide-react";

import {
  Sidebar,
  SidebarContent,
  SidebarFooter,
  SidebarGroup,
  SidebarGroupContent,
  SidebarGroupLabel,
  SidebarHeader,
  SidebarMenu,
  SidebarMenuButton,
  SidebarMenuItem,
} from "@/components/ui/sidebar";

const navItems = [
  { label: "Dashboard", href: "/", icon: LayoutDashboard },
  { label: "Routes", href: "/routes", icon: Route },
  { label: "Trips", href: "/trips", icon: CarFront },
  { label: "Drivers", href: "/drivers", icon: Users },
  { label: "Issues", href: "/issues", icon: AlertTriangle },
  { label: "Telemetry Simulator", href: "/telemetry-simulator", icon: Radar },
] as const;

export function AppSidebar() {
  const pathname = usePathname();

  return (
    <Sidebar collapsible="icon" variant="inset">
      <SidebarHeader>
        <div className="px-2 py-1">
          <p className="text-xs text-sidebar-foreground/70">TraceData</p>
          <p className="text-sm font-semibold">Fleet Console</p>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel>Navigation</SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const active = pathname === item.href;
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      isActive={active}
                      tooltip={item.label}
                      render={<Link href={item.href} />}
                    >
                      <item.icon />
                      <span>{item.label}</span>
                    </SidebarMenuButton>
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>
      <SidebarFooter>
        <p className="px-2 text-xs text-sidebar-foreground/70">
          Ctrl/Cmd + B to toggle
        </p>
      </SidebarFooter>
    </Sidebar>
  );
}
