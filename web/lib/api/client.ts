/* eslint-disable @typescript-eslint/no-explicit-any */
// High level Fetch SDK Wrapper enforcing centralized contexts, tracing, and tenant UUIDs.

export interface APIRequestOptions {
  method?: "GET" | "POST" | "PUT" | "DELETE" | "PATCH";
  body?: any;
  headers?: Record<string, string>;
  tenantId?: string;
}

const DEFAULT_API_BASE = "/api/v1";

export async function requestBFF<T>(endpoint: string, options: APIRequestOptions = {}): Promise<T> {
  const method = options.method || "GET";
  const tenantId = options.tenantId || "default_tenant";

  const headers: Record<string, string> = {
    "Content-Type": "application/json",
    "X-Tenant-ID": tenantId,
    "X-Request-ID": `req_${Math.random().toString(36).substring(2, 9)}`,
    ...options.headers,
  };

  const config: RequestInit = {
    method,
    headers,
  };

  if (options.body && method !== "GET") {
    config.body = JSON.stringify(options.body);
  }

  // Communicate strictly with Next.js BFF proxy routes or directly with FastAPI
  const url = `${DEFAULT_API_BASE}${endpoint}`;
  const response = await fetch(url, config);

  if (!response.ok) {
    const errorBody = await response.json().catch(() => ({}));
    throw new Error(errorBody.detail || `Network response failed with status ${response.status}`);
  }

  if (response.status === 204) {
    return {} as T;
  }

  return response.json() as Promise<T>;
}
