import { dashboardConfig } from "@/config/dashboard";

export function FleetEquilibrium() {
  const { equilibrium } = dashboardConfig;
  
  // Calculate stroke dashoffset for a circle with r=40 (circumference ≈ 251.2)
  const circumference = 2 * Math.PI * 40;
  const getOffset = (percent: number) => circumference - (percent / 100) * circumference;

  return (
    <div className="bg-card rounded-xl border border-border p-6 shadow-sm flex flex-col h-full" data-purpose="fleet-equilibrium">
      <h3 className="text-sm font-bold text-foreground mb-6">Fleet Equilibrium</h3>
      
      <div className="flex flex-col items-center justify-between flex-1 gap-8">
        {/* Donut Charts */}
        <div className="flex gap-8 w-full justify-center">
          {/* Safety Chart */}
          <div className="flex flex-col items-center gap-2">
            <div className="relative w-28 h-28">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle className="text-muted" cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" strokeWidth="8" />
                <circle 
                  className="text-brand-blue drop-shadow-md" 
                  cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" 
                  strokeDasharray={circumference} 
                  strokeDashoffset={getOffset(equilibrium.safetyIndex.value)} 
                  strokeWidth="8" 
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-bold text-xl text-foreground">{equilibrium.safetyIndex.value}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">{equilibrium.safetyIndex.label}</span>
          </div>

          {/* Fairness Chart */}
          <div className="flex flex-col items-center gap-2">
            <div className="relative w-28 h-28">
              <svg className="w-full h-full transform -rotate-90" viewBox="0 0 100 100">
                <circle className="text-muted" cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" strokeWidth="8" />
                <circle 
                  className="text-brand-teal drop-shadow-md" 
                  cx="50" cy="50" fill="transparent" r="40" stroke="currentColor" 
                  strokeDasharray={circumference} 
                  strokeDashoffset={getOffset(equilibrium.fairnessIndex.value)} 
                  strokeWidth="8" 
                  strokeLinecap="round"
                />
              </svg>
              <div className="absolute inset-0 flex flex-col items-center justify-center">
                <span className="font-bold text-xl text-foreground">{equilibrium.fairnessIndex.value}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">{equilibrium.fairnessIndex.label}</span>
          </div>
        </div>
        
        {/* Sentiment Trend Bar Chart */}
        <div className="w-full p-4 bg-muted/30 rounded-lg border border-border mt-auto">
          <div className="flex items-center justify-between mb-3">
            <span className="text-[11px] font-bold text-muted-foreground uppercase tracking-wider">Fleet Sentiment Trends</span>
            <span className={`text-xs font-bold ${equilibrium.sentimentTrend >= 0 ? 'text-brand-teal' : 'text-red-500'}`}>
              {equilibrium.sentimentTrend > 0 ? '+' : ''}{equilibrium.sentimentTrend}%
            </span>
          </div>
          
          <div className="h-12 w-full flex items-end justify-between gap-1.5">
            {equilibrium.sentimentHistory.map((val, i) => {
              const isLastTwo = i >= equilibrium.sentimentHistory.length - 2;
              return (
                <div 
                  key={i}
                  className={`w-full rounded-t-sm transition-all duration-500 hover:opacity-80 ${isLastTwo ? 'bg-[image:var(--background-image-gradient-brand)] shadow-sm' : 'bg-brand-blue/20 dark:bg-brand-blue/30'}`}
                  style={{ height: `${val}%` }}
                  title={`Sentiment Score: ${val}`}
                ></div>
              );
            })}
          </div>
        </div>
      </div>
    </div>
  );
}
