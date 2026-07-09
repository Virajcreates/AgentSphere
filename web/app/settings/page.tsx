"use client";

import React, { useState } from "react";
import { Card, Typography, FormField } from "../shared/design-system";
import { ErrorBoundary } from "../components/ErrorBoundary";

type SettingsModule = "general" | "providers" | "security" | "runtime" | "knowledge" | "api_keys" | "appearance" | "tenants";

export default function SettingsPage() {
  const [activeModule, setActiveModule] = useState<SettingsModule>("general");

  return (
    <ErrorBoundary>
      <div className="space-y-8">
        <div>
          <Typography.H1>System Settings</Typography.H1>
          <Typography.Paragraph>Manage system whitelists, providers configurations, limits, security, and tenant parameters.</Typography.Paragraph>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-4 gap-8">
          {/* Left panel: Modules side list */}
          <div className="space-y-1.5 lg:col-span-1">
            {([
              { id: "general", label: "⚙️ General Options" },
              { id: "providers", label: "☁️ Whitelist Providers" },
              { id: "security", label: "🔒 Security & Keys" },
              { id: "runtime", label: "⏱️ Runtime Limits" },
              { id: "knowledge", label: "📚 Knowledge Settings" },
              { id: "api_keys", label: "🔑 Dynamic API Keys" },
              { id: "appearance", label: "🎨 Theme Appearance" },
              { id: "tenants", label: "🏢 Multi-Tenancy" },
            ] as const).map((mod) => (
              <button
                key={mod.id}
                onClick={() => setActiveModule(mod.id)}
                className={`w-full text-left px-4 py-2.5 rounded-lg text-xs font-bold transition-all border ${
                  activeModule === mod.id
                    ? "bg-blue-600 text-white border-blue-500 shadow-md shadow-blue-500/5"
                    : "bg-slate-100/50 dark:bg-slate-900/30 border-slate-200 dark:border-slate-800 text-slate-400 hover:text-slate-600 dark:hover:text-slate-200"
                }`}
              >
                {mod.label}
              </button>
            ))}
          </div>

          {/* Right panel: Active modules values */}
          <div className="lg:col-span-3">
            {activeModule === "general" && (
              <Card title="General Configurations" subtitle="Platform metadata configs">
                <div className="space-y-4 max-w-md">
                  <FormField label="System Project Name" id="name" placeholder="AgentSphere" value="AgentSphere" onChange={() => {}} />
                  <FormField label="Environment Mode" id="env" placeholder="development" value="development" onChange={() => {}} />
                </div>
              </Card>
            )}

            {activeModule === "providers" && (
              <Card title="Cloud Whitelisted Providers" subtitle="Active provider endpoint whitelists">
                <div className="space-y-4 text-sm font-semibold text-slate-500 dark:text-slate-400">
                  {["OpenAI", "Gemini", "Anthropic", "Groq", "Ollama", "NVIDIA"].map((p, i) => (
                    <div key={i} className="flex justify-between items-center p-3 bg-slate-100/50 dark:bg-slate-900/50 border border-slate-200/50 dark:border-slate-800/50 rounded-xl">
                      <span className="text-slate-900 dark:text-white font-bold">{p}</span>
                      <span className="px-2.5 py-0.5 rounded-full bg-emerald-50 dark:bg-emerald-950/20 text-emerald-600 border border-emerald-100 dark:border-emerald-900 font-bold text-[10px]">
                        Active enabled
                      </span>
                    </div>
                  ))}
                </div>
              </Card>
            )}

            {activeModule === "security" && (
              <Card title="Security Parameters" subtitle="Data security whitelists keys">
                <div className="space-y-4 max-w-md">
                  <FormField label="Allowed CORS Origins" id="cors" placeholder="*" value="*" onChange={() => {}} />
                  <FormField label="Encryption Salt algorithm" id="algo" placeholder="Argon2id" value="Argon2id" onChange={() => {}} />
                </div>
              </Card>
            )}

            {activeModule === "runtime" && (
              <Card title="Runtime Limits Guardrails" subtitle="Safety policies parameters caps">
                <div className="space-y-4 max-w-md">
                  <FormField label="Max Execution Depth (loops)" id="depth" placeholder="10" value="10" onChange={() => {}} />
                  <FormField label="Max Tool Calls per workflow" id="tools" placeholder="15" value="15" onChange={() => {}} />
                  <FormField label="Max Step Retries allowed" id="retries" placeholder="5" value="5" onChange={() => {}} />
                </div>
              </Card>
            )}

            {activeModule === "knowledge" && (
              <Card title="Knowledge Slicing Guidelines" subtitle="RAG parsing constraints">
                <div className="space-y-4 max-w-md">
                  <FormField label="Default Chunker Size (characters)" id="size" placeholder="500" value="500" onChange={() => {}} />
                  <FormField label="Default Chunker Overlap" id="overlap" placeholder="50" value="50" onChange={() => {}} />
                </div>
              </Card>
            )}

            {activeModule === "api_keys" && (
              <Card title="Dynamic API Keys" subtitle="External system credentials whitelists">
                <div className="space-y-4 max-w-md">
                  <FormField label="Active live API prefix" id="prefix" placeholder="as_live_..." value="as_live_******" onChange={() => {}} />
                </div>
              </Card>
            )}

            {activeModule === "appearance" && (
              <Card title="ThemeProvider Styling" subtitle="Custom design theme tokens">
                <div className="space-y-4 text-xs font-semibold text-slate-500">
                  <div className="p-3.5 bg-slate-100/50 dark:bg-slate-900/50 border rounded-xl flex justify-between">
                    <span>Base Spacing Scale</span> <span className="font-mono text-slate-900 dark:text-white">Tailwind 4px / rem</span>
                  </div>
                  <div className="p-3.5 bg-slate-100/50 dark:bg-slate-900/50 border rounded-xl flex justify-between">
                    <span>Default Radius</span> <span className="font-mono text-slate-900 dark:text-white">12px (rounded-xl)</span>
                  </div>
                </div>
              </Card>
            )}

            {activeModule === "tenants" && (
              <Card title="Active isolated Tenant Spaces" subtitle="Database tenant-partition settings">
                <div className="p-3.5 bg-slate-100/50 dark:bg-slate-900/50 border rounded-xl flex justify-between text-xs font-semibold text-slate-500">
                  <span>Current Space ID</span> <span className="font-mono text-slate-900 dark:text-white">tenant_abc</span>
                </div>
              </Card>
            )}
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
