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
        <div className="glass rounded-lg px-3 py-2">
          <p className="text-[11px] font-semibold uppercase tracking-[0.16em] text-[var(--info)]">
            TraceData
          </p>
          <p className="text-sm font-bold tracking-tight">Fleet Console</p>
        </div>
      </SidebarHeader>
      <SidebarContent>
        <SidebarGroup>
          <SidebarGroupLabel className="font-semibold uppercase tracking-[0.12em]">
            Navigation
          </SidebarGroupLabel>
          <SidebarGroupContent>
            <SidebarMenu>
              {navItems.map((item) => {
                const active = pathname === item.href;
                return (
                  <SidebarMenuItem key={item.href}>
                    <SidebarMenuButton
                      isActive={active}
                      tooltip={item.label}
                      className="font-medium"
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
        <p className="px-2 text-xs font-medium text-sidebar-foreground/70">
          Ctrl/Cmd + B to toggle
        </p>
      </SidebarFooter>
    </Sidebar>
  );
}
