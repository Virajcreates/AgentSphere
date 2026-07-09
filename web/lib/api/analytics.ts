import { requestBFF } from "./client";

export async function fetchAnalyticsData(tenantId?: string): Promise<any> {
  return requestBFF<any>("/analytics", { method: "GET", tenantId });
}
