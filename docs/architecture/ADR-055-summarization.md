# ADR-055: Summarization

## Status
Accepted

## Context
Long-running conversation threads quickly consume LLM context window boundaries. Passing entire message loops on every turn increases latencies, drastically elevates costs, and dilutes the model's focus on immediate objectives.

## Decision
We implement a highly reliable dynamic summarization flow:
* **`SummarizationService` Interface:** Exposed public service wrapper that converts raw conversational histories into condensed text summaries using AI Gateway complete calls.
* **Automatic Summary Triggers:** When message turn lists cross `summary_turns_threshold` limits (e.g. 5, 10, etc.), the conversation manager dynamically triggers summarization and saves the snapshot into `ConversationSummaryModel`.
* **Complete History Retention:** The raw historical message array remains completely untouched in the database, allowing subsequent evaluations or analysis pipelines to parse exact traces if necessary.

## Consequences
* **Pros:** Minimizes prompt latencies and expenditures, protects window bounds, and retains raw historical audit logs.
* **Cons:** Introduces moderate LLM complete latency during summary-generation intervals.
