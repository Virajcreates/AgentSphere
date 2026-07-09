from uuid import UUID

from agentsphere.common.uuid7 import uuid7


def build_api_key_entity(
    key_id: UUID | None = None,
    tenant_id: UUID | None = None,
    name: str = "Test Key",
    scopes: list | None = None,
) -> dict:
    return {
        "id": key_id or uuid7(),
        "tenant_id": tenant_id or uuid7(),
        "key_prefix": "as_live_test",
        "key_hash": "hashed_key_value",
        "name": name,
        "scopes": scopes or ["conversations:read"],
        "expires_at": None,
        "is_active": True,
    }
