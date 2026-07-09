import { NextRequest, NextResponse } from "next/server";

// Dynamic BFF proxy address pointing directly to Python FastAPI server
const BACKEND_API_BASE = process.env.BACKEND_API_URL || "http://localhost:8000";

async function proxyRequest(request: NextRequest, { params }: { params: Promise<{ path: string[] }> }) {
  const { path } = await params;
  const pathSegment = path ? path.join("/") : "";
  const searchParams = request.nextUrl.search;

  // Formulate dynamic targeting URL to FastAPI Python backend
  const targetUrl = `${BACKEND_API_BASE}/api/v1/${pathSegment}${searchParams}`;

  // centralize security header injections and tenant mappings
  const tenantId = request.headers.get("X-Tenant-ID") || "default_tenant";
  const requestId = request.headers.get("X-Request-ID") || `req_bff_${Date.now()}`;

  const headers = new Headers();
  headers.set("Content-Type", "application/json");
  headers.set("X-Tenant-ID", tenantId);
  headers.set("X-Request-ID", requestId);

  // Forward authorization keys if present
  const auth = request.headers.get("Authorization");
  if (auth) {
    headers.set("Authorization", auth);
  }

  const method = request.method;
  const config: RequestInit = {
    method,
    headers,
  };

  if (method !== "GET" && method !== "HEAD") {
    const rawBody = await request.text();
    if (rawBody) {
      config.body = rawBody;
    }
  }

  try {
    const backendResponse = await fetch(targetUrl, config);
    
    if (backendResponse.status === 204) {
      return new NextResponse(null, { status: 204 });
    }

    const data = await backendResponse.json();
    return NextResponse.json(data, {
      status: backendResponse.status,
      headers: {
        "X-BFF-Proxy": "true",
        "X-Request-ID": requestId,
      }
    });
  } catch (error: any) {
    return NextResponse.json(
      { detail: `BFF Proxy routing failed: ${error.message}` },
      { status: 502 }
    );
  }
}

export const GET = proxyRequest;
export const POST = proxyRequest;
export const PUT = proxyRequest;
export const DELETE = proxyRequest;
export const PATCH = proxyRequest;
export const OPTIONS = proxyRequest;
