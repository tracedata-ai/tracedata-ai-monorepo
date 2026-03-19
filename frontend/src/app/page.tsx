import Link from "next/link";
import {
  ArrowRight,
  BarChart3,
  Gauge,
  GitBranch,
  Network,
  Scale,
  Shield,
  Siren,
  Sparkles,
  Workflow,
} from "lucide-react";

const agents = [
  {
    title: "Safety Agent",
    description:
      "Monitors hard braking, overspeed, and collision proximity in real-time.",
    icon: Shield,
  },
  {
    title: "Fairness Agent",
    description: "Audits assignment logic for equitable workload distribution.",
    icon: Scale,
  },
  {
    title: "Context Agent",
    description:
      "Correlates traffic, weather, and route context with driving behavior.",
    icon: Workflow,
  },
  {
    title: "Performance Agent",
    description:
      "Optimizes route execution, fuel efficiency, and fleet throughput.",
    icon: Gauge,
  },
  {
    title: "Compliance Agent",
    description:
      "Automates audit trails and policy-grade reporting for each trip.",
    icon: Siren,
  },
  {
    title: "Integrity Agent",
    description:
      "Detects telemetry anomalies and potential data tampering patterns.",
    icon: Sparkles,
  },
  {
    title: "Network Agent",
    description:
      "Maintains resilient edge-to-cloud synchronization for connected fleets.",
    icon: Network,
  },
  {
    title: "Analytics Agent",
    description:
      "Synthesizes fleet-wide trends for operational and strategic insights.",
    icon: BarChart3,
  },
];

export default function HomePage() {
  return (
    <div className="min-h-screen bg-[#0c1030] text-[#dfe0ff]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(112,210,255,0.18),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(192,128,255,0.14),transparent_30%)]" />

      <nav className="sticky top-0 z-50 border-b border-[#3d484f]/30 bg-[#0c1030]/90 backdrop-blur">
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-6">
            <p className="text-xl font-bold tracking-tighter text-[#70d2ff]">
              TraceData
            </p>
            <div className="hidden gap-6 text-sm md:flex">
              <a className="border-b-2 border-[#70d2ff] pb-1 text-[#70d2ff]">
                Platform
              </a>
              <a className="text-[#bdc8d0] hover:text-white">Docs</a>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-lg px-4 py-2 text-sm text-[#bdc8d0] transition-colors hover:text-white"
            >
              Login
            </Link>
            <Link
              href="/login"
              className="rounded-lg bg-gradient-to-br from-[#70d2ff] to-[#00aadd] px-5 py-2 text-sm font-semibold text-[#003547] transition-opacity hover:opacity-90"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <header className="relative overflow-hidden pt-14">
        <div className="mx-auto grid w-full max-w-7xl grid-cols-1 gap-12 px-6 pb-24 pt-10 lg:grid-cols-2 lg:items-center">
          <div className="space-y-8">
            <div className="inline-flex items-center gap-2 rounded-full border border-[#70d2ff]/25 bg-[#2792ff]/15 px-3 py-1 text-xs uppercase tracking-[0.18em] text-[#70d2ff]">
              <span className="relative flex h-2 w-2">
                <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-[#70d2ff] opacity-75" />
                <span className="relative inline-flex h-2 w-2 rounded-full bg-[#70d2ff]" />
              </span>
              Live Deployment v4.2.0
            </div>

            <h1 className="text-5xl font-black leading-[0.95] tracking-tight text-white md:text-7xl">
              Intelligent
              <br />
              <span className="bg-gradient-to-r from-[#70d2ff] via-[#70d2ff] to-[#a5c8ff] bg-clip-text text-transparent">
                Fleet Orchestration
              </span>
            </h1>

            <p className="max-w-xl text-base leading-relaxed text-[#bdc8d0] md:text-lg">
              Decentralized, agent-driven observability for logistics. Real-time
              event streams meet explainable analytics to automate fleet safety,
              fairness, and performance.
            </p>

            <div className="flex flex-wrap gap-4 pt-2">
              <Link
                href="/fleet-manager"
                className="inline-flex items-center gap-2 rounded-xl bg-[#70d2ff] px-7 py-4 font-bold text-[#003547] transition hover:brightness-110"
              >
                Launch Dashboard
                <ArrowRight className="h-4 w-4" />
              </Link>
              <Link
                href="/login"
                className="rounded-xl border border-[#3d484f]/40 bg-[#2e3253] px-7 py-4 font-bold text-[#dfe0ff] transition hover:bg-[#333758]"
              >
                Open Login
              </Link>
            </div>
          </div>

          <div className="hidden lg:block">
            <div className="rounded-xl border border-[#3d484f]/40 bg-[#191d3d]/70 p-6 shadow-2xl backdrop-blur">
              <div className="mb-4 flex items-center justify-between border-b border-[#3d484f]/35 pb-4">
                <span className="text-xs uppercase tracking-[0.16em] text-[#70d2ff]">
                  system_status: stable
                </span>
                <div className="flex gap-1">
                  <div className="h-2 w-2 rounded-full bg-[#ffb4ab]" />
                  <div className="h-2 w-2 rounded-full bg-[#ddb7ff]" />
                  <div className="h-2 w-2 rounded-full bg-[#70d2ff]" />
                </div>
              </div>
              <div className="space-y-3">
                <div className="h-4 w-3/4 rounded-full bg-[#151939]" />
                <div className="h-4 w-full rounded-full bg-[#151939]" />
                <div className="h-4 w-1/2 rounded-full bg-[#151939]" />
                <div className="grid grid-cols-3 gap-2 pt-4">
                  <div className="rounded-lg border border-[#70d2ff]/25 bg-[#70d2ff]/10 p-3 text-center">
                    <p className="text-xl font-bold text-[#70d2ff]">99.9%</p>
                    <p className="text-[10px] uppercase text-[#bdc8d0]">
                      Uptime
                    </p>
                  </div>
                  <div className="rounded-lg border border-[#a5c8ff]/25 bg-[#2792ff]/15 p-3 text-center">
                    <p className="text-xl font-bold text-[#a5c8ff]">12ms</p>
                    <p className="text-[10px] uppercase text-[#bdc8d0]">
                      Latency
                    </p>
                  </div>
                  <div className="rounded-lg border border-[#ddb7ff]/25 bg-[#c080ff]/15 p-3 text-center">
                    <p className="text-xl font-bold text-[#ddb7ff]">2.4k</p>
                    <p className="text-[10px] uppercase text-[#bdc8d0]">
                      Agents
                    </p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </header>

      <section className="bg-[#151939] py-24">
        <div className="mx-auto w-full max-w-7xl px-6">
          <h2 className="mb-4 text-4xl font-bold tracking-tight text-white">
            8-Agent Ecosystem
          </h2>
          <p className="mb-14 max-w-2xl text-[#bdc8d0]">
            The architectural lens into your fleet&apos;s cognitive structure.
            Each agent monitors a critical dimension of operational performance.
          </p>
          <div className="grid grid-cols-1 gap-px bg-[#3d484f]/25 md:grid-cols-2 lg:grid-cols-4">
            {agents.map((agent) => (
              <div
                key={agent.title}
                className="border border-[#3d484f]/10 bg-[#191d3d] p-7 transition-colors hover:bg-[#232748]"
              >
                <agent.icon className="mb-4 h-5 w-5 text-[#70d2ff]" />
                <h3 className="mb-2 text-lg font-bold text-white">
                  {agent.title}
                </h3>
                <p className="text-sm text-[#bdc8d0]">{agent.description}</p>
              </div>
            ))}
          </div>
        </div>
      </section>

      <section className="py-28">
        <div className="mx-auto grid w-full max-w-7xl grid-cols-1 gap-16 px-6 lg:grid-cols-2 lg:items-center">
          <div className="rounded-2xl border border-[#3d484f]/35 bg-[#191d3d]/70 p-8 backdrop-blur">
            <div className="mb-8 flex items-center justify-between">
              <p className="text-xs uppercase tracking-[0.18em] text-[#70d2ff]">
                Model Explanation: SHAP Deep Dive
              </p>
              <GitBranch className="h-5 w-5 text-[#bdc8d0]" />
            </div>
            <div className="space-y-6">
              <div className="flex items-end gap-3">
                <div className="h-28 w-10 rounded-t bg-[#70d2ff]/30" />
                <div className="h-44 w-10 rounded-t bg-[#70d2ff]" />
                <div className="h-24 w-10 rounded-t bg-[#ddb7ff]" />
                <div className="h-36 w-10 rounded-t bg-[#70d2ff]/55" />
              </div>
              <div className="space-y-3 border-t border-[#3d484f]/35 pt-4 text-sm">
                <div className="flex items-center justify-between">
                  <span className="text-[#bdc8d0]">Speed Deviation</span>
                  <span className="font-semibold text-[#70d2ff]">
                    HIGH IMPACT
                  </span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-[#070a2b]">
                  <div className="h-full w-3/4 bg-[#70d2ff]" />
                </div>
                <div className="flex items-center justify-between">
                  <span className="text-[#bdc8d0]">Weather Context</span>
                  <span className="font-semibold text-[#a5c8ff]">NEUTRAL</span>
                </div>
                <div className="h-2 overflow-hidden rounded-full bg-[#070a2b]">
                  <div className="h-full w-1/4 bg-[#a5c8ff]/60" />
                </div>
              </div>
            </div>
          </div>

          <div className="space-y-6">
            <h2 className="text-4xl font-extrabold leading-tight text-white md:text-5xl">
              Meet the Brain:
              <br />
              <span className="text-[#70d2ff]">Predictive Orchestration.</span>
            </h2>
            <p className="text-lg text-[#bdc8d0]">
              TraceData does not just collect logs. It explains why outcomes are
              produced through a streaming intelligence pipeline.
            </p>
            <div className="space-y-4">
              <div className="rounded-xl border border-[#3d484f]/25 bg-[#191d3d]/70 p-4">
                <p className="font-bold text-white">SHAP-based Metrics</p>
                <p className="text-sm text-[#bdc8d0]">
                  Understand exact feature weights behind every safety score.
                </p>
              </div>
              <div className="rounded-xl border border-[#3d484f]/25 bg-[#191d3d]/70 p-4">
                <p className="font-bold text-white">Real-time Processing</p>
                <p className="text-sm text-[#bdc8d0]">
                  Sub-millisecond event detection and automated escalation.
                </p>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="border-y border-[#3d484f]/20 bg-[#151939] py-24">
        <div className="mx-auto grid w-full max-w-7xl grid-cols-1 gap-10 px-6 lg:grid-cols-3">
          <div>
            <h2 className="mb-4 text-4xl font-bold text-white">
              Human-in-the-Loop
            </h2>
            <p className="mb-8 text-[#bdc8d0]">
              Keep human expertise in every critical decision pathway.
            </p>
            <div className="inline-flex flex-col gap-2 rounded-xl border border-[#ddb7ff]/25 bg-[#c080ff]/10 p-4">
              <span className="text-xs font-bold uppercase tracking-[0.14em] text-[#ddb7ff]">
                Active Interventions
              </span>
              <span className="text-3xl font-black text-white">482</span>
            </div>
          </div>
          <div className="rounded-2xl border border-[#3d484f]/20 bg-[#191d3d] p-8">
            <h3 className="mb-3 text-xl font-bold text-white">
              Appeals Workflow
            </h3>
            <p className="text-sm leading-relaxed text-[#bdc8d0]">
              Drivers can challenge automated scores through an auditable,
              context-rich review flow.
            </p>
          </div>
          <div className="rounded-2xl border border-[#3d484f]/20 bg-[#191d3d] p-8">
            <h3 className="mb-3 text-xl font-bold text-white">
              Expert Interventions
            </h3>
            <p className="text-sm leading-relaxed text-[#bdc8d0]">
              Override route decisions for edge cases while preserving full
              traceability.
            </p>
          </div>
        </div>
      </section>

      <section className="py-28">
        <div className="mx-auto w-full max-w-7xl px-6">
          <p className="mb-3 text-center text-xs uppercase tracking-[0.22em] text-[#70d2ff]">
            Architecture and Integration
          </p>
          <h2 className="mb-12 text-center text-4xl font-extrabold text-white">
            Built for Scalable Data Flows
          </h2>
          <div className="grid grid-cols-1 overflow-hidden rounded-2xl border border-[#3d484f]/25 bg-[#3d484f]/20 lg:grid-cols-2">
            <div className="bg-[#0c1030] p-10">
              <h3 className="mb-6 flex items-center gap-3 text-2xl font-bold text-white">
                <Workflow className="h-6 w-6 text-[#70d2ff]" />
                Data Flow
              </h3>
              <div className="space-y-3 text-sm">
                <div className="rounded border border-[#3d484f]/25 bg-[#070a2b] p-3 text-[#dfe0ff]">
                  01 Ingest: Edge telemetry and sensors
                </div>
                <div className="rounded border border-[#3d484f]/25 bg-[#070a2b] p-3 text-[#dfe0ff]">
                  02 Process: Agent cognitive layer
                </div>
                <div className="rounded border border-[#3d484f]/25 bg-[#070a2b] p-3 text-[#dfe0ff]">
                  03 Egress: Kafka, webhook, and data warehouse
                </div>
              </div>
            </div>
            <div className="bg-[#0c1030] p-10">
              <h3 className="mb-6 flex items-center gap-3 text-2xl font-bold text-white">
                <Network className="h-6 w-6 text-[#a5c8ff]" />
                System Integration
              </h3>
              <div className="space-y-3 text-sm text-[#bdc8d0]">
                <div className="flex items-center justify-between border-b border-[#3d484f]/25 py-2">
                  <span>API Version</span>
                  <span className="text-[#a5c8ff]">v2.1.0-stable</span>
                </div>
                <div className="flex items-center justify-between border-b border-[#3d484f]/25 py-2">
                  <span>Auth Method</span>
                  <span className="text-[#a5c8ff]">OAuth2 / PKI</span>
                </div>
                <div className="flex items-center justify-between border-b border-[#3d484f]/25 py-2">
                  <span>Cloud Support</span>
                  <span className="text-[#a5c8ff]">AWS, GCP, Azure</span>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden py-24">
        <div className="absolute inset-0 bg-gradient-to-br from-[#70d2ff]/10 via-transparent to-[#ddb7ff]/10" />
        <div className="relative mx-auto w-full max-w-4xl px-6 text-center">
          <h2 className="mb-6 text-5xl font-black tracking-tight text-white">
            Ready to orchestrate?
          </h2>
          <p className="mb-10 text-lg text-[#bdc8d0]">
            Join modern fleet operators using TraceData to build safer, fairer,
            and more efficient logistics networks.
          </p>
          <div className="flex flex-col justify-center gap-4 sm:flex-row">
            <Link
              href="/login"
              className="rounded-xl bg-[#70d2ff] px-10 py-5 font-bold text-[#003547] transition hover:scale-[1.01]"
            >
              Get Started Today
            </Link>
            <Link
              href="/login"
              className="rounded-xl border border-[#3d484f]/30 bg-[#2e3253] px-10 py-5 font-bold text-white transition hover:bg-[#333758]"
            >
              Talk to Engineering
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#3d484f]/20 bg-[#070a2b]">
        <div className="mx-auto flex w-full max-w-7xl flex-col items-center justify-between gap-6 px-6 py-10 text-sm text-[#bdc8d0] md:flex-row">
          <p>
            <span className="font-bold text-[#70d2ff]">TraceData</span> | 2026
            TraceData Command Center. The Architectural Lens.
          </p>
          <div className="flex gap-6">
            <a className="transition-colors hover:text-white">Documentation</a>
            <a className="transition-colors hover:text-white">System Status</a>
            <a className="transition-colors hover:text-white">Security</a>
          </div>
        </div>
      </footer>
    </div>
  );
}
