import Image from "next/image";

export function HeroSection() {
  return (
    <section className="relative min-h-screen flex items-center pt-20 overflow-hidden" data-purpose="hero-section" id="hero">
      <div className="absolute inset-0 grid-overlay -z-10"></div>
      <div className="absolute top-1/4 -right-20 w-96 h-96 bg-brand-magenta/20 blur-[120px] rounded-full"></div>
      <div className="absolute bottom-1/4 -left-20 w-96 h-96 bg-brand-blue/20 blur-[120px] rounded-full"></div>
      
      <div className="container mx-auto px-6 grid lg:grid-cols-2 gap-12 items-center">
        <div data-purpose="hero-content">
          <h1 className="text-6xl md:text-7xl font-extrabold mb-6 leading-tight fragmented-header text-white">
            INTELLIGENT{" "}
            <span className="text-transparent bg-clip-text bg-[image:var(--background-image-gradient-brand)]">
              FLEET
            </span>{" "}
            ORCHESTRATION
          </h1>
          <p className="text-xl text-white/70 mb-10 max-w-xl leading-relaxed">
            Fragmented data points coalescing into a coherent structure. TraceData leverages XAI metrics to harmonize global logistics in real-time.
          </p>
          
          <div className="flex flex-wrap gap-4">
            <button className="px-8 py-4 bg-white text-brand-deep-navy font-bold rounded-lg hover:bg-brand-light-gray transition-colors">
              Launch Dashboard
            </button>
            <button className="px-8 py-4 border border-white/20 text-white hover:bg-white/5 rounded-lg transition-colors font-semibold">
              Watch Identity Film
            </button>
          </div>
          
          {/* XAI Metrics Small Card */}
          <div className="mt-12 p-4 bg-brand-slate/50 border border-white/10 rounded-xl backdrop-blur-sm flex items-center gap-6 max-w-md">
            <div className="flex flex-col">
              <span className="text-[10px] text-brand-magenta font-bold uppercase tracking-widest">
                Active Orchestration
              </span>
              <span className="text-2xl font-mono text-white">
                99.98<span className="text-brand-blue text-sm">%</span>
              </span>
            </div>
            <div className="h-10 w-px bg-white/10"></div>
            <div className="flex flex-col">
              <span className="text-[10px] text-brand-blue font-bold uppercase tracking-widest">
                Latency
              </span>
              <span className="text-2xl font-mono text-white">
                12<span className="text-brand-magenta text-sm">ms</span>
              </span>
            </div>
            <div className="h-10 w-px bg-white/10"></div>
            <div className="flex-grow flex justify-end">
              <div className="flex gap-1 items-end h-8">
                <div className="w-1 bg-brand-magenta h-4"></div>
                <div className="w-1 bg-brand-blue h-6"></div>
                <div className="w-1 bg-brand-magenta h-8"></div>
                <div className="w-1 bg-brand-blue h-5"></div>
              </div>
            </div>
          </div>
        </div>
        
        {/* Hero Visual */}
        <div className="relative group" data-purpose="hero-visual">
          <div className="absolute -inset-4 bg-[image:var(--background-image-gradient-brand)] opacity-20 blur-xl group-hover:opacity-30 transition-opacity"></div>
          {/* eslint-disable-next-line @next/next/no-img-element */}
          <img
            alt="High-tech XAI metrics visualization"
            className="relative rounded-2xl border border-white/10 shadow-2xl w-full object-cover"
            src="https://lh3.googleusercontent.com/aida-public/AB6AXuDDGW_Ial_icBZQUtxVNE5rxHPcUVm1r6XR2lpzlzksi2bub6VthpXrFSpKYMj7LP7C7TDP-LJJaKEvBATgJKTDecPz666JgtV8hUYNTI3qAhoObk57E3nxtK_UrYh_QZQ0cOl6isBTWkyg8lELV029x1SM_I1I8g2dFiQj_W4DpvAh5BI1HvtPPVi1IPVTT_jvbIcZFztInCI5qbWhVVa0AyocH3-3pXp30t8AxhWlpLmYPPvhDrmsGk23XYenX10BaVhll1U5616L"
          />
        </div>
      </div>
    </section>
  );
}
