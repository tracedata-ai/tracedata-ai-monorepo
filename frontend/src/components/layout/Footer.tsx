import { Linkedin, Twitter } from "lucide-react";
import Link from "next/link";
import { landingConfig } from "@/config/landing";

export function Footer() {
  const { footer, navbar } = landingConfig;
  
  return (
    <footer className="py-20 bg-muted/30 border-t border-border" data-purpose="main-footer">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-12 mb-16 text-foreground">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 bg-[image:var(--background-image-gradient-brand)] motif-fragment flex items-center justify-center">
                <div className="w-3 h-3 bg-background rounded-sm"></div>
              </div>
              <span className="text-xl font-bold tracking-tight">
                {navbar.logo.prefix}{navbar.logo.highlight}
              </span>
            </div>
            <p className="text-muted-foreground max-w-sm">
              {footer.description}
            </p>
          </div>
          
          {footer.links.map((linkGroup, i) => (
            <div key={i}>
              <h5 className="font-bold text-foreground mb-6 uppercase text-xs tracking-widest">
                {linkGroup.title}
              </h5>
              <ul className="space-y-4 text-sm text-muted-foreground">
                {linkGroup.items.map((item, j) => (
                  <li key={j}>
                    <Link href={item.href} className="hover:text-foreground transition-colors">
                      {item.label}
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
          ))}
          
          <div>
            <h5 className="font-bold text-foreground mb-6 uppercase text-xs tracking-widest">Connect</h5>
            <div className="flex gap-4 cursor-pointer text-muted-foreground">
              {footer.socials.map((social, i) => {
                const isLinkedIn = social.platform === "LinkedIn";
                const hoverClass = isLinkedIn 
                  ? "hover:bg-brand-teal/10 hover:border-brand-teal hover:text-brand-teal" 
                  : "hover:bg-brand-blue/10 hover:border-brand-blue hover:text-brand-blue";
                
                return (
                  <Link key={i} href={social.href} className={`w-10 h-10 rounded-full border border-border flex items-center justify-center transition-all ${hoverClass}`}>
                    <span className="sr-only">{social.platform}</span>
                    {isLinkedIn ? <Linkedin className="w-4 h-4" /> : <Twitter className="w-4 h-4" />}
                  </Link>
                );
              })}
            </div>
          </div>
        </div>
        
        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-border text-[10px] text-muted-foreground uppercase tracking-[0.2em]">
          <p>{footer.copyright}</p>
          <div className="flex gap-8 mt-4 md:mt-0">
            {footer.legalLinks.map((link, i) => (
              <Link key={i} href={link.href} className="hover:text-foreground transition-colors">
                {link.label}
              </Link>
            ))}
          </div>
        </div>
      </div>
    </footer>
  );
}
