"use client";

import Image from "next/image";
import Link from "next/link";
import { JetBrains_Mono, Manrope, Sora } from "next/font/google";
import { useEffect, useRef, useState } from "react";
import {
  Activity,
  ArrowRight,
  Bolt,
  Database,
  GitBranch,
  Network,
  PlayCircle,
  Scale,
  Settings2,
  Shield,
  Workflow,
} from "lucide-react";

const displayFont = Sora({
  subsets: ["latin"],
  weight: ["600", "700", "800"],
});

const bodyFont = Manrope({
  subsets: ["latin"],
  weight: ["400", "500", "600", "700"],
});

const monoFont = JetBrains_Mono({
  subsets: ["latin"],
  weight: ["500", "600"],
});

const homepageCopy = {
  brand: {
    name: "TraceData",
    logoAlt: "TraceData logo",
  },
  nav: {
    active: "Overview",
    items: ["7 Gaps", "Agent Scope", "Tech Stack", "Governance"],
    signIn: "Sign In",
    getStarted: "Get Started",
  },
  hero: {
    imageAlt:
      "Cinematic wide shot of a high-tech semi-truck on highway with glowing data beam",
    badge: "AI Intelligence Middleware for Fleet Management",
    titleLine1: "Fair, Explainable",
    titleAccent: "Fleet Intelligence",
    description:
      "Built for SMB fleets, TraceData addresses 7 critical telematics gaps with a people-first philosophy.",
    primaryCta: "Get Started",
    secondaryCta: "View Fleet Manager",
    scrollHint: "Scroll for Architecture",
  },
  ecosystem: {
    eyebrow: "Proposed High-Level Architecture",
    title: "5 Agents + Shared Tool Gateway",
    description:
      "TraceData uses 5 autonomous agents and a shared Tool Gateway to deliver fairness, coaching, burnout detection, appeals, contextual enrichment, and integrated safety-welfare response.",
    cards: {
      safety: {
        title: "Safety Agent",
        body: "Processes critical events via queue.critical with a 3-level intervention flow: app notification, formal message, and direct fleet-manager call under a sub-5-second target.",
        queue: "> QUEUE: queue.critical",
        action: "> ACTION: emergency_services + fleet_manager_alert",
      },
      behavior: {
        title: "Scoring Agent",
        body: "Scores trips and drivers (0-100) using XGBoost, then applies AIF360 fairness mitigation and SHAP/LIME explanations for every decision.",
      },
      orchestrator: {
        title: "Orchestrator Agent",
        body: "Entry-point router using deterministic and semantic pathways; invokes ingestion validation sidecar and logs every routing decision for accountability.",
      },
      feedback: {
        title: "Support Agent",
        body: "Unifies appeals and coaching using pgvector semantic retrieval plus LLM guidance, ensuring contestability and consistent fleet-manager decisions.",
      },
      sentiment: {
        title: "Sentiment Agent",
        body: "Tracks emotional trajectory using a rolling event window and escalates burnout risk alerts to fleet managers with recommended interventions.",
      },
      coaching: {
        title: "Tool Gateway: Context Enrichment",
        body: "Enriches every inbound event with driver history, route context, and environmental data before agent dispatch.",
      },
      context: {
        title: "Tool Gateway: Ingestion Validation",
        body: "Validates all incoming telemetry schema and filters malformed events before they reach the agent layer.",
      },
      ingestion: {
        title: "Fairness-First Operations",
        body: "Core philosophy: fairness first, driver-centric design, and transparent contestable outcomes with auditable governance.",
      },
    },
  },
  explainability: {
    eyebrow: "Trust, Fairness, Accountability",
    titleLine1: "Explainability",
    titleLine2: "and Assurance Layer",
    description:
      "TraceData pairs fairness controls with explainability artifacts so every intervention is observable, reviewable, and contestable across operational and compliance workflows.",
    points: [
      {
        title: "LangGraph + Priority Queue Execution",
        body: "Agent flows run through LangGraph while Celery/Redis routes critical, high, medium, and low events with deterministic response paths.",
      },
      {
        title: "AIF360 Fairness + SHAP/LIME Attribution",
        body: "Bias mitigation and feature-level explanations are generated for scoring decisions, with recurring fairness audits for drift control.",
      },
    ],
    liveFeed: {
      title: "Governed Decision Stream",
      dashboardAlt:
        "Technical data visualization dashboard with SHAP graphs and fleet status",
      stats: ["SLA: < 5s", "SPD TARGET: < 0.5", "QUEUE: queue.critical"],
      shapTitle: "SHAP Influence",
    },
  },
  integrity: {
    eyebrow: "Driver-Centric Governance",
    title: "Human-in-the-Loop",
    description:
      "Drivers can contest scores through structured appeals while fleet managers override with context and reasoning logs. The operating model is support over surveillance.",
    cards: [
      {
        title: "Direct Appeals",
        body: "Drivers contest unfair outcomes with semantic retrieval against precedent cases.",
      },
      {
        title: "Tone-Calibrated Coaching",
        body: "Support guidance adapts using sentiment context (encouraging, supportive, or directive).",
      },
    ],
    dashboard: {
      title: "Operator Dashboard",
      body: "Every intervention stores decision rationale, FM action, and AI reasoning for traceability.",
      cta: "Review Cases",
    },
    people: {
      images: [
        {
          src: "https://lh3.googleusercontent.com/aida-public/AB6AXuAVpEexdcfJyIwB0ipJOiqAj-NulcQDxstVnkNO7Mmxu-Zo933WVl5y7-OvNqqKMmn6TOvEzgAmDIOlTYvppBDSgkC9VoBibB-yUB8IgmD-Xrmi88scdtbEBt72WV0Y-2FOCJGxFYwdgBFSHTb1G87as-ou0_g_U8_KvnioDPCLu3b4ZjAUy1_YoabpBapNrtcQuUklxlDndERkHbxmRWOPet3Ku2jK5MifsR15xWhZfrWpzkwjY4CEHpUyZusHh1KRuVfdr5ckovy7",
          alt: "Operator 1",
        },
        {
          src: "https://lh3.googleusercontent.com/aida-public/AB6AXuCox4zHJkZyBu2N9ha09xeXdRRLEM_Mt9PgOfVORU3tubHE_IRe12t4a-bWt5XxWTjVNdvsk24zfttDTJ5UA0MZYs0RZ5mwFAa2l5qvSYDhA3GGXSFP6k_FPZMAjPOOZRMljAB9PNWBCt_oluHzrcpSwMSOsXH0c3IWcVn4kwXzOm3msM7icj7vNubucSIJ0lm2NNJFpVsgQA7Rg9Ds--K3M8n-A9-wpDIUTeXZ7ptUI8DQECRr9AD3l9jXvuToxZaIbDuJn10OIucg",
          alt: "Operator 2",
        },
        {
          src: "https://lh3.googleusercontent.com/aida-public/AB6AXuAUGO6nGpl5zz34QxqpMGCqD506uFz34LeVIjiUzUW5k3qSDJW_3gonqac5AZ9QbgLxo7eak4ch-6wHYbXvODjRKoGu_qPJ5uDU44jK7D4sermunGaMceglqS737-eXFCVbndkSYAuOSS4K8MO-RX08UX13Ec-X6kaT4D8QsnezekGtOaYhpATvxOK5Ik3BH-8EQgm_iRcINqQxK2L0-6q4P7YRoXiCfF5GHxjye6Td0Q_gHOBEaZxtlosTjnZRWordk3WS4R9mz4xH",
          alt: "Operator 3",
        },
      ],
      trustLine:
        "Built for transparent, contestable, and accountable fleet operations.",
    },
  },
  technicalSpecs: {
    title: "Technical Specifications",
    columns: [
      {
        label: "Agent Orchestration",
        title: "LangGraph + Orchestrator Router",
        body: "Agents execute as graph nodes with deterministic and semantic routing, plus full routing audit trails.",
        icon: "workflow" as const,
      },
      {
        label: "Fairness & Bias",
        title: "AIF360 + SHAP + LIME",
        body: "Bias detection and mitigation are integrated into scoring; SHAP/LIME provides local and global feature explainability.",
        icon: "scale" as const,
      },
      {
        label: "Runtime + Data",
        title: "FastAPI + Celery/Redis + PostgreSQL/pgvector",
        body: "Async APIs, priority queues, ACID event storage, JSONB support, and semantic vector search for appeal consistency.",
        icon: "database" as const,
      },
    ],
  },
  finalCta: {
    title: "Ready for Fair Fleet Intelligence?",
    primary: "Open Platform",
    secondary: "Explore Architecture",
  },
  footer: {
    tagline:
      "Fairness-first, driver-centric, and transparently explainable by design.",
    groups: {
      platform: {
        label: "Platform",
        links: ["Overview", "Agent Scope", "Operational Queues"],
      },
      resources: {
        label: "Resources",
        links: ["Project Proposal", "Project Report", "Risk Register"],
      },
      legal: {
        label: "Governance",
        links: ["Fairness Audit", "Appeals Policy"],
      },
    },
    copyright: "2026 TraceData. All rights reserved.",
  },
};

const navAnchors: Record<string, string> = {
  "7 Gaps": "#ecosystem",
  "Agent Scope": "#explainability",
  "Tech Stack": "#tech-specs",
  Governance: "#integrity",
};

// ─── Animation Hooks ──────────────────────────────────────────────────

function useScrollProgress() {
  const [progress, setProgress] = useState(0);
  useEffect(() => {
    const onScroll = () => {
      const el = document.documentElement;
      const scrolled = el.scrollTop;
      const total = el.scrollHeight - el.clientHeight;
      setProgress(total > 0 ? (scrolled / total) * 100 : 0);
    };
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);
  return progress;
}

function useInView(threshold = 0.18) {
  const ref = useRef<HTMLElement | null>(null);
  const [visible, setVisible] = useState(false);
  useEffect(() => {
    if (!ref.current) return;
    const observer = new IntersectionObserver(
      ([entry]) => {
        if (entry.isIntersecting) {
          setVisible(true);
          observer.disconnect();
        }
      },
      { threshold }
    );
    observer.observe(ref.current);
    return () => observer.disconnect();
  }, [threshold]);
  return { ref, visible };
}

// ─── Scroll Progress Bar ──────────────────────────────────────────────

function ScrollProgressBar({ progress }: { progress: number }) {
  return (
    <div className="pointer-events-none fixed left-0 top-0 z-[60] h-[2px] w-full">
      <div
        className="h-full bg-gradient-to-r from-[#70d2ff] via-[#a5c8ff] to-[#00aadd] transition-[width] duration-100 ease-out"
        style={{ width: `${progress}%` }}
      />
    </div>
  );
}

function TopNav({ scrolled }: { scrolled: boolean }) {
  return (
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
              {homepageCopy.brand.name}
            </p>
          </div>
          <div
            className={`hidden items-center gap-6 text-sm font-medium md:flex ${monoFont.className}`}
          >
            <a
              href="#"
              className="border-b-2 border-[#70d2ff] pb-1 text-[#70d2ff]"
            >
              {homepageCopy.nav.active}
            </a>
            {homepageCopy.nav.items.map((item) => (
              <a
                key={item}
                href={navAnchors[item] ?? "#"}
                className="text-[#bdc8d0] transition-colors hover:text-[#70d2ff]"
              >
                {item}
              </a>
            ))}
          </div>
        </div>
        <div className={`flex items-center gap-3 ${displayFont.className}`}>
          <Link
            href="/login"
            className="rounded-md px-4 py-2 text-sm font-bold text-[#70d2ff] transition-colors hover:bg-[#191d3d]/50"
          >
            {homepageCopy.nav.signIn}
          </Link>
          <Link
            href="/login"
            className="rounded-md bg-gradient-to-r from-[#70d2ff] to-[#00aadd] px-5 py-2 text-sm font-bold text-[#003547] transition active:scale-95"
          >
            {homepageCopy.nav.getStarted}
          </Link>
        </div>
      </div>
    </nav>
  );
}

function HeroSection() {
  return (
    <header className="relative flex min-h-screen w-full items-center overflow-hidden">
      <div className="absolute inset-0 z-0">
        <Image
          fill
          priority
          className="object-cover object-[62%_50%] md:object-[60%_46%]"
          src="/hero-uw.png"
          alt={homepageCopy.hero.imageAlt}
        />
        <div className="absolute inset-0 bg-[linear-gradient(112deg,rgba(12,16,48,0.68)_0%,rgba(12,16,48,0.54)_30%,rgba(12,16,48,0.26)_52%,rgba(12,16,48,0.10)_72%,rgba(12,16,48,0.03)_100%)]" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0c1030]/36 via-transparent to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(12,16,48,0.30),transparent_42%)]" />
        {/* Floating ambient orbs */}
        <div className="orb-float-a pointer-events-none absolute -left-24 top-1/4 h-80 w-80 rounded-full bg-[#70d2ff]/8 blur-[120px]" />
        <div className="orb-float-b pointer-events-none absolute right-1/4 top-1/3 h-64 w-64 rounded-full bg-[#ddb7ff]/10 blur-[100px]" />
      </div>

      <div className="relative z-10 mx-auto grid w-full max-w-7xl grid-cols-1 items-center px-6 py-24 lg:grid-cols-12 lg:gap-8">
        <div className="lg:col-span-6">
          <div className="shimmer-badge mb-6 inline-block rounded-full border border-[#70d2ff]/35 px-4 py-1">
            <span
              className={`text-xs uppercase tracking-[0.2em] text-[#70d2ff] ${monoFont.className}`}
            >
              {homepageCopy.hero.badge}
            </span>
          </div>
          <h1
            className={`mb-8 text-5xl font-black leading-[0.94] tracking-[-0.03em] text-[#dfe0ff] md:text-7xl lg:text-8xl ${displayFont.className}`}
          >
            {homepageCopy.hero.titleLine1}
            <br />
            <span className="bg-gradient-to-r from-[#70d2ff] via-[#a5c8ff] to-[#00aadd] bg-clip-text text-transparent">
              {homepageCopy.hero.titleAccent}
            </span>
          </h1>
          <p className="mb-12 max-w-2xl text-base font-medium leading-8 text-[#bdc8d0] md:text-xl">
            {homepageCopy.hero.description}
          </p>
          <div
            className={`flex flex-col items-start gap-4 sm:flex-row sm:items-center ${displayFont.className}`}
          >
            <Link
              href="/login"
              className="group inline-flex items-center rounded-lg bg-gradient-to-r from-[#70d2ff] to-[#00aadd] px-8 py-4 text-lg font-bold text-[#003547] shadow-xl transition hover:shadow-[#70d2ff]/20"
            >
              {homepageCopy.hero.primaryCta}
              <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="/fleet-manager"
              className="inline-flex items-center rounded-lg border border-[#3d484f]/40 px-8 py-4 text-lg font-bold text-[#bdc8d0] transition-colors duration-200 hover:bg-[#232748]"
            >
              <PlayCircle className="mr-2 h-5 w-5" />
              {homepageCopy.hero.secondaryCta}
            </Link>
          </div>
        </div>
        <div className="hidden lg:col-span-6 lg:block" />
      </div>

      <div className="absolute bottom-12 left-1/2 z-10 -translate-x-1/2 opacity-50">
        <p
          className={`mb-4 text-[10px] uppercase tracking-[0.3em] ${monoFont.className}`}
        >
          {homepageCopy.hero.scrollHint}
        </p>
        <div className="mx-auto h-12 w-px animate-bounce bg-gradient-to-b from-[#70d2ff] to-transparent" />
      </div>
    </header>
  );
}

const staggerClasses = [
  "stagger-1", "stagger-2", "stagger-3", "stagger-4",
  "stagger-5", "stagger-6", "stagger-7", "stagger-8",
];

function EcosystemSection() {
  const { ref, visible } = useInView(0.1);
  return (
    <section
      id="ecosystem"
      ref={ref as React.RefObject<HTMLElement>}
      className="bg-[#0c1030] px-6 py-28 md:px-12"
    >
      <div className="mx-auto max-w-7xl">
        <div
          className={`fade-in-up mb-16 flex flex-col gap-6 md:flex-row md:items-end md:justify-between ${
            visible ? "is-visible" : ""
          }`}
        >
          <div className="max-w-xl">
            <span
              className={`mb-4 block text-sm uppercase tracking-[0.2em] text-[#70d2ff] ${monoFont.className}`}
            >
              {homepageCopy.ecosystem.eyebrow}
            </span>
            <h2
              className={`text-4xl font-extrabold leading-[1.02] tracking-[-0.02em] text-[#dfe0ff] md:text-5xl ${displayFont.className}`}
            >
              {homepageCopy.ecosystem.title}
            </h2>
          </div>
          <p className="max-w-sm text-base font-medium leading-7 text-[#bdc8d0] md:text-right">
            {homepageCopy.ecosystem.description}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          {/* Safety Agent — large featured card */}
          <div
            className={`card-glow fade-in-up stagger-1 flex flex-col rounded-xl bg-[#151939] p-8 transition hover:bg-[#191d3d] md:col-span-2 md:row-span-2 ${
              visible ? "is-visible" : ""
            }`}
          >
            <div className="pulse-ring mb-6 inline-flex h-12 w-12 items-center justify-center rounded-full bg-[#70d2ff]/10">
              <Shield className="h-5 w-5 text-[#70d2ff]" />
            </div>
            <h3
              className={`mb-4 text-2xl font-bold text-[#dfe0ff] ${displayFont.className}`}
            >
              {homepageCopy.ecosystem.cards.safety.title}
            </h3>
            <p className="leading-8 text-[#bdc8d0]">
              {homepageCopy.ecosystem.cards.safety.body}
            </p>
            <div
              className={`mt-auto rounded-lg bg-[#070a2b] p-4 text-xs text-[#70d2ff]/80 ${monoFont.className}`}
            >
              {homepageCopy.ecosystem.cards.safety.queue}
              <br />
              {homepageCopy.ecosystem.cards.safety.action}
            </div>
          </div>

          {[
            { icon: <Scale className="mb-5 h-7 w-7 text-[#a5c8ff]" />, card: homepageCopy.ecosystem.cards.behavior, idx: 2 },
            { icon: <Network className="mb-5 h-7 w-7 text-[#ddb7ff]" />, card: homepageCopy.ecosystem.cards.orchestrator, idx: 3 },
            { icon: <Bolt className="mb-5 h-7 w-7 text-[#00aadd]" />, card: homepageCopy.ecosystem.cards.feedback, idx: 4 },
            { icon: <Activity className="mb-5 h-7 w-7 text-[#ddb7ff]" />, card: homepageCopy.ecosystem.cards.sentiment, idx: 5 },
          ].map(({ icon, card, idx }) => (
            <div
              key={card.title}
              className={`card-glow fade-in-up ${staggerClasses[idx - 1]} rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d] ${
                visible ? "is-visible" : ""
              }`}
            >
              {icon}
              <h3 className={`mb-3 text-xl font-bold ${displayFont.className}`}>
                {card.title}
              </h3>
              <p className="text-sm leading-7 text-[#bdc8d0]">{card.body}</p>
            </div>
          ))}

          <div className={`md:col-span-2 grid grid-cols-2 gap-4`}>
            <div
              className={`card-glow fade-in-up stagger-6 rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d] ${
                visible ? "is-visible" : ""
              }`}
            >
              <h3 className={`mb-2 text-lg font-bold ${displayFont.className}`}>
                {homepageCopy.ecosystem.cards.coaching.title}
              </h3>
              <p className="mt-2 text-sm leading-6 text-[#bdc8d0]">
                {homepageCopy.ecosystem.cards.coaching.body}
              </p>
              <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-[#3d484f]/40">
                <div className="h-full w-full bg-[#a5c8ff]" />
              </div>
            </div>
            <div
              className={`card-glow fade-in-up stagger-7 rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d] ${
                visible ? "is-visible" : ""
              }`}
            >
              <h3 className={`mb-2 text-lg font-bold ${displayFont.className}`}>
                {homepageCopy.ecosystem.cards.context.title}
              </h3>
              <p className="mt-2 text-sm leading-6 text-[#bdc8d0]">
                {homepageCopy.ecosystem.cards.context.body}
              </p>
              <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-[#3d484f]/40">
                <div className="h-full w-full bg-[#00aadd]" />
              </div>
            </div>
            <div
              className={`card-glow fade-in-up stagger-8 col-span-2 flex items-center justify-between rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d] ${
                visible ? "is-visible" : ""
              }`}
            >
              <div>
                <h3 className={`text-lg font-bold ${displayFont.className}`}>
                  {homepageCopy.ecosystem.cards.ingestion.title}
                </h3>
                <p className="text-sm leading-7 text-[#bdc8d0]">
                  {homepageCopy.ecosystem.cards.ingestion.body}
                </p>
              </div>
              <Settings2 className="h-5 w-5 text-[#bdc8d0]" />
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function ExplainabilitySection() {
  const { ref, visible } = useInView(0.15);
  return (
    <section
      id="explainability"
      ref={ref as React.RefObject<HTMLElement>}
      className="overflow-hidden bg-[#070a2b] px-6 py-32 md:px-12"
    >
      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-16 lg:grid-cols-12">
        <div
          className={`fade-in-up relative lg:col-span-5 ${
            visible ? "is-visible" : ""
          }`}
        >
          <div className="absolute -left-16 -top-16 h-64 w-64 rounded-full bg-[#70d2ff]/10 blur-[100px]" />
          <span
            className={`mb-4 block text-sm uppercase tracking-[0.2em] text-[#70d2ff] ${monoFont.className}`}
          >
            {homepageCopy.explainability.eyebrow}
          </span>
          <h2
            className={`mb-8 text-4xl font-black leading-[1.02] tracking-[-0.02em] md:text-5xl ${displayFont.className}`}
          >
            {homepageCopy.explainability.titleLine1}
            <br />
            {homepageCopy.explainability.titleLine2}
          </h2>
          <p className="mb-8 text-base leading-8 text-[#bdc8d0] md:text-lg">
            {homepageCopy.explainability.description}
          </p>
          <ul className="space-y-5">
            <li className="flex items-start gap-4">
              <div className="rounded-md bg-[#70d2ff]/20 p-2">
                <Workflow className="h-4 w-4 text-[#70d2ff]" />
              </div>
              <div>
                <p className={`font-bold ${displayFont.className}`}>
                  {homepageCopy.explainability.points[0].title}
                </p>
                <p className="text-sm leading-7 text-[#bdc8d0]">
                  {homepageCopy.explainability.points[0].body}
                </p>
              </div>
            </li>
            <li className="flex items-start gap-4">
              <div className="rounded-md bg-[#a5c8ff]/20 p-2">
                <GitBranch className="h-4 w-4 text-[#a5c8ff]" />
              </div>
              <div>
                <p className={`font-bold ${displayFont.className}`}>
                  {homepageCopy.explainability.points[1].title}
                </p>
                <p className="text-sm leading-7 text-[#bdc8d0]">
                  {homepageCopy.explainability.points[1].body}
                </p>
              </div>
            </li>
          </ul>
        </div>

        <div
          className={`fade-in-up stagger-3 lg:col-span-7 ${
            visible ? "is-visible" : ""
          }`}
        >
          <div className="rounded-2xl border border-[#3d484f]/20 bg-[#232748] p-4 shadow-2xl">
            <div className="mb-4 flex items-center justify-between px-2">
              <div className="flex gap-1.5">
                <div className="h-3 w-3 rounded-full bg-[#ffb4ab]/40" />
                <div className="h-3 w-3 rounded-full bg-[#a5c8ff]/40" />
                <div className="h-3 w-3 rounded-full bg-[#70d2ff]/40" />
              </div>
              <p
                className={`text-[10px] uppercase tracking-[0.2em] text-[#bdc8d0]/70 ${monoFont.className}`}
              >
                {homepageCopy.explainability.liveFeed.title}
              </p>
            </div>
            <div className="group relative aspect-video overflow-hidden rounded-xl bg-[#151939]">
              <Image
                fill
                className="object-cover opacity-75 grayscale-[60%] transition duration-700 group-hover:grayscale-0 group-hover:opacity-100"
                src="/hero-graph.png"
                alt={homepageCopy.explainability.liveFeed.dashboardAlt}
              />
              <div className="pointer-events-none absolute right-4 top-4 rounded-md border border-[#70d2ff]/20 bg-[#070a2b]/70 px-2 py-1 opacity-100 transition duration-500 group-hover:opacity-0">
                <p
                  className={`text-[9px] uppercase tracking-[0.15em] text-[#70d2ff]/70 ${monoFont.className}`}
                >
                  hover to reveal
                </p>
              </div>
              <div className="absolute inset-0 bg-gradient-to-t from-[#070a2b] via-transparent to-transparent" />
              <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
                <div
                  className={`space-y-1 text-[10px] text-[#70d2ff] ${monoFont.className}`}
                >
                  {homepageCopy.explainability.liveFeed.stats.map((stat) => (
                    <p key={stat}>{stat}</p>
                  ))}
                </div>
                <div className="rounded-lg border border-[#70d2ff]/30 bg-[#70d2ff]/20 p-4 backdrop-blur-md">
                  <p
                    className={`mb-2 text-[10px] uppercase text-[#70d2ff] ${monoFont.className}`}
                  >
                    {homepageCopy.explainability.liveFeed.shapTitle}
                  </p>
                  <div className="flex h-8 items-end gap-2">
                    <div className={`shap-bar w-2 self-stretch bg-[#70d2ff] ${visible ? "is-visible" : ""}`} style={{ transitionDelay: "0.4s", height: "100%" }} />
                    <div className={`shap-bar w-2 bg-[#70d2ff] ${visible ? "is-visible" : ""}`} style={{ transitionDelay: "0.55s", height: "50%" }} />
                    <div className={`shap-bar w-2 bg-[#70d2ff] ${visible ? "is-visible" : ""}`} style={{ transitionDelay: "0.7s", height: "75%" }} />
                    <div className={`shap-bar w-2 bg-[#70d2ff] ${visible ? "is-visible" : ""}`} style={{ transitionDelay: "0.85s", height: "25%" }} />
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>
      </div>
    </section>
  );
}

function IntegritySection() {
  const { ref, visible } = useInView();
  return (
    <section
      id="integrity"
      ref={ref as React.RefObject<HTMLElement>}
      className="bg-[#0c1030] px-6 py-28 md:px-12"
    >
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-16 md:flex-row">
        <div
          className={`fade-in-up stagger-1 order-2 w-full md:order-1 md:w-1/2 ${
            visible ? "is-visible" : ""
          }`}
        >
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border-l-4 border-[#a5c8ff] bg-[#151939] p-6">
              <h4 className={`mb-2 font-bold ${displayFont.className}`}>
                {homepageCopy.integrity.cards[0].title}
              </h4>
              <p className="text-xs text-[#bdc8d0]">
                {homepageCopy.integrity.cards[0].body}
              </p>
            </div>
            <div className="rounded-xl border-l-4 border-[#ddb7ff] bg-[#151939] p-6">
              <h4 className={`mb-2 font-bold ${displayFont.className}`}>
                {homepageCopy.integrity.cards[1].title}
              </h4>
              <p className="text-xs text-[#bdc8d0]">
                {homepageCopy.integrity.cards[1].body}
              </p>
            </div>
            <div className="col-span-2 flex items-center justify-between rounded-xl bg-[#151939] p-8">
              <div>
                <h3 className={`text-xl font-bold ${displayFont.className}`}>
                  {homepageCopy.integrity.dashboard.title}
                </h3>
                <p className="mt-2 text-sm text-[#bdc8d0]">
                  {homepageCopy.integrity.dashboard.body}
                </p>
              </div>
              <button
                className={`rounded-lg border border-[#3d484f]/40 px-5 py-2.5 text-xs font-bold uppercase tracking-[0.12em] text-[#bdc8d0] transition-colors duration-200 hover:bg-[#232748] hover:text-[#dfe0ff] ${monoFont.className}`}
              >
                {homepageCopy.integrity.dashboard.cta}
              </button>
            </div>
          </div>
        </div>
        <div
          className={`fade-in-up stagger-3 order-1 w-full md:order-2 md:w-1/2 ${
            visible ? "is-visible" : ""
          }`}
        >
          <div className="mb-8 flex items-center justify-between">
            <span
              className={`text-sm uppercase tracking-[0.2em] text-[#70d2ff] ${monoFont.className}`}
            >
              {homepageCopy.integrity.eyebrow}
            </span>
          </div>
          <h2
            className={`mb-8 text-4xl font-black leading-[1.02] tracking-[-0.02em] md:text-5xl ${displayFont.className}`}
          >
            {homepageCopy.integrity.title}
          </h2>
          <p className="text-base leading-8 text-[#bdc8d0] md:text-lg">
            {homepageCopy.integrity.description}
          </p>
          <div className="mt-8 flex items-center gap-4">
            <div className="flex -space-x-3">
              {homepageCopy.integrity.people.images.map((person) => (
                <Image
                  key={person.alt}
                  width={40}
                  height={40}
                  className="rounded-full border-2 border-[#0c1030] object-cover"
                  src={person.src}
                  alt={person.alt}
                />
              ))}
            </div>
            <p className="text-sm text-[#bdc8d0]">
              {homepageCopy.integrity.people.trustLine}
            </p>
          </div>
        </div>
      </div>
    </section>
  );
}

const specIcons: Record<string, React.ReactNode> = {
  workflow: <Workflow className="h-5 w-5 text-[#70d2ff]" />,
  scale: <Scale className="h-5 w-5 text-[#a5c8ff]" />,
  database: <Database className="h-5 w-5 text-[#ddb7ff]" />,
};

function TechnicalSpecsSection() {
  const { ref, visible } = useInView();
  return (
    <section
      id="tech-specs"
      ref={ref as React.RefObject<HTMLElement>}
      className="bg-[#070a2b] px-6 py-28 md:px-12"
    >
      <div className="mx-auto max-w-7xl">
        <div className="mb-20 text-center">
          <h2
            className={`mb-4 text-4xl font-black uppercase tracking-[0.08em] ${displayFont.className}`}
          >
            {homepageCopy.technicalSpecs.title}
          </h2>
          <div className="mx-auto h-1 w-24 bg-[#70d2ff]" />
        </div>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {homepageCopy.technicalSpecs.columns.map((column, i) => (
            <div
              key={column.title}
              className={`fade-in-up ${staggerClasses[i]} border-t border-[#3d484f]/20 p-8 ${
                visible ? "is-visible" : ""
              }`}
            >
              <div className="mb-4 inline-flex h-9 w-9 items-center justify-center rounded-lg bg-[#151939]">
                {specIcons[column.icon]}
              </div>
              <span
                className={`mb-3 block text-xs uppercase tracking-[0.18em] text-[#70d2ff] ${monoFont.className}`}
              >
                {column.label}
              </span>
              <h4 className={`mb-4 text-xl font-bold ${displayFont.className}`}>
                {column.title}
              </h4>
              <p className="text-sm leading-7 text-[#bdc8d0]">{column.body}</p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCtaSection() {
  const { ref, visible } = useInView();
  return (
    <section
      ref={ref as React.RefObject<HTMLElement>}
      className="relative overflow-hidden bg-[#070a2b] px-6 py-36 md:px-12"
    >
      <div className="absolute inset-0 bg-gradient-to-br from-[#70d2ff]/10 via-transparent to-[#ddb7ff]/10" />
      <div
        className={`fade-in-up relative mx-auto w-full max-w-4xl text-center ${
          visible ? "is-visible" : ""
        }`}
      >
        <h2
          className={`mb-10 text-4xl font-black leading-[1.05] tracking-[-0.02em] md:text-6xl ${displayFont.className}`}
        >
          {homepageCopy.finalCta.title}
        </h2>
        <div
          className={`flex flex-col justify-center gap-4 sm:flex-row ${displayFont.className}`}
        >
          <Link
            href="/login"
            className="rounded-md bg-gradient-to-r from-[#70d2ff] to-[#00aadd] px-12 py-5 text-xl font-black uppercase tracking-tight text-[#003547]"
          >
            {homepageCopy.finalCta.primary}
          </Link>
          <Link
            href="/login"
            className="rounded-md border border-[#3d484f] bg-transparent px-12 py-5 text-xl font-black uppercase tracking-tight text-[#dfe0ff] transition hover:bg-[#151939]"
          >
            {homepageCopy.finalCta.secondary}
          </Link>
        </div>
      </div>
    </section>
  );
}

const footerAnchors: Record<string, Record<string, string>> = {
  platform: {
    Overview: "#",
    "Agent Scope": "#explainability",
    "Operational Queues": "#ecosystem",
  },
  resources: {
    "Project Proposal": "#",
    "Project Report": "#",
    "Risk Register": "#",
  },
  legal: {
    "Fairness Audit": "#",
    "Appeals Policy": "#",
  },
};

function FooterSection() {
  return (
    <footer className="border-t border-[#3d484f]/20 bg-[#070a2b] px-6 py-12 md:px-12">
      <div className="mx-auto grid max-w-7xl grid-cols-2 gap-8 md:grid-cols-5">
        <div className="col-span-2">
          <div className="mb-4 flex items-center gap-2">
            <div className="rounded-md bg-white p-1 shadow-[0_4px_18px_rgba(0,0,0,0.25)]">
              <Image
                src="/logo.png"
                alt={homepageCopy.brand.logoAlt}
                width={24}
                height={24}
                className="rounded-sm"
              />
            </div>
            <p
              className={`text-lg font-black text-[#70d2ff] ${displayFont.className}`}
            >
              {homepageCopy.brand.name}
            </p>
          </div>
          <p
            className={`max-w-xs text-xs uppercase tracking-[0.2em] text-[#bdc8d0] ${monoFont.className}`}
          >
            {homepageCopy.footer.tagline}
          </p>
        </div>
        <div className="flex flex-col gap-4">
          <span
            className={`text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60 ${monoFont.className}`}
          >
            {homepageCopy.footer.groups.platform.label}
          </span>
          {homepageCopy.footer.groups.platform.links.map((item) => (
            <a
              key={item}
              href={footerAnchors.platform[item] ?? "#"}
              className={`text-xs uppercase tracking-[0.16em] text-[#bdc8d0] transition-colors hover:text-[#70d2ff] ${monoFont.className}`}
            >
              {item}
            </a>
          ))}
        </div>
        <div className="flex flex-col gap-4">
          <span
            className={`text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60 ${monoFont.className}`}
          >
            {homepageCopy.footer.groups.resources.label}
          </span>
          {homepageCopy.footer.groups.resources.links.map((item) => (
            <a
              key={item}
              href={footerAnchors.resources[item] ?? "#"}
              className={`text-xs uppercase tracking-[0.16em] text-[#bdc8d0] transition-colors hover:text-[#70d2ff] ${monoFont.className}`}
            >
              {item}
            </a>
          ))}
        </div>
        <div className="flex flex-col gap-4">
          <span
            className={`text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60 ${monoFont.className}`}
          >
            {homepageCopy.footer.groups.legal.label}
          </span>
          {homepageCopy.footer.groups.legal.links.map((item) => (
            <a
              key={item}
              href={footerAnchors.legal[item] ?? "#"}
              className={`text-xs uppercase tracking-[0.16em] text-[#bdc8d0] transition-colors hover:text-[#70d2ff] ${monoFont.className}`}
            >
              {item}
            </a>
          ))}
        </div>
      </div>
      <div className="mx-auto mt-12 max-w-7xl border-t border-[#3d484f]/20 pt-8 text-center">
        <p
          className={`text-[10px] uppercase tracking-[0.3em] text-[#bdc8d0] ${monoFont.className}`}
        >
          {homepageCopy.footer.copyright}
        </p>
      </div>
    </footer>
  );
}

export default function HomePage() {
  const [scrolled, setScrolled] = useState(false);
  const scrollProgress = useScrollProgress();

  useEffect(() => {
    const onScroll = () => setScrolled(window.scrollY > 100);
    onScroll();
    window.addEventListener("scroll", onScroll);
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div
      className={`min-h-screen overflow-x-hidden bg-[#0c1030] text-[#dfe0ff] ${bodyFont.className}`}
    >
      <ScrollProgressBar progress={scrollProgress} />
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_15%_20%,rgba(112,210,255,0.18),transparent_28%),radial-gradient(circle_at_80%_0%,rgba(192,128,255,0.14),transparent_30%)]" />
      <TopNav scrolled={scrolled} />
      <HeroSection />
      <EcosystemSection />
      <ExplainabilitySection />
      <IntegritySection />
      <TechnicalSpecsSection />
      <FinalCtaSection />
      <FooterSection />
    </div>
  );
}
