"use client";

import React, { useEffect, useState } from "react";
import { Card, Typography, Table, EmptyState, Sparkline, MiniBarChart } from "../shared/design-system";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { fetchAnalyticsData } from "../lib/api/analytics";

export default function DashboardPage() {
  const [stats, setStats] = useState<any>({
    active_conversations: 12,
    active_agents: 5,
    knowledge_bases: 4,
    tokens: 425000,
    cost: 1.2845,
    latency: 0.38,
    circuit_breakers_status: "Healthy",
  });
  const [recentActivity, setRecentActivity] = useState<any[]>([]);

  useEffect(() => {
    // Polling simulation for active metrics
    const fetchStats = async () => {
      try {
        const raw = await fetchAnalyticsData();
        if (raw && raw.summary) {
          setStats({
            active_conversations: raw.summary.total_threads_count,
            active_agents: 5,
            knowledge_bases: 4,
            tokens: raw.summary.total_tokens_processed,
            cost: raw.summary.total_expenses_usd,
            latency: raw.summary.average_processing_latency_sec,
            circuit_breakers_status: "Healthy",
          });
        }
      } catch (err) {
        console.warn("Dashboard metrics load failed:", err);
      }
    };

    fetchStats();
    const interval = setInterval(fetchStats, 5000);

    setRecentActivity([
      { time: "10:32 AM", agent: "Support Agent", event: "Completed calculations workflow", status: "Success" },
      { time: "10:14 AM", agent: "Marketing Agent", event: "Triggered dynamic email copying", status: "Success" },
      { time: "09:45 AM", agent: "Support Agent", event: "RAG index lookups on Database_Manual", status: "Success" },
    ]);

    return () => clearInterval(interval);
  }, []);

  return (
    <ErrorBoundary>
      <div className="space-y-10 animate-in fade-in duration-300">
        
        {/* A. PREMIUM HERO WELCOME PANEL */}
        <div className="p-8 bg-slate-900 border border-slate-800 rounded-2xl relative overflow-hidden flex flex-col justify-between min-h-[160px] shadow-sm">
          <div className="absolute right-0 top-0 w-80 h-80 bg-blue-600/10 rounded-full blur-3xl pointer-events-none select-none" />
          <div className="flex items-start justify-between z-10">
            <div>
              <Typography.H1 className="text-white tracking-tight">Good morning, Operator</Typography.H1>
              <Typography.Paragraph className="text-slate-400 mt-2 font-medium">
                Welcome back. The AgentSphere platform is running smoothly with zero active anomalies.
              </Typography.Paragraph>
            </div>
            <div className="flex items-center gap-2 px-3.5 py-1.5 bg-emerald-500/10 border border-emerald-500/20 rounded-full text-emerald-400 text-xs font-bold animate-pulse select-none">
              <span className="w-1.5 h-1.5 rounded-full bg-emerald-500" />
              SYSTEM LIFE STATUS: HEALTHY
            </div>
          </div>
          <div className="flex items-center gap-6 mt-6 text-xs font-semibold text-slate-400 z-10 border-t border-slate-800 pt-4">
            <div>Active Agents: <span className="text-white font-bold">{stats.active_agents}</span></div>
            <span className="text-slate-700">•</span>
            <div>Knowledge Bases: <span className="text-white font-bold">{stats.knowledge_bases}</span></div>
            <span className="text-slate-700">•</span>
            <div>Gateway Cooldown: <span className="text-emerald-500 font-bold">Closed (Healthy)</span></div>
          </div>
        </div>

        {/* B. QUICK ACTIONS PANE */}
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-400 dark:text-slate-500 mb-3.5 block">⚡ Quick Administrative Actions</span>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {[
              { title: "🤖 Deploy Agent", desc: "Build definitions & whitelists", link: "/agents" },
              { title: "📝 Write Prompts", desc: "Monaco variable compilation", link: "/prompts" },
              { title: "📚 Index document", desc: "Upload and split files", link: "/knowledge" },
              { title: "🧪 Open Sandbox", desc: "Completions playground", link: "/playground" },
            ].map((act, i) => (
              <button
                key={i}
                onClick={() => { window.location.href = act.link; }}
                className="p-4 text-left bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800/80 rounded-xl hover:border-blue-500 dark:hover:border-blue-600 hover:shadow-md hover:scale-[1.02] active:scale-95 transition-all duration-150 flex flex-col justify-between"
              >
                <span className="font-extrabold text-sm text-slate-900 dark:text-white block">{act.title}</span>
                <span className="text-xs text-slate-400 dark:text-slate-500 mt-1 block font-medium">{act.desc}</span>
              </button>
            ))}
          </div>
        </div>

        {/* C. KEY PERFORMANCE INDICATORS GRID (WITH SPARKLINES) */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
          <Card title="Active Threads" subtitle="Conversations Volume">
            <div className="flex items-end justify-between mt-2">
              <div className="text-3xl font-black text-blue-600 dark:text-blue-400 tracking-tight">
                {stats.active_conversations} <span className="text-xs text-slate-400 font-semibold font-sans">active</span>
              </div>
              <Sparkline data={[5, 8, 4, 12, 10, 15, stats.active_conversations]} color="#3b82f6" />
            </div>
          </Card>
          <Card title="Total Tokens" subtitle="Processed Volumes count">
            <div className="flex items-end justify-between mt-2">
              <div className="text-3xl font-black text-purple-600 dark:text-purple-400 tracking-tight">
                {(stats.tokens / 1000).toFixed(1)}k <span className="text-xs text-slate-400 font-semibold font-sans">total</span>
              </div>
              <Sparkline data={[30000, 50000, 92000, 84000, 105000, stats.tokens]} color="#a855f7" />
            </div>
          </Card>
          <Card title="Aggregated Costs" subtitle="Expenditures USD">
            <div className="flex items-end justify-between mt-2">
              <div className="text-3xl font-black text-rose-600 dark:text-rose-400 tracking-tight">
                ${stats.cost.toFixed(4)} <span className="text-xs text-slate-400 font-semibold font-sans">USD</span>
              </div>
              <Sparkline data={[0.15, 0.45, 0.39, 0.65, stats.cost]} color="#f43f5e" />
            </div>
          </Card>
          <Card title="Average Latency" subtitle="Processing Durations">
            <div className="flex items-end justify-between mt-2">
              <div className="text-3xl font-black text-amber-600 dark:text-amber-400 tracking-tight">
                {stats.latency.toFixed(2)}s <span className="text-xs text-slate-400 font-semibold font-sans">per call</span>
              </div>
              <Sparkline data={[0.42, 0.38, 0.35, 0.45, 0.39, stats.latency]} color="#f59e0b" />
            </div>
          </Card>
        </div>

        {/* D. WORKFLOW REPLAYS & HEALTH STATUS */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          <div className="lg:col-span-2">
            <Card
              title="Recent Execution Streams"
              subtitle="Live state events trace logs"
              action={
                <button
                  onClick={() => { window.location.href = "/conversations"; }}
                  className="px-3 py-1 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 text-xs font-semibold rounded"
                >
                  View All
                </button>
              }
            >
              <Table
                headers={["Time", "Orchestrator Agent", "Trigger Event", "Result State"]}
                rows={recentActivity.map((r, i) => [
                  <span key={0} className="font-semibold text-slate-400">{r.time}</span>,
                  <span key={1} className="font-bold text-slate-900 dark:text-white">{r.agent}</span>,
                  <span key={2} className="text-slate-600 dark:text-slate-300 font-medium">{r.event}</span>,
                  <span key={3} className="px-2.5 py-1 rounded-full text-xs font-bold bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 dark:text-emerald-400 border border-emerald-100 dark:border-emerald-800">
                    {r.status}
                  </span>,
                ])}
              />
            </Card>
          </div>

          <div>
            <Card title="Provider Benchmarks" subtitle="Weekly volume allocations">
              <div className="flex justify-center py-4">
                <MiniBarChart data={[45, 68, 92, 84, 105, 25, 18]} color="#3b82f6" />
              </div>
              <div className="space-y-3 mt-4">
                {[
                  { name: "OpenAI", health: "100%", latency: "0.45s", color: "text-emerald-500" },
                  { name: "Gemini", health: "100%", latency: "0.32s", color: "text-emerald-500" },
                ].map((prov, i) => (
                  <div key={i} className="flex items-center justify-between p-3 bg-slate-100/50 dark:bg-slate-900/50 rounded-xl border border-slate-200/50 dark:border-slate-800/50">
                    <span className="font-bold text-slate-900 dark:text-white text-xs">{prov.name}</span>
                    <div className="flex items-center gap-3 text-xs font-semibold">
                      <span className="text-slate-400 font-medium">Lat: {prov.latency}</span>
                      <span className={`${prov.color} flex items-center gap-1.5`}>
                        <span className="w-1.5 h-1.5 rounded-full bg-current animate-pulse" />
                        {prov.health}
                      </span>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
