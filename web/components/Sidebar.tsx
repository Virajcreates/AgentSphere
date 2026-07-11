"use client";

import React, { useState } from "react";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTheme } from "./ThemeProvider";
import useCommandPaletteStore from "../stores/command-palette-store";

export function Sidebar() {
  const pathname = usePathname();
  const { toggleTheme, theme } = useTheme();
  const { open } = useCommandPaletteStore();

  const [workspace, setWorkspace] = useState("Viraj's Space");
  const [isWfGroupCollapsed, setIsWfCollapsed] = useState(false);

  // Helper function to check if active route matched pathname
  const isActive = (route: string) => {
    if (route === "/" && pathname === "/") return true;
    return route !== "/" && pathname.startsWith(route);
  };

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col justify-between p-4 text-slate-400 select-none">
      <div className="space-y-6">
        {/* A. Workspace Switcher Header */}
        <div className="flex items-center justify-between p-2 hover:bg-slate-800/40 rounded-xl cursor-pointer transition-colors border border-transparent hover:border-slate-800/50">
          <div className="flex items-center gap-3">
            <div className="w-8 h-8 rounded-lg bg-blue-600 flex items-center justify-center text-white font-extrabold text-sm shadow-md shadow-blue-500/10">
              VS
            </div>
            <div className="text-left">
              <span className="font-extrabold text-white text-sm block leading-none">{workspace}</span>
              <span className="text-[10px] text-slate-500 font-semibold block mt-1">Enterprise Tier</span>
            </div>
          </div>
          <span className="text-xs text-slate-500">↕</span>
        </div>

        {/* B. Search launch trigger displaying Ctrl+K indicator */}
        <button
          onClick={open}
          className="w-full flex items-center justify-between px-3 py-2 bg-slate-800/40 hover:bg-slate-800/60 rounded-lg text-xs font-semibold text-slate-500 border border-slate-800/60 transition-colors"
        >
          <span className="flex items-center gap-2">🔍 Quick Search...</span>
          <kbd className="px-1.5 py-0.5 bg-slate-900 border border-slate-800 rounded font-sans text-[9px] shadow-sm">Ctrl+K</kbd>
        </button>

        {/* C. Favorites List */}
        <div>
          <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3 block mb-2">⭐ Favorites</span>
          <div className="space-y-1">
            <Link
              href="/agents"
              className="flex items-center gap-2.5 px-3 py-1.5 hover:bg-slate-800/30 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
            >
              <span>🤖</span> Support Agent
            </Link>
            <Link
              href="/prompts"
              className="flex items-center gap-2.5 px-3 py-1.5 hover:bg-slate-800/30 rounded-lg text-xs font-semibold text-slate-400 hover:text-slate-200 transition-colors"
            >
              <span>📝</span> Welcoming Template
            </Link>
          </div>
        </div>

        {/* D. Main Nav Groups */}
        <nav className="space-y-5">
          {/* Group 1: Core Analysis */}
          <div>
            <span className="text-[10px] font-bold uppercase tracking-wider text-slate-500 px-3 block mb-2">📊 Analytics & Core</span>
            <div className="space-y-1">
              {[
                { id: "/", label: "Dashboard", icon: "📊" },
                { id: "/analytics", label: "Telemetry Charts", icon: "📈" },
                { id: "/providers", label: "Benchmarking", icon: "☁️" },
              ].map((item) => (
                <Link
                  key={item.id}
                  href={item.id}
                  className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-bold transition-all border ${
                    isActive(item.id)
                      ? "bg-blue-600 text-white border-blue-700 shadow-md shadow-blue-500/5"
                      : "bg-transparent border-transparent hover:bg-slate-800/40 hover:text-slate-200"
                  }`}
                >
                  <span>{item.icon}</span> {item.label}
                </Link>
              ))}
            </div>
          </div>

          {/* Group 2: Orchestration (Collapsible) */}
          <div>
            <div
              onClick={() => setIsWfCollapsed(!isWfGroupCollapsed)}
              className="flex items-center justify-between px-3 cursor-pointer text-[10px] font-bold uppercase tracking-wider text-slate-500 mb-2 hover:text-slate-300 transition-colors"
            >
              <span>🤖 Agents & Workflows</span>
              <span>{isWfGroupCollapsed ? "＋" : "−"}</span>
            </div>
            {!isWfGroupCollapsed && (
              <div className="space-y-1 animate-in slide-in-from-top-1 duration-150">
                {[
                  { id: "/agents", label: "Agents Manager", icon: "🤖" },
                  { id: "/conversations", label: "Conversations History", icon: "💬" },
                  { id: "/knowledge", label: "Knowledge Bases", icon: "📚" },
                  { id: "/prompts", label: "Prompt Studio", icon: "📝" },
                  { id: "/playground", label: "Playground Arena", icon: "🧪" },
                ].map((item) => (
                  <Link
                    key={item.id}
                    href={item.id}
                    className={`w-full flex items-center gap-3 px-3.5 py-2.5 rounded-lg text-xs font-bold transition-all border ${
                      isActive(item.id)
                        ? "bg-blue-600 text-white border-blue-700 shadow-md shadow-blue-500/5"
                        : "bg-transparent border-transparent hover:bg-slate-800/40 hover:text-slate-200"
                    }`}
                  >
                    <span>{item.icon}</span> {item.label}
                  </Link>
                ))}
              </div>
            )}
          </div>
        </nav>
      </div>

      {/* E. Bottom Utilities & Version Controls */}
      <div className="border-t border-slate-800 pt-4 space-y-4">
        <div className="flex items-center justify-between px-2">
          {/* Quick theme toggler */}
          <button onClick={toggleTheme} className="p-2 bg-slate-800/50 hover:bg-slate-800 text-sm rounded-lg transition-colors">
            {theme === "light" ? "🌙" : "☀️"}
          </button>
          
          {/* Quick settings link */}
          <Link href="/settings" className={`p-2 bg-slate-800/50 hover:bg-slate-800 text-sm rounded-lg transition-all ${isActive("/settings") ? "text-blue-500" : ""}`}>
            ⚙️
          </Link>
        </div>

        <div className="px-2 text-[10px] text-slate-600 font-semibold flex justify-between items-center">
          <span>AgentSphere Platform</span>
          <span>v0.5.0</span>
        </div>
      </div>
    </aside>
  );
}
export default Sidebar;
