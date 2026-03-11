interface LandingBadgeProps {
  text: string;
  statusColor?: string;
  className?: string;
}

export function LandingBadge({ text, statusColor = "bg-brand-teal", className = "" }: LandingBadgeProps) {
  return (
    <div className={`inline-flex items-center gap-3 px-4 py-1.5 rounded-full bg-white/50 dark:bg-white/5 border border-black/5 dark:border-white/10 glass-card shadow-sm ${className}`}>
      <div className="relative flex h-2 w-2">
        <span className={`animate-ping absolute inline-flex h-full w-full rounded-full ${statusColor} opacity-75`}></span>
        <span className={`relative inline-flex rounded-full h-2 w-2 ${statusColor} shadow-[0_0_8px_rgba(20,184,166,0.5)]`}></span>
      </div>
      <span className="text-[10px] font-black text-foreground dark:text-white uppercase tracking-[0.2em]">
        {text}
      </span>
    </div>
  );
}
