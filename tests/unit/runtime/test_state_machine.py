import pytest

from agentsphere.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from agentsphere.runtime.exceptions.base import InvalidStateTransitionError
from agentsphere.runtime.state.state_machine import RuntimeStateMachine


@pytest.fixture
def sm() -> RuntimeStateMachine:
    event_bus = InMemoryEventBus()
    return RuntimeStateMachine(execution_id="exec_123", event_bus=event_bus)


@pytest.mark.asyncio
async def test_initial_state_is_created(sm: RuntimeStateMachine) -> None:
    assert sm.current_state == "Created"
    assert len(sm.history.state_transitions) == 1
    assert sm.history.state_transitions[0]["to_state"] == "Created"


@pytest.mark.asyncio
async def test_valid_transitions_sequence(sm: RuntimeStateMachine) -> None:
    # Created -> Planning -> Executing -> Completed
    await sm.transition_to("Planning")
    assert sm.current_state == "Planning"

    await sm.transition_to("Executing")
    assert sm.current_state == "Executing"

    await sm.transition_to("Completed")
    assert sm.current_state == "Completed"

    assert len(sm.history.state_transitions) == 4


@pytest.mark.asyncio
async def test_invalid_transition_raises_error(sm: RuntimeStateMachine) -> None:
    # Created -> Executing is invalid (must go through Planning)
    with pytest.raises(InvalidStateTransitionError) as exc:
        await sm.transition_to("Executing")
    assert "Cannot transition execution state" in str(exc.value)


@pytest.mark.asyncio
async def test_terminal_state_frozen(sm: RuntimeStateMachine) -> None:
    await sm.transition_to("Cancelled")
    assert sm.current_state == "Cancelled"

    # Terminal states can never transition anywhere else
    with pytest.raises(InvalidStateTransitionError):
        await sm.transition_to("Planning")
