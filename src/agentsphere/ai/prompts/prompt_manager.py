import re
from typing import Any

from agentsphere.ai.exceptions.base import PromptValidationError


class PromptManager:
    def __init__(self) -> None:
        # System defaults: (namespace, template_name, version) -> template_str
        self._system_templates: dict[tuple[str, str, str], str] = {}
        # Tenant overrides: (tenant_id, namespace, template_name) -> template_str
        self._tenant_templates: dict[tuple[str, str, str], str] = {}

    def register_system_template(
        self, namespace: str, name: str, template: str, version: str = "latest"
    ) -> None:
        key = (namespace.lower(), name.lower(), version.lower())
        self._system_templates[key] = template
        # If registering a specific version, also set it as 'latest' if 'latest' isn't set
        if version != "latest":
            latest_key = (namespace.lower(), name.lower(), "latest")
            if latest_key not in self._system_templates:
                self._system_templates[latest_key] = template

    def register_tenant_template(
        self, tenant_id: str, namespace: str, name: str, template: str
    ) -> None:
        key = (tenant_id.lower(), namespace.lower(), name.lower())
        self._tenant_templates[key] = template

    def get_template(
        self,
        namespace: str,
        name: str,
        tenant_id: str | None = None,
        version: str = "latest",
    ) -> str:
        ns = namespace.lower()
        nm = name.lower()
        ver = version.lower()

        # Check tenant override first
        if tenant_id:
            t_key = (tenant_id.lower(), ns, nm)
            if t_key in self._tenant_templates:
                return self._tenant_templates[t_key]

        # Check system default
        s_key = (ns, nm, ver)
        if s_key not in self._system_templates:
            raise PromptValidationError(
                f"Prompt template '{name}' in namespace '{namespace}' "
                f"(version: {version}) not found"
            )
        return self._system_templates[s_key]

    def validate_variables(self, template: str, variables: dict[str, Any]) -> None:
        # Check template syntax for unclosed/mismatched curly braces
        open_count = template.count("{{")
        close_count = template.count("}}")
        if open_count != close_count:
            raise PromptValidationError(
                f"Mismatched curly braces in template. "
                f"Open '{{{{': {open_count}, Close '}}}}': {close_count}"
            )

        # Extract variables from template using regex
        # Finds any variable pattern inside double braces {{variable_name}}
        placeholders = set(re.findall(r"\{\{\s*([a-zA-Z_][a-zA-Z0-9_]*)\s*\}\}", template))

        # Check for missing variables
        provided_vars = set(variables.keys())
        missing = placeholders - provided_vars
        if missing:
            raise PromptValidationError(
                f"Missing required placeholders in prompt variables: {', '.join(missing)}"
            )

        # Check for unused variables (warning or error)
        unused = provided_vars - placeholders
        if unused:
            # We can log or warn. Let's warn but not raise, or raise only if requested.
            # For strictness we can log or raise. Let's allow unused variables but track them.
            pass

    def render(
        self,
        namespace: str,
        name: str,
        variables: dict[str, Any],
        tenant_id: str | None = None,
        version: str = "latest",
    ) -> str:
        template = self.get_template(namespace, name, tenant_id, version)

        # Validate before rendering
        self.validate_variables(template, variables)

        # Perform replacement
        rendered = template
        for var_name, var_val in variables.items():
            # Use regex to replace {{var_name}} with optional spaces
            pattern = r"\{\{\s*" + re.escape(var_name) + r"\s*\}\}"
            rendered = re.sub(pattern, str(var_val), rendered)

        return rendered
