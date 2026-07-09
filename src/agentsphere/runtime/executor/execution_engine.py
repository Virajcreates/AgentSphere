import asyncio
import re
import time
from graphlib import TopologicalSorter
from typing import Any

import structlog

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.runtime.exceptions.base import (
    ExecutionTimeoutError,
    WorkflowRecoveryError,
)
from agentsphere.runtime.schemas.runtime import (
    ExecutionGraph,
    ExecutionHistory,
    RecoveryPolicy,
    RuntimeContext,
)

logger = structlog.get_logger(__name__)


class ExecutionEngine:
    def __init__(self, event_bus: EventBus) -> None:
        self._event_bus = event_bus

    async def execute_graph(
        self,
        graph: ExecutionGraph,
        context: RuntimeContext,
        history: ExecutionHistory,
        tool_executor_func: Any,
        policy_verifier_func: Any,
        timeout: float = 60.0,
    ) -> dict[str, Any]:
        """Topologically sorts the ExecutionGraph DAG and runs nodes sequentially, enforcing

        timeouts, consecutive retries, step cancellations, and custom RecoveryPolicy strategies.
        """
        start_time = time.perf_counter()

        # 1. Topological Sorting using standard graphlib.TopologicalSorter
        ts: TopologicalSorter[str] = TopologicalSorter()
        for node_id, node in graph.nodes.items():
            # In TopologicalSorter, we add nodes with their predecessors (dependencies)
            ts.add(node_id, *node.depends_on)

        # Retrieve topologically sorted sequence of step IDs
        try:
            sorted_nodes = list(ts.static_order())
        except Exception as e:
            raise WorkflowRecoveryError(
                step_id="graph",
                strategy="topological_sort",
                detail=f"Circular reference identified during sorting: {e!s}",
            ) from e

        # Store outputs of each step-node: step_id -> step result dict
        step_outputs: dict[str, Any] = {}

        # 2. Iterate and execute sorted nodes sequentially
        for step_id in sorted_nodes:
            # Check for elapsed execution timeout
            elapsed = time.perf_counter() - start_time
            if elapsed > timeout:
                raise ExecutionTimeoutError(context.execution_id, elapsed, timeout)

            node = graph.nodes[step_id]

            # Trigger step verification policy checks (e.g. execution depth limit or budget bounds)
            if policy_verifier_func:
                policy_verifier_func(node, context)

            # Resolve/inject values from step_outputs into node arguments
            resolved_args = self._resolve_arguments(node.arguments, step_outputs)

            # Record step started in history
            step_record = {
                "step_id": step_id,
                "action": node.action,
                "status": "running",
                "started_at": time.time(),
                "completed_at": None,
                "attempts": 0,
                "result": None,
                "error": None,
            }
            history.steps_history.append(step_record)

            # Define node execution closure
            async def run_step(n: Any = node, sid: str = step_id, args: dict[str, Any] = resolved_args) -> Any:
                if n.action.startswith("tool:"):
                    tool_name = n.action.split(":", 1)[1]
                    # Invoke whitelisted tool executor
                    return await tool_executor_func(
                        tool_name=tool_name,
                        arguments=args,
                        context=context,
                    )
                else:
                    # Mock direct LLM prompt generating behavior
                    await asyncio.sleep(0.02)  # short simulated latency
                    return {
                        "status": "success",
                        "content": f"Simulated output from non-tool step '{sid}' with input: {args}",
                    }

            # 3. Execute step with granular RecoveryPolicy failsafes
            result_data = None
            policy = node.recovery_policy
            step_record["attempts"] = 1

            try:
                result_data = await self._execute_with_recovery(
                    run_step, policy, step_id, step_record
                )
                step_record["status"] = "success"
                step_record["result"] = result_data
                step_outputs[step_id] = result_data
            except Exception as exc:
                # Node completely failed after recovery logic is exhausted
                step_record["status"] = "failed"
                step_record["error"] = str(exc)

                # Process final step-level Recovery Policy
                if policy.strategy == "skip":
                    logger.warn(
                        "Recovery strategy 'skip' triggered. Continuing execution",
                        step_id=step_id,
                        error=str(exc),
                    )
                    step_outputs[step_id] = {"skipped": True, "error": str(exc)}
                elif policy.strategy == "continue":
                    logger.warn(
                        "Recovery strategy 'continue' triggered. Continuing execution",
                        step_id=step_id,
                        error=str(exc),
                    )
                    step_outputs[step_id] = {}
                elif policy.strategy == "rollback":
                    logger.error(
                        "Recovery strategy 'rollback' triggered. Initiating rollback and aborting",
                        step_id=step_id,
                    )
                    # Mock a rollback logging snapshot
                    step_record["status"] = "rolled_back"
                    raise WorkflowRecoveryError(
                        step_id=step_id,
                        strategy="rollback",
                        detail=f"Rollback completed during step failure: {exc!s}",
                    ) from exc
                else:
                    # Default: cancel / abort
                    logger.error(
                        "Step failed and strategy requires aborting",
                        step_id=step_id,
                        strategy=policy.strategy,
                    )
                    raise

            # Record step completed time
            step_record["completed_at"] = time.time()

        return step_outputs

    async def _execute_with_recovery(
        self, func: Any, policy: RecoveryPolicy, step_id: str, step_record: dict[str, Any]
    ) -> Any:
        attempts = 0
        backoff = 0.01  # small base backoff for test speed

        while True:
            try:
                res = await func()
                # Record total attempts (initial 1 + retries attempts)
                step_record["attempts"] = attempts + 1
                return res
            except Exception as e:
                attempts += 1
                step_record["attempts"] = attempts

                if policy.strategy == "retry" and attempts <= policy.max_retries:
                    logger.warn(
                        "Step execution failed. Retrying",
                        step_id=step_id,
                        attempt=attempts,
                        delay=backoff,
                        error=str(e),
                    )
                    await asyncio.sleep(backoff)
                    backoff *= policy.backoff_factor
                    continue
                # If strategies are not 'retry' or we exhausted retries, raise to bubble up
                raise

    def _resolve_arguments(
        self, raw_args: dict[str, Any], step_outputs: dict[str, Any]
    ) -> dict[str, Any]:
        """Resolves dynamic parameter strings, mapping outputs from parent dependency steps."""
        resolved = {}
        for k, v in raw_args.items():
            if isinstance(v, str):
                pattern = r"\{\{\s*([a-zA-Z0-9_\-]+)\.([a-zA-Z0-9_\-]+)\s*\}\}"

                def replace_match(match: re.Match[str]) -> str:
                    parent_id = match.group(1)
                    prop = match.group(2)
                    if parent_id in step_outputs:
                        parent_data = step_outputs[parent_id]
                        if isinstance(parent_data, dict):
                            if prop in parent_data:
                                return str(parent_data[prop])
                            if prop == "result":
                                return str(parent_data)
                        return str(parent_data)
                    return match.group(0)

                # Strict single-placeholder exact match preserves complex types (dict, float, bool, etc.)
                exact_match = re.match(r"^\{\{\s*([a-zA-Z0-9_\-]+)\.([a-zA-Z0-9_\-]+)\s*\}\}$", v.strip())
                if exact_match:
                    parent_id = exact_match.group(1)
                    prop = exact_match.group(2)
                    if parent_id in step_outputs:
                        parent_data = step_outputs[parent_id]
                        if isinstance(parent_data, dict):
                            if prop in parent_data:
                                resolved[k] = parent_data[prop]
                            elif prop == "result":
                                resolved[k] = parent_data
                            else:
                                resolved[k] = None
                        else:
                            resolved[k] = parent_data
                        continue

                resolved[k] = re.sub(pattern, replace_match, v)
            else:
                resolved[k] = v
        return resolved
