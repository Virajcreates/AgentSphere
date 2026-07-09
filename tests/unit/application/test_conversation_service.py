from datetime import datetime, timedelta
from typing import Any
import uuid
from unittest.mock import AsyncMock, MagicMock
import pytest

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.application.services.conversation_service import ConversationService
from agentsphere.application.services.summarization_service import SummarizationService
from agentsphere.infrastructure.persistence.repositories.conversation_repository import ConversationRepository
from agentsphere.runtime.exceptions.base import PolicyLimitViolationError


class FakeSession:
    async def __aenter__(self):
        return self

    async def __aexit__(self, *args):
        pass


@pytest.fixture
def mock_repo() -> ConversationRepository:
    repo = MagicMock(spec=ConversationRepository)
    # mock conversation fetch
    mock_conv = {
        "id": uuid.uuid4(),
        "tenant_id": uuid.uuid4(),
        "status": "active",
        "turns_count": 4,  # close to summary_turns_threshold
        "created_at": datetime.now(),
    }
    repo.get = AsyncMock(return_value=mock_conv)
    repo.get_messages = AsyncMock(return_value=[])
    repo.add_message = AsyncMock(return_value={"id": uuid.uuid4()})
    repo.add_summary = AsyncMock(return_value={"id": uuid.uuid4()})
    repo.update = AsyncMock()
    return repo


@pytest.fixture
def mock_summarizer() -> SummarizationService:
    service = MagicMock(spec=SummarizationService)
    service.summarize_history = AsyncMock(return_value="Mock summary text.")
    return service


@pytest.fixture
def mock_db() -> Any:
    db = MagicMock()
    db.get_session = MagicMock(return_value=FakeSession())
    return db


@pytest.mark.asyncio
async def test_conversation_service_evaluates_turn_policy_and_triggers_summary(
    mock_db: Any, mock_repo: ConversationRepository, mock_summarizer: SummarizationService
) -> None:
    event_bus = MagicMock(spec=EventBus)
    service = ConversationService(
        db=mock_db,
        conversation_repo_factory=MagicMock(return_value=mock_repo),
        summarization_service=mock_summarizer,
        event_bus=event_bus,
    )

    # 1. Standard message adding with turn count = 4
    # We configure summary_turns_threshold = 5.
    # Appending another message brings turns_count to 5, which must trigger automatic summarization!
    service.summary_turns_threshold = 5

    id_uuid = uuid.uuid4()
    msg = await service.add_message(
        conversation_id=id_uuid,
        role="user",
        content="Hello, please trigger summary",
    )

    assert msg is not None
    # Verify that updater was called to increment turns_count
    mock_repo.update.assert_any_call(id_uuid, turns_count=5)
    # Verify that LLM automatic summarizer was executed!
    mock_summarizer.summarize_history.assert_called_once()
    mock_repo.add_summary.assert_called_once_with(id_uuid, "Mock summary text.")


@pytest.mark.asyncio
async def test_conversation_service_max_turns_policy(
    mock_db: Any, mock_repo: ConversationRepository, mock_summarizer: SummarizationService
) -> None:
    event_bus = MagicMock(spec=EventBus)
    service = ConversationService(
        db=mock_db,
        conversation_repo_factory=MagicMock(return_value=mock_repo),
        summarization_service=mock_summarizer,
        event_bus=event_bus,
    )

    # Set turn limit strictly to 2
    service.max_turns_policy = 2
    # mock repo to say we have already run 3 turns!
    mock_repo.get = AsyncMock(return_value={
        "id": uuid.uuid4(),
        "status": "active",
        "turns_count": 3,
        "created_at": datetime.now(),
    })

    with pytest.raises(PolicyLimitViolationError) as exc:
        await service.add_message(uuid.uuid4(), "user", "help")
    assert "max_turns_policy" in str(exc.value)


@pytest.mark.asyncio
async def test_conversation_service_idle_timeout(
    mock_db: Any, mock_repo: ConversationRepository, mock_summarizer: SummarizationService
) -> None:
    event_bus = MagicMock(spec=EventBus)
    service = ConversationService(
        db=mock_db,
        conversation_repo_factory=MagicMock(return_value=mock_repo),
        summarization_service=mock_summarizer,
        event_bus=event_bus,
    )

    # Set idle policy limit of 10s
    service.idle_timeout_policy = 10
    # prev message was 1 hour ago!
    previous_time = datetime.now() - timedelta(hours=1)
    mock_repo.get_messages = AsyncMock(return_value=[
        {"role": "user", "content": "hi", "created_at": previous_time}
    ])

    with pytest.raises(PolicyLimitViolationError) as exc:
        await service.add_message(uuid.uuid4(), "user", "are you there")
    assert "idle_timeout" in str(exc.value)
