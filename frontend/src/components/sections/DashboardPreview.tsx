export function DashboardPreview() {
  return (
    <section className="py-24 overflow-hidden" data-purpose="dashboard-preview">
      <div className="container mx-auto px-6">
        <div className="flex flex-col lg:flex-row items-center gap-16">
          <div className="lg:w-1/3">
            <h2 className="text-sm font-bold text-brand-blue uppercase tracking-[0.3em] mb-4">
              Intervention Hub
            </h2>
            <h3 className="text-4xl font-bold mb-6 fragmented-header text-white">
              Human-In-The-Loop Center
            </h3>
            <p className="text-white/60 mb-8 leading-relaxed">
              Empowering operators with the ability to override AI logic. Our Mission Control features a dedicated Appeals workflow and Coaching intervention system for high-stakes decision auditing.
            </p>
            <ul className="space-y-4">
              <li className="flex items-center gap-3 text-sm text-white">
                <span className="w-2 h-2 rounded-full bg-brand-magenta"></span>
                One-click Appeals for AI Routing Decisions
              </li>
              <li className="flex items-center gap-3 text-sm text-white">
                <span className="w-2 h-2 rounded-full bg-brand-blue"></span>
                Real-time Coaching Intervention Popups
              </li>
              <li className="flex items-center gap-3 text-sm text-white">
                <span className="w-2 h-2 rounded-full bg-white"></span>
                Transparency Logs for Ethical Compliance
              </li>
            </ul>
          </div>
          
          <div className="lg:w-2/3 relative">
            <div className="bg-brand-slate border-4 border-white/10 rounded-3xl overflow-hidden shadow-2xl relative">
              <div className="h-8 bg-white/5 flex items-center px-4 gap-2">
                <div className="w-2 h-2 rounded-full bg-red-500/50"></div>
                <div className="w-2 h-2 rounded-full bg-yellow-500/50"></div>
                <div className="w-2 h-2 rounded-full bg-green-500/50"></div>
              </div>
              {/* eslint-disable-next-line @next/next/no-img-element */}
              <img
                alt="Mission Control Dashboard Preview"
                className="w-full"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuAr3RmLOAdG-PuFQCmbApOcasUYfhSRZ3o7DWqb5d4IJzB97gWL0ES7yHyy32F4K4-ytadITRVBb5GYm29HEYBN4tr-8PiC6Ij27tWIiylFxPN06eTBH0KOos2cAIu6B15jjAFsdBY-2buzS0uPZ_8hONmYg4_NCDbgErQ74A5h_uLHqqaLcqA6bHuGf8V7Wl48K3JXMun1Oqj_Z2_gFjZwLpOWzElorsivU3ZWywbYUmKacwGwveUNc5M6DtPVe6ZTJjG-JeKVFh2U"
              />
            </div>
            
            <div className="absolute -bottom-10 -right-10 w-40 h-40 bg-[image:var(--background-image-gradient-brand)] motif-fragment opacity-40 blur-lg -z-10"></div>
          </div>
        </div>
      </div>
    </section>
  );
}
