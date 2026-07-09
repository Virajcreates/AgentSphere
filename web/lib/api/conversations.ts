import { AddMessageRequest, CreateConversationRequest } from "../../types/schemas";
import { requestBFF } from "./client";

export async function createConversation(body: CreateConversationRequest, tenantId?: string): Promise<any> {
  return requestBFF<any>("/conversations", { method: "POST", body, tenantId });
}

export async function getConversationHistory(id: string, tenantId?: string): Promise<any[]> {
  return requestBFF<any[]>(`/conversations/${id}`, { method: "GET", tenantId });
}

export async function addConversationMessage(id: string, body: AddMessageRequest, tenantId?: string): Promise<any> {
  return requestBFF<any>(`/conversations/${id}/messages`, { method: "POST", body, tenantId });
}

export async function getLatestConversationSummary(id: string, tenantId?: string): Promise<any | null> {
  return requestBFF<any | null>(`/conversations/${id}/summary`, { method: "GET", tenantId });
}
