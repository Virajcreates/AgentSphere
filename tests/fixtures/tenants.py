from uuid import UUID

from agentsphere.common.uuid7 import uuid7


def build_tenant_entity(
    tenant_id: UUID | None = None,
    name: str = "Test Tenant",
    slug: str = "test-tenant",
) -> dict:
    return {
        "id": tenant_id or uuid7(),
        "name": name,
        "slug": slug,
        "settings": {},
        "feature_flags": {},
        "is_active": True,
    }
