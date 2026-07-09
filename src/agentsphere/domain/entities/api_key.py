from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from agentsphere.common.uuid7 import uuid7


@dataclass
class ApiKeyEntity:
    id: UUID = field(default_factory=uuid7)
    tenant_id: UUID | None = None
    key_prefix: str = ""
    key_hash: str = ""
    name: str = ""
    scopes: list[Any] = field(default_factory=list)
    expires_at: str | None = None
    is_active: bool = True
