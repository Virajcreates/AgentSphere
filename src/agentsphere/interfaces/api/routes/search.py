from typing import Any

from dependency_injector.wiring import Provide, inject
from fastapi import APIRouter, Depends

from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.interfaces.container import ApplicationContainer

router = APIRouter(prefix="/api/v1/search", tags=["Global Search"])


@router.get("")
@inject
async def execute_command_palette_search(
    q: str = "",
    prompt_manager: PromptManager = Depends(Provide[ApplicationContainer.ai.prompt_manager]),
) -> dict[str, list[dict[str, Any]]]:
    """Unified search resolver querying prompts, agents, documents, and workflows simultaneously."""
    query = q.lower().strip()

    # 1. Search prompts
    matched_prompts = []
    for (ns, name, ver), template in prompt_manager._system_templates.items():
        if not query or query in name.lower() or query in ns.lower() or query in template.lower():
            matched_prompts.append({
                "title": f"Prompt: {ns}.{name}",
                "subtitle": f"System default template ({ver})",
                "route": "/prompts",
                "type": "prompt",
            })

    # 2. Search agents (mock matching using seeds)
    agents = [
        {"name": "Support Agent", "desc": "Enterprise customer support agent orchestrator.", "id": "agent_123"},
        {"name": "Marketing Agent", "desc": "Compiles dynamic email subject copies.", "id": "agent_abc"},
    ]
    matched_agents = []
    for ag in agents:
        if not query or query in ag["name"].lower() or query in ag["desc"].lower():
            matched_agents.append({
                "title": f"Agent: {ag['name']}",
                "subtitle": ag["desc"],
                "route": "/agents",
                "type": "agent",
            })

    # 3. Search document chunks
    chunks = [
        {"file": "RAG_Overview.txt", "content": "AgentSphere delivers isolated Knowledge Bases (RAG)."},
        {"file": "Platform_Rules.md", "content": "Execution plans are strictly Directed Acyclic Graphs (DAG)."},
    ]
    matched_docs = []
    for ch in chunks:
        if not query or query in ch["file"].lower() or query in ch["content"].lower():
            matched_docs.append({
                "title": f"Doc: {ch['file']}",
                "subtitle": ch["content"],
                "route": "/knowledge",
                "type": "document",
            })

    # 4. Search navigation paths
    paths = [
        {"title": "Open Dashboard", "subtitle": "View token usage, cost, and activity summaries.", "route": "/"},
        {"title": "Open Playground", "subtitle": "Streaming completions sandbox.", "route": "/playground"},
        {"title": "Open Providers Benchmarks", "subtitle": "Live latency and success rankings.", "route": "/providers"},
        {"title": "Open Analytics Panels", "subtitle": "Recharts visual telemetry graphs.", "route": "/analytics"},
        {"title": "Open Admin Settings", "subtitle": "Manage API keys, whitelists, and tenants.", "route": "/settings"},
    ]
    matched_nav = []
    for p in paths:
        if not query or query in p["title"].lower() or query in p["subtitle"].lower():
            matched_nav.append({
                "title": p["title"],
                "subtitle": p["subtitle"],
                "route": p["route"],
                "type": "navigation",
            })

    return {
        "prompts": matched_prompts[:5],
        "agents": matched_agents[:5],
        "documents": matched_docs[:5],
        "navigation": matched_nav[:5],
    }
