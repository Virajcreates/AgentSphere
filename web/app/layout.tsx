"use client";

import React, { useState, useEffect } from "react";
import "./globals.css";
import { ThemeProvider, useTheme } from "../components/ThemeProvider";
import { useKeyboardShortcuts } from "../hooks/useKeyboardShortcuts";
import { useNotificationStore } from "../stores/notification-store";
import { useCommandPaletteStore } from "../stores/command-palette-store";
import { Sidebar } from "../components/Sidebar";

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <ThemeProvider>
          <LayoutContent>{children}</LayoutContent>
        </ThemeProvider>
      </body>
    </html>
  );
}

function LayoutContent({ children }: { children: React.ReactNode }) {
  const { toggleTheme, theme } = useTheme();
  const { isOpen, toggle, close } = useCommandPaletteStore();
  const { notifications } = useNotificationStore();

  const [searchQuery, setSearchQuery] = useState<string>("");
  const [searchResults, setSearchResults] = useState<any[]>([]);

  // 1. Universal keyboard shortcuts hooks
  useKeyboardShortcuts({
    onCtrlK: () => toggle(),
    onCtrlShiftP: () => toggle(),
    onEsc: () => close(),
  });

  // 2. Mock command palette search results on typing
  useEffect(() => {
    if (!searchQuery) {
      setSearchResults([]);
      return;
    }

    const q = searchQuery.toLowerCase();
    const items = [
      { title: "Dashboard Panel", subtitle: "Averages latencies and expenditure metrics", route: "/", type: "navigation" },
      { title: "Agents Manager", subtitle: "Configure agent policies and whitelist tools", route: "/agents", type: "navigation" },
      { title: "Knowledge Base", subtitle: "Upload notes and index document slices", route: "/knowledge", type: "navigation" },
      { title: "Prompt Studio", subtitle: "Compile variables and preview renders", route: "/prompts", type: "navigation" },
      { title: "Playground Sandbox", subtitle: "Streaming completions and testing workspace", route: "/playground", type: "navigation" },
      { title: "System Analytics", subtitle: "Plot chart graphs for token metrics", route: "/analytics", type: "navigation" },
      { title: "Security Settings", subtitle: "Manage API keys and whitelisted providers", route: "/settings", type: "navigation" },
    ];

    const filtered = items.filter(
      (item) => item.title.toLowerCase().includes(q) || item.subtitle.toLowerCase().includes(q)
    );
    setSearchResults(filtered);
  }, [searchQuery]);

  const handleNav = (route: string) => {
    close();
    setSearchQuery("");
    // Standard routing via direct hash navigations or router pushes
    window.location.href = route;
  };

  return (
    <div className="flex h-screen overflow-hidden">
      {/* Redesigned standard SaaS-grade Sidebar */}
      <Sidebar />

      {/* Main Administrative dashboard */}
      <div className="flex-1 flex flex-col overflow-hidden bg-slate-50 dark:bg-slate-950">
        {/* Header container */}
        <header className="h-16 border-b border-slate-200 dark:border-slate-800/80 bg-white dark:bg-slate-900 flex items-center justify-between px-8 z-10 shadow-sm">
          <div className="flex items-center gap-3 text-xs font-bold text-slate-400 uppercase tracking-wider">
            <span>AgentSphere</span>
            <span>/</span>
            <span className="text-slate-900 dark:text-white">Active Console</span>
          </div>

          <div className="flex items-center gap-4">
            {/* Quick search button displaying the Ctrl+K label! */}
            <button
              onClick={() => toggle()}
              className="px-4 py-1.5 text-xs text-slate-400 bg-slate-100 dark:bg-slate-800 rounded-lg hover:bg-slate-200 dark:hover:bg-slate-700/50 border border-slate-200 dark:border-slate-700 transition-all flex items-center gap-6"
            >
              <span>Quick search...</span>
              <kbd className="font-sans px-1.5 py-0.5 bg-white dark:bg-slate-900 border rounded text-[10px] shadow-sm">Ctrl+K</kbd>
            </button>

            {/* Quick Dark Toggle */}
            <button onClick={toggleTheme} className="p-2 bg-slate-100 dark:bg-slate-800 hover:bg-slate-200 dark:hover:bg-slate-700 rounded-lg transition-colors">
              {theme === "light" ? "🌙" : "☀️"}
            </button>

            {/* Notifications counter panel */}
            <div className="relative">
              <button className="p-2 bg-slate-100 dark:bg-slate-800 rounded-lg relative">
                🔔
                {notifications.some((n) => !n.read) && (
                  <span className="absolute top-1 right-1 w-2.5 h-2.5 bg-red-500 rounded-full animate-pulse" />
                )}
              </button>
            </div>

            <div className="w-8 h-8 rounded-full bg-slate-200 dark:bg-slate-800 flex items-center justify-center font-bold text-sm">
              JD
            </div>
          </div>
        </header>

        {/* Dynamic page target view panel - NATIVE NESTING OF app/ PATH PAGES */}
        <main className="flex-1 overflow-auto p-8">
          {children}
        </main>
      </div>

      {/* Centralized Command Palette Popup (cmdk style) */}
      {isOpen && (
        <div className="fixed inset-0 z-50 flex items-start justify-center pt-24 bg-black/50 backdrop-blur-sm">
          <div className="w-full max-w-xl bg-white dark:bg-slate-900 border border-slate-200 dark:border-slate-800 rounded-xl shadow-2xl overflow-hidden">
            <div className="flex items-center gap-3 px-4 border-b border-slate-200 dark:border-slate-800">
              <span className="text-slate-400">🔍</span>
              <input
                type="text"
                placeholder="Type a command or search (Agents, Docs, Workflows)..."
                value={searchQuery}
                onChange={(e) => setSearchQuery(e.target.value)}
                className="w-full py-4 text-sm bg-transparent border-none outline-none focus:ring-0 text-slate-900 dark:text-white"
                autoFocus
              />
              <button onClick={() => close()} className="text-xs text-slate-400 hover:text-slate-600 px-2 py-1 bg-slate-100 dark:bg-slate-800 rounded">
                Esc
              </button>
            </div>

            {searchQuery === "" ? (
              <div className="p-4 text-xs text-slate-400">
                <p className="font-semibold mb-2">QUICK NAVIGATION</p>
                <div className="space-y-1">
                  {[
                    { label: "🤖 Jump to Agents Manager", action: () => handleNav("/agents") },
                    { label: "💬 Jump to Conversations", action: () => handleNav("/conversations") },
                    { label: "📚 Jump to Knowledge Base", action: () => handleNav("/knowledge") },
                    { label: "📝 Open Prompt Studio", action: () => handleNav("/prompts") },
                    { label: "🧪 Open Playground", action: () => handleNav("/playground") },
                  ].map((cmd, i) => (
                    <button
                      key={i}
                      onClick={cmd.action}
                      className="w-full text-left px-3 py-2 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 text-slate-700 dark:text-slate-300 font-medium transition-colors border border-transparent"
                    >
                      {cmd.label}
                    </button>
                  ))}
                </div>
              </div>
            ) : (
              <div className="max-h-80 overflow-y-auto p-2">
                {searchResults.length === 0 ? (
                  <div className="p-8 text-center text-sm text-slate-400">
                    No results found matching "{searchQuery}"
                  </div>
                ) : (
                  searchResults.map((res, i) => (
                    <button
                      key={i}
                      onClick={() => handleNav(res.route)}
                      className="w-full text-left p-3 rounded-lg hover:bg-slate-50 dark:hover:bg-slate-800/50 flex flex-col transition-colors border border-transparent hover:border-slate-100 dark:hover:border-slate-800"
                    >
                      <span className="text-sm font-bold text-slate-900 dark:text-white flex items-center gap-2">
                        {res.title}
                      </span>
                      <span className="text-xs text-slate-400 dark:text-slate-500 mt-0.5">{res.subtitle}</span>
                    </button>
                  ))
                )}
              </div>
            )}
          </div>
        </div>
      )}
    </div>
  );
}
