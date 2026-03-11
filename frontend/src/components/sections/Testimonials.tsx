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
        <div className="max-w-3xl mx-auto text-center mb-16">
          <h2 className="text-4xl md:text-5xl font-black mb-6 text-foreground tracking-tighter text-balance">
            {testimonials.title}
          </h2>
          <p className="text-xl text-muted-foreground leading-relaxed font-medium">
            {testimonials.description}
          </p>
        </div>

        {/* Masonry-style Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-8">
          {columns.map((column, colIndex) => (
            <div key={colIndex} className="flex flex-col gap-8">
              {column.map((item, i) => (
                <div 
                  key={i} 
                  className="glass-card p-10 rounded-[2.5rem] border border-black/5 dark:border-white/10 hover:shadow-2xl hover:shadow-brand-teal/5 transition-all duration-500 group"
                >
                  <p className="text-xl text-foreground/90 dark:text-white/90 leading-relaxed mb-10 font-medium italic">
                    "{item.quote}"
                  </p>
                  
                  <div className="flex items-center gap-4">
                    <div className="w-12 h-12 rounded-full bg-brand-teal/10 border border-brand-teal/20 flex items-center justify-center text-brand-teal font-black text-sm">
                      {item.avatar}
                    </div>
                    <div>
                      <h4 className="text-base font-bold text-foreground dark:text-white leading-none mb-1">
                        {item.author}
                      </h4>
                      <p className="text-xs text-muted-foreground dark:text-gray-400 font-bold uppercase tracking-widest">
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
