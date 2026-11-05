"""Keep legacy direct dispatch callers explicit until each is migrated or retired."""
from __future__ import annotations

import ast
from collections import Counter
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src" / "whaxon"

# (source path, containing function path, method) -> number of syntactic calls.
# Every item except core/providers.py is a legacy path. That provider is the
# canonical scheduler-authorized Engine V2 dispatch and stays separately pinned.
EXPECTED_RUNNER_CALLS = Counter(
    {
        ("ai/executor.py", "_validate_and_run", "run_tool"): 1,
        ("ai/executor.py", "_validate_and_run", "run_in_session"): 1,
        ("ai/providers/llm.py", "_to_action", "run_tool"): 1,
        ("ai/providers/rules.py", "plan_step", "run_tool"): 5,
        ("ai/providers/rules.py", "plan_step", "run_in_session"): 1,
        ("core/ai_bridge.py", "_run_tool", "run_tool"): 1,
        ("core/ai_bridge.py", "build_executor._run_in_session", "run_in_session"): 1,
        ("core/providers.py", "dispatch", "run_tool"): 1,
        ("core/worker.py", "drain_async", "run_tool"): 1,
        ("interfaces/cli/run_cmd.py", "main._go", "run_tool"): 1,
        ("interfaces/cli/run_cmd.py", "main._go", "run_in_session"): 1,
        ("interfaces/gui/main_window.py", "_run_tool", "run_tool"): 2,
        ("interfaces/tui/screens/main.py", "_run_tool", "run_tool"): 2,
        ("interfaces/web/server.py", "_run_job_blocking", "run_tool"): 1,
    }
)

# These services can perform network work without entering ToolRunner. Keep
# their public execution entry points visible separately from runner calls.
EXPECTED_SERVICE_CALLS = Counter(
    {
        ("interfaces/cli/recon_cmd.py", "main", "core.recon.run"): 1,
        ("interfaces/cli/validate_cmd.py", "main", "validator.validate"): 1,
        ("interfaces/cli/retest_cmd.py", "main", "validator.revalidate"): 1,
        ("interfaces/web/server.py", "create_app.api_validate", "v.validate"): 1,
        ("interfaces/web/server.py", "create_app.api_retest", "v.revalidate"): 1,
        ("interfaces/web/server.py", "create_app.msf_run._do_run", "adapter.run_module"): 1,
        ("core/validator.py", "revalidate", "self.validate"): 1,
    }
)

SERVICE_CALL_NAMES = {item[2] for item in EXPECTED_SERVICE_CALLS}


def _dotted_name(node: ast.expr) -> str | None:
    if isinstance(node, ast.Name):
        return node.id
    if isinstance(node, ast.Attribute):
        prefix = _dotted_name(node.value)
        return f"{prefix}.{node.attr}" if prefix else None
    return None


class _RunnerCallVisitor(ast.NodeVisitor):
    def __init__(self, path: str) -> None:
        self.path = path
        self.functions: list[str] = []
        self.calls: Counter[tuple[str, str, str]] = Counter()

    def visit_FunctionDef(self, node: ast.FunctionDef) -> None:
        self._visit_function(node)

    def visit_AsyncFunctionDef(self, node: ast.AsyncFunctionDef) -> None:
        self._visit_function(node)

    def _visit_function(self, node: ast.FunctionDef | ast.AsyncFunctionDef) -> None:
        self.functions.append(node.name)
        self.generic_visit(node)
        self.functions.pop()

    def visit_Call(self, node: ast.Call) -> None:
        if isinstance(node.func, ast.Attribute) and node.func.attr in {
            "run_tool",
            "run_in_session",
        }:
            scope = ".".join(self.functions)
            self.calls[(self.path, scope, node.func.attr)] += 1
        self.generic_visit(node)


class _ServiceCallVisitor(_RunnerCallVisitor):
    def __init__(self, path: str) -> None:
        super().__init__(path)
        self.service_calls: Counter[tuple[str, str, str]] = Counter()

    def visit_Call(self, node: ast.Call) -> None:
        call_name = _dotted_name(node.func)
        if call_name in SERVICE_CALL_NAMES:
            scope = ".".join(self.functions)
            self.service_calls[(self.path, scope, call_name)] += 1
        self.generic_visit(node)


def _runner_call_inventory() -> Counter[tuple[str, str, str]]:
    calls: Counter[tuple[str, str, str]] = Counter()
    for source in sorted(SOURCE_ROOT.rglob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        visitor = _RunnerCallVisitor(source.relative_to(SOURCE_ROOT).as_posix())
        visitor.visit(tree)
        calls.update(visitor.calls)
    return calls


def test_legacy_and_v2_runner_dispatch_callsites_are_explicit() -> None:
    actual = _runner_call_inventory()
    assert actual == EXPECTED_RUNNER_CALLS, (
        "Execution callsites changed. Review the Engine V2 caller inventory, classify "
        "each addition as legacy or scheduler-authorized V2, then update this map. "
        f"Unexpected: {actual - EXPECTED_RUNNER_CALLS}; "
        f"missing: {EXPECTED_RUNNER_CALLS - actual}"
    )


def test_recon_validation_and_retest_service_callsites_are_explicit() -> None:
    actual: Counter[tuple[str, str, str]] = Counter()
    for source in sorted(SOURCE_ROOT.rglob("*.py")):
        tree = ast.parse(source.read_text(encoding="utf-8"), filename=str(source))
        visitor = _ServiceCallVisitor(source.relative_to(SOURCE_ROOT).as_posix())
        visitor.visit(tree)
        actual.update(visitor.service_calls)

    assert actual == EXPECTED_SERVICE_CALLS, (
        "Recon/validation/retest service callsites changed. Review the Engine V2 "
        "service inventory, classification, and authorization boundary before "
        "updating this map. "
        f"Unexpected: {actual - EXPECTED_SERVICE_CALLS}; "
        f"missing: {EXPECTED_SERVICE_CALLS - actual}"
    )
