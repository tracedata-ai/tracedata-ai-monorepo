import { LandingBadge } from "./LandingBadge";

interface SectionHeaderProps {
  badge?: string;
  title: string;
  description?: string;
  align?: "left" | "center";
  className?: string;
}

export function SectionHeader({ badge, title, description, align = "left", className = "" }: SectionHeaderProps) {
  const alignmentClass = align === "center" ? "text-center mx-auto" : "text-left";
  
  return (
    <div className={`max-w-4xl mb-24 ${alignmentClass} ${className}`}>
      {badge && <LandingBadge text={badge} className="mb-8" />}
      <h2 className="text-5xl md:text-8xl font-black tracking-[-0.04em] mb-6 text-balance leading-[0.9]">
        {title}
      </h2>
      {description && (
        <p className="text-xl md:text-2xl text-muted-foreground dark:text-white/40 font-medium tracking-tight">
          {description}
        </p>
      )}
    </div>
  );
}
