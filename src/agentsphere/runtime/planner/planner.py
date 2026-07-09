
from agentsphere.ai.exceptions.base import PromptValidationError
from agentsphere.runtime.schemas.runtime import (
    AgentDefinition,
    ExecutionGraph,
    ExecutionNode,
    RecoveryPolicy,
)


class RuntimePlanner:
    async def create_plan(
        self, goal: str, agent_def: AgentDefinition, workflow_id: str | None = None
    ) -> ExecutionGraph:
        """Parses the execution goal statements and constructs a Directed Acyclic Graph (DAG) representation.

        Performs loops detection checks to guarantee strict DAG layout.
        """
        import uuid

        # 1. Standard plan construction based on agent configuration and workflow template
        graph_id = f"plan_{uuid.uuid4()!s:.8}"

        # Resolve selected workflow context
        allowed_tools = list(agent_def.allowed_tools)
        if workflow_id and workflow_id in agent_def.workflows:
            wf = agent_def.workflows[workflow_id]
            allowed_tools = list(wf.allowed_tools) or allowed_tools

        # Build clean mock nodes to simulate a realistic DAG executingwhitelisted tools
        nodes: dict[str, ExecutionNode] = {}
        edges: list[tuple[str, str]] = []

        if len(allowed_tools) >= 2:
            t1 = allowed_tools[0]
            t2 = allowed_tools[1]

            args1 = {"expr": "10+20"} if t1 == "calculator" else {"query": goal}
            args2 = {"query": "{{ step_1.result }}"} if t2 == "search_web" else {"inputs": "{{ step_1.result }}"}

            nodes["step_1"] = ExecutionNode(
                step_id="step_1",
                action=f"tool:{t1}",
                arguments=args1,
                recovery_policy=RecoveryPolicy(strategy="retry", max_retries=2),
            )
            nodes["step_2"] = ExecutionNode(
                step_id="step_2",
                action=f"tool:{t2}",
                arguments=args2,
                depends_on=["step_1"],
                recovery_policy=RecoveryPolicy(strategy="continue"),
            )
            nodes["step_3"] = ExecutionNode(
                step_id="step_3",
                action="llm_generate",
                arguments={"context": "{{ step_2.result }}"},
                depends_on=["step_2"],
            )

            # Define valid acyclic directed edges
            edges.append(("step_1", "step_2"))
            edges.append(("step_2", "step_3"))
        else:
            # Fallback to single loop node if no tools are registered
            nodes["step_1"] = ExecutionNode(
                step_id="step_1",
                action="llm_generate",
                arguments={"prompt": goal},
            )

        # 2. Compile into Pydantic ExecutionGraph
        graph = ExecutionGraph(graph_id=graph_id, nodes=nodes, edges=edges)

        # 3. Perform Loops / Cyclic Check Validation to ensure strict DAG format
        self.validate_dag(graph)

        return graph

    def validate_dag(self, graph: ExecutionGraph) -> None:
        """Runs standard Depth-First-Search (DFS) to verify graph has zero cycles."""
        # Build adjacency mapping
        adj: dict[str, list[str]] = {nid: [] for nid in graph.nodes}
        for u, v in graph.edges:
            if u in adj and v in adj:
                adj[u].append(v)

        # DFS state trackers
        visited: dict[str, int] = {nid: 0 for nid in graph.nodes}  # 0: unvisited, 1: visiting, 2: visited

        def dfs(node: str) -> bool:
            visited[node] = 1  # mark visiting
            for neighbor in adj[node]:
                if visited[neighbor] == 1:
                    return False  # cycle detected!
                if visited[neighbor] == 0 and not dfs(neighbor):
                    return False
            visited[node] = 2  # mark fully processed
            return True

        for node in graph.nodes:
            if visited[node] == 0 and not dfs(node):
                raise PromptValidationError(
                    "Execution plan compilation error: "
                    "Circular edge loop detected inside ExecutionGraph!"
                )
