from datetime import datetime, timedelta

from agentsphere.ai.exceptions.refinement_exceptions import QuotaExceededError


class UsageQuota:
    def __init__(self) -> None:
        self.daily_cost_limit: float = 100.0  # Default: $100.00 / day
        self.monthly_cost_limit: float = 2000.0  # Default: $2000.00 / month

        # Real-time recorded transactions: list of tuples (timestamp, cost_usd, tokens)
        self.transactions: list[tuple[datetime, float, int]] = []

    def clean_transactions(self, now: datetime) -> None:
        # Keep only the transactions within the last 30 days
        cutoff = now - timedelta(days=30)
        self.transactions = [tx for tx in self.transactions if tx[0] >= cutoff]

    def get_accumulated_usage(self, now: datetime, window_days: int) -> tuple[float, int]:
        cutoff = now - timedelta(days=window_days)
        total_cost = 0.0
        total_tokens = 0
        for tx_time, cost, tokens in self.transactions:
            if tx_time >= cutoff:
                total_cost += cost
                total_tokens += tokens
        return total_cost, total_tokens


class QuotaManager:
    def __init__(self) -> None:
        # Tenant IDs mapped to their active UsageQuota status
        self._tenant_quotas: dict[str, UsageQuota] = {}
        # Provider IDs mapped to their active UsageQuota status
        self._provider_quotas: dict[str, UsageQuota] = {}

    def get_tenant_quota(self, tenant_id: str) -> UsageQuota:
        tid = tenant_id.lower()
        if tid not in self._tenant_quotas:
            self._tenant_quotas[tid] = UsageQuota()
        return self._tenant_quotas[tid]

    def get_provider_quota(self, provider: str) -> UsageQuota:
        prov = provider.lower()
        if prov not in self._provider_quotas:
            self._provider_quotas[prov] = UsageQuota()
        return self._provider_quotas[prov]

    def set_tenant_limits(
        self, tenant_id: str, daily_cost_limit: float, monthly_cost_limit: float
    ) -> None:
        quota = self.get_tenant_quota(tenant_id)
        quota.daily_cost_limit = daily_cost_limit
        quota.monthly_cost_limit = monthly_cost_limit

    def check_quota(self, tenant_id: str | None, provider: str, estimated_cost: float) -> None:
        """Checks if executing a transaction with estimated cost will exceed any daily or monthly

        expenditure limits.
        """
        now = datetime.now()

        # 1. Verify tenant quotas
        if tenant_id:
            quota = self.get_tenant_quota(tenant_id)
            quota.clean_transactions(now)

            daily_spent, _ = quota.get_accumulated_usage(now, 1)
            monthly_spent, _ = quota.get_accumulated_usage(now, 30)

            if daily_spent + estimated_cost > quota.daily_cost_limit:
                raise QuotaExceededError(
                    f"Tenant '{tenant_id}' has exceeded their daily expenditure allowance. "
                    f"Spent: ${daily_spent:.4f}/${quota.daily_cost_limit:.2f} USD."
                )

            if monthly_spent + estimated_cost > quota.monthly_cost_limit:
                raise QuotaExceededError(
                    f"Tenant '{tenant_id}' has exceeded their monthly expenditure allowance. "
                    f"Spent: ${monthly_spent:.4f}/${quota.monthly_cost_limit:.2f} USD."
                )

        # 2. Verify provider-level budgets (optional layer, defaults can be high)
        prov_quota = self.get_provider_quota(provider)
        prov_quota.clean_transactions(now)

        prov_daily, _ = prov_quota.get_accumulated_usage(now, 1)
        if prov_daily + estimated_cost > prov_quota.daily_cost_limit:
            raise QuotaExceededError(
                f"Global provider quota limit hit for '{provider}'. "
                f"Accumulated daily spending: ${prov_daily:.4f}/"
                f"${prov_quota.daily_cost_limit:.2f} USD."
            )

    def record_usage(self, tenant_id: str | None, provider: str, cost: float, tokens: int) -> None:
        """Records a successful transaction inside the tenant and provider quotas."""
        now = datetime.now()

        if tenant_id:
            quota = self.get_tenant_quota(tenant_id)
            quota.transactions.append((now, cost, tokens))

        prov_quota = self.get_provider_quota(provider)
        prov_quota.transactions.append((now, cost, tokens))
