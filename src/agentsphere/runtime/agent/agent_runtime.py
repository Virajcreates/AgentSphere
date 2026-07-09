import asyncio
import time
from collections.abc import Callable, Coroutine
from datetime import datetime
from typing import Any, Literal

import structlog

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.runtime.conversation.conversation_manager import ConversationManager
from agentsphere.runtime.events.events import (
    ExecutionCompleted,
    ExecutionFailed,
    ExecutionStarted,
)
from agentsphere.runtime.executor.execution_engine import ExecutionEngine
from agentsphere.runtime.interfaces.checkpoint import CheckpointStore
from agentsphere.runtime.memory.memory_manager import MemoryManager
from agentsphere.runtime.planner.planner import RuntimePlanner
from agentsphere.runtime.policies.policies import RuntimePolicyEvaluator
from agentsphere.runtime.schemas.runtime import (
    AgentDefinition,
    ExecutionNode,
    RuntimeContext,
    RuntimeRequest,
    RuntimeResponse,
    ToolInvocation,
)
from agentsphere.runtime.serialization.serializer import RuntimeSerializer
from agentsphere.runtime.state.state_machine import RuntimeStateMachine
from agentsphere.runtime.telemetry.tracker import RuntimeTracker
from agentsphere.runtime.tools.tool_framework import ToolExecutor

logger = structlog.get_logger(__name__)

HookName = Literal[
    "BeforePlanning",
    "AfterPlanning",
    "BeforeExecution",
    "AfterExecution",
    "BeforeTool",
    "AfterTool",
    "BeforeResponse",
    "AfterResponse",
]


class AgentRuntime:
    def __init__(
        self,
        event_bus: EventBus,
        conversation_manager: ConversationManager,
        planner: RuntimePlanner,
        execution_engine: ExecutionEngine,
        tool_executor: ToolExecutor,
        memory_manager: MemoryManager,
        policy_evaluator: RuntimePolicyEvaluator,
        tracker: RuntimeTracker,
        serializer: RuntimeSerializer,
        checkpoint_store: CheckpointStore,
    ) -> None:
        self.event_bus = event_bus
        self.conversation_manager = conversation_manager
        self.planner = planner
        self.execution_engine = execution_engine
        self.tool_executor = tool_executor
        self.memory_manager = memory_manager
        self.policy_evaluator = policy_evaluator
        self.tracker = tracker
        self.serializer = serializer
        self.checkpoint_store = checkpoint_store

        # Dynamic registry for Runtime Lifecycle Hooks: hook_name -> list of async callbacks
        self._hooks: dict[HookName, list[Callable[[Any], Coroutine[Any, Any, None]]]] = {
            "BeforePlanning": [],
            "AfterPlanning": [],
            "BeforeExecution": [],
            "AfterExecution": [],
            "BeforeTool": [],
            "AfterTool": [],
            "BeforeResponse": [],
            "AfterResponse": [],
        }

    def register_hook(
        self, hook_name: HookName, callback: Callable[[Any], Coroutine[Any, Any, None]]
    ) -> None:
        if hook_name in self._hooks and callback not in self._hooks[hook_name]:
            self._hooks[hook_name].append(callback)

    async def _trigger_hook(self, hook_name: HookName, payload: Any) -> None:
        callbacks = self._hooks.get(hook_name, [])
        if callbacks:
            logger.info(
                "Executing Runtime Lifecycle Hook", hook_name=hook_name, count=len(callbacks)
            )
            tasks = [cb(payload) for cb in callbacks]
            await asyncio.gather(*tasks, return_exceptions=True)

    async def execute(
        self, request: RuntimeRequest, agent_def: AgentDefinition, timeout: float = 60.0
    ) -> RuntimeResponse:
        """Starts and orchestrates the complete Agent request execution lifecycle."""
        import uuid

        exec_id = f"exec_{uuid.uuid4()!s:.8}"

        # 1. Initialize Runtime Context
        context = RuntimeContext(
            request_id=f"req_{uuid.uuid4()!s:.8}",
            tenant_id=request.tenant_id,
            execution_id=exec_id,
            workflow_id=request.workflow_id,
            agent_id=request.agent_id,
        )

        # 2. Setup validated State Machine
        sm = RuntimeStateMachine(
            execution_id=exec_id, event_bus=self.event_bus, workflow_id=request.workflow_id
        )

        # Dispatch ExecutionStarted start event
        await self.event_bus.publish(
            ExecutionStarted(
                execution_id=exec_id,
                workflow_id=request.workflow_id,
                goal=request.goal,
                timestamp=datetime.now(),
            )
        )

        # Set up active Working Memory context variables
        working_mem = await self.memory_manager.get_working_memory(exec_id)
        for k, v in request.variables.items():
            await working_mem.set(k, v)

        # Start lifecycle timer
        start_time = time.perf_counter()

        try:
            # 3. Hook: BeforePlanning
            await self._trigger_hook("BeforePlanning", {"context": context, "request": request})

            # 4. State: Planning
            await sm.transition_to("Planning")

            # Compile execution goals into structured ExecutionGraph DAG
            graph = await self.planner.create_plan(
                goal=request.goal, agent_def=agent_def, workflow_id=request.workflow_id
            )
            context.plan_id = graph.graph_id

            # Save dynamic plan ID inside state machine snapshot
            sm.history.workflow_id = request.workflow_id

            plan_latency = time.perf_counter() - start_time
            self.tracker.track_planning(plan_latency)

            # 5. Hook: AfterPlanning (e.g. static loop check validations)
            await self._trigger_hook("AfterPlanning", {"context": context, "graph": graph})

            # 6. State: Executing
            await sm.transition_to("Executing")

            # 7. Hook: BeforeExecution
            await self._trigger_hook("BeforeExecution", {"context": context, "graph": graph})

            # Defined helper closures to map tools execution and policy evaluation rules
            async def run_tool_with_hooks(
                tool_name: str, arguments: dict[str, Any], context: RuntimeContext
            ) -> dict[str, Any]:
                invocation = ToolInvocation(
                    tool_name=tool_name, arguments=arguments, caller="AgentRuntime"
                )

                # Triggers Step-level hooks
                await self._trigger_hook(
                    "BeforeTool", {"context": context, "invocation": invocation}
                )

                t_start = time.perf_counter()
                res = await self.tool_executor.invoke(invocation, context)
                t_duration = time.perf_counter() - t_start

                self.tracker.track_tool(tool_name, t_duration)

                await self._trigger_hook("AfterTool", {"context": context, "result": res})
                return res

            def verify_policy_with_limits(node: ExecutionNode, context: RuntimeContext) -> None:
                self.policy_evaluator.verify_step_policy(node, context)

            # 8. Traverse DAG nodes and execute sequentially using execution engine
            exec_outputs = await self.execution_engine.execute_graph(
                graph=graph,
                context=context,
                history=sm.history,
                tool_executor_func=run_tool_with_hooks,
                policy_verifier_func=verify_policy_with_limits,
                timeout=timeout,
            )

            # Save successful output data
            for k, v in exec_outputs.items():
                await working_mem.set(f"result_{k}", v)

            # 9. Hook: AfterExecution
            await self._trigger_hook(
                "AfterExecution", {"context": context, "outputs": exec_outputs}
            )

            # 10. State: Completed
            await sm.transition_to("Completed")

            # 11. Perform dynamic Checkpoint saving using RuntimeSerializer
            serialized_state = self.serializer.serialize_runtime(
                state=sm.current_state,
                context=context,
                graph=graph,
                memory=await working_mem.get_all(),  # use get_all Protocol method
            )
            await self.checkpoint_store.save(exec_id, {"payload": serialized_state})

            # 12. Hook: BeforeResponse
            await self._trigger_hook(
                "BeforeResponse", {"context": context, "outputs": exec_outputs}
            )

            # Dispatch success end event
            await self.event_bus.publish(
                ExecutionCompleted(
                    execution_id=exec_id,
                    workflow_id=request.workflow_id,
                    output_data=exec_outputs,
                    timestamp=datetime.now(),
                )
            )

            response = RuntimeResponse(
                execution_id=exec_id,
                state=sm.current_state,
                history=sm.history,
                output_data=exec_outputs,
            )

            # 13. Hook: AfterResponse
            await self._trigger_hook("AfterResponse", {"context": context, "response": response})

            # Record successful telemetry
            self.tracker.track_execution(time.perf_counter() - start_time, success=True)

            return response

        except Exception as e:
            # 14. Fallback execution failure state
            logger.error("Agent execution loop failed", execution_id=exec_id, error=str(e))

            # Transition state machine to failed
            from contextlib import suppress

            with suppress(Exception):
                await sm.transition_to("Failed", reason=str(e))

            # Publish failed telemetry events
            await self.event_bus.publish(
                ExecutionFailed(
                    execution_id=exec_id,
                    workflow_id=request.workflow_id,
                    error_message=str(e),
                    timestamp=datetime.now(),
                )
            )

            self.tracker.track_execution(time.perf_counter() - start_time, success=False)
            raise e
        finally:
            # Clean dynamic thread contexts to prevent memory growth
            self.policy_evaluator.cleanup(exec_id)
            await self.memory_manager.cleanup(exec_id)
