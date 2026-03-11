"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Rocket, LayoutDashboard, Bot, Truck, AlertTriangle, BarChart3, Settings, Users, Route, Building2 } from "lucide-react";
import { dashboardConfig } from "@/config/dashboard";
import { useAuth } from "@/context/AuthContext";

const getIcon = (iconName: string) => {
  switch (iconName) {
    case "LayoutDashboard": return <LayoutDashboard className="w-5 h-5" />;
    case "Bot": return <Bot className="w-5 h-5" />;
    case "Users": return <Users className="w-5 h-5" />;
    case "Route": return <Route className="w-5 h-5" />;
    case "Truck": return <Truck className="w-5 h-5" />;
    case "AlertTriangle": return <AlertTriangle className="w-5 h-5" />;
    case "BarChart3": return <BarChart3 className="w-5 h-5" />;
    case "Settings": return <Settings className="w-5 h-5" />;
    default: return <LayoutDashboard className="w-5 h-5" />;
  }
};

export function Sidebar() {
  const { navigation } = dashboardConfig;
  const pathname = usePathname();
  const { role, tenantId, logout } = useAuth();

  // Filter links based on current user role
  const filteredLinks = navigation.links.filter(link => {
    if (!role) return false;
    return link.roles ? link.roles.includes(role) : true;
  });

  return (
    <aside className="w-64 flex-shrink-0 border-r border-border bg-background flex flex-col" data-purpose="dashboard-sidebar">
      <div className="p-6 border-b border-border flex items-center gap-3">
        <div className="w-8 h-8 bg-brand-blue flex items-center justify-center text-white icon-motif-mask">
          <Rocket className="w-5 h-5" />
        </div>
        <div>
          <h1 className="text-sm font-bold tracking-tight text-foreground">{navigation.title}</h1>
          <p className="text-[10px] uppercase tracking-widest text-muted-foreground font-semibold">{navigation.subtitle}</p>
        </div>
      </div>
      
      <nav className="flex-1 overflow-y-auto p-4 space-y-1">
        {filteredLinks.map((link, i) => {
          const isActive = pathname === link.href || (pathname.startsWith(link.href) && link.href !== '/dashboard');
          
          return (
            <Link 
              key={i} 
              href={link.href}
              className={`flex items-center gap-3 px-3 py-2 rounded-lg transition-colors ${
                isActive 
                  ? "bg-brand-blue/10 text-brand-blue font-medium" 
                  : "text-muted-foreground hover:bg-muted font-medium"
              }`}
            >
              {getIcon(link.icon)}
              <span className="text-sm">{link.label}</span>
              
              {link.badge && (
                <span className="ml-auto bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400 text-[10px] px-1.5 py-0.5 rounded font-bold">
                  {link.badge}
                </span>
              )}
            </Link>
          )
        })}
      </nav>
      
      <div className="p-4 border-t border-border mt-auto">
        <div 
          className="flex items-center gap-3 p-2 rounded-lg hover:bg-red-500/10 hover:text-red-500 cursor-pointer transition-colors group"
          onClick={logout}
          title="Click to logout"
        >
          <div className="w-8 h-8 rounded-full bg-brand-blue/10 text-brand-blue flex items-center justify-center border border-brand-blue/20 group-hover:bg-red-500/20 group-hover:text-red-500 group-hover:border-red-500/30 transition-colors">
            <Building2 className="w-4 h-4" />
          </div>
          <div className="flex flex-col">
            <span className="text-xs font-semibold text-foreground uppercase tracking-wider">{tenantId?.replace('_', ' ') || "Guest"}</span>
            <span className="text-[10px] text-muted-foreground">{role || "Unauthenticated"}</span>
          </div>
        </div>
      </div>
    </aside>
  );
}
