import time
from typing import Literal

from agentsphere.ai.exceptions.base import CircuitBreakerOpenError

State = Literal["CLOSED", "OPEN", "HALF_OPEN"]


class CircuitBreaker:
    def __init__(
        self,
        failure_threshold: int = 3,
        cooldown_period: float = 10.0,
        half_open_success_threshold: int = 2,
    ) -> None:
        self.failure_threshold = failure_threshold
        self.cooldown_period = cooldown_period
        self.half_open_success_threshold = half_open_success_threshold

        # Dicts keying provider_name to states
        self._states: dict[str, State] = {}
        self._failures: dict[str, int] = {}
        self._successes: dict[str, int] = {}
        self._last_state_change: dict[str, float] = {}

    def get_state(self, provider: str) -> State:
        prov = provider.lower()
        if prov not in self._states:
            self._states[prov] = "CLOSED"
            self._failures[prov] = 0
            self._successes[prov] = 0
            self._last_state_change[prov] = 0.0

        state = self._states[prov]
        if state == "OPEN":
            # Check if cooldown has expired to transition to HALF_OPEN
            elapsed = time.perf_counter() - self._last_state_change[prov]
            if elapsed >= self.cooldown_period:
                self._states[prov] = "HALF_OPEN"
                self._successes[prov] = 0
                self._last_state_change[prov] = time.perf_counter()
                return "HALF_OPEN"
        return self._states[prov]

    def allow_request(self, provider: str) -> bool:
        prov = provider.lower()
        state = self.get_state(prov)
        if state == "OPEN":
            elapsed = time.perf_counter() - self._last_state_change[prov]
            cooldown_remaining = max(0.0, self.cooldown_period - elapsed)
            raise CircuitBreakerOpenError(provider, cooldown_remaining)
        return True

    def record_success(self, provider: str) -> None:
        prov = provider.lower()
        state = self.get_state(prov)
        self._failures[prov] = 0  # Reset consecutive failures

        if state == "HALF_OPEN":
            self._successes[prov] += 1
            if self._successes[prov] >= self.half_open_success_threshold:
                self._states[prov] = "CLOSED"
                self._successes[prov] = 0
                self._failures[prov] = 0
                self._last_state_change[prov] = time.perf_counter()

    def record_failure(self, provider: str) -> None:
        prov = provider.lower()
        state = self.get_state(prov)

        if state == "CLOSED":
            self._failures[prov] += 1
            if self._failures[prov] >= self.failure_threshold:
                self._states[prov] = "OPEN"
                self._last_state_change[prov] = time.perf_counter()
        elif state == "HALF_OPEN":
            # Any failure in HALF_OPEN trips it right back to OPEN
            self._states[prov] = "OPEN"
            self._last_state_change[prov] = time.perf_counter()
            self._failures[prov] = 1
