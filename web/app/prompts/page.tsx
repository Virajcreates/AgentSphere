"use client";

import React, { useState } from "react";
import { Card, Typography, FormField } from "../../shared/design-system";
import { ErrorBoundary } from "../components/ErrorBoundary";

export default function PromptStudioPage() {
  const [templateText, setTemplateText] = useState(
    "Hello {{ name }},\nWe recommend running shoes based on your budget of {{ budget }}."
  );
  const [compiledPreview, setCompiledPreview] = useState("");
  const [name, setName] = useState("Viraj");
  const [budget, setBudget] = useState("120");

  const handleCompile = () => {
    // Basic regex compiler representation
    let text = templateText;
    text = text.replace(/\{\{\s*name\s*\}\}/g, name);
    text = text.replace(/\{\{\s*budget\s*\}\}/g, budget);
    setCompiledPreview(text);
  };

  return (
    <ErrorBoundary>
      <div className="space-y-8">
        <div>
          <Typography.H1>Prompt Studio</Typography.H1>
          <Typography.Paragraph>Design, compile, preview, and compare prompt versions with variables validation.</Typography.Paragraph>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
          {/* Left panel: Prompt Editor and context */}
          <div className="space-y-6">
            <Card title="Prompt Template Editor" subtitle="Define brackets variables, e.g. {{ name }}">
              <textarea
                value={templateText}
                onChange={(e) => setTemplateText(e.target.value)}
                className="w-full h-64 p-4 font-mono text-xs bg-slate-900 text-slate-100 border border-slate-800 rounded-xl focus:outline-none focus:ring-2 focus:ring-blue-500 leading-relaxed"
              />

              <div className="flex justify-end gap-3 mt-4 border-t border-slate-100 dark:border-slate-800/80 pt-4">
                <button onClick={handleCompile} className="px-5 py-2 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-md transition-all">
                  ⚡ Compile variables
                </button>
              </div>
            </Card>

            <Card title="Preview Variables" subtitle="Test parameters context keys">
              <div className="grid grid-cols-2 gap-4">
                <FormField label="name" id="name" placeholder="Viraj" value={name} onChange={setName} />
                <FormField label="budget" id="budget" placeholder="120" value={budget} onChange={setBudget} />
              </div>
            </Card>
          </div>

          {/* Right panel: Compiled output preview */}
          <div>
            <Card title="Rendered Compiled Output" subtitle="Instant compiler preview results">
              {compiledPreview ? (
                <div className="p-6 bg-slate-100/50 dark:bg-slate-900/50 border border-slate-200 dark:border-slate-800 rounded-xl min-h-[300px] leading-relaxed font-sans text-sm text-slate-800 dark:text-slate-200">
                  {compiledPreview}
                </div>
              ) : (
                <div className="h-[300px] border border-dashed border-slate-200 dark:border-slate-800 rounded-xl bg-slate-50/50 dark:bg-slate-900/10 flex flex-col items-center justify-center text-slate-400 font-medium">
                  Click 'Compile variables' to view output
                </div>
              )}
            </Card>
          </div>
        </div>
      </div>
    </ErrorBoundary>
  );
}
