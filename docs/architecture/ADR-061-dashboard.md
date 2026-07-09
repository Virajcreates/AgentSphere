# ADR-061: Dashboard

## Status
Accepted

## Context
Operators need an instantaneous system status summary: total spent budgets, latency overviews, circuit breakers alerts, and active threads volume. Lacking a centralized panel slows down operational incident response.

## Decision
We implement a highly polished **Operations Dashboard**:
* **High-Impact Widgets Grid:** Plots active thread indices, accumulated token totals, expenditure USD charts, and Average latencies side-by-side.
* **Live Benchmarking rankings:** Automatically lists performance profiles (health ratios, retry frequencies) dynamically calculated by telemeters.
* **Time-Series Charts:** Renders responsive Tailwind bar charts representing weekly cumulative processing metrics.

## Consequences
* **Pros:** Complete operational observability, fast incident diagnostics, and clean layout patterns.
* **Cons:** High numbers of live queries can put burden on metrics databases (resolved using polling caches).
