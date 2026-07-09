import uuid
from collections.abc import Callable
from datetime import datetime
from typing import Any

import structlog

from agentsphere.application.ports.event_bus import EventBus
from agentsphere.application.ports.repositories import ConversationRepositoryProtocol
from agentsphere.application.services.summarization_service import SummarizationService
from agentsphere.runtime.exceptions.base import PolicyLimitViolationError

logger = structlog.get_logger(__name__)


class ConversationService:
    def __init__(
        self,
        db: Any,
        conversation_repo_factory: Callable[..., ConversationRepositoryProtocol],
        summarization_service: SummarizationService,
        event_bus: EventBus,
    ) -> None:
        self._db = db
        self._repo_factory = conversation_repo_factory
        self._summarizer = summarization_service
        self._event_bus = event_bus

        # Default Active conversation policy bounds
        self.max_turns_policy: int = 20
        self.summary_turns_threshold: int = 5
        self.idle_timeout_policy: int = 3600  # seconds (1 hour)
        self.token_budget_policy: int = 50000  # max allowable tokens per request

    async def create_conversation(
        self, tenant_id: uuid.UUID, metadata: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        """Creates a new stateful conversation thread within an isolated transaction session."""
        logger.info("Initializing Conversation Thread", tenant_id=str(tenant_id))
        async with self._db.get_session() as session:
            repo = self._repo_factory(session=session)
            return await repo.create(
                tenant_id=tenant_id,
                status="active",
                meta_info=metadata or {},
                turns_count=0,
            )

    async def add_message(
        self, conversation_id: uuid.UUID, role: str, content: str
    ) -> dict[str, Any]:
        """Appends a new turn message onto the conversation thread, evaluating policies, and

        triggering automatic LLM summaries on threshold triggers.
        """
        async with self._db.get_session() as session:
            repo = self._repo_factory(session=session)

            # 1. Fetch current conversation state
            conv = await repo.get(conversation_id)
            if not conv:
                raise ValueError(f"Conversation with id '{conversation_id}' not found")

            # 2. Evaluate Idle Timeout policy
            last_message_time = conv.get("created_at")
            messages = await repo.get_messages(conversation_id)
            if messages:
                last_message_time = messages[-1]["created_at"]

            if last_message_time:
                now = datetime.now(last_message_time.tzinfo) if last_message_time.tzinfo else datetime.now()
                elapsed_sec = (now - last_message_time).total_seconds()
                if elapsed_sec > self.idle_timeout_policy:
                    # Thread has expired due to idle timeout
                    await repo.update(conversation_id, status="expired")
                    raise PolicyLimitViolationError(
                        limit_name="idle_timeout",
                        allowed=self.idle_timeout_policy,
                        actual=elapsed_sec,
                    )

            # 3. Evaluate Maximum Turns policy
            current_turns = conv["turns_count"]
            if current_turns >= self.max_turns_policy:
                raise PolicyLimitViolationError(
                    limit_name="max_turns_policy",
                    allowed=self.max_turns_policy,
                    actual=current_turns,
                )

            # 4. Evaluate Token Budget policy (coarse heuristic)
            estimated_tokens = int(len(content) / 3.8)
            if estimated_tokens > self.token_budget_policy:
                raise PolicyLimitViolationError(
                    limit_name="token_budget_policy",
                    allowed=self.token_budget_policy,
                    actual=estimated_tokens,
                )

            # 5. Insert raw message
            msg = await repo.add_message(conversation_id, role, content)

            # 6. Update Turns Count
            new_turns = current_turns + 1
            await repo.update(conversation_id, turns_count=new_turns)

            # 7. Check Summarization threshold limits
            if new_turns >= self.summary_turns_threshold:
                logger.info(
                    "Summary Turns limit triggered. Generating dynamic LLM summary",
                    conv_id=str(conversation_id),
                )
                all_messages = await repo.get_messages(conversation_id)

                try:
                    formatted_msgs = [{"role": m["role"], "content": m["content"]} for m in all_messages]
                    summary_text = await self._summarizer.summarize_history(formatted_msgs)
                    await repo.add_summary(conversation_id, summary_text)
                    logger.info("Automatic Conversation Summary Saved", conv_id=str(conversation_id))
                except Exception as e:
                    logger.error("Failed to generate automatic summary", error=str(e))

            return msg

    async def get_history(self, conversation_id: uuid.UUID) -> list[dict[str, Any]]:
        """Returns the full sequence of raw messages history for the requested conversation."""
        async with self._db.get_session() as session:
            repo = self._repo_factory(session=session)
            return await repo.get_messages(conversation_id)

    async def get_latest_summary(self, conversation_id: uuid.UUID) -> dict[str, Any] | None:
        """Retrieves the latest compiled LLM conversation summary snapshot."""
        async with self._db.get_session() as session:
            repo = self._repo_factory(session=session)
            return await repo.get_latest_summary(conversation_id)
