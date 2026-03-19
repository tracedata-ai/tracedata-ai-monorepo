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

const homepageCopy = {
  brand: {
    name: "TraceData",
    logoAlt: "TraceData logo",
  },
  nav: {
    active: "Explorer",
    items: ["Metrics", "Logs", "Traces", "Docs"],
    signIn: "Sign In",
    getStarted: "Get Started",
  },
  hero: {
    imageAlt:
      "Cinematic wide shot of a high-tech semi-truck on highway with glowing data beam",
    badge: "Mission Control Alpha v2.4",
    titleLine1: "Intelligent Fleet",
    titleAccent: "Orchestration",
    description:
      "AI intelligence middleware for small-to-medium fleets. TraceData closes 7 critical gaps in telematics: fairness, coaching, burnout detection, appeals, contextual scoring, trust, and integrated safety-welfare response.",
    primaryCta: "Get Started",
    secondaryCta: "Watch Demo",
    scrollHint: "Scroll to Discover",
  },
  ecosystem: {
    eyebrow: "The Neural Backbone",
    title: "The 8-Agent Ecosystem",
    description:
      "Eight autonomous agents operating through a central orchestration graph to ensure fairness, accountability, explainability, and operational safety.",
    cards: {
      safety: {
        title: "Safety Agent",
        body: "Priority-queue critical incident response with multi-level intervention (app notification, formal message, direct call) under a sub-5-second response objective.",
        queue: "> QUEUE: queue.critical",
        action: "> ACTION: emergency_services + fleet_manager_alert",
      },
      behavior: {
        title: "Behavior Agent",
        body: "XGBoost trip scoring (0-100) with AIF360 fairness audits and SHAP/LIME explainability for every score decision.",
      },
      orchestrator: {
        title: "Orchestrator Agent",
        body: "Central router using deterministic rules plus semantic routing for unstructured text, with full audit logging.",
      },
      feedback: {
        title: "Feedback & Advocacy Agent",
        body: "Driver appeals and feedback ingestion with semantic retrieval, ensuring contestable and transparent outcomes.",
      },
      sentiment: {
        title: "Sentiment Agent",
        body: "Emotional trajectory analysis to identify burnout risk early and trigger supportive fleet-manager interventions.",
      },
      coaching: "Coaching Agent",
      context: "Context Enrichment Agent",
      ingestion: {
        title: "Ingestion Quality Agent",
        body: "Validates telemetry plus unstructured appeal payloads, handles batched pings and critical bypass routing.",
      },
    },
  },
  explainability: {
    eyebrow: "Deep Tech Stack",
    titleLine1: "Mission Control",
    titleLine2: "Explainability",
    description:
      "TraceData does not just score events; it exposes decision logic. SHAP and LIME explainability are paired with fairness checks so every intervention is observable, reviewable, and contestable.",
    points: [
      {
        title: "Kafka-Driven Orchestration",
        body: "FastAPI + Celery + Redis priority queues route critical, high, medium, and low events with deterministic SLAs.",
      },
      {
        title: "Fairness + SHAP/LIME Attribution",
        body: "Monthly bias audits (AIF360) and feature-level explanations for each behavioral score and appeal decision.",
      },
    ],
    liveFeed: {
      title: "Live Explainability Feed",
      dashboardAlt:
        "Technical data visualization dashboard with SHAP graphs and fleet status",
      stats: ["LATENCY: 12ms", "JITTER: 0.02ms", "NODE_ID: TR-808"],
      shapTitle: "SHAP Influence",
    },
  },
  integrity: {
    eyebrow: "The Integrity Layer",
    title: "Human-in-the-Loop",
    description:
      "Drivers can appeal decisions and fleet managers can override with complete context. The goal is support over surveillance, with transparent intervention logs for governance.",
    cards: [
      {
        title: "Direct Appeals",
        body: "Instant override capability for human operators in edge cases.",
      },
      {
        title: "Post-Action Coaching",
        body: "Intervention data continuously improves agent logic.",
      },
    ],
    dashboard: {
      title: "Operator Dashboard",
      body: "Machines ask for permission, not forgiveness.",
      cta: "Launch Shell",
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
      trustLine: "Trusted by 2,000+ logistics supervisors worldwide.",
    },
  },
  technicalSpecs: {
    title: "Technical Specifications",
    columns: [
      {
        label: "Orchestration",
        title: "LangGraph + Router Core",
        body: "Agent nodes execute through conditional routing with audited decisions from the central Orchestrator Agent.",
      },
      {
        label: "Fairness & Explainability",
        title: "AIF360 + SHAP + LIME",
        body: "Bias detection, mitigation, and interpretable scoring are built directly into the Behavior Agent lifecycle.",
      },
      {
        label: "Runtime Stack",
        title: "FastAPI + Celery/Redis + PostgreSQL/pgvector",
        body: "Production-ready async APIs, priority task queues, ACID event storage, and vector search for appeal context retrieval.",
      },
    ],
  },
  finalCta: {
    title: "Ready to Orchestrate?",
    primary: "Deploy Now",
    secondary: "Request Specs",
  },
  footer: {
    tagline:
      "Built for the Architectural Lens. High-integrity fleet intelligence.",
    groups: {
      platform: {
        label: "Platform",
        links: ["Explorer", "Metrics", "Status"],
      },
      resources: {
        label: "Resources",
        links: ["Docs", "Changelog", "Security"],
      },
      legal: {
        label: "Legal",
        links: ["Privacy", "Terms"],
      },
    },
    copyright: "2026 TraceData. All rights reserved.",
  },
};

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
          <div className="hidden items-center gap-6 text-sm font-medium md:flex">
            <a className="border-b-2 border-[#70d2ff] pb-1 text-[#70d2ff]">
              {homepageCopy.nav.active}
            </a>
            {homepageCopy.nav.items.map((item) => (
              <a key={item} className="text-[#bdc8d0] hover:text-[#70d2ff]">
                {item}
              </a>
            ))}
          </div>
        </div>
        <div className="flex items-center gap-3">
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
        <img
          className="h-full w-full object-cover object-[62%_50%] md:object-[60%_46%]"
          src="/hero-uw.png"
          alt={homepageCopy.hero.imageAlt}
        />
        <div className="absolute inset-0 bg-[linear-gradient(112deg,rgba(12,16,48,0.68)_0%,rgba(12,16,48,0.54)_30%,rgba(12,16,48,0.26)_52%,rgba(12,16,48,0.10)_72%,rgba(12,16,48,0.03)_100%)]" />
        <div className="absolute inset-0 bg-gradient-to-t from-[#0c1030]/36 via-transparent to-transparent" />
        <div className="absolute inset-0 bg-[radial-gradient(circle_at_18%_18%,rgba(12,16,48,0.30),transparent_42%)]" />
      </div>

      <div className="relative z-10 mx-auto grid w-full max-w-7xl grid-cols-1 items-center px-6 py-24 lg:grid-cols-12 lg:gap-8">
        <div className="lg:col-span-6">
          <div className="mb-6 inline-block rounded-full border border-[#70d2ff]/35 bg-[#70d2ff]/12 px-4 py-1">
            <span className="text-xs uppercase tracking-[0.2em] text-[#70d2ff]">
              {homepageCopy.hero.badge}
            </span>
          </div>
          <h1 className="mb-8 text-5xl font-black tracking-tighter text-[#dfe0ff] md:text-7xl lg:text-8xl">
            {homepageCopy.hero.titleLine1}
            <br />
            <span className="bg-gradient-to-r from-[#70d2ff] via-[#a5c8ff] to-[#00aadd] bg-clip-text text-transparent">
              {homepageCopy.hero.titleAccent}
            </span>
          </h1>
          <p className="mb-12 max-w-2xl text-lg font-light leading-relaxed text-[#bdc8d0] md:text-2xl">
            {homepageCopy.hero.description}
          </p>
          <div className="flex flex-col items-start gap-4 sm:flex-row sm:items-center">
            <Link
              href="/login"
              className="group inline-flex items-center rounded-lg bg-gradient-to-r from-[#70d2ff] to-[#00aadd] px-8 py-4 text-lg font-bold text-[#003547] shadow-xl transition hover:shadow-[#70d2ff]/20"
            >
              {homepageCopy.hero.primaryCta}
              <ArrowRight className="ml-2 h-5 w-5 transition-transform group-hover:translate-x-1" />
            </Link>
            <Link
              href="/fleet-manager"
              className="inline-flex items-center rounded-lg border border-[#3d484f]/40 px-8 py-4 text-lg font-bold text-[#bdc8d0] transition hover:bg-[#232748]"
            >
              <PlayCircle className="mr-2 h-5 w-5" />
              {homepageCopy.hero.secondaryCta}
            </Link>
          </div>
        </div>
        <div className="hidden lg:col-span-6 lg:block" />
      </div>

      <div className="absolute bottom-12 left-1/2 z-10 -translate-x-1/2 opacity-40">
        <p className="mb-4 text-[10px] uppercase tracking-[0.3em]">
          {homepageCopy.hero.scrollHint}
        </p>
        <div className="mx-auto h-12 w-px bg-gradient-to-b from-[#70d2ff] to-transparent" />
      </div>
    </header>
  );
}

function EcosystemSection() {
  return (
    <section className="bg-[#0c1030] px-6 py-28 md:px-12">
      <div className="mx-auto max-w-7xl">
        <div className="mb-16 flex flex-col gap-6 md:flex-row md:items-end md:justify-between">
          <div className="max-w-xl">
            <span className="mb-4 block text-sm uppercase tracking-[0.2em] text-[#70d2ff]">
              {homepageCopy.ecosystem.eyebrow}
            </span>
            <h2 className="text-5xl font-extrabold tracking-tight text-[#dfe0ff]">
              {homepageCopy.ecosystem.title}
            </h2>
          </div>
          <p className="max-w-sm text-lg font-light text-[#bdc8d0] md:text-right">
            {homepageCopy.ecosystem.description}
          </p>
        </div>

        <div className="grid grid-cols-1 gap-4 md:grid-cols-4">
          <div className="rounded-xl bg-[#151939] p-8 transition hover:bg-[#191d3d] md:col-span-2 md:row-span-2">
            <div className="mb-6 inline-flex h-12 w-12 items-center justify-center rounded-full bg-[#70d2ff]/10">
              <Shield className="h-5 w-5 text-[#70d2ff]" />
            </div>
            <h3 className="mb-4 text-2xl font-bold text-[#dfe0ff]">
              {homepageCopy.ecosystem.cards.safety.title}
            </h3>
            <p className="leading-relaxed text-[#bdc8d0]">
              {homepageCopy.ecosystem.cards.safety.body}
            </p>
            <div className="mt-10 rounded-lg bg-[#070a2b] p-4 text-xs text-[#70d2ff]/80">
              {homepageCopy.ecosystem.cards.safety.queue}
              <br />
              {homepageCopy.ecosystem.cards.safety.action}
            </div>
          </div>

          <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
            <Scale className="mb-5 h-7 w-7 text-[#a5c8ff]" />
            <h3 className="mb-3 text-xl font-bold">
              {homepageCopy.ecosystem.cards.behavior.title}
            </h3>
            <p className="text-sm text-[#bdc8d0]">
              {homepageCopy.ecosystem.cards.behavior.body}
            </p>
          </div>
          <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
            <Network className="mb-5 h-7 w-7 text-[#ddb7ff]" />
            <h3 className="mb-3 text-xl font-bold">
              {homepageCopy.ecosystem.cards.orchestrator.title}
            </h3>
            <p className="text-sm text-[#bdc8d0]">
              {homepageCopy.ecosystem.cards.orchestrator.body}
            </p>
          </div>
          <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
            <Bolt className="mb-5 h-7 w-7 text-[#00aadd]" />
            <h3 className="mb-3 text-xl font-bold">
              {homepageCopy.ecosystem.cards.feedback.title}
            </h3>
            <p className="text-sm text-[#bdc8d0]">
              {homepageCopy.ecosystem.cards.feedback.body}
            </p>
          </div>
          <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
            <Lock className="mb-5 h-7 w-7 text-[#ddb7ff]" />
            <h3 className="mb-3 text-xl font-bold">
              {homepageCopy.ecosystem.cards.sentiment.title}
            </h3>
            <p className="text-sm text-[#bdc8d0]">
              {homepageCopy.ecosystem.cards.sentiment.body}
            </p>
          </div>

          <div className="md:col-span-2 grid grid-cols-2 gap-4">
            <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
              <h3 className="mb-2 text-lg font-bold">
                {homepageCopy.ecosystem.cards.coaching}
              </h3>
              <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-[#3d484f]/40">
                <div className="h-full w-full bg-[#a5c8ff]" />
              </div>
            </div>
            <div className="rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
              <h3 className="mb-2 text-lg font-bold">
                {homepageCopy.ecosystem.cards.context}
              </h3>
              <div className="mt-4 h-1 w-full overflow-hidden rounded-full bg-[#3d484f]/40">
                <div className="h-full w-full bg-[#00aadd]" />
              </div>
            </div>
            <div className="col-span-2 flex items-center justify-between rounded-xl bg-[#151939] p-7 transition hover:bg-[#191d3d]">
              <div>
                <h3 className="text-lg font-bold">
                  {homepageCopy.ecosystem.cards.ingestion.title}
                </h3>
                <p className="text-sm text-[#bdc8d0]">
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
  return (
    <section className="overflow-hidden bg-[#070a2b] px-6 py-32 md:px-12">
      <div className="mx-auto grid max-w-7xl grid-cols-1 items-center gap-16 lg:grid-cols-12">
        <div className="relative lg:col-span-5">
          <div className="absolute -left-16 -top-16 h-64 w-64 rounded-full bg-[#70d2ff]/10 blur-[100px]" />
          <span className="mb-4 block text-sm uppercase tracking-[0.2em] text-[#70d2ff]">
            {homepageCopy.explainability.eyebrow}
          </span>
          <h2 className="mb-8 text-5xl font-black tracking-tighter leading-none">
            {homepageCopy.explainability.titleLine1}
            <br />
            {homepageCopy.explainability.titleLine2}
          </h2>
          <p className="mb-8 text-lg leading-relaxed text-[#bdc8d0]">
            {homepageCopy.explainability.description}
          </p>
          <ul className="space-y-5">
            <li className="flex items-start gap-4">
              <div className="rounded-md bg-[#70d2ff]/20 p-2">
                <Workflow className="h-4 w-4 text-[#70d2ff]" />
              </div>
              <div>
                <p className="font-bold">
                  {homepageCopy.explainability.points[0].title}
                </p>
                <p className="text-sm text-[#bdc8d0]">
                  {homepageCopy.explainability.points[0].body}
                </p>
              </div>
            </li>
            <li className="flex items-start gap-4">
              <div className="rounded-md bg-[#a5c8ff]/20 p-2">
                <GitBranch className="h-4 w-4 text-[#a5c8ff]" />
              </div>
              <div>
                <p className="font-bold">
                  {homepageCopy.explainability.points[1].title}
                </p>
                <p className="text-sm text-[#bdc8d0]">
                  {homepageCopy.explainability.points[1].body}
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
                {homepageCopy.explainability.liveFeed.title}
              </p>
            </div>
            <div className="relative aspect-video overflow-hidden rounded-xl bg-[#151939]">
              <img
                className="h-full w-full object-cover opacity-55 grayscale transition duration-700 hover:grayscale-0"
                src="https://lh3.googleusercontent.com/aida-public/AB6AXuCWFnGNuyZQNfXMSZnEr5350Lej79-PItNK_hVzMWatAmrOOytEvLa6CuyD7t1R_deSXI66vMIwQO4ivD5x6PmvFj7yJad97HQ8ouLXRZAbkWeiMRUpPX9Pp5T955VTBUdltb5p8kxvcshJmtVB5qD2sgtOrFPDezhpB9PYyXrOOPsrLTK3FJa0bKJECQ1igM910LQFO_vvb_uWTSRF_CIr_NiBlAqJ4f9ac1UOURWfglbVzGnlBJQ7muupLiTbpaH9BCezIEfaYaEF"
                alt={homepageCopy.explainability.liveFeed.dashboardAlt}
              />
              <div className="absolute inset-0 bg-gradient-to-t from-[#070a2b] via-transparent to-transparent" />
              <div className="absolute bottom-6 left-6 right-6 flex items-end justify-between">
                <div className="space-y-1 text-[10px] text-[#70d2ff]">
                  {homepageCopy.explainability.liveFeed.stats.map((stat) => (
                    <p key={stat}>{stat}</p>
                  ))}
                </div>
                <div className="rounded-lg border border-[#70d2ff]/30 bg-[#70d2ff]/20 p-4 backdrop-blur-md">
                  <p className="mb-2 text-[10px] uppercase text-[#70d2ff]">
                    {homepageCopy.explainability.liveFeed.shapTitle}
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
  );
}

function IntegritySection() {
  return (
    <section className="bg-[#0c1030] px-6 py-28 md:px-12">
      <div className="mx-auto flex max-w-7xl flex-col items-center gap-16 md:flex-row">
        <div className="order-2 w-full md:order-1 md:w-1/2">
          <div className="grid grid-cols-2 gap-4">
            <div className="rounded-xl border-l-4 border-[#a5c8ff] bg-[#151939] p-6">
              <h4 className="mb-2 font-bold">
                {homepageCopy.integrity.cards[0].title}
              </h4>
              <p className="text-xs text-[#bdc8d0]">
                {homepageCopy.integrity.cards[0].body}
              </p>
            </div>
            <div className="rounded-xl border-l-4 border-[#ddb7ff] bg-[#151939] p-6">
              <h4 className="mb-2 font-bold">
                {homepageCopy.integrity.cards[1].title}
              </h4>
              <p className="text-xs text-[#bdc8d0]">
                {homepageCopy.integrity.cards[1].body}
              </p>
            </div>
            <div className="col-span-2 flex items-center justify-between rounded-xl bg-[#151939] p-8">
              <div>
                <h3 className="text-xl font-bold">
                  {homepageCopy.integrity.dashboard.title}
                </h3>
                <p className="mt-2 text-sm text-[#bdc8d0]">
                  {homepageCopy.integrity.dashboard.body}
                </p>
              </div>
              <button className="rounded bg-[#3d484f]/30 px-4 py-2 text-xs uppercase tracking-[0.16em] transition hover:bg-[#3d484f]/45">
                {homepageCopy.integrity.dashboard.cta}
              </button>
            </div>
          </div>
        </div>
        <div className="order-1 w-full md:order-2 md:w-1/2">
          <div className="mb-8 flex items-center justify-between">
            <span className="text-sm uppercase tracking-[0.2em] text-[#70d2ff]">
              {homepageCopy.integrity.eyebrow}
            </span>
          </div>
          <h2 className="mb-8 text-5xl font-black tracking-tighter">
            {homepageCopy.integrity.title}
          </h2>
          <p className="text-lg text-[#bdc8d0]">
            {homepageCopy.integrity.description}
          </p>
          <div className="mt-8 flex items-center gap-4">
            <div className="flex -space-x-3">
              {homepageCopy.integrity.people.images.map((person) => (
                <img
                  key={person.alt}
                  className="h-10 w-10 rounded-full border-2 border-[#0c1030] object-cover"
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

function TechnicalSpecsSection() {
  return (
    <section className="bg-[#070a2b] px-6 py-28 md:px-12">
      <div className="mx-auto max-w-7xl">
        <div className="mb-20 text-center">
          <h2 className="mb-4 text-4xl font-black uppercase tracking-[0.12em]">
            {homepageCopy.technicalSpecs.title}
          </h2>
          <div className="mx-auto h-1 w-24 bg-[#70d2ff]" />
        </div>
        <div className="grid grid-cols-1 gap-8 md:grid-cols-3">
          {homepageCopy.technicalSpecs.columns.map((column) => (
            <div
              key={column.title}
              className="border-t border-[#3d484f]/20 p-8"
            >
              <span className="mb-4 block text-xs uppercase tracking-[0.18em] text-[#70d2ff]">
                {column.label}
              </span>
              <h4 className="mb-4 text-xl font-bold">{column.title}</h4>
              <p className="text-sm leading-relaxed text-[#bdc8d0]">
                {column.body}
              </p>
            </div>
          ))}
        </div>
      </div>
    </section>
  );
}

function FinalCtaSection() {
  return (
    <section className="relative overflow-hidden bg-[#070a2b] px-6 py-36 md:px-12">
      <div className="absolute inset-0 bg-gradient-to-br from-[#70d2ff]/10 via-transparent to-[#ddb7ff]/10" />
      <div className="relative mx-auto w-full max-w-4xl text-center">
        <h2 className="mb-12 text-5xl font-black tracking-tighter md:text-6xl">
          {homepageCopy.finalCta.title}
        </h2>
        <div className="flex flex-col justify-center gap-4 sm:flex-row">
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
            <p className="text-lg font-black text-[#70d2ff]">
              {homepageCopy.brand.name}
            </p>
          </div>
          <p className="max-w-xs text-xs uppercase tracking-[0.2em] text-[#bdc8d0]">
            {homepageCopy.footer.tagline}
          </p>
        </div>
        <div className="flex flex-col gap-4">
          <span className="text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60">
            {homepageCopy.footer.groups.platform.label}
          </span>
          {homepageCopy.footer.groups.platform.links.map((item) => (
            <a
              key={item}
              className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]"
            >
              {item}
            </a>
          ))}
        </div>
        <div className="flex flex-col gap-4">
          <span className="text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60">
            {homepageCopy.footer.groups.resources.label}
          </span>
          {homepageCopy.footer.groups.resources.links.map((item) => (
            <a
              key={item}
              className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]"
            >
              {item}
            </a>
          ))}
        </div>
        <div className="flex flex-col gap-4">
          <span className="text-[10px] uppercase tracking-[0.2em] text-[#70d2ff]/60">
            {homepageCopy.footer.groups.legal.label}
          </span>
          {homepageCopy.footer.groups.legal.links.map((item) => (
            <a
              key={item}
              className="text-xs uppercase tracking-[0.16em] text-[#bdc8d0] hover:text-[#70d2ff]"
            >
              {item}
            </a>
          ))}
        </div>
      </div>
      <div className="mx-auto mt-12 max-w-7xl border-t border-[#3d484f]/20 pt-8 text-center">
        <p className="text-[10px] uppercase tracking-[0.3em] text-[#bdc8d0]">
          {homepageCopy.footer.copyright}
        </p>
      </div>
    </footer>
  );
}

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
