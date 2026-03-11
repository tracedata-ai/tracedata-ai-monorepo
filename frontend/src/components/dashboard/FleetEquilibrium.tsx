"use client";

import { dashboardConfig } from "@/config/dashboard";
import { Pie, PieChart, Bar, BarChart, Cell } from "recharts";
import { ChartContainer, ChartTooltip, ChartTooltipContent } from "@/components/ui/chart";

export function FleetEquilibrium() {
  const { equilibrium } = dashboardConfig;

  // Pie chart data
  const safetyData = [
    { name: "Safety", value: equilibrium.safetyIndex.value },
    { name: "Remaining", value: 100 - equilibrium.safetyIndex.value },
  ];
  
  const fairnessData = [
    { name: "Fairness", value: equilibrium.fairnessIndex.value },
    { name: "Remaining", value: 100 - equilibrium.fairnessIndex.value },
  ];

  // Bar chart data
  const sentimentData = equilibrium.sentimentHistory.map((val, i) => ({
    day: `Day ${i + 1}`,
    score: val,
    // Add a custom property to color the last two bars differently based on original design
    isRecent: i >= equilibrium.sentimentHistory.length - 2
  }));

  const pieConfig = {
    value: { label: "Score" }
  };

  const barConfig = {
    score: { label: "Sentiment Trend" }
  };

  return (
    <div className="bg-card rounded-xl border border-border p-6 shadow-sm flex flex-col h-full" data-purpose="fleet-equilibrium">
      <h3 className="text-sm font-bold text-foreground mb-6">Fleet Equilibrium</h3>
      
      <div className="flex flex-col items-center justify-between flex-1 gap-8">
        {/* Donut Charts */}
        <div className="flex gap-8 w-full justify-center">
          {/* Safety Chart */}
          <div className="flex flex-col items-center gap-2">
            <div className="relative w-28 h-28">
              <ChartContainer config={pieConfig} className="w-full h-full !aspect-auto">
                <PieChart>
                  <ChartTooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
                  <Pie
                    data={safetyData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={36}
                    outerRadius={48}
                    strokeWidth={0}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <Cell key="cell-0" fill="#2575fc" className="drop-shadow-md" />
                    <Cell key="cell-1" fill="hsl(var(--muted))" />
                  </Pie>
                </PieChart>
              </ChartContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
                <span className="font-bold text-xl text-foreground">{equilibrium.safetyIndex.value}%</span>
              </div>
            </div>
            <span className="text-xs font-semibold text-muted-foreground uppercase tracking-widest">{equilibrium.safetyIndex.label}</span>
          </div>

          {/* Fairness Chart */}
          <div className="flex flex-col items-center gap-2">
            <div className="relative w-28 h-28">
              <ChartContainer config={pieConfig} className="w-full h-full !aspect-auto">
                <PieChart>
                  <ChartTooltip cursor={false} content={<ChartTooltipContent hideLabel />} />
                  <Pie
                    data={fairnessData}
                    dataKey="value"
                    nameKey="name"
                    innerRadius={36}
                    outerRadius={48}
                    strokeWidth={0}
                    startAngle={90}
                    endAngle={-270}
                  >
                    <Cell key="cell-0" fill="#0d9488" className="drop-shadow-md" />
                    <Cell key="cell-1" fill="hsl(var(--muted))" />
                  </Pie>
                </PieChart>
              </ChartContainer>
              <div className="absolute inset-0 flex flex-col items-center justify-center pointer-events-none">
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
            <span className={`text-xs font-bold ${equilibrium.sentimentTrend >= 0 ? 'text-[#0d9488]' : 'text-red-500'}`}>
              {equilibrium.sentimentTrend > 0 ? '+' : ''}{equilibrium.sentimentTrend}%
            </span>
          </div>
          
          <div className="h-16 w-full mt-2">
            <ChartContainer config={barConfig} className="w-full h-full !aspect-auto">
              <BarChart data={sentimentData} margin={{ top: 0, right: 0, bottom: 0, left: 0 }}>
                <ChartTooltip cursor={{ fill: 'hsl(var(--muted))', opacity: 0.5 }} content={<ChartTooltipContent hideLabel />} />
                <Bar 
                  dataKey="score" 
                  radius={[2, 2, 0, 0]}
                >
                  {sentimentData.map((entry, index) => (
                    <Cell 
                      key={`cell-${index}`} 
                      fill={entry.isRecent ? 'url(#colorGradient)' : '#2575fc40'} 
                    />
                  ))}
                </Bar>
                <defs>
                  <linearGradient id="colorGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="0%" stopColor="#d62d85" />
                    <stop offset="100%" stopColor="#2575fc" />
                  </linearGradient>
                </defs>
              </BarChart>
            </ChartContainer>
          </div>
        </div>
      </div>
    </div>
  );
}
