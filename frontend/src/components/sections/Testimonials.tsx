import { landingConfig } from "@/config/landing";
import { SectionHeader } from "../landing/SectionHeader";
import { PremiumCard } from "../landing/PremiumCard";
import { SectionWrapper } from "../landing/SectionWrapper";

export function Testimonials() {
  const { testimonials } = landingConfig;
  
  // Split testimonials into 3 columns for desktop masonry effect
  const col1 = [testimonials.items[0], testimonials.items[3]];
  const col2 = [testimonials.items[1], testimonials.items[4]];
  const col3 = [testimonials.items[2], testimonials.items[5]];

  const columns = [col1, col2, col3];

  return (
    <SectionWrapper id="testimonials">
      <SectionHeader 
        title={testimonials.title} 
        description={testimonials.description} 
        align="center" 
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
        {columns.map((column, colIndex) => (
          <div key={colIndex} className="flex flex-col gap-10">
            {column.map((item, i) => (
              <PremiumCard 
                key={i} 
                className="p-12 rounded-[3.5rem]"
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
              </PremiumCard>
            ))}
          </div>
        ))}
      </div>
    </SectionWrapper>
  );
}
