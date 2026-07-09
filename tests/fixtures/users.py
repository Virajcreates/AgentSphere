from uuid import UUID

from agentsphere.common.uuid7 import uuid7


def build_user_entity(
    user_id: UUID | None = None,
    tenant_id: UUID | None = None,
    email: str = "test@example.com",
    role: str = "admin",
    password_hash: str = "hashed_password",
) -> dict:
    return {
        "id": user_id or uuid7(),
        "tenant_id": tenant_id or uuid7(),
        "email": email,
        "password_hash": password_hash,
        "display_name": "Test User",
        "role": role,
        "is_active": True,
    }
