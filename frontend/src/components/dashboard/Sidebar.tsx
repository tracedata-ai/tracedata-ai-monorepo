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
import { dashboardConfig } from "@/config/dashboard";
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

export function Sidebar() {
  const { navigation } = dashboardConfig;
  const pathname = usePathname();
  const { role, tenantId, logout } = useAuth();

  // Filter links based on current user role
  const filteredLinks = navigation.links.filter((link) => {
    if (!role) return false;
    return link.roles ? link.roles.includes(role) : true;
  });

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
              {navigation.title}
            </h1>
            <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold">
              {navigation.subtitle}
            </p>
          </div>
        </div>
      </SidebarHeader>

      <SidebarContent className="p-2 gap-0 overflow-x-hidden">
        <SidebarGroup className="p-0">
          <SidebarGroupContent>
            <SidebarMenu className="gap-1">
              {filteredLinks.map((link, i) => {
                const isActive =
                  pathname === link.href ||
                  (pathname.startsWith(link.href) &&
                    link.href !== "/dashboard");

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
                      isActive={isActive}
                      tooltip={link.label}
                      className={`h-10 transition-colors ${isActive ? "bg-brand-blue/10 text-brand-blue font-medium hover:bg-brand-blue/15 hover:text-brand-blue" : "text-muted-foreground font-medium"}`}
                    />
                    {link.badge && (
                      <SidebarMenuBadge className="bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 font-bold px-1.5 py-0.5 pointer-events-none">
                        {link.badge}
                      </SidebarMenuBadge>
                    )}
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
                  {tenantId?.replace("_", " ") || "Guest"}
                </span>
                <span className="text-[10px] text-muted-foreground">
                  {role || "Unauthenticated"}
                </span>
              </div>
            </SidebarMenuButton>
          </SidebarMenuItem>
        </SidebarMenu>
      </SidebarFooter>
    </ShadcnSidebar>
  );
}
