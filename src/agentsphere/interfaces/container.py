from dependency_injector import containers, providers

from agentsphere.ai.core.inference import AIInferenceService
from agentsphere.ai.core.policy_engine import AIPolicyEngine
from agentsphere.ai.core.semantic_cache import InMemorySemanticAICache
from agentsphere.ai.cost.cost_tracker import CostTracker
from agentsphere.ai.cost.quota_manager import QuotaManager
from agentsphere.ai.executor.executor import MockExecutor
from agentsphere.ai.gateway.ai_gateway import AIGateway
from agentsphere.ai.gateway.circuit_breaker import CircuitBreaker
from agentsphere.ai.gateway.retry_policy import RetryPolicy
from agentsphere.ai.memory.memory import MockConversationMemory, MockMemoryStore
from agentsphere.ai.planner.planner import MockPlanner
from agentsphere.ai.prompts.prompt_compiler import PromptCompiler
from agentsphere.ai.prompts.prompt_manager import PromptManager
from agentsphere.ai.providers.anthropic import AnthropicProvider
from agentsphere.ai.providers.azure_openai import AzureOpenAIProvider
from agentsphere.ai.providers.gemini import GeminiProvider
from agentsphere.ai.providers.groq import GroqProvider
from agentsphere.ai.providers.nvidia import NvidiaProvider
from agentsphere.ai.providers.ollama import OllamaProvider
from agentsphere.ai.providers.openai import OpenAIProvider
from agentsphere.ai.providers.openrouter import OpenRouterProvider
from agentsphere.ai.registry.capability_negotiator import CapabilityNegotiator
from agentsphere.ai.registry.model_registry import ModelRegistry
from agentsphere.ai.telemetry.benchmarking import ProviderBenchmarkCollector
from agentsphere.ai.telemetry.lineage import PromptLineageTracker
from agentsphere.ai.telemetry.tracker import TelemetryTracker
from agentsphere.ai.tokenizer.token_counter import TokenCounter
from agentsphere.application.services.conversation_service import ConversationService
from agentsphere.application.services.embedding_service import EmbeddingService
from agentsphere.application.services.knowledge_service import KnowledgeService
from agentsphere.application.services.retriever_service import RetrieverService
from agentsphere.application.services.summarization_service import SummarizationService
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
from agentsphere.infrastructure.event_bus.in_memory_event_bus import InMemoryEventBus
from agentsphere.infrastructure.persistence.repositories.api_key_repository import ApiKeyRepository
from agentsphere.infrastructure.persistence.repositories.conversation_repository import (
    ConversationRepository,
)
from agentsphere.infrastructure.persistence.repositories.knowledge_repository import (
    KnowledgeRepository,
)
from agentsphere.infrastructure.persistence.repositories.tenant_repository import TenantRepository
from agentsphere.infrastructure.persistence.repositories.user_repository import UserRepository
from agentsphere.infrastructure.rag.parsing.document_parser import DocumentParser
from agentsphere.interfaces.adapters.langgraph.adapter import LangGraphAdapter
from agentsphere.interfaces.adapters.langgraph.nodes import LangGraphNodes
from agentsphere.runtime.agent.agent_runtime import AgentRuntime
from agentsphere.runtime.checkpoint.in_memory_store import InMemoryCheckpointStore
from agentsphere.runtime.conversation.conversation_manager import ConversationManager
from agentsphere.runtime.executor.execution_engine import ExecutionEngine
from agentsphere.runtime.memory.memory_manager import MemoryManager
from agentsphere.runtime.planner.planner import RuntimePlanner
from agentsphere.runtime.policies.policies import RuntimePolicyEvaluator
from agentsphere.runtime.serialization.serializer import RuntimeSerializer
from agentsphere.runtime.telemetry.tracker import RuntimeTracker
from agentsphere.runtime.tools.tool_framework import ToolExecutor, ToolRegistry


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


class AIContainer(containers.DeclarativeContainer):
    model_registry = providers.Singleton(ModelRegistry)
    prompt_manager = providers.Singleton(PromptManager)
    token_counter = providers.Singleton(TokenCounter)
    cost_tracker = providers.Singleton(CostTracker, model_registry=model_registry)
    telemetry_tracker = providers.Singleton(TelemetryTracker)
    circuit_breaker = providers.Singleton(CircuitBreaker)
    retry_policy = providers.Singleton(RetryPolicy)

    # Refinements Singletons
    capability_negotiator = providers.Singleton(
        CapabilityNegotiator, model_registry=model_registry
    )
    prompt_compiler = providers.Singleton(PromptCompiler, prompt_manager=prompt_manager)
    policy_engine = providers.Singleton(AIPolicyEngine, model_registry=model_registry)
    quota_manager = providers.Singleton(QuotaManager)
    semantic_cache = providers.Singleton(InMemorySemanticAICache)
    benchmark_collector = providers.Singleton(ProviderBenchmarkCollector)
    lineage_tracker = providers.Singleton(PromptLineageTracker)

    # Providers (as factories)
    openai_provider = providers.Factory(OpenAIProvider)
    gemini_provider = providers.Factory(GeminiProvider)
    anthropic_provider = providers.Factory(AnthropicProvider)
    openrouter_provider = providers.Factory(OpenRouterProvider)
    groq_provider = providers.Factory(GroqProvider)
    azure_openai_provider = providers.Factory(AzureOpenAIProvider)
    ollama_provider = providers.Factory(OllamaProvider)
    nvidia_provider = providers.Factory(NvidiaProvider)

    # Placeholders
    planner = providers.Singleton(MockPlanner)
    executor = providers.Singleton(MockExecutor)
    memory_store = providers.Singleton(MockMemoryStore)
    conversation_memory = providers.Singleton(MockConversationMemory)

    # Gateway
    gateway = providers.Singleton(
        AIGateway,
        model_registry=model_registry,
        circuit_breaker=circuit_breaker,
        retry_policy=retry_policy,
        telemetry_tracker=telemetry_tracker,
        cost_tracker=cost_tracker,
        llm_providers=providers.Dict(
            openai=openai_provider,
            gemini=gemini_provider,
            anthropic=anthropic_provider,
            openrouter=openrouter_provider,
            groq=groq_provider,
            azure_openai=azure_openai_provider,
            ollama=ollama_provider,
            nvidia=nvidia_provider,
        ),
        embedding_providers=providers.Dict(
            openai=openai_provider,
            gemini=gemini_provider,
            azure_openai=azure_openai_provider,
            ollama=ollama_provider,
            nvidia=nvidia_provider,
        ),
        benchmark_collector=benchmark_collector,
    )

    # Inference Service
    inference = providers.Singleton(
        AIInferenceService,
        prompt_manager=prompt_manager,
        gateway=gateway,
        model_registry=model_registry,
        token_counter=token_counter,
        prompt_compiler=prompt_compiler,
        policy_engine=policy_engine,
        quota_manager=quota_manager,
        cache=semantic_cache,
        lineage_tracker=lineage_tracker,
        capability_negotiator=capability_negotiator,
    )


class RuntimeContainer(containers.DeclarativeContainer):
    core = providers.DependenciesContainer()
    ai = providers.DependenciesContainer()

    # Core event bus shared across components
    event_bus = providers.Singleton(InMemoryEventBus)

    # Core repositories
    conversation_repo_factory = providers.Factory(ConversationRepository)
    knowledge_repo_factory = providers.Factory(KnowledgeRepository)

    # Core singletons
    conversation_manager = providers.Singleton(ConversationManager, event_bus=event_bus)
    planner = providers.Singleton(RuntimePlanner)
    execution_engine = providers.Singleton(ExecutionEngine, event_bus=event_bus)
    tool_registry = providers.Singleton(ToolRegistry)
    tool_executor = providers.Singleton(ToolExecutor, registry=tool_registry, event_bus=event_bus)
    memory_manager = providers.Singleton(MemoryManager, event_bus=event_bus)
    policy_evaluator = providers.Singleton(RuntimePolicyEvaluator)
    tracker = providers.Singleton(RuntimeTracker)
    serializer = providers.Singleton(RuntimeSerializer)
    checkpoint_store = providers.Singleton(InMemoryCheckpointStore)

    # Document Pipeline
    document_parser = providers.Singleton(DocumentParser)

    # Core Public Services (Encapsulating subsystems as per structural requirements)
    embedding_service = providers.Singleton(EmbeddingService, gateway=ai.gateway)
    summarization_service = providers.Singleton(SummarizationService, gateway=ai.gateway)
    retriever_service = providers.Singleton(
        RetrieverService,
        db=core.db,
        knowledge_repo_factory=knowledge_repo_factory,
        embedding_service=embedding_service,
        event_bus=event_bus,
    )
    conversation_service = providers.Singleton(
        ConversationService,
        db=core.db,
        conversation_repo_factory=conversation_repo_factory,
        summarization_service=summarization_service,
        event_bus=event_bus,
    )
    knowledge_service = providers.Singleton(
        KnowledgeService,
        db=core.db,
        knowledge_repo_factory=knowledge_repo_factory,
        embedding_service=embedding_service,
        document_parser=document_parser,
    )

    # LangGraph Adapters
    langgraph_nodes = providers.Singleton(
        LangGraphNodes,
        inference_service=ai.inference,
        retriever_service=retriever_service,
        tool_executor=tool_executor,
        memory_manager=memory_manager,
    )
    langgraph_adapter = providers.Singleton(
        LangGraphAdapter,
        nodes=langgraph_nodes,
    )

    # Core Agent Runtime Orchestrator
    agent_runtime = providers.Singleton(
        AgentRuntime,
        event_bus=event_bus,
        conversation_manager=conversation_manager,
        planner=planner,
        execution_engine=execution_engine,
        tool_executor=tool_executor,
        memory_manager=memory_manager,
        policy_evaluator=policy_evaluator,
        tracker=tracker,
        serializer=serializer,
        checkpoint_store=checkpoint_store,
    )


class ApplicationContainer(containers.DeclarativeContainer):
    core = providers.Container(CoreContainer)
    auth = providers.Container(AuthContainer, core=core)
    use_cases = providers.Container(UseCasesContainer, core=core, auth=auth)
    ai = providers.Container(AIContainer)
    runtime = providers.Container(RuntimeContainer, ai=ai, core=core)


_container: ApplicationContainer | None = None


def init_container() -> ApplicationContainer:
    global _container
    _container = ApplicationContainer()
    return _container


def get_container() -> ApplicationContainer:
    if _container is None:
        raise RuntimeError("Container not initialized")
    return _container
