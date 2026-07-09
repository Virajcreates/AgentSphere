from agentsphere.config.settings import Settings


class TestSettings:
    def test_default_values(self):
        settings = Settings(JWT_SECRET="test-secret-that-is-long-enough-32chars")
        assert settings.ENVIRONMENT == "development"
        assert settings.APP_VERSION == "0.1.0"
        assert settings.JWT_ACCESS_TOKEN_EXPIRE_MINUTES == 15
