"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { 
  MapIcon, 
  TruckIcon, 
  UsersIcon, 
  AlertCircleIcon, 
  LayoutDashboardIcon,
  SettingsIcon
} from "lucide-react";
import { cn } from "@/lib/utils";

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
    <div className="flex flex-col w-64 glass-card border-r h-screen sticky top-0">
      <div className="p-6">
        <h1 className="text-2xl font-bold bg-gradient-to-r from-brand-blue to-brand-teal bg-clip-text text-transparent fragmented-header">
          TraceData
        </h1>
      </div>
      
      <nav className="flex-1 px-4 space-y-2 mt-4">
        {navigation.map((item) => {
          const isActive = pathname === item.href;
          return (
            <Link
              key={item.name}
              href={item.href}
              className={cn(
                "flex items-center gap-3 px-3 py-2 rounded-lg transition-all duration-200 group",
                isActive 
                  ? "bg-brand-blue/10 text-brand-blue" 
                  : "text-muted-foreground hover:bg-muted"
              )}
            >
              <item.icon className={cn(
                "w-5 h-5 transition-colors",
                isActive ? "text-brand-blue" : "group-hover:text-foreground"
              )} />
              <span className="font-medium">{item.name}</span>
              {isActive && (
                <div className="ml-auto w-1.5 h-1.5 rounded-full bg-brand-blue animate-pulse" />
              )}
            </Link>
          );
        })}
      </nav>

      <div className="p-4 mt-auto border-t border-border/50">
        <button className="flex items-center gap-3 px-3 py-2 w-full text-muted-foreground hover:bg-muted rounded-lg transition-all">
          <SettingsIcon className="w-5 h-5" />
          <span className="font-medium">Settings</span>
        </button>
      </div>
    </div>
  );
}
