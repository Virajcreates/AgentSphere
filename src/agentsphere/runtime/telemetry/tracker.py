import structlog
from prometheus_client import Counter, Histogram

logger = structlog.get_logger(__name__)

# Prometheus metrics for Agent Runtime Performance tracking
PLANNING_LATENCY = Histogram(
    "runtime_planning_latency_seconds",
    "Time taken to compile execution graphs in seconds",
)
EXECUTION_LATENCY = Histogram(
    "runtime_execution_latency_seconds",
    "Time taken to traverse and execute execution graphs",
)
TOOL_EXEC_DURATION = Histogram(
    "runtime_tool_execution_seconds",
    "Time taken per individual tool call in seconds",
    ["tool_name"],
)
MEMORY_OPS = Counter(
    "runtime_memory_operations_total",
    "Total count of memory reads, writes, and clearing snapshots",
    ["operation_type"],  # e.g. read, write, clear
)
RETRY_COUNT = Counter(
    "runtime_step_retries_total",
    "Total step retry operations performed under RecoveryPolicy constraints",
)
CANCELLATIONS = Counter(
    "runtime_cancellations_total",
    "Total task cancellation events registered",
)
EXECUTION_STATS = Counter(
    "runtime_execution_status_total",
    "Total count of execution sessions compiled",
    ["status"],  # success, failure
)


class RuntimeTracker:
    def track_planning(self, latency: float) -> None:
        PLANNING_LATENCY.observe(latency)
        logger.info("Telemetry Track Planning Complete", latency=latency)

    def track_execution(self, latency: float, success: bool) -> None:
        EXECUTION_LATENCY.observe(latency)
        status = "success" if success else "failure"
        EXECUTION_STATS.labels(status=status).inc()
        logger.info("Telemetry Track Execution Complete", latency=latency, success=success)

    def track_tool(self, tool_name: str, duration: float) -> None:
        TOOL_EXEC_DURATION.labels(tool_name=tool_name).observe(duration)
        logger.info("Telemetry Track Tool Complete", tool_name=tool_name, duration=duration)

    def track_memory_op(self, op: str) -> None:
        MEMORY_OPS.labels(operation_type=op).inc()

    def track_retry(self) -> None:
        RETRY_COUNT.inc()

    def track_cancellation(self) -> None:
        CANCELLATIONS.inc()
