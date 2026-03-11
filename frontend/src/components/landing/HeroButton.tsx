import React from "react";

interface HeroButtonProps extends React.ButtonHTMLAttributes<HTMLButtonElement> {
  variant?: "primary" | "secondary";
  children: React.ReactNode;
}

export function HeroButton({ variant = "primary", children, className = "", ...props }: HeroButtonProps) {
  const baseStyles = "h-16 px-10 font-bold rounded-2xl transition-all flex items-center gap-3 active:scale-[0.97]";
  
  const variants = {
    primary: "bg-brand-teal hover:bg-brand-teal/90 text-white shadow-[0_20px_40px_-10px_rgba(20,184,166,0.3)] hover:scale-[1.03]",
    secondary: "glass-card text-foreground dark:text-white border border-black/5 dark:border-white/10 hover:bg-black/5 dark:hover:bg-white/5",
  };

  return (
    <button className={`${baseStyles} ${variants[variant]} ${className}`} {...props}>
      {children}
    </button>
  );
}
