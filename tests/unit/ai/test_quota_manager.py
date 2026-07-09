import pytest

from agentsphere.ai.cost.quota_manager import QuotaManager
from agentsphere.ai.exceptions.refinement_exceptions import QuotaExceededError


@pytest.fixture
def manager() -> QuotaManager:
    return QuotaManager()


def test_quota_record_and_enforce_limit(manager: QuotaManager) -> None:
    # Default: limits are high ($100/day). Let's set a custom tight limit of $1.50 per day
    tenant_id = "tenant_123"
    manager.set_tenant_limits(tenant_id, daily_cost_limit=1.50, monthly_cost_limit=20.0)

    # Check quota with small estimated cost of $0.50 -> Should Pass
    manager.check_quota(tenant_id, "openai", estimated_cost=0.50)

    # Record actual usage of $1.00
    manager.record_usage(tenant_id, "openai", cost=1.00, tokens=1000)

    # Now, try check_quota with estimated cost of $0.60 (Total: $1.00 spent + $0.60 est = $1.60 > $1.50 cap)
    # -> Should raise QuotaExceededError
    with pytest.raises(QuotaExceededError) as exc:
        manager.check_quota(tenant_id, "openai", estimated_cost=0.60)
    assert "has exceeded their daily expenditure allowance" in str(exc.value)


def test_quota_monthly_limit(manager: QuotaManager) -> None:
    tenant_id = "tenant_monthly"
    manager.set_tenant_limits(tenant_id, daily_cost_limit=100.0, monthly_cost_limit=5.00)

    # Record actual monthly usage of $4.50
    manager.record_usage(tenant_id, "openai", cost=4.50, tokens=1000)

    # Next call estimated at $1.00 (Total: $4.50 spent + $1.00 est = $5.50 > $5.00 monthly cap)
    with pytest.raises(QuotaExceededError) as exc:
        manager.check_quota(tenant_id, "openai", estimated_cost=1.00)
    assert "exceeded their monthly expenditure allowance" in str(exc.value)


def test_global_provider_quota_budget(manager: QuotaManager) -> None:
    # Set tight daily limit on openai of $10.00
    manager.get_provider_quota("openai").daily_cost_limit = 10.00

    # Estimate of $11.00 should exceed provider daily allowance
    with pytest.raises(QuotaExceededError) as exc:
        manager.check_quota(None, "openai", estimated_cost=11.00)
    assert "Global provider quota limit hit" in str(exc.value)
