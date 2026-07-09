import secrets
import string
from uuid import UUID

from agentsphere.infrastructure.auth.password_hasher import PasswordHasher


class APIKeyHandler:
    _alphabet = string.ascii_letters + string.digits

    def __init__(self, prefix: str = "as_live", password_hasher: PasswordHasher | None = None):
        self._prefix = prefix
        self._hasher = password_hasher or PasswordHasher()

    def generate(self, tenant_id: UUID, key_id: UUID) -> tuple[str, str, str]:
        tenant_prefix = str(tenant_id)[:8]
        prefix = f"{self._prefix}_{tenant_prefix}"
        random_part = "".join(secrets.choice(self._alphabet) for _ in range(32))
        raw_key = f"{prefix}_{random_part}"
        key_hash = self._hasher.hash(raw_key)
        return raw_key, prefix, key_hash

    def verify(self, raw_key: str, key_hash: str) -> bool:
        return self._hasher.verify(raw_key, key_hash)
