from dataclasses import dataclass, field
from uuid import UUID

from agentsphere.common.uuid7 import uuid7


@dataclass
class UserEntity:
    id: UUID = field(default_factory=uuid7)
    tenant_id: UUID | None = None
    email: str = ""
    password_hash: str = ""
    display_name: str = ""
    role: str = "viewer"
    is_active: bool = True
