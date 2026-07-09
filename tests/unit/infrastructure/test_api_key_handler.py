from agentsphere.common.uuid7 import uuid7
from agentsphere.infrastructure.auth.api_key_handler import APIKeyHandler


class TestAPIKeyHandler:
    def setup_method(self):
        self.handler = APIKeyHandler(prefix="as_test")

    def test_generate_returns_components(self):
        tenant_id = uuid7()
        key_id = uuid7()
        raw_key, prefix, key_hash = self.handler.generate(tenant_id, key_id)
        assert raw_key.startswith("as_test_")
        assert prefix == f"as_test_{str(tenant_id)[:8]}"
        assert key_hash != raw_key

    def test_verify_valid_key(self):
        tenant_id = uuid7()
        key_id = uuid7()
        raw_key, _prefix, key_hash = self.handler.generate(tenant_id, key_id)
        assert self.handler.verify(raw_key, key_hash) is True

    def test_verify_invalid_key(self):
        tenant_id = uuid7()
        key_id = uuid7()
        _raw, _prefix, key_hash = self.handler.generate(tenant_id, key_id)
        assert self.handler.verify("wrong-key", key_hash) is False
