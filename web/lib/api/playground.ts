import { requestBFF } from "./client";

export async function executePlaygroundCompletion(body: any, tenantId?: string): Promise<any> {
  // Proxies sandbox prompting to central platform AIInferenceService
  return requestBFF<any>("/prompts/compile", { method: "POST", body, tenantId });
}
