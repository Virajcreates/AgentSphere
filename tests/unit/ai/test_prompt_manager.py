import pytest

from agentsphere.ai.exceptions.base import PromptValidationError
from agentsphere.ai.prompts.prompt_manager import PromptManager


@pytest.fixture
def manager() -> PromptManager:
    return PromptManager()


def test_register_and_get_system_template(manager: PromptManager) -> None:
    template = "Hello, {{ name }}!"
    manager.register_system_template("default", "welcome", template)

    assert manager.get_template("default", "welcome") == template
    # Also defaults to 'latest'
    assert manager.get_template("default", "welcome", version="latest") == template


def test_register_system_template_versioning(manager: PromptManager) -> None:
    template_v1 = "Hello, {{ name }}!"
    template_v2 = "Welcome back, {{ name }}!"

    manager.register_system_template("default", "welcome", template_v1, version="v1")
    manager.register_system_template("default", "welcome", template_v2, version="v2")

    assert manager.get_template("default", "welcome", version="v1") == template_v1
    assert manager.get_template("default", "welcome", version="v2") == template_v2


def test_tenant_override_template(manager: PromptManager) -> None:
    system_temp = "Welcome, {{ name }}."
    tenant_temp = "Aloha, {{ name }}!"

    manager.register_system_template("default", "welcome", system_temp)
    manager.register_tenant_template("tenant_123", "default", "welcome", tenant_temp)

    # Retrieves tenant template when tenant_id matches
    assert manager.get_template("default", "welcome", tenant_id="tenant_123") == tenant_temp
    # Retrieves system default if tenant_id doesn't match or is None
    assert manager.get_template("default", "welcome") == system_temp
    assert manager.get_template("default", "welcome", tenant_id="other_tenant") == system_temp


def test_validate_variables_success(manager: PromptManager) -> None:
    template = "Welcome {{ name }} to {{ city }}!"
    # Variables match perfectly
    manager.validate_variables(template, {"name": "Viraj", "city": "Seattle"})


def test_validate_variables_missing(manager: PromptManager) -> None:
    template = "Welcome {{ name }} to {{ city }}!"
    with pytest.raises(PromptValidationError) as exc:
        manager.validate_variables(template, {"name": "Viraj"})
    assert "Missing required placeholders" in str(exc.value)


def test_validate_mismatched_brackets(manager: PromptManager) -> None:
    template = "Welcome {{ name } to {{ city }}!"  # Unclosed brace
    with pytest.raises(PromptValidationError) as exc:
        manager.validate_variables(template, {"name": "Viraj", "city": "Seattle"})
    assert "Mismatched curly braces" in str(exc.value)


def test_render_template(manager: PromptManager) -> None:
    template = "Welcome {{ name }} to {{ city }}!"
    manager.register_system_template("default", "welcome", template)

    rendered = manager.render("default", "welcome", {"name": "Viraj", "city": "Seattle"})
    assert rendered == "Welcome Viraj to Seattle!"


def test_render_with_whitespace_in_braces(manager: PromptManager) -> None:
    template = "Welcome {{name}} to {{  city  }}!"
    manager.register_system_template("default", "welcome", template)

    rendered = manager.render("default", "welcome", {"name": "Viraj", "city": "Seattle"})
    assert rendered == "Welcome Viraj to Seattle!"
