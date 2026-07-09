import uuid
from dataclasses import dataclass, field
from datetime import UTC, datetime


@dataclass
class DomainEvent:
    event_id: str = field(default_factory=lambda: str(uuid.uuid4()))
    event_type: str = field(default="")
    occurred_at: datetime = field(default_factory=lambda: datetime.now(UTC))

    def __post_init__(self) -> None:
        if not self.event_type:
            self.event_type = self.__class__.__name__
