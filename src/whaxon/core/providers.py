"""Bridge WHAXON's real catalog tools and adapters into Engine v2 capabilities."""
from __future__ import annotations

import asyncio
import ipaddress
import uuid
from urllib.parse import urlsplit

from .capabilities import (
    CapabilityManifest,
    CapabilityRegistry,
    CapabilityRequirements,
    CapabilityUnavailable,
)
from .workflow import WorkflowTask

# Deliberately excludes credential attacks, exploit frameworks, command execution,
# and session operations. Those require dedicated capability and approval models.
_READ_ONLY_TOOLS = frozenset({
    "nmap", "nikto", "gobuster", "ffuf", "nuclei", "wpscan", "sqlmap",
    "whois", "dig", "whatweb", "theharvester", "dnsrecon", "arjun",
})


def _target_type(target: str) -> str:
    """Classify literal targets without DNS lookups or network side effects."""
    if not isinstance(target, str) or not target or target != target.strip():
        raise ValueError("target must be a non-empty normalized string")
    if "://" in target:
        parsed = urlsplit(target)
        if parsed.scheme not in ("http", "https") or not parsed.hostname or parsed.username or parsed.password or parsed.fragment:
            raise ValueError("unsupported URL target")
        return "url"
    try:
        ipaddress.ip_address(target.strip("[]"))
        return "ip"
    except ValueError:
        if any(c in target for c in "/?#@\\\\") or any(c.isspace() for c in target):
            raise ValueError("invalid hostname target") from None
        return "hostname"


class CatalogAdapterProvider:
    """Resolve approved read-only catalog tools and execute through ToolRunner.

    ToolRunner remains the sole execution path: scope checks, argv construction,
    process isolation, timeout handling, adapter parsing and evidence events
    are therefore shared with the existing CLI and UI.
    """

    def __init__(self, *, catalog, runner, store, registry: CapabilityRegistry):
        self.catalog = catalog
        self.runner = runner
        self.store = store
        self.registry = registry
        self._tool_by_provider: dict[str, str] = {}
        self._manifest_by_provider: dict[str, CapabilityManifest] = {}
        from ..adapters import get_adapter

        for tool in catalog.list():
            if tool.id not in _READ_ONLY_TOOLS or get_adapter(tool.id) is None:
                continue
            provider_id = f"whaxon.adapter.{tool.id}"
            manifest = CapabilityManifest(
                capability_id=f"tool.{tool.id}",
                provider_id=provider_id,
                provider_version="catalog-v1",
                transports=("local_process",),
                target_types=("hostname", "ip", "url"),
                permissions=("network.scan",),
                side_effects=("network_traffic", "target_service_logs"),
                impact="moderate",
                readiness="registered",
                timeout_s=300.0,
                input_schema={"type": "object", "properties": {}, "additionalProperties": False},
                output_schema={"type": "object"},
                limitations=("Requires the catalog binary to be installed.",),
            )
            registry.register(manifest)
            self._tool_by_provider[provider_id] = tool.id
            self._manifest_by_provider[provider_id] = manifest

    async def dispatch(self, task: WorkflowTask) -> dict:
        if task.inputs:
            raise ValueError(
                "catalog adapter providers accept no dynamic inputs; use the approved catalog defaults"
            )
        resolution = self.registry.resolve(
            task.capability_id,
            CapabilityRequirements(
                transport="local_process",
                target_type=_target_type(task.target),
                required_permissions=tuple(task.permissions),
                minimum_readiness="registered",
                allowed_providers=(f"whaxon.adapter.{task.capability_id.removeprefix('tool.')}",),
            ),
        )
        tool_id = self._tool_by_provider.get(resolution.manifest.provider_id)
        if tool_id is None or resolution.manifest.capability_id != f"tool.{tool_id}":
            raise RuntimeError("resolved provider is not bound to this Core instance")
        expected_manifest = self._manifest_by_provider.get(resolution.manifest.provider_id)
        if expected_manifest is None or expected_manifest.fingerprint != resolution.manifest.fingerprint:
            raise CapabilityUnavailable(task.capability_id, (
                "provider manifest differs from the bound execution adapter",))
        tool = self.catalog.get(tool_id)
        if tool is None or not tool.available:
            raise RuntimeError(f"required tool is not installed: {tool_id}")
        # Never allow a stale persisted registry entry to dispatch through a
        # different adapter or a newer manifest version by accident.
        if resolution.manifest.provider_version != "catalog-v1":
            raise CapabilityUnavailable(task.capability_id, (
                "resolved catalog provider version is not supported by this adapter",))

        job_id = uuid.uuid4().hex[:12]
        timeout_s = min(float(task.timeout_s), resolution.manifest.timeout_s)
        await self.runner.run_tool(
            tool_id=tool_id,
            target=task.target,
            job_id=job_id,
            timeout_s=timeout_s,
            phase="workflow",
        )
        # EventBus persistence is scheduled onto the bound Core event loop.
        await asyncio.sleep(0)
        job = self.store.get(job_id)
        if job is None:
            raise RuntimeError(f"tool execution {job_id} did not persist a job record")
        if job.get("tool") not in (None, tool_id) or job.get("target") not in (None, task.target):
            raise RuntimeError("persisted provider job identity does not match dispatched task")
        if job.get("error") == "timeout":
            raise TimeoutError(f"{tool_id} exceeded {timeout_s:g}s")
        if job.get("status") != "finished" or job.get("exit_code") != 0:
            raise RuntimeError(
                f"{tool_id} failed (status={job.get('status')}, exit_code={job.get('exit_code')})"
            )
        return {
            "job_id": job_id,
            "tool_id": tool_id,
            "target": task.target,
            "exit_code": job["exit_code"],
            "duration_s": job.get("duration_s"),
            "findings": self.store.get_findings(job_id) or [],
        }
