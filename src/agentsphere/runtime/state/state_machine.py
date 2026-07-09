import asyncio
from datetime import datetime
from typing import ClassVar, Literal

import structlog

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.runtime.exceptions.base import InvalidStateTransitionError
from agentsphere.runtime.schemas.runtime import ExecutionHistory

logger = structlog.get_logger(__name__)

State = Literal["Created", "Planning", "Executing", "Waiting", "Completed", "Failed", "Cancelled"]


class RuntimeStateMachine:
    # Explicit valid transition maps
    _VALID_TRANSITIONS: ClassVar[dict[State, set[State]]] = {
        "Created": {"Planning", "Cancelled"},
        "Planning": {"Executing", "Failed", "Cancelled"},
        "Executing": {"Waiting", "Completed", "Failed", "Cancelled"},
        "Waiting": {"Executing", "Failed", "Cancelled"},
        "Completed": set(),
        "Failed": set(),
        "Cancelled": set(),
    }

    def __init__(
        self, execution_id: str, event_bus: EventBus, workflow_id: str | None = None
    ) -> None:
        self.execution_id = execution_id
        self.workflow_id = workflow_id
        self._event_bus = event_bus

        self._current_state: State = "Created"
        self._history = ExecutionHistory(execution_id=execution_id, workflow_id=workflow_id)
        self._lock = asyncio.Lock()

        # Log initial Created state entry
        self._record_transition(None, "Created")

    @property
    def current_state(self) -> State:
        return self._current_state

    @property
    def history(self) -> ExecutionHistory:
        return self._history

    def _record_transition(self, from_state: State | None, to_state: State) -> None:
        transition = {
            "from_state": from_state,
            "to_state": to_state,
            "timestamp": datetime.now().isoformat(),
        }
        self._history.state_transitions.append(transition)

    async def transition_to(self, target_state: State, reason: str | None = None) -> None:
        """Atomically validates and transitions the runtime to the target state,

        appending immutable snapshots to the execution history, and publishing
        state-change events via the shared platform EventBus.
        """
        async with self._lock:
            from_state = self._current_state
            if from_state == target_state:
                return  # Idempotent return

            allowed = self._VALID_TRANSITIONS.get(from_state, set())
            if target_state not in allowed:
                raise InvalidStateTransitionError(from_state, target_state)

            self._current_state = target_state
            self._record_transition(from_state, target_state)

            logger.info(
                "Execution State Transitioned",
                execution_id=self.execution_id,
                from_state=from_state,
                to_state=target_state,
                reason=reason,
            )

            # Fire standard platform events asynchronously using our shared EventBus
            from agentsphere.runtime.events.events import ExecutionStateChangedEvent

            event = ExecutionStateChangedEvent(
                execution_id=self.execution_id,
                workflow_id=self.workflow_id,
                from_state=from_state,
                to_state=target_state,
                reason=reason,
                timestamp=datetime.now(),
            )
            await self._event_bus.publish(event)
