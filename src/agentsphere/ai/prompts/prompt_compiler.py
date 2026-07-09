import re
from datetime import datetime
from typing import Any

from agentsphere.ai.exceptions.refinement_exceptions import PromptCompilationError
from agentsphere.ai.prompts.prompt_manager import PromptManager


class PromptCompiler:
    def __init__(self, prompt_manager: PromptManager) -> None:
        self._manager = prompt_manager
        # In-memory compile caching: (tenant_id, namespace, name, hash_of_variables) -> rendered_str
        self._compile_cache: dict[tuple[str | None, str, str, int], str] = {}

    def compile(
        self,
        namespace: str,
        name: str,
        variables: dict[str, Any],
        tenant_id: str | None = None,
        version: str = "latest",
        bypass_cache: bool = False,
    ) -> str:
        """Fully compiles a prompt template by recursively resolving includes, processing macros,

        validating variables, and performing final parameter expansions.
        """
        # 1. Establish cache key
        # We freeze the variables to create a unique hash key
        var_hash = hash(frozenset((k, str(v)) for k, v in variables.items()))
        cache_key = (tenant_id, namespace.lower(), name.lower(), var_hash)

        if not bypass_cache and cache_key in self._compile_cache:
            return self._compile_cache[cache_key]

        # 2. Get base template
        try:
            template = self._manager.get_template(namespace, name, tenant_id, version)
        except Exception as e:
            raise PromptCompilationError(f"Base template not found: {e!s}") from e

        # 3. Recursively resolve imports / includes
        # Matches: {{ include "namespace.name" }} or {{ include 'namespace.name' }}
        template = self._resolve_includes(template, tenant_id, version)

        # 4. Process macros (dynamic runtime placeholders)
        template = self._process_macros(template)

        # 5. Validate variables against compiled template
        try:
            self._manager.validate_variables(template, variables)
        except Exception as e:
            raise PromptCompilationError(f"Variables validation failed: {e!s}") from e

        # 6. Perform final variable replacement
        rendered = template
        for var_name, var_val in variables.items():
            pattern = r"\{\{\s*" + re.escape(var_name) + r"\s*\}\}"
            rendered = re.sub(pattern, str(var_val), rendered)

        # 7. Store in compile cache
        self._compile_cache[cache_key] = rendered

        return rendered

    def _resolve_includes(
        self, template: str, tenant_id: str | None, version: str, depth: int = 0
    ) -> str:
        if depth > 10:
            raise PromptCompilationError(
                "Circular or too deep nested imports detected in templates"
            )

        pattern = r"\{\{\s*include\s+[\"\']([a-zA-Z0-9_\-]+)\.([a-zA-Z0-9_\-]+)[\"\']\s*\}\}"

        def replace_include(match: re.Match[str]) -> str:
            inc_namespace = match.group(1)
            inc_name = match.group(2)
            try:
                inc_template = self._manager.get_template(
                    inc_namespace, inc_name, tenant_id, version
                )
                # Recursively resolve any includes inside the imported template
                return self._resolve_includes(inc_template, tenant_id, version, depth + 1)
            except Exception as e:
                raise PromptCompilationError(
                    f"Failed to resolve include '{inc_namespace}.{inc_name}': {e!s}"
                ) from e

        return re.sub(pattern, replace_include, template)

    def _process_macros(self, template: str) -> str:
        # Standard macros: {{ current_date }}, {{ current_year }}, {{ current_iso }}
        now = datetime.now()

        # {{ current_date }} -> YYYY-MM-DD
        template = re.sub(r"\{\{\s*current_date\s*\}\}", now.strftime("%Y-%m-%d"), template)

        # {{ current_year }} -> YYYY
        template = re.sub(r"\{\{\s*current_year\s*\}\}", now.strftime("%Y"), template)

        # {{ current_iso }} -> ISO timestamp
        template = re.sub(r"\{\{\s*current_iso\s*\}\}", now.isoformat(), template)

        return template
