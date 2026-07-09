from agentsphere.infrastructure.auth.password_hasher import PasswordHasher


class TestPasswordHasher:
    def setup_method(self):
        self.hasher = PasswordHasher()

    def test_hash_and_verify(self):
        password = "test-password-123"
        hashed = self.hasher.hash(password)
        assert hashed != password
        assert self.hasher.verify(password, hashed) is True

    def test_verify_wrong_password(self):
        hashed = self.hasher.hash("correct-password")
        assert self.hasher.verify("wrong-password", hashed) is False
