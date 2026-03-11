import { Linkedin, Twitter } from "lucide-react";
import Link from "next/link";

export function Footer() {
  return (
    <footer className="py-20 bg-muted/30 border-t border-border" data-purpose="main-footer">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-12 mb-16 text-foreground">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 bg-[image:var(--background-image-gradient-brand)] motif-fragment flex items-center justify-center">
                <div className="w-3 h-3 bg-background rounded-sm"></div>
              </div>
              <span className="text-xl font-bold tracking-tight">TraceData</span>
            </div>
            <p className="text-muted-foreground max-w-sm">
              Fragmenting the future of data orchestration to create a more coherent, efficient, and intelligent world.
            </p>
          </div>
          
          <div>
            <h5 className="font-bold text-foreground mb-6 uppercase text-xs tracking-widest">Company</h5>
            <ul className="space-y-4 text-sm text-muted-foreground">
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">About Us</Link>
              </li>
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">Careers</Link>
              </li>
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">Brand Identity</Link>
              </li>
              <li>
                <Link href="#" className="hover:text-foreground transition-colors">Contact</Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-bold text-foreground mb-6 uppercase text-xs tracking-widest">Connect</h5>
            <div className="flex gap-4 cursor-pointer text-muted-foreground">
              <div className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-brand-teal/10 hover:border-brand-teal hover:text-brand-teal transition-all">
                <span className="sr-only">LinkedIn</span>
                <Linkedin className="w-4 h-4" />
              </div>
              <div className="w-10 h-10 rounded-full border border-border flex items-center justify-center hover:bg-brand-blue/10 hover:border-brand-blue hover:text-brand-blue transition-all">
                <span className="sr-only">Twitter</span>
                <Twitter className="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-border text-[10px] text-muted-foreground uppercase tracking-[0.2em]">
          <p>© 2024 TraceData Systems. All Rights Reserved.</p>
          <div className="flex gap-8 mt-4 md:mt-0">
            <Link href="#" className="hover:text-foreground transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-foreground transition-colors">Security Protocols</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
