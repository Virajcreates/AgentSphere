import { CreateKnowledgeBaseRequest, DocumentQueryRequest } from "../../types/schemas";
import { requestBFF } from "./client";

export async function createKnowledgeBase(body: CreateKnowledgeBaseRequest, tenantId?: string): Promise<any> {
  return requestBFF<any>("/knowledge-bases", { method: "POST", body, tenantId });
}

export async function uploadKnowledgeDocument(
  id: string,
  file: File,
  chunkStrategy: string = "recursive",
  tenantId?: string
): Promise<any> {
  // Multipart uploading has dedicated browser format
  const formData = new FormData();
  formData.append("file", file);
  formData.append("chunk_strategy", chunkStrategy);

  const url = `/api/v1/knowledge-bases/${id}/documents`;
  const response = await fetch(url, {
    method: "POST",
    headers: {
      "X-Tenant-ID": tenantId || "default_tenant",
    },
    body: formData,
  });

  if (!response.ok) {
    throw new Error("File indexing upload failed");
  }
  return response.json();
}

export async function queryKnowledgeBase(id: string, body: DocumentQueryRequest, tenantId?: string): Promise<any[]> {
  return requestBFF<any[]>(`/knowledge-bases/${id}/query`, { method: "POST", body, tenantId });
}
