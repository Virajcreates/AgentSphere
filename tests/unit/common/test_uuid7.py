from agentsphere.common.uuid7 import uuid7


class TestUuid7:
    def test_generates_valid_uuid(self):
        result = uuid7()
        assert result.version == 7

    def test_generates_unique_values(self):
        values = {uuid7() for _ in range(100)}
        assert len(values) == 100

    def test_returns_uuid_object(self):
        result = uuid7()
        import uuid
        assert isinstance(result, uuid.UUID)
