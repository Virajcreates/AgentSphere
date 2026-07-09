"use client";

import React, { useState } from "react";
import { Card, Typography, Table } from "../../../shared/design-system";
import { ErrorBoundary } from "../../../components/ErrorBoundary";

type TabName = "timeline" | "graph" | "prompt" | "chunks" | "tools" | "metadata" | "logs";

export default function ConversationReplayPage() {
  const [activeTab, setActiveTab] = useState<TabName>("timeline");

  return (
    <ErrorBoundary>
      <div className="space-y-8">
        <div>
          <Typography.H1>Execution Replay Visualizer</Typography.H1>
          <Typography.Paragraph>Deep debugging dashboard. Inspect step timings, retries, and tool calls.</Typography.Paragraph>
        </div>

        {/* Tab Controls */}
        <div className="flex border-b border-slate-200 dark:border-slate-800 gap-2">
          {([
            { id: "timeline", label: "⏱️ Execution Timeline" },
            { id: "graph", label: "🕸️ Execution Graph" },
            { id: "prompt", label: "📝 System Default Prompt" },
            { id: "chunks", label: "📚 Retrieved Chunks" },
            { id: "tools", label: "🛠️ Tool Executions" },
            { id: "metadata", label: "📊 Runtime Metadata" },
            { id: "logs", label: "⚙️ System Logs" },
          ] as const).map((tab) => (
            <button
              key={tab.id}
              onClick={() => setActiveTab(tab.id)}
              className={`px-4 py-2 text-sm font-semibold border-b-2 transition-all ${
                activeTab === tab.id
                  ? "border-blue-600 text-blue-600"
                  : "border-transparent text-slate-400 hover:text-slate-600"
              }`}
            >
              {tab.label}
            </button>
          ))}
        </div>

        {/* Tabbed Inspector Content Views */}
        <div className="min-h-[400px]">
          {activeTab === "timeline" && (
            <Card title="Execution Sequential Steps" subtitle="Total latencies overview timeline">
              <div className="relative border-l border-slate-200 dark:border-slate-800 ml-4 space-y-8 mt-4">
                {[
                  { title: "Created session", desc: "Instantiated execution context", time: "10:32:01 AM", duration: "12ms", status: "success" },
                  { title: "Planning graph compiled", desc: "Constructed Directed Acyclic Graph (DAG) with 3 nodes", time: "10:32:02 AM", duration: "84ms", status: "success" },
                  { title: "Executed step_1", desc: "Tool 'calculator' evaluation completed", time: "10:32:03 AM", duration: "1.4s", status: "success" },
                  { title: "Executed step_2", desc: "RAG lookup successfully completed", time: "10:32:05 AM", duration: "0.8s", status: "success" },
                  { title: "Completed workflow", desc: "Saved final session checkpoint to store", time: "10:32:06 AM", duration: "25ms", status: "success" },
                ].map((step, i) => (
                  <div key={i} className="relative pl-6">
                    <span className="absolute -left-[6px] top-1.5 w-3 h-3 bg-blue-600 rounded-full border-2 border-white dark:border-slate-950" />
                    <div className="flex justify-between items-start">
                      <div>
                        <span className="font-bold text-slate-900 dark:text-white">{step.title}</span>
                        <p className="text-xs text-slate-400 dark:text-slate-500 mt-1">{step.desc}</p>
                      </div>
                      <div className="text-right text-xs font-semibold text-slate-400">
                        <div>{step.time}</div>
                        <div className="text-[10px] text-slate-400 font-mono mt-0.5">+{step.duration}</div>
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {activeTab === "graph" && (
            <Card title="Interactive Execution Graph" subtitle="Visualized DAG dependencies graph">
              {/* React Flow simplified visualization panel */}
              <div className="h-96 border border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-900/30 flex flex-col items-center justify-center p-8">
                <div className="flex items-center gap-12">
                  <div className="px-4 py-3 bg-blue-50 dark:bg-blue-950/20 text-blue-600 dark:text-blue-400 border border-blue-200 dark:border-blue-900 rounded-xl font-bold font-mono text-xs flex flex-col items-center shadow-sm">
                    <span>Node A</span>
                    <span className="text-[10px] text-slate-400 mt-1">tool:calculator</span>
                  </div>
                  <span className="text-2xl text-slate-300">➔</span>
                  <div className="px-4 py-3 bg-purple-50 dark:bg-purple-950/20 text-purple-600 dark:text-purple-400 border border-purple-200 dark:border-purple-900 rounded-xl font-bold font-mono text-xs flex flex-col items-center shadow-sm">
                    <span>Node B</span>
                    <span className="text-[10px] text-slate-400 mt-1">tool:search_web</span>
                  </div>
                  <span className="text-2xl text-slate-300">➔</span>
                  <div className="px-4 py-3 bg-amber-50 dark:bg-amber-950/20 text-amber-600 dark:text-amber-400 border border-amber-200 dark:border-amber-900 rounded-xl font-bold font-mono text-xs flex flex-col items-center shadow-sm">
                    <span>Node C</span>
                    <span className="text-[10px] text-slate-400 mt-1">llm_generate</span>
                  </div>
                </div>
                <div className="text-xs text-slate-400 mt-10 text-center font-medium max-w-sm leading-relaxed">
                  Directed Acyclic Graph (DAG) parsed topologically by TopologicalSorter, executed sequentially inside AgentRuntime.
                </div>
              </div>
            </Card>
          )}

          {activeTab === "prompt" && (
            <Card title="Original Prompt Source" subtitle="Rendered system welcome default template text">
              <pre className="p-6 bg-slate-100 dark:bg-slate-900 rounded-xl font-mono text-xs text-slate-700 dark:text-slate-300 border border-slate-200 dark:border-slate-800 leading-relaxed overflow-auto max-h-80">
                {`System Prompt Context:
You are customer support agent model for the corporate division of AgentSphere platform.
Please run whitelisted calculator tool and retrieve matching manual records files if applicable.

Current Date: 2026-07-09
Tenant ID: tenant_abc
User statement query was: "Calculate standard formulas for RAG limits."`}
              </pre>
            </Card>
          )}

          {activeTab === "chunks" && (
            <Card title="Retrieved document chunks" subtitle="Vector indices matches source attribution pages">
              <Table
                headers={["Chunk ID", "Document File", "Excerpt Segment Content", "Cosine Similarity"]}
                rows={[
                  [
                    <Typography.Code key={0}>chk_dfa3</Typography.Code>,
                    <span key={1} className="font-bold">RAG_Overview.txt</span>,
                    <span key={2}>"AgentSphere delivers enterprise-grade multi-tenant isolated Knowledge Bases."</span>,
                    <span key={3} className="font-mono text-emerald-500 font-bold">0.8450</span>,
                  ],
                  [
                    <Typography.Code key={0}>chk_71be</Typography.Code>,
                    <span key={1} className="font-bold">Platform_Rules.md</span>,
                    <span key={2}>"Execution plans are compiled strictly as Directed Acyclic Graphs (DAG)."</span>,
                    <span key={3} className="font-mono text-emerald-500 font-bold">0.7812</span>,
                  ],
                ]}
              />
            </Card>
          )}

          {activeTab === "tools" && (
            <Card title="Tool invocations" subtitle="Triggered whitelisted APIs call stats">
              <Table
                headers={["Tool Name", "Arguments Payload", "Returns Output", "Timing Duration"]}
                rows={[
                  [
                    <span key={0} className="font-bold font-mono">calculator</span>,
                    <Typography.Code key={1}>{"{expr: '10+20'}"}</Typography.Code>,
                    <Typography.Code key={2}>{"{result: 30.0}"}</Typography.Code>,
                    <span key={3} className="font-semibold text-slate-400">1.4s</span>,
                  ],
                  [
                    <span key={0} className="font-bold font-mono">search_web</span>,
                    <Typography.Code key={1}>{"{query: 'RAG limits'}"}</Typography.Code>,
                    <Typography.Code key={2}>{"{snippet: 'Calculations...'}"}</Typography.Code>,
                    <span key={3} className="font-semibold text-slate-400">0.8s</span>,
                  ],
                ]}
              />
            </Card>
          )}

          {activeTab === "metadata" && (
            <Card title="Runtime execution metadata" subtitle="Tracing parameters contexts">
              <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mt-4">
                {[
                  { label: "Execution ID", val: "exec_abc123" },
                  { label: "Workflow ID", val: "wf1" },
                  { label: "Agent ID", val: "agent_123" },
                  { label: "Request ID", val: "req_bff_987" },
                  { label: "Total Latency", val: "2.35 seconds" },
                  { label: "Active Tenant", val: "tenant_abc" },
                ].map((item, i) => (
                  <div key={i} className="flex justify-between items-center p-3.5 bg-slate-100/50 dark:bg-slate-900/50 rounded-xl border border-slate-200/50 dark:border-slate-800/50">
                    <span className="text-xs text-slate-400 font-semibold">{item.label}</span>
                    <span className="font-bold text-slate-900 dark:text-white font-mono text-xs">{item.val}</span>
                  </div>
                ))}
              </div>
            </Card>
          )}

          {activeTab === "logs" && (
            <Card title="Raw execution logs" subtitle="Structured administrative thread events">
              <pre className="p-6 bg-slate-900 text-slate-100 rounded-xl font-mono text-xs border border-slate-800 max-h-80 overflow-auto space-y-1">
                {`2026-07-09 10:32:01 [info] Initializing execution session exec_abc123
2026-07-09 10:32:01 [info] State changed: Created -> Planning
2026-07-09 10:32:02 [info] DAG compilation success. Zero loops found.
2026-07-09 10:32:02 [info] State changed: Planning -> Executing
2026-07-09 10:32:03 [info] Calling tool 'calculator' with args: {"expr": "10+20"}
2026-07-09 10:32:04 [info] Tool calculator complete duration: 1.4s
2026-07-09 10:32:05 [info] Calling tool 'search_web' with args: {"query": "RAG limits"}
2026-07-09 10:32:06 [info] Tool search_web complete duration: 0.8s
2026-07-09 10:32:06 [info] State changed: Executing -> Completed`}
              </pre>
            </Card>
          )}
        </div>
      </div>
    </ErrorBoundary>
  );
}
export default ConversationReplayPage;
