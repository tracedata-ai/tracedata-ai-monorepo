export function HumanInTheLoop() {
  return (
    <section className="py-24 bg-[image:var(--background-image-mission-control)]" data-purpose="human-in-the-loop">
      <div className="container mx-auto px-6 text-center">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-sm font-bold text-brand-magenta uppercase tracking-[0.3em] mb-4">
            Human & AI Harmony
          </h2>
          <h3 className="text-4xl md:text-5xl font-bold mb-8 fragmented-header text-white">
            Human-In-The-Loop Governance
          </h3>
          <p className="text-xl text-white/70 mb-12">
            Technology doesn&apos;t replace intuition; it amplifies it. Our XAI system provides &apos;explainable&apos; insights, allowing human operators to override and fine-tune complex decisions with complete context.
          </p>
          
          <div className="inline-flex flex-col md:flex-row gap-8 items-center bg-brand-deep-navy/50 p-8 rounded-3xl border border-white/10 backdrop-blur-xl">
            <div className="text-center md:text-left">
              <span className="block text-4xl font-bold text-brand-blue">SHAP</span>
              <span className="text-xs uppercase tracking-widest text-white/40">Feature Attribution</span>
            </div>
            <div className="w-12 h-px md:w-px md:h-12 bg-white/20"></div>
            <div className="text-center md:text-left">
              <span className="block text-4xl font-bold text-brand-magenta">0.88</span>
              <span className="text-xs uppercase tracking-widest text-white/40">Fleet Equilibrium Score</span>
            </div>
            <div className="w-12 h-px md:w-px md:h-12 bg-white/20"></div>
            <div className="text-center md:text-left">
              <span className="block text-4xl font-bold text-white">XAI</span>
              <span className="text-xs uppercase tracking-widest text-white/40">Explainability Depth</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
