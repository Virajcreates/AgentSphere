import time
import pytest

from agentsphere.ai.exceptions.base import CircuitBreakerOpenError
from agentsphere.ai.gateway.circuit_breaker import CircuitBreaker


@pytest.fixture
def cb() -> CircuitBreaker:
    return CircuitBreaker(
        failure_threshold=3, cooldown_period=0.1, half_open_success_threshold=2
    )


def test_initial_state_is_closed(cb: CircuitBreaker) -> None:
    assert cb.get_state("openai") == "CLOSED"
    assert cb.allow_request("openai") is True


def test_failure_transitions_to_open(cb: CircuitBreaker) -> None:
    # Under failure threshold
    cb.record_failure("openai")
    cb.record_failure("openai")
    assert cb.get_state("openai") == "CLOSED"
    assert cb.allow_request("openai") is True

    # Reaches failure threshold -> OPEN
    cb.record_failure("openai")
    assert cb.get_state("openai") == "OPEN"

    with pytest.raises(CircuitBreakerOpenError) as exc:
        cb.allow_request("openai")
    assert "is OPEN" in str(exc.value)


def test_cooldown_transitions_to_half_open(cb: CircuitBreaker) -> None:
    cb.record_failure("openai")
    cb.record_failure("openai")
    cb.record_failure("openai")
    assert cb.get_state("openai") == "OPEN"

    # Sleep past cooldown period (0.1s in our fixture)
    time.sleep(0.12)

    # Should automatically transition to HALF_OPEN
    assert cb.get_state("openai") == "HALF_OPEN"
    assert cb.allow_request("openai") is True


def test_half_open_success_closes_circuit(cb: CircuitBreaker) -> None:
    cb.record_failure("openai")
    cb.record_failure("openai")
    cb.record_failure("openai")
    time.sleep(0.12)
    assert cb.get_state("openai") == "HALF_OPEN"

    # First success
    cb.record_success("openai")
    assert cb.get_state("openai") == "HALF_OPEN"

    # Second success closes circuit
    cb.record_success("openai")
    assert cb.get_state("openai") == "CLOSED"
    assert cb.allow_request("openai") is True


def test_half_open_failure_reopens_immediately(cb: CircuitBreaker) -> None:
    cb.record_failure("openai")
    cb.record_failure("openai")
    cb.record_failure("openai")
    time.sleep(0.12)
    assert cb.get_state("openai") == "HALF_OPEN"

    # Failure in HALF_OPEN trips immediately back to OPEN without waiting for failure threshold
    cb.record_failure("openai")
    assert cb.get_state("openai") == "OPEN"
    with pytest.raises(CircuitBreakerOpenError):
        cb.allow_request("openai")
