import { Search, Bell, Plus } from "lucide-react";
import { dashboardConfig } from "@/config/dashboard";
import { Button } from "@/components/ui/button";

export function Header() {
  const { header } = dashboardConfig;

  return (
    <header className="h-16 border-b border-border bg-background flex items-center justify-between px-8 z-10" data-purpose="dashboard-header">
      <div className="flex items-center gap-4">
        <h2 className="text-xl font-bold text-foreground">{header.title}</h2>
      </div>
      
      <div className="flex items-center gap-6">
        <div className="relative w-96 hidden md:block">
          <Search className="absolute left-3 top-1/2 -translate-y-1/2 text-muted-foreground w-4 h-4" />
          <input 
            className="w-full pl-10 pr-4 py-1.5 bg-muted/50 border border-border rounded-lg text-sm focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue transition-all text-foreground placeholder:text-muted-foreground" 
            placeholder={header.searchPlaceholder} 
            type="text"
          />
        </div>
        
        <div className="flex items-center gap-3">
          <Button variant="outline" size="icon" className="w-9 h-9">
            <Bell className="w-4 h-4" />
          </Button>
          <Button className="bg-brand-blue text-white hover:bg-brand-blue/90 font-semibold gap-2 shadow-sm">
            <Plus className="w-4 h-4" />
            <span>Dispatch</span>
          </Button>
        </div>
      </div>
    </header>
  );
}
