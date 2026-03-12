import { ShieldAlert, Scale, BrainCircuit, Activity, HeartHandshake, Smile, GraduationCap, Network } from "lucide-react";

export const landingConfig = {
  navbar: {
    logo: {
      prefix: "Trace",
      highlight: "Data",
    },
    links: [
      { label: "Transparency", href: "#transparency" },
      { label: "Driver Advocacy", href: "#advocacy" },
      { label: "Solutions", href: "#solutions" },
      { label: "Resources", href: "#resources" },
    ],
    cta: "Launch Dashboard",
  },
  hero: {
    title: {
      prefix: "TRANSPARENCY ",
      highlight: "ON THE ROAD",
      suffix: "",
    },
    description: "Demystifying data to empower every driver and optimize every fleet. TraceData turns complex telemetry into clear, actionable insights.",
    primaryCta: "Get Started",
    secondaryCta: "Watch How It Works",
    metrics: {
      driverSatisfaction: {
        label: "Driver Satisfaction",
        value: "94",
        unit: "%"
      },
      dataClarity: {
        label: "Data Clarity Index",
        value: "0.98",
        unit: ""
      }
    },
    visualAlt: "Premium logistics hub at sunset",
    visualSrc: "/images/hero-bg.webp"
  },
  trustedBy: [
    { name: "DHL", logo: "/logos/dhl.svg" },
    { name: "FedEx", logo: "/logos/fedex.svg" },
    { name: "Amazon", logo: "/logos/amazon.svg" },
    { name: "Maersk", logo: "/logos/maersk.svg" },
  ],
  solutions: {
    badge: "The Future of Fleet",
    title: "Intelligence that works for you",
    items: [
      {
        title: "Driver Empowerment",
        description: "Giving drivers full visibility into their performance data and the 'why' behind system decisions.",
        icon: BrainCircuit,
        color: "brand-teal"
      },
      {
        title: "Operational Clarity",
        description: "Breaking down silos between management and the field with unified, transparent data streams.",
        icon: Network,
        color: "brand-blue"
      },
      {
        title: "Ethical Logistics",
        description: "AI that prioritizes fairness, safety, and human-centric orchestration.",
        icon: Scale,
        color: "brand-teal"
      }
    ]
  },
  transparency: {
    subheading: "Explainable AI",
    title: "Demystifying the Black Box",
    description: "Technology shouldn't be a mystery. Our XAI system provides drivers with clear explanations for route changes, safety alerts, and performance scores, ensuring trust through transparency.",
    features: [
      { text: "Real-time Explanation for AI Routing", color: "brand-teal" },
      { text: "Fair Performance Scoring with Feedback Loops", color: "brand-blue" },
      { text: "Open Ledger for Driver Decision Auditing", color: "foreground" }
    ],
    visualAlt: "XAI Transparency Dashboard",
    visualSrc: "https://lh3.googleusercontent.com/aida-public/AB6AXuAr3RmLOAdG-PuFQCmbApOcasUYfhSRZ3o7DWqb5d4IJzB97gWL0ES7yHyy32F4K4-ytadITRVBb5GYm29HEYBN4tr-8PiC6Ij27tWIiylFxPN06eTBH0KOos2cAIu6B15jjAFsdBY-2buzS0uPZ_8hONmYg4_NCDbgErQ74A5h_uLHqqaLcqA6bHuGf8V7Wl48K3JXMun1Oqj_Z2_gFjZwLpOWzElorsivU3ZWywbYUmKacwGwveUNc5M6DtPVe6ZTJjG-JeKVFh2U"
  },
  stats: {
    title: "Proven Results. Real Trust.",
    items: [
      { value: "40%", label: "Reduction in Driver Turnover", color: "brand-teal" },
      { value: "50%", label: "Faster Incident Resolution", color: "brand-blue" },
      { value: "94%", label: "Driver Sentiment Score", color: "brand-teal" }
    ]
  },
  footer: {
    description: "Building a more transparent, efficient, and human-centric world through intelligent data orchestration.",
    links: [
      {
        title: "Platform",
        items: [
          { label: "Transparency", href: "#" },
          { label: "Governance", href: "#" },
          { label: "Case Studies", href: "#" },
          { label: "API Docs", href: "#" }
        ]
      }
    ],
    socials: [
      { platform: "LinkedIn", href: "#", color: "brand-teal" },
      { platform: "Twitter", href: "#", color: "brand-blue" }
    ],
    copyright: "© 2026 TraceData AI. All Rights Reserved.",
    legalLinks: [
      { label: "Privacy Policy", href: "#" },
      { label: "Terms of Service", href: "#" }
    ]
  },
  testimonials: {
    title: "Some kind words from early customers...",
    description: "We work closely with fleet managers and drivers to ensure TraceData provides the transparency and clarity they need. Here's what they say about the impact on their daily operations.",
    items: [
      {
        quote: "TraceData's transparency is second to none. Decisions that used to feel random are now easy to understand for every driver on my team.",
        author: "Antonio Littel",
        role: "Fleet Operations Lead",
        avatar: "AL"
      },
      {
        quote: "I run a medium-sized logistics firm in Singapore and could never find a reliable way to explain performance scores. Now I can justify every metric in minutes.",
        author: "Cameron Considine",
        role: "Logistics Entrepreneur",
        avatar: "CC"
      },
      {
        quote: "I couldn't believe how fast TraceData moved us from reactive to proactive management. We're optimizing routes more accurately in half the time.",
        author: "Steven Hackett",
        role: "Safety Compliance Officer",
        avatar: "SH"
      },
      {
        quote: "Even though I was excited to start, I was pessimistic that AI wouldn't actually be fair to my drivers. I was wrong—this transparency is all they needed.",
        author: "Lynn Nolan",
        role: "Driver Dispatch Manager",
        avatar: "LN"
      },
      {
        quote: "The complete package is worth it for the real-time telemetry alerts alone. I've learned so much about fleet health watching the system in action.",
        author: "Regina Wisoky",
        role: "Operations Analyst",
        avatar: "RW"
      },
      {
        quote: "I never thought I would enjoy deep data diving but using the XAI insights in TraceData, it's become a great way for me to stay ahead of the curve.",
        author: "Carla Schoen",
        role: "Fleet Director",
        avatar: "CS"
      }
    ]
  }
};
