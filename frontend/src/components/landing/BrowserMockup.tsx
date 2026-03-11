import React from "react";

interface BrowserMockupProps {
  src: string;
  alt: string;
  className?: string;
}

export function BrowserMockup({ src, alt, className = "" }: BrowserMockupProps) {
  return (
    <div className={`glass-card p-3 rounded-[3rem] border border-black/[0.05] dark:border-white/[0.05] shadow-[0_60px_100px_-20px_rgba(0,0,0,0.2)] dark:shadow-[0_60px_100px_-20px_rgba(0,0,0,0.6)] relative z-10 transition-transform duration-700 hover:scale-[1.02] bg-white/50 dark:bg-white/[0.03] ${className}`}>
      <div className="h-12 bg-black/5 dark:bg-white/5 rounded-t-[2.2rem] flex items-center px-8 gap-3 mb-3 border-b border-black/[0.03] dark:border-white/[0.03]">
        <div className="w-3 h-3 rounded-full bg-red-400 opacity-40"></div>
        <div className="w-3 h-3 rounded-full bg-yellow-400 opacity-40"></div>
        <div className="w-3 h-3 rounded-full bg-green-400 opacity-40"></div>
        <div className="ml-6 h-5 w-40 bg-black/5 dark:bg-white/5 rounded-full"></div>
      </div>
      
      <div className="relative rounded-b-[2.2rem] overflow-hidden border-t border-black/[0.03] dark:border-white/[0.03]">
        {/* eslint-disable-next-line @next/next/no-img-element */}
        <img
          alt={alt}
          className="w-full grayscale-[10%] hover:grayscale-0 transition-all duration-1000"
          src={src}
        />
        <div className="absolute inset-0 bg-gradient-to-t from-black/20 to-transparent pointer-events-none"></div>
      </div>
    </div>
  );
}
