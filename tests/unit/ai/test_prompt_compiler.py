from datetime import datetime
import pytest

from agentsphere.ai.exceptions.refinement_exceptions import PromptCompilationError
from agentsphere.ai.prompts.prompt_compiler import PromptCompiler
from agentsphere.ai.prompts.prompt_manager import PromptManager


@pytest.fixture
def compiler() -> PromptCompiler:
    manager = PromptManager()
    # Register basic header/footer imports
    manager.register_system_template("common", "header", "System: Initializing Agent Sphere platform.")
    manager.register_system_template("common", "footer", "Footer: Generated at {{ current_year }}.")

    # Register dynamic template
    manager.register_system_template(
        "agents",
        "chat_bot",
        "{{ include 'common.header' }}\nUser Request: {{ query }}\n{{ include 'common.footer' }}",
    )

    return PromptCompiler(prompt_manager=manager)


def test_compile_with_includes_and_macros(compiler: PromptCompiler) -> None:
    variables = {"query": "Tell me a story"}
    compiled = compiler.compile("agents", "chat_bot", variables)

    # 1. Verify header inclusion worked recursively
    assert "System: Initializing Agent Sphere platform." in compiled

    # 2. Verify variable expansion worked
    assert "User Request: Tell me a story" in compiled

    # 3. Verify dynamic macro replacement (current_year) worked inside include!
    expected_year = str(datetime.now().year)
    assert f"Footer: Generated at {expected_year}." in compiled


def test_compile_cache_works(compiler: PromptCompiler) -> None:
    variables = {"query": "Cache test"}

    # First compile
    first_run = compiler.compile("agents", "chat_bot", variables)

    # Modify system template in the manager under-the-hood to see if cached result is returned
    compiler._manager.register_system_template("common", "header", "MODIFIED HEADER")

    # Second compile
    second_run = compiler.compile("agents", "chat_bot", variables)

    # They should be identical due to cache!
    assert first_run == second_run
    assert "MODIFIED HEADER" not in second_run

    # Bypassing the cache should fetch the new header
    bypass_run = compiler.compile("agents", "chat_bot", variables, bypass_cache=True)
    assert "MODIFIED HEADER" in bypass_run


def test_circular_imports_raised(compiler: PromptCompiler) -> None:
    # Set up circular templates
    compiler._manager.register_system_template("circular", "t1", "{{ include 'circular.t2' }}")
    compiler._manager.register_system_template("circular", "t2", "{{ include 'circular.t1' }}")

    with pytest.raises(PromptCompilationError) as exc:
        compiler.compile("circular", "t1", {})
    assert "Circular or too deep nested imports" in str(exc.value)


def test_compile_missing_variables_fails(compiler: PromptCompiler) -> None:
    # 'query' is required by chat_bot template
    with pytest.raises(PromptCompilationError) as exc:
        compiler.compile("agents", "chat_bot", {})
    assert "Variables validation failed" in str(exc.value)
