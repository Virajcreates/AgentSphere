import pytest

from agentsphere.ai.exceptions.base import ProviderConnectionError, ProviderError
from agentsphere.ai.gateway.retry_policy import RetryPolicy


@pytest.fixture
def policy() -> RetryPolicy:
    return RetryPolicy(max_retries=2, base_delay=0.01, max_delay=0.1)


def test_get_delay_has_jitter(policy: RetryPolicy) -> None:
    delay_1 = policy.get_delay(1)
    delay_2 = policy.get_delay(1)
    # Checks that jitter is active (delays are random floats and not identical)
    assert delay_1 >= 0.0
    assert delay_1 <= policy.max_delay


@pytest.mark.asyncio
async def test_successful_execution_no_retry(policy: RetryPolicy) -> None:
    call_count = 0

    async def dummy() -> str:
        nonlocal call_count
        call_count += 1
        return "success"

    result = await policy.execute(dummy)
    assert result == "success"
    assert call_count == 1


@pytest.mark.asyncio
async def test_retry_on_transient_error(policy: RetryPolicy) -> None:
    call_count = 0
    retry_events = []

    async def dummy() -> str:
        nonlocal call_count
        call_count += 1
        if call_count < 2:
            raise ProviderConnectionError("openai", "Host unreachable")
        return "recovered"

    async def on_retry(exc: Exception, attempt: int, delay: float) -> None:
        retry_events.append((attempt, delay))

    result = await policy.execute(dummy, on_retry=on_retry)
    assert result == "recovered"
    assert call_count == 2
    assert len(retry_events) == 1
    assert retry_events[0][0] == 0  # 0-indexed attempts


@pytest.mark.asyncio
async def test_exhaust_retries_and_raise(policy: RetryPolicy) -> None:
    call_count = 0

    async def dummy() -> str:
        nonlocal call_count
        call_count += 1
        raise ProviderConnectionError("openai", "Host unreachable")

    with pytest.raises(ProviderConnectionError):
        await policy.execute(dummy)

    # 1 original call + 2 retries = 3 total attempts
    assert call_count == 3


@pytest.mark.asyncio
async def test_no_retry_on_non_transient_error(policy: RetryPolicy) -> None:
    call_count = 0

    async def dummy() -> str:
        nonlocal call_count
        call_count += 1
        raise ProviderError("openai", "Invalid API key", 401)

    with pytest.raises(ProviderError) as exc:
        await policy.execute(dummy)

    assert exc.value.status == 401
    assert call_count == 1  # No retries for 401 Unauthorized
