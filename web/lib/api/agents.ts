import { AgentDefinition, CreateAgentRequest } from "../../types/schemas";
import { requestBFF } from "./client";

export async function listAgents(tenantId?: string): Promise<AgentDefinition[]> {
  return requestBFF<AgentDefinition[]>("/agents", { method: "GET", tenantId });
}

export async function createAgent(body: CreateAgentRequest, tenantId?: string): Promise<AgentDefinition> {
  return requestBFF<AgentDefinition>("/agents", { method: "POST", body, tenantId });
}

export async function getAgent(id: string, tenantId?: string): Promise<AgentDefinition> {
  return requestBFF<AgentDefinition>(`/agents/${id}`, { method: "GET", tenantId });
}

export async function updateAgent(id: string, body: CreateAgentRequest, tenantId?: string): Promise<AgentDefinition> {
  return requestBFF<AgentDefinition>(`/agents/${id}`, { method: "PUT", body, tenantId });
}

export async function deleteAgent(id: string, tenantId?: string): Promise<void> {
  return requestBFF<void>(`/agents/${id}`, { method: "DELETE", tenantId });
}
