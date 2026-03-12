"use client";

import { useState, useEffect, useRef } from "react";
import { dashboardConfig } from "@/config/dashboard";
import type { OrchestrationEvent } from "@/config/dashboard";

const getSeverityColor = (severity: OrchestrationEvent["severity"]) => {
  switch (severity) {
    case "info": return "bg-brand-blue";
    case "warning": return "bg-amber-500";
    case "error": return "bg-red-500";
    default: return "bg-muted";
  }
};

// Pool of live events that rotate in every 6s
const liveEventPool: Omit<OrchestrationEvent, "id" | "timestamp">[] = [
  { agentId: "AG-03", agentName: "Orchestrator", message: "Routed telemetry batch for TRP-10042 to Behavior Agent.", severity: "info" },
  { agentId: "AG-04", agentName: "Behavior", message: "Partial scoring in progress — TR-8291 en route RT-001-A.", severity: "info" },
  { agentId: "AG-06", agentName: "Context", message: "Weather enrichment applied — moderate rain expected Jurong sector.", severity: "warning" },
  { agentId: "AG-01", agentName: "Ingestion Quality", message: "Validated and routed 48 telemetry segments from VEH-3345.", severity: "info" },
  { agentId: "AG-07", agentName: "Safety", message: "Monitoring VEH-4501 — thermal stabilising post charge halt.", severity: "warning" },
  { agentId: "AG-09", agentName: "Coaching", message: "Feedback plan dispatched to TR-3310 mobile app.", severity: "info" },
  { agentId: "AG-08", agentName: "Advocacy", message: "Escalated app-1 (TR-8291) to senior fleet manager for review.", severity: "info" },
  { agentId: "AG-02", agentName: "PII Scrubber", message: "Redacted 3 personally identifiable fields from appeal app-2.", severity: "info" },
];

let poolIndex = 0;
let eventCounter = 100;

export function LiveOrchestration() {
  const [feed, setFeed] = useState<OrchestrationEvent[]>(dashboardConfig.orchestrationFeed);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    const interval = setInterval(() => {
      const template = liveEventPool[poolIndex % liveEventPool.length];
      poolIndex++;
      eventCounter++;

      const newEvent: OrchestrationEvent = {
        ...template,
        id: `evt-live-${eventCounter}`,
        timestamp: "Just Now",
      };

      setFeed((prev) => {
        // Age timestamps of prior events
        const aged = prev.map((e, i) => {
          if (i === 0 && e.timestamp === "Just Now") return { ...e, timestamp: "6s ago" };
          if (e.timestamp === "6s ago") return { ...e, timestamp: "12s ago" };
          if (e.timestamp === "12s ago") return { ...e, timestamp: "30s ago" };
          return e;
        });
        // Prepend new event and cap at 10 items
        return [newEvent, ...aged].slice(0, 10);
      });
    }, 6000);

    return () => clearInterval(interval);
  }, []);

  // Auto-scroll to top when new events arrive (newest at top)
  useEffect(() => {
    if (scrollRef.current) {
      scrollRef.current.scrollTop = 0;
    }
  }, [feed.length]);

  return (
    <div className="bg-card rounded-xl border border-border flex flex-col h-[320px] shadow-sm" data-purpose="live-orchestration">
      <div className="p-4 border-b border-border flex items-center justify-between sticky top-0 bg-card rounded-t-xl z-10">
        <h3 className="text-sm font-bold text-foreground">Live Orchestration</h3>
        <div className="flex items-center gap-2">
          <span className="text-[10px] text-muted-foreground font-mono">{feed.length} events</span>
          <div className="flex gap-1 animate-pulse">
            <span className="w-1 h-1 bg-brand-teal rounded-full shadow-[0_0_8px_rgba(13,148,136,0.8)]"></span>
            <span className="w-1 h-1 bg-brand-teal rounded-full shadow-[0_0_8px_rgba(13,148,136,0.8)]"></span>
          </div>
        </div>
      </div>

      <div ref={scrollRef} className="flex-1 overflow-y-auto p-4 space-y-4 custom-scrollbar">
        {feed.map((event) => (
          <div key={event.id} className="flex gap-3 items-start hover:bg-muted/30 p-2 -mx-2 rounded-lg transition-colors cursor-default">
            <div className={`mt-1.5 w-2 h-2 rounded-full flex-shrink-0 ${getSeverityColor(event.severity)}`}></div>
            <div className="flex-1 min-w-0">
              <p className="text-xs text-foreground leading-relaxed">
                <span className="font-bold mr-1">{event.agentId}</span>
                {event.message}
              </p>
              <div className="flex items-center gap-2 mt-1">
                <span className="text-[10px] text-muted-foreground uppercase font-medium">
                  {event.timestamp}
                </span>
                <span className={`text-[9px] px-1.5 py-0.5 rounded-sm font-semibold uppercase ${
                  event.severity === "info" ? "bg-brand-blue/10 text-brand-blue" :
                  event.severity === "warning" ? "bg-amber-100 dark:bg-amber-900/30 text-amber-600 dark:text-amber-500" :
                  "bg-red-100 dark:bg-red-900/30 text-red-600 dark:text-red-400"
                }`}>
                  {event.agentName}
                </span>
              </div>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}
