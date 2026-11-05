"""Keep legacy direct dispatch callers explicit until each is migrated or retired."""
from __future__ import annotations

import ast
import json
from collections import Counter
from pathlib import Path

SOURCE_ROOT = Path(__file__).resolve().parents[1] / "src" / "whaxon"

EXPECTED_CATALOG_TRANSPORTS = {
    "nmap": "cli",
    "nikto": "cli",
    "gobuster": "cli",
    "echo": "cli",
    "sqlmap": "cli",
    "whois": "cli",
    "dig": "cli",
    "nuclei": "cli",
    "commix": "cli",
    "ffuf": "cli",
    "wpscan": "cli",
    "impacket": "cli",
    "theharvester": "cli",
    "dnsrecon": "cli",
    "msf_sysinfo": "msf_session",
    "msf_getuid": "msf_session",
    "msf_hashdump": "msf_session",
    "ssh_cmd": "ssh",
    "smb_shares": "smb",
    "smb_ls": "smb",
    "netexec": "cli",
    "arjun": "cli",
    "hydra": "cli",
    "wmi_exec": "wmi",
}
EXPECTED_V2_TARGET_TYPES = {
    "arjun": ("url",),
    "dig": ("hostname",),
    "dnsrecon": ("hostname",),
    "ffuf": ("url",),
    "gobuster": ("hostname", "ip"),
    "nikto": ("hostname", "ip", "url"),
    "nmap": ("hostname", "ip"),
    "nuclei": ("url",),
    "sqlmap": ("url",),
    "theharvester": ("hostname",),
    "whois": ("hostname", "ip"),
    "wpscan": ("url",),
}
EXPECTED_V2_SEMANTIC_OPERATIONS = {
    "arjun": "web.parameters.discover",
    "dig": "dns.records.query",
    "dnsrecon": "dns.records.enumerate",
    "ffuf": "web.paths.fuzz",
    "gobuster": "web.directories.enumerate",
    "nikto": "web.server.audit",
    "nmap": "network.services.discover",
    "nuclei": "web.templates.assess",
    "sqlmap": "web.sql_injection.assess",
    "theharvester": "osint.domain.contacts.search",
    "whois": "domain.registration.lookup",
    "wpscan": "web.wordpress.audit",
}

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
        ("interfaces/web/server.py", "create_app.msf_session_exec", "client.session_exec"): 1,
        ("core/runner.py", "_run_msf_session", "client.session_exec"): 1,
        ("adapters/msf.py", "run_module", "self._client.execute"): 2,
        ("core/validator.py", "revalidate", "self.validate"): 1,
    }
)

# Consequential API surfaces: direct effects, authorization state, V2 lifecycle,
# cancellation, and deployment provisioning. This deliberately complements the
# full UI/control inventory; it does not claim to pin every read-only API route.
EXPECTED_API_ROUTE_HANDLERS = {
    ("GET", "/api/v2/capabilities"): "workflow_v2_capabilities",
    ("GET", "/api/v2/providers"): "workflow_v2_providers",
    ("GET", "/api/v2/providers/portfolio-audit"): "workflow_v2_portfolio_audit",
    ("POST", "/api/v2/workflows"): "workflow_v2_save_plan",
    ("POST", "/api/v2/workflows/<plan_id>/run"): "workflow_v2_run",
    ("POST", "/api/v2/workflow-runs/<request_id>/cancel"): "workflow_v2_cancel_run_request",
    ("POST", "/api/run"): "run_tool",
    ("POST", "/api/ai/run"): "ai_run",
    ("POST", "/api/msf/run"): "msf_run",
    ("POST", "/api/msf/sessions/<session_id>/exec"): "msf_session_exec",
    ("GET", "/api/msf/sessions/<session_id>/portfwd"): "pf_list",
    ("POST", "/api/msf/sessions/<session_id>/portfwd"): "pf_add",
    ("DELETE", "/api/msf/sessions/<session_id>/portfwd"): "pf_del",
    ("POST", "/api/validate/<job_id>/<int:seq>"): "api_validate",
    ("POST", "/api/retest/<job_id>/<int:seq>"): "api_retest",
    ("POST", "/api/approvals/<job_id>/<int:seq>/resolve"): "api_approval_resolve",
    ("GET", "/api/scope"): "get_scope",
    ("POST", "/api/scope"): "save_scope",
    ("POST", "/api/scope/check"): "check_scope",
    ("POST", "/api/scope/override"): "log_override",
    ("POST", "/api/jobs/<job_id>/cancel"): "cancel_job",
    ("POST", "/api/dependencies/install"): "api_dependencies_install",
    ("POST", "/api/dependencies/install-batch"): "api_dependencies_install_batch",
    ("POST", "/api/dependencies/install/<operation_id>/cancel"): "api_dependencies_install_cancel",
}

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


def test_consequential_api_route_methods_and_handlers_are_explicit() -> None:
    server = SOURCE_ROOT / "interfaces" / "web" / "server.py"
    tree = ast.parse(server.read_text(encoding="utf-8"), filename=str(server))
    actual: dict[tuple[str, str], str] = {}
    for node in ast.walk(tree):
        if not isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            continue
        for decorator in node.decorator_list:
            if not isinstance(decorator, ast.Call):
                continue
            func = decorator.func
            if (
                not isinstance(func, ast.Attribute)
                or not isinstance(func.value, ast.Name)
                or func.value.id != "app"
                or not decorator.args
            ):
                continue
            if func.attr in {"get", "post", "put", "patch", "delete"}:
                route = ast.literal_eval(decorator.args[0])
                methods = [func.attr.upper()]
            elif func.attr == "route":
                route = ast.literal_eval(decorator.args[0])
                methods = next(
                    (ast.literal_eval(item.value) for item in decorator.keywords
                     if item.arg == "methods"),
                    ["GET"],
                )
            else:
                continue
            for method in methods:
                key = (method.upper(), route)
                if key in EXPECTED_API_ROUTE_HANDLERS:
                    actual[key] = node.name

    assert actual == EXPECTED_API_ROUTE_HANDLERS, (
        "Consequential API method/handler bindings changed. Review the G01 route "
        "ownership and authorization map before updating it. "
        f"Unexpected: {actual.keys() - EXPECTED_API_ROUTE_HANDLERS.keys()}; "
        f"missing: {EXPECTED_API_ROUTE_HANDLERS.keys() - actual.keys()}; "
        f"changed: {[key for key in actual.keys() & EXPECTED_API_ROUTE_HANDLERS.keys() if actual[key] != EXPECTED_API_ROUTE_HANDLERS[key]]}"
    )


def test_catalog_transports_and_v2_admission_are_explicit() -> None:
    catalog = json.loads(
        (SOURCE_ROOT / "data" / "tools.json").read_text(encoding="utf-8")
    )
    actual_transports = {
        tool["id"]: tool.get("transport", "cli") for tool in catalog["tools"]
    }
    assert actual_transports == EXPECTED_CATALOG_TRANSPORTS

    from whaxon.core.providers import _CATALOG_TARGETS, SEMANTIC_OPERATION_IDS

    assert _CATALOG_TARGETS == EXPECTED_V2_TARGET_TYPES
    assert SEMANTIC_OPERATION_IDS == EXPECTED_V2_SEMANTIC_OPERATIONS
