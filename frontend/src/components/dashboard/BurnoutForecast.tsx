import { useEffect, useState } from "react";

export function BurnoutForecast() {
  // Generate a mock 12x12 grid for the heatmap
  const [grid, setGrid] = useState<number[][]>([]);

  useEffect(() => {
    // Generate seeded random pattern that looks like a realistic heatmap
    const mockGrid = Array.from({ length: 7 }, (_, row) => 
      Array.from({ length: 14 }, (_, col) => {
        // Create clustering of "high risk" around certain times/sectors
        const baseRisk = Math.random() * 4;
        const timeRisk = col > 6 && col < 11 ? 3 : 0; // Peak risk around middle hours
        const sectorRisk = row === 3 || row === 4 ? 2 : 0; // Sectors 3-4 are higher risk
        
        let risk = baseRisk + timeRisk + sectorRisk;
        // Cap at 9 (for our color scales 0-9)
        return Math.floor(Math.min(9, Math.max(0, risk))); 
      })
    );
    setGrid(mockGrid);
  }, []);

  const getHeatmapColor = (riskLevel: number) => {
    if (riskLevel <= 1) return "bg-brand-teal/20 dark:bg-brand-teal/10";
    if (riskLevel <= 3) return "bg-brand-teal/40 dark:bg-brand-teal/20";
    if (riskLevel <= 5) return "bg-brand-teal/70 dark:bg-brand-teal/50";
    if (riskLevel <= 6) return "bg-brand-blue/50 dark:bg-brand-blue/40";
    if (riskLevel <= 7) return "bg-brand-magenta/40 dark:bg-amber-500/40 text-background"; // Keeping amber for warning
    if (riskLevel <= 8) return "bg-amber-500/70 dark:bg-amber-500/70 text-background";
    return "bg-red-500 dark:bg-red-600 text-white shadow-sm ring-1 ring-red-500/50"; // Max risk
  };

  return (
    <div className="bg-card rounded-xl border border-border p-6 shadow-sm" data-purpose="burnout-forecast">
      <div className="flex items-center justify-between mb-6">
        <div>
          <h3 className="text-sm font-bold text-foreground">Burnout Forecast</h3>
          <p className="text-xs text-muted-foreground">Fatigue risk visualization across fleet sectors</p>
        </div>
        <select className="text-xs border-border bg-background rounded-lg py-1 px-2 focus:ring-brand-blue/20 outline-none">
          <option>Next 24 Hours</option>
          <option>Next 48 Hours</option>
          <option>Historical (7d)</option>
        </select>
      </div>

      <div className="flex flex-col gap-[3px] flex-1 min-h-[140px] w-full mt-2">
        {grid.map((row, rowIndex) => (
          <div key={rowIndex} className="flex gap-[3px] flex-1">
            {row.map((risk, colIndex) => (
              <div 
                key={`${rowIndex}-${colIndex}`} 
                className={`flex-1 rounded-[2px] transition-colors hover:ring-1 hover:ring-foreground/50 cursor-crosshair ${getHeatmapColor(risk)}`}
                title={`Sector ${rowIndex + 1}, Block ${colIndex + 1} | Risk: ${risk}/9`}
              ></div>
            ))}
          </div>
        ))}
      </div>

      <div className="flex justify-between mt-4 text-[10px] text-muted-foreground uppercase font-bold tracking-wider">
        <span>00:00</span>
        <span>06:00</span>
        <span>12:00</span>
        <span>18:00</span>
        <span>23:59</span>
      </div>
    </div>
  );
}
