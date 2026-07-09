import ast
from pathlib import Path

import pytest

SRC = Path(__file__).resolve().parents[2] / "src" / "agentsphere"

REQUIRED_DIRS = [
    "domain",
    "application",
    "infrastructure",
    "interfaces",
    "common",
    "config",
]

# Known unavoidable violations (e.g., domain ORM models import Base from config).
# Key: (relative_file_path, forbidden_layer, import_module_name)
KNOWN_LAYER_VIOLATIONS: set[tuple[str, str, str]] = set()


def _get_layer(file_path: Path) -> str | None:
    rel = file_path.relative_to(SRC)
    parts = rel.parts
    if len(parts) < 1:
        return None
    layer = parts[0]
    if layer in REQUIRED_DIRS:
        return layer
    return None


def _is_forbidden_import(import_module: str, from_layer: str) -> str | None:
    if not import_module.startswith("agentsphere."):
        return None
    target_module = import_module[len("agentsphere.") :]
    target_layer = target_module.split(".")[0]

    if target_layer not in REQUIRED_DIRS:
        return None

    cross_cutting = {"common", "config"}

    forbidden: dict[str, set[str]] = {
        "domain": {"infrastructure", "interfaces", "application"},
        "application": {"interfaces", "infrastructure"},
        "infrastructure": {"interfaces"},
    }

    if target_layer in cross_cutting:
        return None
    forbidden_targets = forbidden.get(from_layer, set())
    if target_layer in forbidden_targets:
        return target_layer
    return None


@pytest.mark.architecture
def test_domain_does_not_depend_on_infrastructure_or_interfaces() -> None:
    violations = _find_violations("domain")
    known = {(f, l) for f, l, _ in KNOWN_LAYER_VIOLATIONS if f.startswith("domain/")}
    actual = {(f, l) for f, l in violations}
    extra = actual - known
    assert not extra, f"Domain layer violations: {extra}"


@pytest.mark.architecture
def test_application_does_not_depend_on_interfaces_or_infrastructure() -> None:
    violations = _find_violations("application")
    known = {(f, l) for f, l, _ in KNOWN_LAYER_VIOLATIONS if f.startswith("application/")}
    actual = {(f, l) for f, l in violations}
    extra = actual - known
    assert not extra, f"Application layer violations: {extra}"


@pytest.mark.architecture
def test_infrastructure_does_not_depend_on_api_layer() -> None:
    violations = _find_violations("infrastructure")
    known = {(f, l) for f, l, _ in KNOWN_LAYER_VIOLATIONS if f.startswith("infrastructure/")}
    actual = {(f, l) for f, l in violations}
    extra = actual - known
    assert not extra, f"Infrastructure layer violations: {extra}"


def _find_violations(target_layer: str) -> list[tuple[str, str]]:
    violations: list[tuple[str, str]] = []
    for py_file in (SRC / target_layer).rglob("*.py"):
        layer = _get_layer(py_file)
        if layer is None:
            continue
        mod_path = py_file.read_text(encoding="utf-8")
        try:
            tree = ast.parse(mod_path)
        except SyntaxError:
            continue
        for node in ast.walk(tree):
            if isinstance(node, ast.Import):
                for alias in node.names:
                    forbidden = _is_forbidden_import(alias.name, layer)
                    if forbidden:
                        found_violation = _check_known(py_file, alias.name)
                        if not found_violation:
                            violations.append((str(py_file.relative_to(SRC)), forbidden))
            elif isinstance(node, ast.ImportFrom):
                if node.module and node.module.startswith("agentsphere."):
                    forbidden = _is_forbidden_import(node.module, layer)
                    if forbidden:
                        found_violation = _check_known(py_file, node.module)
                        if not found_violation:
                            violations.append((str(py_file.relative_to(SRC)), forbidden))
    return violations


def _check_known(py_file: Path, import_name: str) -> bool:
    rel = str(py_file.relative_to(SRC))
    for known_file, _, known_import in KNOWN_LAYER_VIOLATIONS:
        if known_file == rel and known_import == import_name:
            return True
    return False