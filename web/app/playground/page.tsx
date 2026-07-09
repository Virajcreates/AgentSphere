"use client";

import React, { useState } from "react";
import { Card, Typography, FormField } from "../shared/design-system";
import { ErrorBoundary } from "../components/ErrorBoundary";

export default function PlaygroundPage() {
  const [provider, setProvider] = useState("openai");
  const [model, setModel] = useState("gpt-4o-mini");
  const [prompt, setPrompt] = useState("Who is AgentSphere?");
  const [streamText, setStreamText] = useState("");
  const [isStreaming, setIsStreaming] = useState(false);
  const [stats, setStats] = useState<any>(null);

  const handleStreamTest = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!prompt.trim()) return;

    setIsStreaming(true);
    setStreamText("");
    setStats(null);

    // Dynamic mock streaming generator yielding incremental chunks
    const responseText = "AgentSphere is an enterprise-grade multi-tenant conversational AI platform. It implements stateful pipelines, pgvector search, and resilient gateways.";
    const words = responseText.split(" ");
    let compiled = "";

    for (let i = 0; i < words.length; i++) {
      await new Promise((resolve) => setTimeout(resolve, 80));
      compiled += words[i] + " ";
      setStreamText(compiled);
    }

    setStats({
      provider,
      model,
      latency_sec: 0.35,
      tokens_count: 24,
      cost_usd: 0.00015,
      trace_id: "trace_play_9f8d",
    });
    setIsStreaming(false);
  };

  return (
    <ErrorBoundary>
      <div className="space-y-8">
        <div>
          <Typography.H1>Playground Arena</Typography.H1>
          <Typography.Paragraph>Sandbox testing suite. Complete completions streaming and inspect pricing telemetry.</Typography.Paragraph>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Controls Widgets Panel */}
          <div className="space-y-6">
            <Card title="Configurations" subtitle="Endpoint parameters parameters">
              <form onSubmit={handleStreamTest} className="space-y-4">
                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold text-slate-500">Provider Selector</label>
                  <select
                    value={provider}
                    onChange={(e) => setProvider(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                  >
                    <option value="openai">OpenAI</option>
                    <option value="gemini">Gemini</option>
                    <option value="anthropic">Anthropic</option>
                    <option value="groq">Groq</option>
                  </select>
                </div>

                <div className="space-y-1.5">
                  <label className="block text-xs font-semibold text-slate-500">Model ID</label>
                  <select
                    value={model}
                    onChange={(e) => setModel(e.target.value)}
                    className="w-full px-4 py-2.5 bg-slate-50 dark:bg-slate-800 border border-slate-200 dark:border-slate-700 rounded-lg text-sm"
                  >
                    <option value="gpt-4o-mini">gpt-4o-mini</option>
                    <option value="gpt-4o">gpt-4o</option>
                    <option value="gemini-1.5-flash">gemini-1.5-flash</option>
                    <option value="claude-3-5-sonnet">claude-3-5-sonnet</option>
                  </select>
                </div>

                <FormField label="Prompt input Statement" id="prompt" placeholder="Who is AgentSphere?" value={prompt} onChange={setPrompt} required />

                <button type="submit" disabled={isStreaming} className="w-full py-3 bg-blue-600 hover:bg-blue-700 disabled:bg-blue-300 text-white font-bold text-sm rounded-xl shadow-md transition-all">
                  {isStreaming ? "Streaming response..." : "⚡ Run stream complete"}
                </button>
              </form>
            </Card>

            {stats && (
              <Card title="Completions Telemetry" subtitle="Latency & pricing metrics log">
                <div className="space-y-3 mt-2 text-xs font-semibold text-slate-500 dark:text-slate-400">
                  <div className="flex justify-between p-2.5 bg-slate-100/50 dark:bg-slate-900/50 rounded-lg">
                    <span>Provider</span> <span className="font-bold text-slate-900 dark:text-white font-mono">{stats.provider}</span>
                  </div>
                  <div className="flex justify-between p-2.5 bg-slate-100/50 dark:bg-slate-900/50 rounded-lg">
                    <span>Model ID</span> <span className="font-bold text-slate-900 dark:text-white font-mono">{stats.model}</span>
                  </div>
                  <div className="flex justify-between p-2.5 bg-slate-100/50 dark:bg-slate-900/50 rounded-lg">
                    <span>Latency</span> <span className="font-bold text-amber-500 font-mono">{stats.latency_sec}s</span>
                  </div>
                  <div className="flex justify-between p-2.5 bg-slate-100/50 dark:bg-slate-900/50 rounded-lg">
                    <span>Tokens</span> <span className="font-bold text-purple-500 font-mono">{stats.tokens_count}</span>
                  </div>
                  <div className="flex justify-between p-2.5 bg-slate-100/50 dark:bg-slate-900/50 rounded-lg">
                    <span>Cost</span> <span className="font-bold text-rose-500 font-mono">${stats.cost_usd.toFixed(5)}</span>
                  </div>
                  <div className="flex justify-between p-2.5 bg-slate-100/50 dark:bg-slate-900/50 rounded-lg">
                    <span>Trace ID</span> <span className="font-bold text-blue-500 font-mono">{stats.trace_id}</span>
                  </div>
                </div>
              </Card>
            )}
          </div>

          {/* Playground Canvas Viewer */}
          <div className="lg:col-span-2">
            <Card title="Streaming Completions Output" subtitle="Interactive playground workspace canvas">
              <div className="p-6 h-96 bg-slate-900 text-slate-100 font-mono text-xs rounded-2xl border border-slate-800 leading-relaxed overflow-auto">
                {streamText ? (
                  <p className="whitespace-pre-wrap">{streamText}</p>
                ) : (
                  <span className="text-slate-500 italic font-sans text-sm block h-full flex flex-col items-center justify-center p-12">
                    Enter a prompt and execute to view streaming output here...
                  </span>
                )}
              </div>
            </Card>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
export default PlaygroundPage;
