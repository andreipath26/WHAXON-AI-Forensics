"""Bridge WHAXON's real catalog tools and adapters into Engine v2 capabilities."""
from __future__ import annotations

import asyncio
import uuid

from .capabilities import (
    CapabilityManifest,
    CapabilityRegistry,
    CapabilityRequirements,
)
from .workflow import WorkflowTask

# Deliberately excludes credential attacks, exploit frameworks, command execution,
# and session operations. Those require dedicated capability and approval models.
_READ_ONLY_TOOLS = frozenset({
    "nmap", "nikto", "gobuster", "ffuf", "nuclei", "wpscan", "sqlmap",
    "whois", "dig", "whatweb", "theharvester", "dnsrecon", "arjun",
})


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

    async def dispatch(self, task: WorkflowTask) -> dict:
        if task.inputs:
            raise ValueError(
                "catalog adapter providers accept no dynamic inputs; use the approved catalog defaults"
            )
        resolution = self.registry.resolve(
            task.capability_id,
            CapabilityRequirements(
                transport="local_process",
                minimum_readiness="registered",
                allowed_providers=tuple(self._tool_by_provider),
            ),
        )
        tool_id = self._tool_by_provider.get(resolution.manifest.provider_id)
        if tool_id is None:
            raise RuntimeError("resolved provider is not bound to this Core instance")
        tool = self.catalog.get(tool_id)
        if tool is None or not tool.available:
            raise RuntimeError(f"required tool is not installed: {tool_id}")

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
