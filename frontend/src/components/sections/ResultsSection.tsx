import { landingConfig } from "@/config/landing";

export function ResultsSection() {
  const { stats } = landingConfig;
  
  return (
    <section className="section-padding bg-brand-surface dark:bg-brand-deep-navy text-foreground dark:text-white relative overflow-hidden" id="results">
      {/* Grid Overlay */}
      <div className="absolute inset-0 grid-overlay opacity-5 dark:opacity-20 pointer-events-none"></div>
      
      <div className="container mx-auto px-6 relative z-10">
        <div className="text-center mb-20">
          <h2 className="text-4xl md:text-6xl font-black tracking-tighter mb-4 text-balance">
            {stats.title}
          </h2>
          <p className="text-muted-foreground dark:text-gray-400 font-medium text-lg">Measurable impact across the global logistics chain.</p>
        </div>
        
        <div className="grid md:grid-cols-3 gap-12">
          {stats.items.map((stat, i) => (
            <div key={i} className="text-center relative group">
              <div className="absolute inset-0 bg-brand-teal/5 dark:bg-brand-teal/10 blur-3xl opacity-0 group-hover:opacity-100 transition-opacity rounded-full"></div>
              <div className="relative">
                <div className={`text-6xl md:text-8xl font-black mb-4 font-mono text-brand-teal`}>
                  {stat.value}
                </div>
                <div className="text-muted-foreground dark:text-gray-300 font-bold uppercase tracking-widest text-sm">
                  {stat.label}
                </div>
              </div>
            </div>
          ))}
        </div>
        
        <div className="mt-24 pt-16 border-t border-black/5 dark:border-white/10 flex flex-col md:flex-row items-center justify-between gap-8">
          <div className="flex items-center gap-4">
             <div className="flex -space-x-3">
                {[1,2,3,4,5].map(i => (
                  <div key={i} className="w-12 h-12 rounded-full border-4 border-brand-surface dark:border-brand-deep-navy bg-muted dark:bg-brand-slate flex items-center justify-center text-sm font-bold shadow-sm">
                    {String.fromCharCode(64 + i)}
                  </div>
                ))}
              </div>
              <div>
                <p className="font-bold text-foreground dark:text-white">Join the Network</p>
                <p className="text-xs text-muted-foreground dark:text-gray-500">Over 12,000 operators connected daily.</p>
              </div>
          </div>
          <button className="px-8 py-4 glass-card hover:bg-black/5 dark:hover:bg-white/10 transition-all font-bold rounded-xl border border-black/10 dark:border-white/20 shadow-sm">
            Read Success Stories
          </button>
        </div>
      </div>
    </section>
  );
}
