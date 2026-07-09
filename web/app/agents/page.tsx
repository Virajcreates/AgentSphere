"use client";

import React, { useEffect, useState } from "react";
import { Card, Typography, Table, FormField, Dialog } from "../shared/design-system";
import { ErrorBoundary } from "../components/ErrorBoundary";
import { listAgents, createAgent, updateAgent, deleteAgent } from "../lib/api/agents";
import { AgentDefinition } from "../../types/schemas";

export default function AgentsPage() {
  const [agents, setAgents] = useState<AgentDefinition[]>([]);
  const [isOpen, setIsOpen] = useState(false);
  
  // Form fields states
  const [editingId, setEditingId] = useState<string | null>(null);
  const [name, setName] = useState("");
  const [desc, setDesc] = useState("");
  const [promptRef, setPromptRef] = useState("agent_welcome");
  const [allowedTools, setAllowedTools] = useState<string>("calculator, search_web");

  const loadAgentsList = async () => {
    try {
      const list = await listAgents();
      setAgents(list);
    } catch (err) {
      console.warn("Agents loading failed:", err);
    }
  };

  useEffect(() => {
    loadAgentsList();
  }, []);

  const handleOpenDialog = (agent?: AgentDefinition) => {
    if (agent) {
      setEditingId(agent.agent_id);
      setName(agent.name);
      setDesc(agent.description);
      setPromptRef(agent.prompt_ref);
      setAllowedTools(agent.allowed_tools ? agent.allowed_tools.join(", ") : "");
    } else {
      setEditingStateEmpty();
    }
    setIsOpen(true);
  };

  const handleClose = () => {
    setIsOpen(false);
    setEditingId(null);
  };

  const setEditingStateEmpty = () => {
    setEditingId(null);
    setName("");
    setDesc("");
    setPromptRef("agent_welcome");
    setAllowedTools("calculator, search_web");
  };

  const handleSave = async (e: React.FormEvent) => {
    e.preventDefault();
    const toolsList = allowedTools.split(",").map((t) => t.trim()).filter(Boolean);
    const body = {
      name,
      description: desc,
      prompt_ref: promptRef,
      allowed_tools: toolsList,
    };

    try {
      if (editingId) {
        await updateAgent(editingId, body);
      } else {
        await createAgent(body);
      }
      await loadAgentsList();
    } catch (err) {
      alert(`Operation failed: ${err}`);
    } finally {
      handleClose();
    }
  };

  const handleDelete = async (id: string) => {
    if (confirm(`Are you sure you want to delete agent '${id}'?`)) {
      try {
        await deleteAgent(id);
        await loadAgentsList();
      } catch (err) {
        alert(`Delete failed: ${err}`);
      }
    }
  };

  return (
    <ErrorBoundary>
      <div className="space-y-8">
        <div className="flex items-center justify-between">
          <div>
            <Typography.H1>Agents Registry</Typography.H1>
            <Typography.Paragraph>Configure agent schemas, whitelisted tools, and execution policies.</Typography.Paragraph>
          </div>
          <button onClick={() => handleOpenDialog()} className="px-5 py-2.5 bg-blue-600 hover:bg-blue-700 text-white font-bold rounded-xl text-sm transition-all shadow-md shadow-blue-500/10">
            + New Agent Definition
          </button>
        </div>

        <Card title="Registered Agents" subtitle="Active definitions index table">
          <Table
            headers={["ID", "Agent Name", "Description", "Prompt Reference", "Allowed Tools", "Actions"]}
            rows={agents.map((agent) => [
              <Typography.Code key={0}>{agent.agent_id}</Typography.Code>,
              <span key={1} className="font-bold text-slate-900 dark:text-white">{agent.name}</span>,
              <span key={2} className="text-slate-500 dark:text-slate-400 font-medium">{agent.description}</span>,
              <span key={3} className="text-slate-400 font-semibold">{agent.prompt_ref}</span>,
              <div key={4} className="flex flex-wrap gap-1.5">
                {agent.allowed_tools?.map((tool, idx) => (
                  <span key={idx} className="px-2 py-0.5 bg-slate-100 dark:bg-slate-800 text-[10px] rounded border dark:border-slate-700 font-mono text-slate-500">
                    {tool}
                  </span>
                ))}
              </div>,
              <div key={5} className="flex items-center gap-3">
                <button onClick={() => handleOpenDialog(agent)} className="text-xs font-bold text-blue-600 hover:text-blue-700">
                  Edit
                </button>
                <button onClick={() => handleDelete(agent.agent_id)} className="text-xs font-bold text-red-600 hover:text-red-700">
                  Delete
                </button>
              </div>,
            ])}
          />
        </Card>

        {/* Create/Edit Agent Dialog Modal */}
        <Dialog isOpen={isOpen} onClose={handleClose} title={editingId ? "Edit Agent Definition" : "Create New Agent Definition"}>
          <form onSubmit={handleSave} className="space-y-4">
            <FormField label="Agent Name" id="name" placeholder="Support Agent" value={name} onChange={setName} required />
            <FormField label="Description" id="desc" placeholder="Customer helpdesk agent orchestrator..." value={desc} onChange={setDesc} required />
            <FormField label="Prompt Reference" id="promptRef" placeholder="agent_welcome" value={promptRef} onChange={setPromptRef} required />
            <FormField label="Allowed Tools (comma-separated)" id="tools" placeholder="calculator, search_web" value={allowedTools} onChange={setAllowedTools} />

            <div className="flex items-center justify-end gap-3 border-t border-slate-100 dark:border-slate-800 pt-4 mt-6">
              <button type="button" onClick={handleClose} className="px-4 py-2 text-sm font-semibold text-slate-400 hover:text-slate-600 bg-slate-100 dark:bg-slate-800 dark:hover:bg-slate-700 rounded-lg">
                Cancel
              </button>
              <button type="submit" className="px-5 py-2.5 text-sm font-bold text-white bg-blue-600 hover:bg-blue-700 rounded-lg shadow-md shadow-blue-500/10">
                {editingId ? "Update Definition" : "Save Definition"}
              </button>
            </div>
          </form>
        </Dialog>
      </div>
    </ErrorBoundary>
  );
}
