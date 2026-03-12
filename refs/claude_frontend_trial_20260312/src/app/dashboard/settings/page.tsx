"use client";

import { Save } from "lucide-react";

export default function SettingsPage() {
  return (
    <div className="flex-1 overflow-y-auto p-8 space-y-6 bg-muted/20" data-purpose="settings-page">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-bold text-foreground">System Settings</h2>
          <p className="text-muted-foreground text-sm">Configure LangGraph thresholds and global dashboard settings.</p>
        </div>
        <button className="bg-brand-blue text-white px-4 py-2 rounded-lg text-sm font-semibold hover:bg-brand-blue/90 transition-all shadow-sm flex items-center gap-2">
          <Save className="w-4 h-4" />
          Save Changes
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
            <h3 className="font-bold text-foreground mb-4">Agent Thresholds</h3>
            
            <div className="space-y-4">
              <div className="space-y-2">
                <label className="text-sm font-semibold text-muted-foreground">Fatigue Warning Threshold (%)</label>
                <input type="range" min="0" max="100" defaultValue="75" className="w-full accent-brand-blue" />
                <div className="flex justify-between text-xs text-muted-foreground">
                  <span>0%</span>
                  <span>75%</span>
                  <span>100%</span>
                </div>
              </div>

              <div className="space-y-2 pt-4">
                <label className="text-sm font-semibold text-muted-foreground">Anomaly Detection Sensitivity</label>
                <select className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue">
                  <option>Low (Fewer alerts, higher confidence)</option>
                  <option selected>Medium (Balanced)</option>
                  <option>High (More alerts, lower confidence)</option>
                </select>
              </div>
            </div>
          </div>

          <div className="bg-card rounded-xl border border-border p-6 shadow-sm">
            <h3 className="font-bold text-foreground mb-4">Notification Preferences</h3>
            
            <div className="space-y-3">
              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-border text-brand-blue focus:ring-brand-blue/20" />
                <span className="text-sm text-foreground">Email alerts for Critical System Issues</span>
              </label>
              <label className="flex items-center gap-3">
                <input type="checkbox" defaultChecked className="w-4 h-4 rounded border-border text-brand-blue focus:ring-brand-blue/20" />
                <span className="text-sm text-foreground">Push notifications for Driver Appeals</span>
              </label>
              <label className="flex items-center gap-3">
                <input type="checkbox" className="w-4 h-4 rounded border-border text-brand-blue focus:ring-brand-blue/20" />
                <span className="text-sm text-foreground">Daily Digest Report via Email</span>
              </label>
            </div>
          </div>
        </div>

        <div className="bg-card rounded-xl border border-border p-6 shadow-sm h-fit">
          <h3 className="font-bold text-foreground mb-4">API & Integrations</h3>
          
          <div className="space-y-4">
            <div className="space-y-2">
              <label className="text-sm font-semibold text-muted-foreground">Backend API Endpoint</label>
              <input 
                type="text" 
                defaultValue="https://api.tracedata.com/v1" 
                className="w-full bg-background border border-border rounded-lg px-3 py-2 text-sm text-foreground focus:outline-none focus:ring-2 focus:ring-brand-blue/20 focus:border-brand-blue font-mono" 
              />
            </div>
            
            <div className="pt-4 space-y-2">
              <span className="text-sm font-semibold text-muted-foreground">API Keys</span>
              <div className="bg-muted/50 border border-border rounded-lg p-3 flex justify-between items-center">
                <div className="flex flex-col">
                  <span className="text-xs font-bold text-foreground">Production Key</span>
                  <span className="text-[10px] text-muted-foreground font-mono">tk_live_*******************8a9b</span>
                </div>
                <button className="text-xs font-bold text-brand-blue hover:underline">Reveal</button>
              </div>
              <button className="text-xs font-bold text-foreground border border-border px-3 py-1.5 rounded-lg w-full mt-2 hover:bg-muted transition-colors">Generate New Key</button>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
}
