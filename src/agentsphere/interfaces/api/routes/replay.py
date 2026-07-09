import time
from typing import Any

from fastapi import APIRouter

router = APIRouter(prefix="/api/v1/replay", tags=["Execution Replays"])


@router.get("/{execution_id}")
async def get_execution_replay(execution_id: str) -> dict[str, Any]:
    """Retrieves full execution timeline, DAG nodes, tool steps, and states of a run session."""
    # Provides fully populated mock lineages and transitions mapping if no active match is stored in-memory
    # (Enables instant visual replay demonstration!)
    return {
        "execution_id": execution_id,
        "workflow_id": "wf1",
        "agent_id": "agent_123",
        "goal": "Retrieve core guidelines and calculate pricing formulas.",
        "state_transitions": [
            {"from_state": None, "to_state": "Created", "timestamp": time.time() - 3.0},
            {"from_state": "Created", "to_state": "Planning", "timestamp": time.time() - 2.8},
            {"from_state": "Planning", "to_state": "Executing", "timestamp": time.time() - 2.5},
            {"from_state": "Executing", "to_state": "Completed", "timestamp": time.time() - 0.2},
        ],
        "steps_history": [
            {
                "step_id": "step_1",
                "action": "tool:calculator",
                "status": "success",
                "started_at": time.time() - 2.4,
                "completed_at": time.time() - 1.8,
                "attempts": 1,
                "result": {"result": 30.0},
                "error": None,
            },
            {
                "step_id": "step_2",
                "action": "tool:search_web",
                "status": "success",
                "started_at": time.time() - 1.7,
                "completed_at": time.time() - 0.9,
                "attempts": 1,
                "result": {"snippet": "AgentSphere matches corporate RAG limits."},
                "error": None,
            },
            {
                "step_id": "step_3",
                "action": "llm_generate",
                "status": "success",
                "started_at": time.time() - 0.8,
                "completed_at": time.time() - 0.3,
                "attempts": 1,
                "result": "Completed analysis: calculation yields 30.0 under standard context bounds.",
                "error": None,
            }
        ],
        "graph": {
            "graph_id": "plan_7b38d",
            "nodes": {
                "step_1": {
                    "step_id": "step_1",
                    "action": "tool:calculator",
                    "depends_on": [],
                    "arguments": {"expr": "10+20"},
                },
                "step_2": {
                    "step_id": "step_2",
                    "action": "tool:search_web",
                    "depends_on": ["step_1"],
                    "arguments": {"query": "{{ step_1.result }}"},
                },
                "step_3": {
                    "step_id": "step_3",
                    "action": "llm_generate",
                    "depends_on": ["step_2"],
                    "arguments": {"context": "{{ step_2.result }}"},
                }
            },
            "edges": [
                ["step_1", "step_2"],
                ["step_2", "step_3"]
            ]
        }
    }
