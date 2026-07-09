from dataclasses import dataclass, field
from typing import Any
from uuid import UUID

from agentsphere.common.uuid7 import uuid7


@dataclass
class TenantEntity:
    id: UUID = field(default_factory=uuid7)
    name: str = ""
    slug: str = ""
    settings: dict[str, Any] = field(default_factory=dict)
    feature_flags: dict[str, Any] = field(default_factory=dict)
    is_active: bool = True
