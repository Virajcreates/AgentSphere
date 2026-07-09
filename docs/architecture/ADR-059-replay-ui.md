# ADR-059: Replay UI

## Status
Accepted

## Context
Debugging multi-agent loops is exceptionally difficult. Complex, parallel, or nested steps fail asynchronously. Plain log files are too dense for rapid analysis, and direct thread checking causes race conditions.

## Decision
We implement a highly polished **Replay UI** panel:
* **Interactive Timelines:** Renders a sequential timeline on the left mapping step names, total latency offsets, run attempts counts, and final result/error statuses.
* **React Flow DAG Visualizations:** Builds interactive node dependency graph graphs on the right using React Flow (xyflow), letting engineers see graph dependencies and failures on map paths.
* **Tabbed Details Inspector:** Groups retrieved chunks (Source Attributions), raw parameters, and JSON payloads into tab controllers.

## Consequences
* **Pros:** Unbelievable debugging speed, clear tracing of hallucinations via source links, and clear visibility of loop depths.
* **Cons:** Slicing highly complex multi-stage graphs requires efficient canvas scaling.
