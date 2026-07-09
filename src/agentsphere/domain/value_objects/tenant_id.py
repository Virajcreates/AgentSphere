from uuid import UUID


class TenantId:
    def __init__(self, value: UUID):
        self._value = value

    @property
    def value(self) -> UUID:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, TenantId):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return str(self._value)
