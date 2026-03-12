"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  Rocket,
  LayoutDashboard,
  Bot,
  Truck,
  AlertTriangle,
  BarChart3,
  Settings,
  Users,
  Route,
  Building2,
} from "lucide-react";
import { useAuth } from "@/context/AuthContext";
import {
  Sidebar as ShadcnSidebar,
  SidebarHeader,
  SidebarContent,
  SidebarGroup,
  SidebarGroupContent,
  SidebarMenu,
  SidebarMenuItem,
  SidebarMenuButton,
  SidebarFooter,
  SidebarMenuBadge,
} from "@/components/ui/sidebar";

const getIcon = (iconName: string) => {
  switch (iconName) {
    case "LayoutDashboard":
      return (
        <LayoutDashboard className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    case "Bot":
      return (
        <Bot className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    case "Users":
      return (
        <Users className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    case "Route":
      return (
        <Route className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    case "Truck":
      return (
        <Truck className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    case "AlertTriangle":
      return (
        <AlertTriangle className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    case "BarChart3":
      return (
        <BarChart3 className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    case "Settings":
      return (
        <Settings className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
    default:
      return (
        <LayoutDashboard className="w-5 h-5 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
      );
  }
};

// Role-based navigation configuration
const getRoleBasedNavigation = (role: string | null) => {
  if (role === "Manager") {
    return [
      { label: "Dashboard", href: "/fleet-manager", icon: "LayoutDashboard" },
      { label: "Drivers", href: "/fleet-manager/fleet", icon: "Users" },
      { label: "Observability", href: "/fleet-manager/admin", icon: "BarChart3" },
      { label: "Settings", href: "/fleet-manager/settings", icon: "Settings" },
    ];
  } else if (role === "Driver") {
    return [
      {
        label: "My Dashboard",
        href: "/driver/dashboard",
        icon: "LayoutDashboard",
      },
      { label: "My Profile", href: "/driver/profile", icon: "Users" },
      { label: "My Trips", href: "/driver/trips", icon: "Route" },
      { label: "Appeals", href: "/driver/appeals", icon: "AlertTriangle" },
    ];
  }
  return [];
};

export function Sidebar() {
  const pathname = usePathname();
  const { role, tenantId, logout } = useAuth();

  // Get role-based navigation
  const navLinks = getRoleBasedNavigation(role);

  return (
    <ShadcnSidebar
      variant="sidebar"
      className="border-r border-border bg-white drop-shadow-sm"
      data-purpose="dashboard-sidebar"
    >
      <SidebarHeader className="p-4 border-b border-border">
        <div className="flex items-center gap-3 px-2">
          <div className="w-8 h-8 shrink-0 bg-brand-blue flex items-center justify-center text-white icon-motif-mask rounded-md">
            <Rocket className="w-5 h-5" />
          </div>
          <div className="flex flex-col group-data-[collapsible=icon]:hidden">
            <h1 className="text-sm font-bold tracking-tight text-foreground">
              TraceData
            </h1>
            <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold">
              {role === "Manager"
                ? "Fleet Manager"
                : role === "Driver"
                  ? "Driver Portal"
                  : ""}
            </p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="p-2 gap-0 overflow-x-hidden">
        <SidebarGroup className="p-0">
          <SidebarGroupContent>
            <SidebarMenu className="gap-1">
              {navLinks.map((link, i) => {
                const isActive =
                  pathname === link.href ||
                  (pathname && pathname.startsWith(link.href) &&
                    link.href !== "/fleet-manager");

                return (
                  <SidebarMenuItem key={i}>
                    <SidebarMenuButton
                      render={
                        <Link
                          href={link.href}
                          className="flex items-center gap-3"
                        >
                          {getIcon(link.icon)}
                          <span className="text-sm">{link.label}</span>
                        </Link>
                      }
                      isActive={!!isActive}
                      tooltip={link.label}
                      className={`h-10 transition-colors ${isActive ? "bg-brand-blue/10 text-brand-blue font-medium hover:bg-brand-blue/15 hover:text-brand-blue" : "text-muted-foreground font-medium"}`}
                    />
                  </SidebarMenuItem>
                );
              })}
            </SidebarMenu>
          </SidebarGroupContent>
        </SidebarGroup>
      </SidebarContent>

      <SidebarFooter className="border-t border-border p-2">
        <SidebarMenu>
          <SidebarMenuItem>
            <SidebarMenuButton
              onClick={logout}
              className="h-12 flex items-center gap-3 hover:bg-red-500/10 hover:text-red-500 transition-colors group"
            >
              <div className="w-8 h-8 shrink-0 rounded-full bg-brand-blue/10 text-brand-blue flex items-center justify-center border border-brand-blue/20 group-hover:bg-red-500/20 group-hover:text-red-500 group-hover:border-red-500/30 transition-colors">
                <Building2 className="w-4 h-4 group-data-[collapsible=icon]:w-5 group-data-[collapsible=icon]:h-5" />
              </div>
              <div className="flex flex-col text-left group-data-[collapsible=icon]:hidden">
                <span className="text-xs font-semibold text-foreground uppercase tracking-wider">
                  {role || "Not Logged In"}
                </span>
                <span className="text-[10px] text-muted-foreground">
                  Logout
                </span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </ShadcnSidebar>
  );
}
