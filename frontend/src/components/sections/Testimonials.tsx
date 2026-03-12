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
    <SectionWrapper id="testimonials" variant="light">
      <SectionHeader 
        title={testimonials.title} 
        description={testimonials.description} 
        align="center" 
      />

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-10">
        {testimonials.items.map((item, i) => (
          <PremiumCard 
            key={i} 
            className="p-10 rounded-[3rem] flex flex-col h-full bg-white/70 border-white/50"
          >
            <p className="text-lg text-[#0f172a] leading-relaxed mb-10 font-medium tracking-tight flex-grow">
              "{item.quote}"
            </p>
            
            <div className="flex items-center gap-5 mt-auto">
              <div className="w-12 h-12 rounded-2xl bg-brand-teal/10 border border-brand-teal/20 flex items-center justify-center text-brand-teal font-black text-xs shadow-inner shrink-0">
                {item.avatar}
              </div>
              <div>
                <h4 className="text-base font-black text-[#0f172a] leading-none mb-1.5 tracking-tight uppercase">
                  {item.author}
                </h4>
                <p className="text-[9px] text-[#475569] font-black uppercase tracking-[0.2em]">
                  {item.role}
                </p>
              </div>
            </div>
          </PremiumCard>
        ))}
      </div>
    </SectionWrapper>
  );
}
