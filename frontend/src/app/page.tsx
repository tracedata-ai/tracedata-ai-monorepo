"use client";

import Image from "next/image";
import Link from "next/link";
import { useEffect, useState } from "react";
import {
  ArrowRight,
  Bolt,
  GitBranch,
  Lock,
  Network,
  PlayCircle,
  Scale,
  Settings2,
  Shield,
  Workflow,
} from "lucide-react";

export default function HomePage() {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 100);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="min-h-screen overflow-x-hidden bg-[#0c1030] text-[#dfe0ff]">
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(112,210,255,0.18),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(192,128,255,0.14),transparent_30%)]" />

      <nav
        className={`fixed top-0 z-50 w-full border-b border-[#3d484f]/30 bg-[#0c1030]/85 shadow-[0_20px_40px_rgba(7,10,43,0.4)] backdrop-blur-xl transition-transform duration-500 ${
          scrolled ? "translate-y-0" : "-translate-y-full"
        }`}
      >
        <div className="mx-auto flex h-16 w-full max-w-7xl items-center justify-between px-6">
          <div className="flex items-center gap-8">
            <div className="flex items-center gap-2">
              <div className="rounded-md bg-white p-1.5 shadow-[0_4px_18px_rgba(0,0,0,0.25)]">
                <Image
                  src="/logo.png"
                  alt="TraceData logo"
                  width={28}
                  height={28}
                  className="rounded-sm"
                  priority
                />
              </div>
              <p className="bg-gradient-to-r from-[#70d2ff] to-[#00aadd] bg-clip-text text-xl font-bold tracking-tighter text-transparent">
                TraceData
              </p>
            </div>
            <div className="hidden items-center gap-6 text-sm font-medium md:flex">
              <a className="border-b-2 border-[#70d2ff] pb-1 text-[#70d2ff]">
                Explorer
              </a>
              <a className="text-[#bdc8d0] hover:text-[#70d2ff]">Metrics</a>
              <a className="text-[#bdc8d0] hover:text-[#70d2ff]">Logs</a>
              <a className="text-[#bdc8d0] hover:text-[#70d2ff]">Traces</a>
              <a className="text-[#bdc8d0] hover:text-[#70d2ff]">Docs</a>
            </div>
          </div>
          <div className="flex items-center gap-3">
            <Link
              href="/login"
              className="rounded-md px-4 py-2 text-sm font-bold text-[#70d2ff] transition-colors hover:bg-[#191d3d]/50"
            >
              Sign In
            </Link>
            <Link
              href="/login"
              className="rounded-md bg-gradient-to-r from-[#70d2ff] to-[#00aadd] px-5 py-2 text-sm font-bold text-[#003547] transition active:scale-95"
            >
              Get Started
            </Link>
          </div>
        </div>
      </nav>

      <header className="relative flex min-h-screen w-full items-center overflow-hidden">
        <div className="absolute inset-0 z-0">
          <img
            className="h-full w-full object-cover object-[62%_50%] md:object-[60%_46%]"
            src="/hero-uw.png"
            alt="Cinematic wide shot of a high-tech semi-truck on highway with glowing data beam"
          />
          <div className="absolute inset-0 bg-[linear-gradient(112deg,rgba(12,16,48,0.68)_0%,rgba(12,16,48,0.54)_30%,rgba(12,16,48,0.26)_52%,rgba(12,16,48,0.10)_72%,rgba(12,16,48,0.03)_100%)]" />
          <div className="absolute inset-0 bg-gradient-to-t from-[#0c1030]/36 via-transparent to-transparent" />
          <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(12,16,48,0.30),transparent_42%)]" />
        </div>

        <div className="relative z-10 mx-auto grid w-full max-w-7xl grid-cols-1 items-center px-6 py-24 lg:grid-cols-12 lg:gap-8">
          <div className="lg:col-span-6">
            <div className="mb-6 inline-block rounded-full border border-[#70d2ff]/35 bg-[#70d2ff]/12 px-4 py-1">
              <span className="text-xs uppercase tracking-[0.2em] text-[#70d2ff]">
                Mission Control Alpha v2.4
              </span>
            </div>
            <h1 className="mb-8 text-5xl font-black tracking-tighter text-[#dfe0ff] md:text-7xl lg:text-8xl">
              Intelligent Fleet
              <br />
              <span className="bg-gradient-to-r from-[#70d2ff] via-[#a5c8ff] to-[#00aadd] bg-clip-text text-transparent">
                Orchestration
              </span>
            </h1>
            <p className="mb-12 max-w-2xl text-lg font-light leading-relaxed text-[#bdc8d0] md:text-2xl">
              AI intelligence middleware for small-to-medium fleets. TraceData
              closes 7 critical gaps in telematics: fairness, coaching, burnout
              detection, appeals, contextual scoring, trust, and integrated
              safety-welfare response.
            </p>
            <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
              <Link
                href="/login"
                className="group inline-flex items-center rounded-lg bg-gradient-to-r from-[#70d2ff] to-[#00aadd] px-8 py-4 text-lg font-bold text-[#003547] shadow-xl transition hover:shadow-[#70d2ff]/20"
              >
                Get Started
                <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
              </Link>
              <Link
                href="/fleet-manager"
                className="inline-flex items-center rounded-lg border border-[#3d484f]/40 px-8 py-4 text-lg font-bold text-[#bdc8d0] transition hover:bg-[#232748]"
              >
                <PlayCircle className="mr-2 h-5 w-5" />
                Watch Demo
              </Link>
            </div>
          </div>
          <div className="hidden lg:col-span-6 lg:block" />
        </div>

        <div className="absolute bottom-12 left-1/2 z-10 -translate-x-1/2 opacity-40">
          <p className="mb-4 text-[10px] uppercase tracking-[0.3em]">
            Scroll to Discover
          </p>
          <div className="mx-auto h-12 w-px bg-gradient-to-b from-[#70d2ff] to-transparent" />
        </div>
      </header>

      <section className="bg-[#0c1030] px-6 py-28 md:px-12">
        <div className="mx-auto max-w-7xl">
          <div className="mb-16 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
            <div className="max-w-xl">
              <span className="mb-4 block text-sm uppercase tracking-[0.2em] text-[#70d2ff]">
                The Neural Backbone
              </span>
              <h2 className="text-5xl font-extrabold tracking-tight text-[#dfe0ff]">
                The 8-Agent Ecosystem
              </h2>
            </div>
            <p className="max-w-sm text-lg font-light text-[#bdc8d0] md:text-right">
              Eight autonomous agents operating through a central orchestration
              graph to ensure fairness, accountability, explainability, and
              operational safety.
            </p>
          </div>

          <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
            <div className="rounded-xl bg-[#151939] p-8 transition hover:bg-[#191d3d] md:col-span-2 md:row-span-2">
              <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-full bg-[#70d2ff]/10">
                <Shield className="h-5 w-5 text-[#70d2ff]" />
              </div>
              <h3 className="mb-4 text-2xl font-bold text-[#dfe0ff]">
                Safety Agent
              </h3>
              <p className="leading-relaxed text-[#bdc8d0]">
                Priority-queue critical incident response with multi-level
                intervention (app notification, formal message, direct call)
                under a sub-5-second response objective.
              </p>
              <div className="mt-10 rounded-lg bg-[#070a2b] p-4 text-xs text-[#70d2ff]/80">
                &gt; QUEUE: queue.critical
                <br />
                &gt; ACTION: emergency_services + fleet_manager_alert
              </div>
            </div>

            <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
              <Scale className="mb-5 h-7 w-7 text-[#a5c8ff]" />
              <h3 className="mb-3 text-xl font-bold">Behavior Agent</h3>
              <p className="text-sm text-[#bdc8d0]">
                XGBoost trip scoring (0-100) with AIF360 fairness audits and
                SHAP/LIME explainability for every score decision.
              </p>
            </div>
            <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
              <Network className="mb-5 h-7 w-7 text-[#ddb7ff]" />
              <h3 className="mb-3 text-xl font-bold">Orchestrator Agent</h3>
              <p className="text-sm text-[#bdc8d0]">
                Central router using deterministic rules plus semantic routing
                for unstructured text, with full audit logging.
              </p>
            </div>
            <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
              <Bolt className="mb-5 h-7 w-7 text-[#00aadd]" />
              <h3 className="mb-3 text-xl font-bold">
                Feedback &amp; Advocacy Agent
              </h3>
              <p className="text-sm text-[#bdc8d0]">
                Driver appeals and feedback ingestion with semantic retrieval,
                ensuring contestable and transparent outcomes.
              </p>
            </div>
            <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
              <Lock className="mb-5 h-7 w-7 text-[#ddb7ff]" />
              <h3 className="mb-3 text-xl font-bold">Sentiment Agent</h3>
              <p className="text-sm text-[#bdc8d0]">
                Emotional trajectory analysis to identify burnout risk early and
                trigger supportive fleet-manager interventions.
              </p>
            </div>

            <div className="md:col-span-2 grid grid-cols-2 gap-4">
              <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
                <h3 className="mb-2 text-lg font-bold">Coaching Agent</h3>
                <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-[#3d484f]/40">
                  <div className="h-full w-full bg-[#a5c8ff]" />
                </div>
              </div>
              <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
                <h3 className="mb-2 text-lg font-bold">
                  Context Enrichment Agent
                </h3>
                <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-[#3d484f]/40">
                  <div className="h-full w-full bg-[#00aadd]" />
                </div>
              </div>
              <div className="col-span-2 flex items-center justify-between rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
                <div>
                  <h3 className="text-lg font-bold">Ingestion Quality Agent</h3>
                  <p className="text-sm text-[#bdc8d0]">
                    Validates telemetry plus unstructured appeal payloads,
                    handles batched pings and critical bypass routing.
                  </p>
                </div>
                <Settings2 className="h-5 w-5 text-[#bdc8d0]" />
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="overflow-hidden bg-[#070a2b] px-6 py-32 md:px-12">
        <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-16 lg:grid-cols-12">
          <div className="relative lg:col-span-5">
            <div className="absolute -left-16 -top-16 h-64 w-64 rounded-full bg-[#70d2ff]/10 blur-[100px]" />
            <span className="mb-4 block text-sm uppercase tracking-[0.2em] text-[#70d2ff]">
              Deep Tech Stack
            </span>
            <h2 className="mb-8 text-5xl font-black tracking-tighter leading-none">
              Mission Control
              <br />
              Explainability
            </h2>
            <p className="mb-8 text-lg leading-relaxed text-[#bdc8d0]">
              TraceData does not just score events; it exposes decision logic.
              SHAP and LIME explainability are paired with fairness checks so
              every intervention is observable, reviewable, and contestable.
            </p>
            <ul className="space-y-5">
              <li className="flex items-start gap-4">
                <div className="rounded-md bg-[#70d2ff]/20 p-2">
                  <Workflow className="h-4 w-4 text-[#70d2ff]" />
                </div>
                <div>
                  <p className="font-bold">Kafka-Driven Orchestration</p>
                  <p className="text-sm text-[#bdc8d0]">
                    FastAPI + Celery + Redis priority queues route critical,
                    high, medium, and low events with deterministic SLAs.
                  </p>
                </div>
              </li>
              <li className="flex items-start gap-4">
                <div className="rounded-md bg-[#a5c8ff]/20 p-2">
                  <GitBranch className="h-4 w-4 text-[#a5c8ff]" />
                </div>
                <div>
                  <p className="font-bold">Fairness + SHAP/LIME Attribution</p>
                  <p className="text-sm text-[#bdc8d0]">
                    Monthly bias audits (AIF360) and feature-level explanations
                    for each behavioral score and appeal decision.
                  </p>
                </div>
              </li>
            </ul>
          </div>

          <div className="lg:col-span-7">
            <div className="rounded-2xl border border-[#3d484f]/20 bg-[#232748] p-4 shadow-2xl">
              <div className="mb-4 flex items-center justify-between px-2">
                <div className="flex gap-1.5">
                  <div className="h-3 w-3 rounded-full bg-[#ffb4ab]/40" />
                  <div className="h-3 w-3 rounded-full bg-[#a5c8ff]/40" />
                  <div className="h-3 w-3 rounded-full bg-[#70d2ff]/40" />
                </div>
                <p className="text-[10px] uppercase tracking-[0.2em] text-[#bdc8d0]/70">
                  Live Explainability Feed
                </p>
              </div>
              <div className="relative aspect-video overflow-hidden rounded-xl bg-[#151939]">
                <img
                  className="h-full w-full object-cover opacity-55 grayscale transition duration-700 hover:grayscale-0"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuCWFnGNuyZQNfXMSZnEr5350Lej79-PItNK_hVzMWatAmrOOytEvLa6CuyD7t1R_deSXI66vMIwQO4ivD5x6PmvFj7yJad97HQ8ouLXRZAbkWeiMRUpPX9Pp5T955VTBUdltb5p8kxvcshJmtVB5qD2sgtOrFPDezhpB9PYyXrOOPsrLTK3FJa0bKJECQ1igM910LQFO_vvb_uWTSRF_CIr_NiBlAqJ4f9ac1UOURWfglbVzGnlBJQ7muupLiTbpaH9BCezIEfaYaEF"
                  alt="Technical data visualization dashboard with SHAP graphs and fleet status"
                />
                <div className="absolute inset-0 bg-gradient-to-t from-[#070a2b] via-transparent to-transparent" />
                <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
                  <div className="space-y-1 text-[10px] text-[#70d2ff]">
                    <p>LATENCY: 12ms</p>
                    <p>JITTER: 0.02ms</p>
                    <p>NODE_ID: TR-808</p>
                  </div>
                  <div className="rounded-lg border border-[#70d2ff]/30 bg-[#70d2ff]/20 p-4 backdrop-blur-md">
                    <p className="mb-2 text-[10px] uppercase text-[#70d2ff]">
                      SHAP Influence
                    </p>
                    <div className="flex h-8 items-end gap-2">
                      <div className="h-full w-2 bg-[#70d2ff]" />
                      <div className="h-4 w-2 bg-[#70d2ff]" />
                      <div className="h-6 w-2 bg-[#70d2ff]" />
                      <div className="h-2 w-2 bg-[#70d2ff]" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-[#0c1030] px-6 py-28 md:px-12">
        <div className="mx-auto flex max-w-7xl flex-col items-center gap-16 md:flex-row">
          <div className="order-2 w-full md:order-1 md:w-1/2">
            <div className="grid grid-cols-2 gap-4">
              <div className="rounded-xl border-l-4 border-[#a5c8ff] bg-[#151939] p-6">
                <h4 className="mb-2 font-bold">Direct Appeals</h4>
                <p className="text-xs text-[#bdc8d0]">
                  Instant override capability for human operators in edge cases.
                </p>
              </div>
              <div className="rounded-xl border-l-4 border-[#ddb7ff] bg-[#151939] p-6">
                <h4 className="mb-2 font-bold">Post-Action Coaching</h4>
                <p className="text-xs text-[#bdc8d0]">
                  Intervention data continuously improves agent logic.
                </p>
              </div>
              <div className="col-span-2 flex items-center justify-between rounded-xl bg-[#151939] p-8">
                <div>
                  <h3 className="text-xl font-bold">Operator Dashboard</h3>
                  <p className="mt-2 text-sm text-[#bdc8d0]">
                    Machines ask for permission, not forgiveness.
                  </p>
                </div>
                <button className="rounded bg-[#3d484f]/30 px-4 py-2 text-xs uppercase tracking-[0.16em] transition hover:bg-[#3d484f]/45">
                  Launch Shell
                </button>
              </div>
            </div>
          </div>
          <div className="order-1 w-full md:order-2 md:w-1/2">
            <div className="mb-8 flex items-center justify-between">
              <span className="text-sm uppercase tracking-[0.2em] text-[#70d2ff]">
                The Integrity Layer
              </span>
            </div>
            <h2 className="mb-8 text-5xl font-black tracking-tighter">
              Human-in-the-Loop
            </h2>
            <p className="text-lg text-[#bdc8d0]">
              Drivers can appeal decisions and fleet managers can override with
              complete context. The goal is support over surveillance, with
              transparent intervention logs for governance.
            </p>
            <div className="mt-8 flex items-center gap-4">
              <div className="flex -space-x-3">
                <img
                  className="h-10 w-10 rounded-full border-2 border-[#0c1030] object-cover"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAVpEexdcfJyIwB0ipJOiqAj-NulcQDxstVnkNO7Mmxu-Zo933WVl5y7-OvNqqKMmn6TOvEzgAmDIOlTYvppBDSgkC9VoBibB-yUB8IgmD-Xrmi88scdtbEBt72WV0Y-2FOCJGxFYwdgBFSHTb1G87as-ou0_g_U8_KvnioDPCLu3b4ZjAUy1_YoabpBapNrtcQuUklxlDndERkHbxmRWOPet3Ku2jK5MifsR15xWhZfrWpzkwjY4CEHpUyZusHh1KRuVfdr5ckovy7"
                  alt="Operator 1"
                />
                <img
                  className="h-10 w-10 rounded-full border-2 border-[#0c1030] object-cover"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuCox4zHJkZyBu2N9ha09xeXdRRLEM_Mt9PgOfVORU3tubHE_IRe12t4a-bWt5XxWTjVNdvsk24zfttDTJ5UA0MZYs0RZ5mwFAa2l5qvSYDhA3GGXSFP6k_FPZMAjPOOZRMljAB9PNWBCt_oluHzrcpSwMSOsXH0c3IWcVn4kwXzOm3msM7icj7vNubucSIJ0lm2NNJFpVsgQA7Rg9Ds--K3M8n-A9-wpDIUTeXZ7ptUI8DQECRr9AD3l9jXvuToxZaIbDuJn10OIucg"
                  alt="Operator 2"
                />
                <img
                  className="h-10 w-10 rounded-full border-2 border-[#0c1030] object-cover"
                  src="https://lh3.googleusercontent.com/aida-public/AB6AXuAUGO6nGpl5zz34QxqpMGCqD506uFz34LeVIjiUzUW5k3qSDJW_3gonqac5AZ9QbgLxo7eak4ch-6wHYbXvODjRKoGu_qPJ5uDU44jK7D4sermunGaMceglqS737-eXFCVbndkSYAuOSS4K8MO-RX08UX13Ec-X6kaT4D8QsnezekGtOaYhpATvxOK5Ik3BH-8EQgm_iRcINqQxK2L0-6q4P7YRoXiCfF5GHxjye6Td0Q_gHOBEaZxtlosTjnZRWordk3WS4R9mz4xH"
                  alt="Operator 3"
                />
              </div>
              <p className="text-sm text-[#bdc8d0]">
                Trusted by 2,000+ logistics supervisors worldwide.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="bg-[#070a2b] px-6 py-28 md:px-12">
        <div className="mx-auto max-w-7xl">
          <div className="mb-20 text-center">
            <h2 className="mb-4 text-4xl font-black uppercase tracking-[0.12em]">
              Technical Specifications
            </h2>
            <div className="mx-auto h-1 w-24 bg-[#70d2ff]" />
          </div>
          <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
            <div className="border-t border-[#3d484f]/20 p-8">
              <span className="mb-4 block text-xs uppercase tracking-[0.18em] text-[#70d2ff]">
                Orchestration
              </span>
              <h4 className="mb-4 text-xl font-bold">
                LangGraph + Router Core
              </h4>
              <p className="text-sm leading-relaxed text-[#bdc8d0]">
                Agent nodes execute through conditional routing with audited
                decisions from the central Orchestrator Agent.
              </p>
            </div>
            <div className="border-t border-[#3d484f]/20 p-8">
              <span className="mb-4 block text-xs uppercase tracking-[0.18em] text-[#70d2ff]">
                Fairness &amp; Explainability
              </span>
              <h4 className="mb-4 text-xl font-bold">AIF360 + SHAP + LIME</h4>
              <p className="text-sm leading-relaxed text-[#bdc8d0]">
                Bias detection, mitigation, and interpretable scoring are built
                directly into the Behavior Agent lifecycle.
              </p>
            </div>
            <div className="border-t border-[#3d484f]/20 p-8">
              <span className="mb-4 block text-xs uppercase tracking-[0.18em] text-[#70d2ff]">
                Runtime Stack
              </span>
              <h4 className="mb-4 text-xl font-bold">
                FastAPI + Celery/Redis + PostgreSQL/pgvector
              </h4>
              <p className="text-sm leading-relaxed text-[#bdc8d0]">
                Production-ready async APIs, priority task queues, ACID event
                storage, and vector search for appeal context retrieval.
              </p>
            </div>
          </div>
        </div>
      </section>

      <section className="relative overflow-hidden bg-[#070a2b] px-6 py-36 md:px-12">
        <div className="absolute inset-0 bg-gradient-to-br from-[#70d2ff]/10 via-transparent to-[#ddb7ff]/10" />
        <div className="relative mx-auto w-full max-w-4xl text-center">
          <h2 className="mb-12 text-5xl font-black tracking-tighter md:text-6xl">
            Ready to Orchestrate?
          </h2>
          <div className="flex flex-col justify-center gap-4 sm:flex-row">
            <Link
              href="/login"
              className="rounded-md bg-gradient-to-r from-[#70d2ff] to-[#00aadd] px-12 py-5 text-xl font-black uppercase tracking-tight text-[#003547]"
            >
              Deploy Now
            </Link>
            <Link
              href="/login"
              className="rounded-md border border-[#3d484f] bg-transparent px-12 py-5 text-xl font-black uppercase tracking-tight text-[#dfe0ff] transition hover:bg-[#151939]"
            >
              Request Specs
            </Link>
          </div>
        </div>
      </section>

      <footer className="border-t border-[#3d484f]/20 bg-[#070a2b] px-6 py-12 md:px-12">
        <div className="mx-auto grid max-w-7xl grid-cols-2 gap-8 md:grid-cols-5">
          <div className="col-span-2">
            <div className="mb-4 flex items-center gap-2">
              <div className="rounded-md bg-white p-1 shadow-[0_4px_18px_rgba(0,0,0,0.25)]">
                <Image
                  src="/logo.png"
                  alt="TraceData logo"
                  width={24}
                  height={24}
                  className="rounded-sm"
                />
              </div>
              <p className="text-lg font-black text-[#70d2ff]">TraceData</p>
            </div>
            <p className="max-w-xs text-xs uppercase tracking-[0.2em] text-[#bdc8d0]">
              Built for the Architectural Lens. High-integrity fleet
              intelligence.
            </p>
          </div>
          <div className="flex flex-col gap-4">
            <span className="text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60">
              Platform
            </span>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Explorer
            </a>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Metrics
            </a>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Status
            </a>
          </div>
          <div className="flex flex-col gap-4">
            <span className="text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60">
              Resources
            </span>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Docs
            </a>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Changelog
            </a>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Security
            </a>
          </div>
          <div className="flex flex-col gap-4">
            <span className="text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60">
              Legal
            </span>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Privacy
            </a>
            <a className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]">
              Terms
            </a>
          </div>
        </div>
        <div className="mx-auto mt-12 max-w-7xl border-t border-[#3d484f]/20 pt-8 text-center">
          <p className="text-[10px] uppercase tracking-[0.3em] text-[#bdc8d0]">
            2026 TraceData. All rights reserved.
          </p>
        </div>
      </footer>
    </div>
  );
}
