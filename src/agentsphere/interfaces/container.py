from dependency_injector import containers, providers

from agentsphere.application.use_cases.auth.create_api_key import CreateApiKeyUseCase
from agentsphere.application.use_cases.auth.login import LoginUseCase
from agentsphere.application.use_cases.auth.refresh_token import RefreshTokenUseCase
from agentsphere.application.use_cases.auth.revoke_api_key import RevokeApiKeyUseCase
from agentsphere.application.use_cases.tenant.create_tenant import CreateTenantUseCase
from agentsphere.application.use_cases.tenant.get_tenant import GetTenantUseCase
from agentsphere.application.use_cases.tenant.update_tenant import UpdateTenantUseCase
from agentsphere.config.database import DatabaseManager
from agentsphere.config.redis import RedisManager
from agentsphere.config.settings import Settings
from agentsphere.infrastructure.auth.api_key_handler import APIKeyHandler
from agentsphere.infrastructure.auth.jwt_handler import JWTHandler
from agentsphere.infrastructure.auth.password_hasher import PasswordHasher
from agentsphere.infrastructure.persistence.repositories.api_key_repository import ApiKeyRepository
from agentsphere.infrastructure.persistence.repositories.tenant_repository import TenantRepository
from agentsphere.infrastructure.persistence.repositories.user_repository import UserRepository


class CoreContainer(containers.DeclarativeContainer):
    settings = providers.Singleton(Settings)
    db = providers.Singleton(DatabaseManager)
    redis = providers.Singleton(RedisManager)


class AuthContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()

    password_hasher = providers.Singleton(PasswordHasher)
    jwt_handler = providers.Factory(JWTHandler, settings=core.settings)
    api_key_handler = providers.Factory(
        APIKeyHandler,
        prefix=core.settings.provided.API_KEY_PREFIX,
        password_hasher=password_hasher,
    )


class UseCasesContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    auth = providers.DependenciesContainer()

    login = providers.Factory(
        LoginUseCase,
        db=core.db,
        user_repo_factory=UserRepository,
        jwt_handler=auth.jwt_handler,
        password_hasher=auth.password_hasher,
    )
    refresh_token = providers.Factory(
        RefreshTokenUseCase,
        jwt_handler=auth.jwt_handler,
    )
    create_api_key = providers.Factory(
        CreateApiKeyUseCase,
        db=core.db,
        api_key_repo_factory=ApiKeyRepository,
        api_key_handler=auth.api_key_handler,
    )
    revoke_api_key = providers.Factory(
        RevokeApiKeyUseCase,
        db=core.db,
        api_key_repo_factory=ApiKeyRepository,
    )
    create_tenant = providers.Factory(
        CreateTenantUseCase,
        db=core.db,
        tenant_repo_factory=TenantRepository,
    )
    get_tenant = providers.Factory(
        GetTenantUseCase,
        db=core.db,
        tenant_repo_factory=TenantRepository,
    )
    update_tenant = providers.Factory(
        UpdateTenantUseCase,
        db=core.db,
        tenant_repo_factory=TenantRepository,
    )


class ApplicationContainer(containers.DeclarativeContainer):
    core = providers.Container(CoreContainer)
    auth = providers.Container(AuthContainer, core=core)
    use_cases = providers.Container(UseCasesContainer, core=core, auth=auth)


_container: ApplicationContainer | None = None


def init_container() -> ApplicationContainer:
    global _container
    _container = ApplicationContainer()
    return _container


def get_container() -> ApplicationContainer:
    if _container is None:
        raise RuntimeError("Container not initialized")
    return _container
