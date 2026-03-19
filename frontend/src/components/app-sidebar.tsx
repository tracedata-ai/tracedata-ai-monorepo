"use client";

import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import {
  AlertTriangle,
  LayoutDashboard,
  Route,
  CarFront,
  Users,
  Radar,
  Home,
} from "lucide-react";

import { BrandMark } from "@/components/shared/BrandMark";
import { Button } from "@/components/ui/button";
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

const fleetManagerItems = [
  { label: "Dashboard", href: "/fleet-manager", icon: LayoutDashboard },
  { label: "Routes", href: "/fleet-manager/routes", icon: Route },
  { label: "Trips", href: "/fleet-manager/trips", icon: CarFront },
  { label: "Drivers", href: "/fleet-manager/drivers", icon: Users },
  { label: "Issues", href: "/fleet-manager/issues", icon: AlertTriangle },
  {
    label: "Telemetry Simulator",
    href: "/fleet-manager/telemetry-simulator",
    icon: Radar,
  },
] as const;

const driverItems = [
  { label: "Dashboard", href: "/driver", icon: LayoutDashboard },
  { label: "Trips", href: "/driver/trips", icon: CarFront },
] as const;

export function AppSidebar() {
  const pathname = usePathname();
  const router = useRouter();

  // Determine role based on current pathname
  const isFleetManager = pathname.startsWith("/fleet-manager");
  const isDriver = pathname.startsWith("/driver");

  const navItems = isFleetManager
    ? fleetManagerItems
    : isDriver
      ? driverItems
      : [];
  const roleLabel = isFleetManager ? "Fleet Manager" : isDriver ? "Driver" : "";

  const handleBack = () => {
    router.push("/");
  };

  if (!navItems.length) return null;

  return (
    <Sidebar collapsible="icon" variant="inset">
      <SidebarHeader>
        <div className="glass rounded-lg px-3 py-2 group-data-[collapsible=icon]:px-1 group-data-[collapsible=icon]:py-1">
          <div className="flex items-center gap-2 group-data-[collapsible=icon]:gap-0">
            <BrandMark size={22} className="rounded-sm" priority />
            <p className="text-sm font-bold tracking-tight whitespace-nowrap group-data-[collapsible=icon]:hidden">
              {roleLabel}
            </p>
          </div>
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
      <SidebarFooter className="space-y-2">
        <Button
          variant="outline"
          size="sm"
          className="w-full justify-start gap-2 group-data-[collapsible=icon]:w-auto group-data-[collapsible=icon]:justify-center group-data-[collapsible=icon]:px-2"
          onClick={handleBack}
        >
          <Home className="h-4 w-4" />
          <span className="group-data-[collapsible=icon]:hidden">
            Back to Home
          </span>
        </Button>
        <p className="px-2 text-xs font-medium text-sidebar-foreground/70 group-data-[collapsible=icon]:hidden">
          Ctrl/Cmd + B to toggle
        </p>
      </SidebarFooter>
    </Sidebar>
  );
}
