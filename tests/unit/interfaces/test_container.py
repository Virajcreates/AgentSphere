import pytest

from agentsphere.interfaces.container import ApplicationContainer, init_container


@pytest.fixture
def container() -> ApplicationContainer:
    return init_container()


class TestContainerResolution:
    def test_core_container_resolves(self, container: ApplicationContainer) -> None:
        settings = container.core.settings()
        assert settings is not None

    def test_auth_container_resolves(self, container: ApplicationContainer) -> None:
        jwt = container.auth.jwt_handler()
        hasher = container.auth.password_hasher()
        api_key = container.auth.api_key_handler()
        assert jwt is not None
        assert hasher is not None
        assert api_key is not None

    def test_use_case_login_resolves(self, container: ApplicationContainer) -> None:
        uc = container.use_cases.login()
        assert uc is not None
        assert hasattr(uc, "_user_repo_factory")
        assert hasattr(uc, "_jwt_handler")
        assert hasattr(uc, "_password_hasher")

    def test_use_case_refresh_token_resolves(self, container: ApplicationContainer) -> None:
        uc = container.use_cases.refresh_token()
        assert uc is not None
        assert hasattr(uc, "_jwt_handler")

    def test_use_case_create_api_key_resolves(self, container: ApplicationContainer) -> None:
        uc = container.use_cases.create_api_key()
        assert uc is not None
        assert hasattr(uc, "_api_key_repo_factory")
        assert hasattr(uc, "_api_key_handler")

    def test_use_case_revoke_api_key_resolves(self, container: ApplicationContainer) -> None:
        uc = container.use_cases.revoke_api_key()
        assert uc is not None
        assert hasattr(uc, "_api_key_repo_factory")

    def test_use_case_create_tenant_resolves(self, container: ApplicationContainer) -> None:
        uc = container.use_cases.create_tenant()
        assert uc is not None
        assert hasattr(uc, "_tenant_repo_factory")

    def test_use_case_get_tenant_resolves(self, container: ApplicationContainer) -> None:
        uc = container.use_cases.get_tenant()
        assert uc is not None
        assert hasattr(uc, "_tenant_repo_factory")

    def test_use_case_update_tenant_resolves(self, container: ApplicationContainer) -> None:
        uc = container.use_cases.update_tenant()
        assert uc is not None
        assert hasattr(uc, "_tenant_repo_factory")

    def test_all_use_cases_resolve(self, container: ApplicationContainer) -> None:
        assert container.use_cases.login()
        assert container.use_cases.refresh_token()
        assert container.use_cases.create_api_key()
        assert container.use_cases.revoke_api_key()
        assert container.use_cases.create_tenant()
        assert container.use_cases.get_tenant()
        assert container.use_cases.update_tenant()

    def test_repo_factories_are_classes(self, container: ApplicationContainer) -> None:
        uc_login = container.use_cases.login()
        assert callable(uc_login._user_repo_factory)
        assert isinstance(uc_login._user_repo_factory, type)

        uc_create_api_key = container.use_cases.create_api_key()
        assert callable(uc_create_api_key._api_key_repo_factory)
        assert isinstance(uc_create_api_key._api_key_repo_factory, type)

        uc_create_tenant = container.use_cases.create_tenant()
        assert callable(uc_create_tenant._tenant_repo_factory)
        assert isinstance(uc_create_tenant._tenant_repo_factory, type)

    def test_repo_factories_produce_repository_instances(
        self, container: ApplicationContainer
    ) -> None:
        session = "mock"
        uc_login = container.use_cases.login()
        repo_login = uc_login._user_repo_factory(session=session)
        assert hasattr(repo_login, "get_by_email")
        assert hasattr(repo_login, "create")

        uc_create_api_key = container.use_cases.create_api_key()
        repo_api_key = uc_create_api_key._api_key_repo_factory(session=session)
        assert hasattr(repo_api_key, "create")

        uc_create_tenant = container.use_cases.create_tenant()
        repo_tenant = uc_create_tenant._tenant_repo_factory(session=session)
        assert hasattr(repo_tenant, "get_by_slug")
        assert hasattr(repo_tenant, "create")