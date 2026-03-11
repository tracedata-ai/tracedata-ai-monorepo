import Link from "next/link";
import { Linkedin, Twitter } from "lucide-react";

export function Footer() {
  return (
    <footer className="py-20 bg-brand-deep-navy border-t border-white/5" data-purpose="main-footer">
      <div className="container mx-auto px-6">
        <div className="grid md:grid-cols-4 gap-12 mb-16 text-white">
          <div className="col-span-1 md:col-span-2">
            <div className="flex items-center gap-2 mb-6">
              <div className="w-8 h-8 bg-[image:var(--background-image-gradient-brand)] motif-fragment flex items-center justify-center">
                <div className="w-3 h-3 bg-brand-deep-navy rounded-sm"></div>
              </div>
              <span className="text-xl font-bold tracking-tight">TraceData</span>
            </div>
            <p className="text-white/40 max-w-sm">
              Fragmenting the future of data orchestration to create a more coherent, efficient, and intelligent world.
            </p>
          </div>
          
          <div>
            <h5 className="font-bold text-white mb-6 uppercase text-xs tracking-widest">Company</h5>
            <ul className="space-y-4 text-sm text-white/50">
              <li>
                <Link href="#" className="hover:text-white transition-colors">About Us</Link>
              </li>
              <li>
                <Link href="#" className="hover:text-white transition-colors">Careers</Link>
              </li>
              <li>
                <Link href="#" className="hover:text-white transition-colors">Brand Identity</Link>
              </li>
              <li>
                <Link href="#" className="hover:text-white transition-colors">Contact</Link>
              </li>
            </ul>
          </div>
          
          <div>
            <h5 className="font-bold text-white mb-6 uppercase text-xs tracking-widest">Connect</h5>
            <div className="flex gap-4 cursor-pointer text-white/40">
              <div className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-brand-magenta/20 hover:text-white transition-all">
                <span className="sr-only">LinkedIn</span>
                <Linkedin className="w-4 h-4" />
              </div>
              <div className="w-10 h-10 rounded-full border border-white/10 flex items-center justify-center hover:bg-brand-blue/20 hover:text-white transition-all">
                <span className="sr-only">Twitter</span>
                <Twitter className="w-4 h-4" />
              </div>
            </div>
          </div>
        </div>
        
        <div className="flex flex-col md:flex-row justify-between items-center pt-8 border-t border-white/5 text-[10px] text-white/30 uppercase tracking-[0.2em]">
          <p>© 2024 TraceData Systems. All Rights Reserved.</p>
          <div className="flex gap-8 mt-4 md:mt-0">
            <Link href="#" className="hover:text-white/50 transition-colors">Privacy Policy</Link>
            <Link href="#" className="hover:text-white/50 transition-colors">Security Protocols</Link>
          </div>
        </div>
      </div>
    </footer>
  );
}
