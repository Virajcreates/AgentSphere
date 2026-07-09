import structlog

from agentsphere.config.logging import setup_logging

logger = structlog.get_logger(__name__)


def configure_logging(log_level: str = "INFO") -> None:
    setup_logging(log_level)
