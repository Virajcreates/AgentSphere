import uuid

from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from agentsphere.runtime.schemas.runtime import AgentDefinition, WorkflowDefinition

router = APIRouter(prefix="/api/v1/agents", tags=["Agents"])

# Stateful in-memory repository for Agent Definitions to support full CRUD without DB bindings
_AGENTS_DB: dict[str, AgentDefinition] = {
    "agent_123": AgentDefinition(
        agent_id="agent_123",
        name="Support Agent",
        description="Enterprise customer support agent orchestrator.",
        prompt_ref="agent_welcome",
        allowed_tools=["calculator", "search_web"],
        workflows={
            "wf1": WorkflowDefinition(
                workflow_id="wf1",
                name="Customer Support Flow",
                description="Standard support path using search and calculations.",
                entry_node="step_1",
                allowed_tools=["calculator", "search_web"],
            )
        },
    )
}


class CreateAgentRequest(BaseModel):
    name: str = Field(..., description="Agent name")
    description: str = Field(..., description="Agent description")
    prompt_ref: str = Field("agent_welcome", description="Template prompt reference")
    allowed_tools: list[str] = Field(default_factory=list, description="List of whitelisted tools")


@router.get("", response_model=list[AgentDefinition])
async def list_agents() -> list[AgentDefinition]:
    """Exposes all registered agent definitions."""
    return list(_AGENTS_DB.values())


@router.post("", response_model=AgentDefinition, status_code=status.HTTP_201_CREATED)
async def create_agent(request: CreateAgentRequest) -> AgentDefinition:
    """Enables creating new AgentDefinitions dynamically."""
    agent_id = f"agent_{uuid.uuid4()!s:.8}"
    agent = AgentDefinition(
        agent_id=agent_id,
        name=request.name,
        description=request.description,
        prompt_ref=request.prompt_ref,
        allowed_tools=request.allowed_tools,
    )
    _AGENTS_DB[agent_id] = agent
    return agent


@router.get("/{id}", response_model=AgentDefinition)
async def get_agent(id: str) -> AgentDefinition:
    """Retrieves detailed agent configurations."""
    if id not in _AGENTS_DB:
        raise HTTPException(status_code=404, detail=f"Agent with id '{id}' not found")
    return _AGENTS_DB[id]


@router.put("/{id}", response_model=AgentDefinition)
async def update_agent(id: str, request: CreateAgentRequest) -> AgentDefinition:
    """Updates an existing agent definition."""
    if id not in _AGENTS_DB:
        raise HTTPException(status_code=404, detail=f"Agent with id '{id}' not found")

    agent = _AGENTS_DB[id]
    agent.name = request.name
    agent.description = request.description
    agent.prompt_ref = request.prompt_ref
    agent.allowed_tools = request.allowed_tools
    return agent


@router.delete("/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_agent(id: str) -> None:
    """Removes an agent from the system."""
    if id not in _AGENTS_DB:
        raise HTTPException(status_code=404, detail=f"Agent with id '{id}' not found")
    del _AGENTS_DB[id]
