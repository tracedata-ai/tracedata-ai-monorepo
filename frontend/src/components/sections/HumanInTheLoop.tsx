export function HumanInTheLoop() {
  return (
    <section className="py-24 bg-card relative overflow-hidden" data-purpose="human-in-the-loop">
      {/* Dynamic Background */}
      <div className="absolute inset-0 bg-[image:var(--background-image-mission-control)] opacity-5 dark:opacity-100 mix-blend-multiply dark:mix-blend-normal pointer-events-none transition-opacity"></div>
      
      <div className="container mx-auto px-6 text-center relative pointer-events-auto">
        <div className="max-w-3xl mx-auto">
          <h2 className="text-sm font-bold text-brand-teal uppercase tracking-[0.3em] mb-4">
            Human & AI Harmony
          </h2>
          <h3 className="text-4xl md:text-5xl font-bold mb-8 fragmented-header text-foreground">
            Human-In-The-Loop Governance
          </h3>
          <p className="text-xl text-muted-foreground mb-12">
            Technology doesn&apos;t replace intuition; it amplifies it. Our XAI system provides &apos;explainable&apos; insights, allowing human operators to override and fine-tune complex decisions with complete context.
          </p>
          
          <div className="inline-flex flex-col md:flex-row gap-8 items-center bg-background/80 p-8 rounded-3xl border border-border shadow-lg backdrop-blur-xl">
            <div className="text-center md:text-left">
              <span className="block text-4xl font-bold text-brand-blue">SHAP</span>
              <span className="text-xs uppercase tracking-widest text-muted-foreground">Feature Attribution</span>
            </div>
            <div className="w-12 h-px md:w-px md:h-12 bg-border"></div>
            <div className="text-center md:text-left">
              <span className="block text-4xl font-bold text-brand-teal">0.88</span>
              <span className="text-xs uppercase tracking-widest text-muted-foreground">Fleet Equilibrium Score</span>
            </div>
            <div className="w-12 h-px md:w-px md:h-12 bg-border"></div>
            <div className="text-center md:text-left">
              <span className="block text-4xl font-bold text-foreground">XAI</span>
              <span className="text-xs uppercase tracking-widest text-muted-foreground">Explainability Depth</span>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}
