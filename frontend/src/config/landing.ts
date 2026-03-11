import { ShieldAlert, Scale, BrainCircuit, Activity, HeartHandshake, Smile, GraduationCap, Network } from "lucide-react";

export const landingConfig = {
  navbar: {
    logo: {
      prefix: "Trace",
      highlight: "Data",
    },
    links: [
      { label: "Ecosystem", href: "#" },
      { label: "Mission Control", href: "#" },
      { label: "Human-XAI", href: "#" },
      { label: "Solutions", href: "#" },
    ],
    cta: "Get Started",
  },
  hero: {
    title: {
      prefix: "INTELLIGENT ",
      highlight: "FLEET",
      suffix: " ORCHESTRATION",
    },
    description: "Fragmented data points coalescing into a coherent structure. TraceData leverages XAI metrics to harmonize global logistics in real-time.",
    primaryCta: "Launch Dashboard",
    secondaryCta: "Watch Identity Film",
    metrics: {
      activeOrchestration: {
        label: "Active Orchestration",
        value: "99.98",
        unit: "%"
      },
      latency: {
        label: "Latency",
        value: "12",
        unit: "ms"
      }
    },
    visualAlt: "High-tech XAI metrics visualization",
    visualSrc: "https://lh3.googleusercontent.com/aida-public/AB6AXuDDGW_Ial_icBZQUtxVNE5rxHPcUVm1r6XR2lpzlzksi2bub6VthpXrFSpKYMj7LP7C7TDP-LJJaKEvBATgJKTDecPz666JgtV8hUYNTI3qAhoObk57E3nxtK_UrYh_QZQ0cOl6isBTWkyg8lELV029x1SM_I1I8g2dFiQj_W4DpvAh5BI1HvtPPVi1IPVTT_jvbIcZFztInCI5qbWhVVa0AyocH3-3pXp30t8AxhWlpLmYPPvhDrmsGk23XYenX10BaVhll1U5616L"
  },
  ecosystem: {
    badge: "The Digital Ecosystem",
    title: "8-Agent Intelligent Network",
    agents: [
      {
        name: "Safety Agent",
        description: "Enforces operational guardrails and risk mitigation protocols.",
        icon: ShieldAlert,
        color: "brand-teal"
      },
      {
        name: "Fairness Agent",
        description: "Audits algorithmic bias in routing and load distribution.",
        icon: Scale,
        color: "brand-blue"
      },
      {
        name: "Context Agent",
        description: "Synthesizes environmental and historical data streams.",
        icon: Network,
        color: "brand-teal"
      },
      {
        name: "Behavior Agent",
        description: "Analyzes operator performance and cognitive load patterns.",
        icon: BrainCircuit,
        color: "brand-blue"
      },
      {
        name: "Advocacy Agent",
        description: "Represents human operator interests in the AI decision loop.",
        icon: HeartHandshake,
        color: "brand-teal"
      },
      {
        name: "Sentiment Agent",
        description: "Real-time morale tracking and wellness signaling.",
        icon: Smile,
        color: "brand-blue"
      },
      {
        name: "Coaching Agent",
        description: "Delivers interventions and performance-enhancing insights.",
        icon: GraduationCap,
        color: "brand-teal"
      },
      {
        name: "Orchestrator",
        description: "Synchronizes multi-agent workflows via LangGraph protocols.",
        icon: Activity,
        color: "brand-blue"
      }
    ],
    langGraph: {
      badge: "Real-Time Engine",
      subheading: "LangGraph & Kafka",
      title: "Unified Event Orchestration",
      description: "Every data point is a message in a high-throughput Kafka stream, processed through dynamic LangGraph workflows. Decisions are not static; they are conversational, evolving paths between 8 specialized agents.",
      features: [
        {
          title: "Sub-100ms Latency",
          description: "Stream processing at the edge for immediate recalibration.",
          color: "brand-teal"
        },
        {
          title: "Stateful Persistence",
          description: "Every agent decision is logged and traceable through our event ledger.",
          color: "brand-blue"
        }
      ],
      visualAlt: "LangGraph Data Flow",
      visualSrc: "https://lh3.googleusercontent.com/aida-public/AB6AXuDj8k8oBK_V3cKPuQDAArogNGh65bncmkSRi9KiUmJteASqPSaGNsf7fkElyp0GfhPogrjn6Y4_8eJSPcjpZ_Q5-WB7DHnicPdsVzPAiLjJpSXD6TIAx5RaRwFh1e_gp9xJs-tq_0Bdx4Jy5mVkGXv2z8UsBLPHx9IUyM1zy5uIx5hC-6NeJONz_eq0bczQNku9FzAQ6IpvDc86-Z887xbhW4ca6tSixBhOrj_yfO7UCO83OFtER0N75TPD-MUDtvqrT7_iJxgrYQUG"
    }
  },
  dashboardPreview: {
    subheading: "Intervention Hub",
    title: "Human-In-The-Loop Center",
    description: "Empowering operators with the ability to override AI logic. Our Mission Control features a dedicated Appeals workflow and Coaching intervention system for high-stakes decision auditing.",
    features: [
      { text: "One-click Appeals for AI Routing Decisions", color: "brand-teal" },
      { text: "Real-time Coaching Intervention Popups", color: "brand-blue" },
      { text: "Transparency Logs for Ethical Compliance", color: "foreground" }
    ],
    visualAlt: "Mission Control Dashboard Preview",
    visualSrc: "https://lh3.googleusercontent.com/aida-public/AB6AXuAr3RmLOAdG-PuFQCmbApOcasUYfhSRZ3o7DWqb5d4IJzB97gWL0ES7yHyy32F4K4-ytadITRVBb5GYm29HEYBN4tr-8PiC6Ij27tWIiylFxPN06eTBH0KOos2cAIu6B15jjAFsdBY-2buzS0uPZ_8hONmYg4_NCDbgErQ74A5h_uLHqqaLcqA6bHuGf8V7Wl48K3JXMun1Oqj_Z2_gFjZwLpOWzElorsivU3ZWywbYUmKacwGwveUNc5M6DtPVe6ZTJjG-JeKVFh2U"
  },
  humanInTheLoop: {
    subheading: "Human & AI Harmony",
    title: "Human-In-The-Loop Governance",
    description: "Technology doesn't replace intuition; it amplifies it. Our XAI system provides 'explainable' insights, allowing human operators to override and fine-tune complex decisions with complete context.",
    metrics: [
      { value: "SHAP", label: "Feature Attribution", color: "brand-blue" },
      { value: "0.88", label: "Fleet Equilibrium Score", color: "brand-teal" },
      { value: "XAI", label: "Explainability Depth", color: "foreground" }
    ]
  },
  burnoutHeatmap: {
    subheading: "Predictive Wellness",
    title: "Operational Burnout Heatmap",
    interventions: [
      {
        title: "Wellness Interventions",
        description: "AI-triggered rest periods and task reallocation based on cognitive load metrics.",
        color: "brand-teal"
      },
      {
        title: "Retention Modeling",
        description: "Predicting turnover risk 30 days in advance using behavior agent sentiment analysis.",
        color: "brand-blue"
      }
    ],
    visualAlt: "Burnout Heatmap",
    visualSrc: "https://lh3.googleusercontent.com/aida-public/AB6AXuDgHewQRcjfFoOJRPcpOU2flMlbQ7ot34CCyMOZBWf_Sp4nzYKKxKROvqs-QwyfyrmLFk_naWyAw_whvaFDRiJOgXG0QvrbWu2W8R9TV3cw2LQ-GroMcszXK6GQeM2VU2MFeQ9cDOyQxZ9YMgqZ0TYlRnnq6mpVmhDdpsi1MZ5GbUl1KvmTU_g15R7TTm8bYmbujcvPljlHXjYpt9GG_FClqwWz5pUuznUA4EWuuwMIKWcfpOr6ka0GnbF6_9J-_E-gbCzILNIFsYrR"
  },
  footer: {
    description: "Fragmenting the future of data orchestration to create a more coherent, efficient, and intelligent world.",
    links: [
      {
        title: "Company",
        items: [
          { label: "About Us", href: "#" },
          { label: "Careers", href: "#" },
          { label: "Brand Identity", href: "#" },
          { label: "Contact", href: "#" }
        ]
      }
    ],
    socials: [
      { platform: "LinkedIn", href: "#", color: "brand-teal" },
      { platform: "Twitter", href: "#", color: "brand-blue" }
    ],
    copyright: "© 2024 TraceData Systems. All Rights Reserved.",
    legalLinks: [
      { label: "Privacy Policy", href: "#" },
      { label: "Security Protocols", href: "#" }
    ]
  }
};
