import Link from "next/link";
import { ArrowRight } from "lucide-react";

export function Navbar() {
  return (
    <nav
      className="fixed top-0 w-full z-50 bg-brand-deep-navy/80 backdrop-blur-md border-b border-white/10"
      data-purpose="main-nav"
    >
      <div className="container mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {/* Logo motif */}
          <div className="w-10 h-10 bg-[image:var(--background-image-gradient-brand)] motif-fragment flex items-center justify-center">
            <div className="w-4 h-4 bg-brand-deep-navy rounded-sm"></div>
          </div>
          <span className="text-2xl font-bold tracking-tight text-white">
            Trace<span className="text-brand-blue">Data</span>
          </span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-semibold uppercase tracking-widest text-white/70">
          <Link href="#" className="hover:text-brand-magenta transition-colors">
            Ecosystem
          </Link>
          <Link href="#" className="hover:text-brand-magenta transition-colors">
            Mission Control
          </Link>
          <Link href="#" className="hover:text-brand-magenta transition-colors">
            Human-XAI
          </Link>
          <Link href="#" className="hover:text-brand-magenta transition-colors">
            Solutions
          </Link>
        </div>
        
        <button className="px-6 py-2 bg-[image:var(--background-image-gradient-brand)] rounded-full font-bold text-sm uppercase text-white tracking-wider hover:opacity-90 transition-opacity flex items-center gap-2">
          Get Started
        </button>
      </div>
    </nav>
  );
}
