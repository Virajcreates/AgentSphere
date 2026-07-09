import re


class Email:
    _pattern = re.compile(r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$")

    def __init__(self, value: str):
        if not self._pattern.match(value):
            raise ValueError(f"Invalid email address: {value}")
        self._value = value.lower()

    @property
    def value(self) -> str:
        return self._value

    def __eq__(self, other: object) -> bool:
        if isinstance(other, Email):
            return self._value == other._value
        return False

    def __hash__(self) -> int:
        return hash(self._value)

    def __str__(self) -> str:
        return self._value
