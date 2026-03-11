import { ShieldAlert, Scale, BrainCircuit, Activity, HeartHandshake, Smile, GraduationCap, Network } from "lucide-react";

export function EcosystemSection() {
  return (
    <>
      <section className="py-24 bg-brand-slate/30 relative" data-purpose="ecosystem-section">
        <div className="container mx-auto px-6">
          <div className="text-center mb-16">
            <h2 className="text-sm font-bold text-brand-magenta uppercase tracking-[0.3em] mb-4">
              The Digital Ecosystem
            </h2>
            <h3 className="text-4xl md:text-5xl font-bold fragmented-header text-white">
              8-Agent Intelligent Network
            </h3>
          </div>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-6 text-white">
            {/* Safety Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-magenta/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-magenta/10 rounded-lg flex items-center justify-center group-hover:bg-brand-magenta/20 transition-colors">
                <ShieldAlert className="w-6 h-6 text-brand-magenta" />
              </div>
              <h4 className="font-bold text-lg mb-2">Safety Agent</h4>
              <p className="text-sm text-white/50">Enforces operational guardrails and risk mitigation protocols.</p>
            </div>
            
            {/* Fairness Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-blue/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-blue/10 rounded-lg flex items-center justify-center group-hover:bg-brand-blue/20 transition-colors">
                <Scale className="w-6 h-6 text-brand-blue" />
              </div>
              <h4 className="font-bold text-lg mb-2">Fairness Agent</h4>
              <p className="text-sm text-white/50">Audits algorithmic bias in routing and load distribution.</p>
            </div>
            
            {/* Context Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-magenta/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-magenta/10 rounded-lg flex items-center justify-center group-hover:bg-brand-magenta/20 transition-colors">
                <Network className="w-6 h-6 text-brand-magenta" />
              </div>
              <h4 className="font-bold text-lg mb-2">Context Agent</h4>
              <p className="text-sm text-white/50">Synthesizes environmental and historical data streams.</p>
            </div>
            
            {/* Behavior Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-blue/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-blue/10 rounded-lg flex items-center justify-center group-hover:bg-brand-blue/20 transition-colors">
                <BrainCircuit className="w-6 h-6 text-brand-blue" />
              </div>
              <h4 className="font-bold text-lg mb-2">Behavior Agent</h4>
              <p className="text-sm text-white/50">Analyzes operator performance and cognitive load patterns.</p>
            </div>
            
            {/* Advocacy Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-magenta/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-magenta/10 rounded-lg flex items-center justify-center group-hover:bg-brand-magenta/20 transition-colors">
                <HeartHandshake className="w-6 h-6 text-brand-magenta" />
              </div>
              <h4 className="font-bold text-lg mb-2">Advocacy Agent</h4>
              <p className="text-sm text-white/50">Represents human operator interests in the AI decision loop.</p>
            </div>
            
            {/* Sentiment Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-blue/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-blue/10 rounded-lg flex items-center justify-center group-hover:bg-brand-blue/20 transition-colors">
                <Smile className="w-6 h-6 text-brand-blue" />
              </div>
              <h4 className="font-bold text-lg mb-2">Sentiment Agent</h4>
              <p className="text-sm text-white/50">Real-time morale tracking and wellness signaling.</p>
            </div>
            
            {/* Coaching Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-magenta/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-magenta/10 rounded-lg flex items-center justify-center group-hover:bg-brand-magenta/20 transition-colors">
                <GraduationCap className="w-6 h-6 text-brand-magenta" />
              </div>
              <h4 className="font-bold text-lg mb-2">Coaching Agent</h4>
              <p className="text-sm text-white/50">Delivers interventions and performance-enhancing insights.</p>
            </div>
            
            {/* Orchestrator Agent */}
            <div className="p-8 bg-brand-deep-navy border border-white/5 rounded-2xl hover:border-brand-blue/50 transition-all cursor-pointer group">
              <div className="w-12 h-12 mb-6 bg-brand-blue/10 rounded-lg flex items-center justify-center group-hover:bg-brand-blue/20 transition-colors">
                <Activity className="w-6 h-6 text-brand-blue" />
              </div>
              <h4 className="font-bold text-lg mb-2">Orchestrator</h4>
              <p className="text-sm text-white/50">Synchronizes multi-agent workflows via LangGraph protocols.</p>
            </div>
          </div>
        </div>
      </section>

      <section className="py-24 bg-brand-deep-navy border-y border-white/5">
        <div className="container mx-auto px-6">
          <div className="grid lg:grid-cols-2 gap-16 items-center">
            <div className="relative">
              <div className="bg-brand-slate/40 p-1 rounded-3xl border border-white/10">
                {/* eslint-disable-next-line @next/next/no-img-element */}
                <img
                  alt="LangGraph Data Flow"
                  className="rounded-2xl w-full object-cover"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuDj8k8oBK_V3cKPuQDAArogNGh65bncmkSRi9KiUmJteASqPSaGNsf7fkElyp0GfhPogrjn6Y4_8eJSPcjpZ_Q5-WB7DHnicPdsVzPAiLjJpSXD6TIAx5RaRwFh1e_gp9xJs-tq_0Bdx4Jy5mVkGXv2z8UsBLPHx9IUyM1zy5uIx5hC-6NeJONz_eq0bczQNku9FzAQ6IpvDc86-Z887xbhW4ca6tSixBhOrj_yfO7UCO83OFtER0N75TPD-MUDtvqrT7_iJxgrYQUG"
                />
              </div>
              <div className="absolute -top-6 -left-6 px-4 py-2 bg-brand-blue rounded-full text-xs font-bold uppercase tracking-widest text-white">
                Real-Time Engine
              </div>
            </div>
            
            <div>
              <h2 className="text-sm font-bold text-brand-blue uppercase tracking-[0.3em] mb-4">
                LangGraph & Kafka
              </h2>
              <h3 className="text-4xl font-bold mb-6 fragmented-header text-white">
                Unified Event Orchestration
              </h3>
              <p className="text-white/60 mb-8">
                Every data point is a message in a high-throughput Kafka stream, processed through dynamic LangGraph workflows. Decisions are not static; they are conversational, evolving paths between 8 specialized agents.
              </p>
              
              <div className="space-y-6">
                <div className="flex items-start gap-4">
                  <Activity className="w-6 h-6 text-brand-magenta shrink-0" />
                  <div>
                    <h5 className="font-bold text-white">Sub-100ms Latency</h5>
                    <p className="text-sm text-white/50">Stream processing at the edge for immediate recalibration.</p>
                  </div>
                </div>
                <div className="flex items-start gap-4">
                  <Activity className="w-6 h-6 text-brand-blue shrink-0" />
                  <div>
                    <h5 className="font-bold text-white">Stateful Persistence</h5>
                    <p className="text-sm text-white/50">Every agent decision is logged and traceable through our event ledger.</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>
    </>
  );
}
