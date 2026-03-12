import { SectionWrapper } from "../landing/SectionWrapper";
import { SectionHeader } from "../landing/SectionHeader";
import { AgentFlowDiagram } from "../shared/AgentFlowDiagram";

const tierDescriptions = [
  {
    label: "Governance",
    color: "text-slate-500",
    borderColor: "border-slate-500/20",
    description: "Ingestion Quality + PII Scrubber validate and sanitise all incoming telemetry before it enters the pipeline.",
  },
  {
    label: "Orchestration",
    color: "text-blue-500",
    borderColor: "border-blue-500/20",
    description: "The Orchestrator (LangGraph) routes events to the right Analysis agents and manages retries, priorities, and escalations.",
  },
  {
    label: "Analysis",
    color: "text-purple-500",
    borderColor: "border-purple-500/20",
    description: "Behavior, Sentiment, and Context agents score trips, detect fatigue, audit fairness, and enrich data with environmental signals.",
  },
  {
    label: "Action",
    color: "text-teal-500",
    borderColor: "border-teal-500/20",
    description: "Safety, Advocacy, and Coaching agents act on analysis — halting unsafe operations, resolving disputes, and delivering feedback.",
  },
];

export function AgentArchitectureSection() {
  return (
    <SectionWrapper id="architecture" variant="navy">
      <SectionHeader
        badge="Multi-Agent Design"
        title="How the Agents Think"
        description="Four tiers of autonomous agents collaborate to govern fleet operations — from raw telemetry to driver coaching."
        align="center"
      />

      {/* Flow diagram */}
      <div className="bg-white/5 rounded-2xl border border-white/10 p-8 mb-12 backdrop-blur-sm">
        <AgentFlowDiagram />
      </div>

      {/* Tier descriptions */}
      <div className="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-4 gap-6">
        {tierDescriptions.map((tier) => (
          <div
            key={tier.label}
            className={`bg-white/5 rounded-xl border ${tier.borderColor} p-6 backdrop-blur-sm`}
          >
            <p className={`text-[10px] font-black uppercase tracking-widest mb-3 ${tier.color}`}>
              {tier.label}
            </p>
            <p className="text-sm text-white/60 leading-relaxed">
              {tier.description}
            </p>
          </div>
        ))}
      </div>
    </SectionWrapper>
  );
}
