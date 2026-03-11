import Link from "next/link";
import { landingConfig } from "@/config/landing";

export function Navbar() {
  const { navbar } = landingConfig;
  
  return (
    <nav
      className="fixed top-0 w-full z-50 bg-background/80 backdrop-blur-md border-b border-border"
      data-purpose="main-nav"
    >
      <div className="container mx-auto px-6 h-20 flex items-center justify-between">
        <div className="flex items-center gap-2">
          {/* Logo motif */}
          <div className="w-10 h-10 bg-[image:var(--background-image-gradient-brand)] motif-fragment flex items-center justify-center">
            <div className="w-4 h-4 bg-background rounded-sm"></div>
          </div>
          <span className="text-2xl font-bold tracking-tight text-foreground">
            {navbar.logo.prefix}<span className="text-brand-blue">{navbar.logo.highlight}</span>
          </span>
        </div>
        
        <div className="hidden md:flex items-center gap-8 text-sm font-semibold uppercase tracking-widest text-muted-foreground">
          {navbar.links.map((link, i) => (
            <Link key={i} href={link.href} className="hover:text-brand-teal transition-colors">
              {link.label}
            </Link>
          ))}
        </div>
        
        <Link href="/login" className="px-6 py-2 bg-[image:var(--background-image-gradient-brand)] rounded-full font-bold text-sm uppercase text-white tracking-wider hover:opacity-90 transition-opacity flex items-center gap-2">
          {navbar.cta}
        </Link>
      </div>
    </nav>
  );
}
