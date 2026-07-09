import { requestBFF } from "./client";

export async function fetchProviderBenchmarks(tenantId?: string): Promise<any[]> {
  return requestBFF<any[]>("/benchmarks", { method: "GET", tenantId });
}
