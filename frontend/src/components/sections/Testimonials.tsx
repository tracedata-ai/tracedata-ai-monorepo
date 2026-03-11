import { landingConfig } from "@/config/landing";

export function Testimonials() {
  const { testimonials } = landingConfig;
  
  // Split testimonials into 3 columns for desktop masonry effect
  const col1 = [testimonials.items[0], testimonials.items[3]];
  const col2 = [testimonials.items[1], testimonials.items[4]];
  const col3 = [testimonials.items[2], testimonials.items[5]];

  const columns = [col1, col2, col3];

  return (
    <section className="section-padding bg-background relative overflow-hidden" id="testimonials">
      <div className="container mx-auto px-6">
        <div className="max-w-4xl mx-auto text-center mb-24">
          <h2 className="text-5xl md:text-[6rem] font-black mb-8 text-foreground dark:text-white tracking-[-0.04em] text-balance leading-[0.85]">
            {testimonials.title}
          </h2>
          <p className="text-xl md:text-2xl text-muted-foreground dark:text-white/40 leading-relaxed font-medium tracking-tight">
            {testimonials.description}
          </p>
        </div>

        {/* Masonry-style Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
          {columns.map((column, colIndex) => (
            <div key={colIndex} className="flex flex-col gap-10">
              {column.map((item, i) => (
                <div 
                  key={i} 
                  className="glass-card p-12 rounded-[3.5rem] border border-black/[0.03] dark:border-white/[0.03] hover:shadow-[0_40px_80px_-20px_rgba(0,0,0,0.15)] transition-all duration-700 group hover:-translate-y-3"
                >
                  <p className="text-2xl text-foreground dark:text-white/90 leading-[1.4] mb-12 font-medium tracking-tight">
                    "{item.quote}"
                  </p>
                  
                  <div className="flex items-center gap-5">
                    <div className="w-14 h-14 rounded-[1.25rem] bg-brand-teal/10 dark:bg-white/5 border border-brand-teal/20 dark:border-white/10 flex items-center justify-center text-brand-teal font-black text-xs shadow-inner">
                      {item.avatar}
                    </div>
                    <div>
                      <h4 className="text-lg font-black text-foreground dark:text-white leading-none mb-1.5 tracking-tight uppercase">
                        {item.author}
                      </h4>
                      <p className="text-[10px] text-muted-foreground dark:text-white/30 font-black uppercase tracking-[0.2em]">
                        {item.role}
                      </p>
                    </div>
                  </div>
                </div>
              ))}
            </div>
          ))}
        </div>
      </div>
      
      {/* Background decoration */}
      <div className="absolute top-1/2 left-0 -translate-y-1/2 w-96 h-96 bg-brand-teal/5 blur-[120px] -z-10 rounded-full"></div>
      <div className="absolute bottom-0 right-0 w-96 h-96 bg-brand-blue/5 blur-[120px] -z-10 rounded-full"></div>
    </section>
  );
}
