"""Bridge WHAXON's real catalog tools and adapters into Engine v2 capabilities."""
from __future__ import annotations

import asyncio
import hashlib
import ipaddress
import json
import re
import shutil
import uuid
from urllib.parse import urlsplit

from .capabilities import (
    CapabilityManifest,
    CapabilityRegistry,
    CapabilityRequirements,
    CapabilityUnavailable,
)
from .workflow import WorkflowTask

# Conservative target formats supported by the actual packaged argv templates.
# These are declarations, not authorization or proof of verified execution.
_CATALOG_TARGETS = {
    "nmap": ("hostname", "ip"),
    "nikto": ("hostname", "ip", "url"),
    "gobuster": ("hostname", "ip"),
    "ffuf": ("url",),
    "nuclei": ("url",),
    "wpscan": ("url",),
    "sqlmap": ("url",),
    "whois": ("hostname", "ip"),
    "dig": ("hostname",),
    "whatweb": ("hostname", "ip", "url"),
    "theharvester": ("hostname",),
    "dnsrecon": ("hostname",),
    "arjun": ("url",),
}
_ADAPTER_SERIES = "catalog-v2"
_HOST_LABEL = re.compile(r"^[A-Za-z0-9](?:[A-Za-z0-9-]{0,61}[A-Za-z0-9])?$")


def _valid_host(host: str) -> bool:
    if not isinstance(host, str) or not host:
        return False
    try:
        ipaddress.ip_address(host)
        return True
    except ValueError:
        pass
    if len(host) > 253 or not host.isascii():
        return False
    return all(_HOST_LABEL.fullmatch(label) for label in host.rstrip(".").split("."))


def _target_type(target: str) -> str:
    """Classify a literal network target without DNS lookups or side effects."""
    if not isinstance(target, str) or not target or target != target.strip():
        raise ValueError("target must be a non-empty normalized string")
    if any(ord(char) < 33 or ord(char) == 127 for char in target):
        raise ValueError("target contains control characters or whitespace")
    if "://" in target:
        try:
            parsed = urlsplit(target)
            hostname, port = parsed.hostname, parsed.port
        except ValueError as exc:
            raise ValueError("invalid URL authority") from exc
        if (
            parsed.scheme not in ("http", "https") or not hostname
            or not _valid_host(hostname) or not parsed.netloc
            or parsed.username is not None or parsed.password is not None
            or parsed.fragment or (port is not None and port <= 0)
        ):
            raise ValueError("unsupported URL target")
        return "url"
    try:
        ipaddress.ip_address(target.strip("[]"))
        return "ip"
    except ValueError:
        if not _valid_host(target) or ":" in target or any(
            char in target for char in "/?#@\\[]"
        ):
            raise ValueError("invalid hostname target") from None
        return "hostname"


def _catalog_version(tool) -> str:
    """Version the tool identity and argv contract, not its availability."""
    fields = {
        key: getattr(tool, key, "") for key in (
            "id", "binary", "args", "transport", "outfile_flag", "command",
        )
    }
    digest = hashlib.sha256(
        json.dumps(fields, sort_keys=True, separators=(",", ":")).encode("utf-8")
    ).hexdigest()[:16]
    return f"{_ADAPTER_SERIES}.{digest}"


def _tool_available(tool) -> bool:
    """Live binary presence is not equivalent to smoke/lab verification."""
    if tool is None or not bool(getattr(tool, "available", False)):
        return False
    binary = getattr(tool, "binary", "")
    return not binary or shutil.which(binary) is not None


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
            if (
                tool.id not in _CATALOG_TARGETS
                or getattr(tool, "transport", "cli") != "cli"
                or get_adapter(tool.id) is None
            ):
                continue
            provider_id = f"whaxon.adapter.{tool.id}"
            manifest = CapabilityManifest(
                capability_id=f"tool.{tool.id}",
                provider_id=provider_id,
                provider_version=_catalog_version(tool),
                transports=("local_process",),
                target_types=_CATALOG_TARGETS[tool.id],
                permissions=("network.scan",),
                side_effects=("network_traffic", "target_service_logs"),
                impact="moderate",
                readiness="registered",
                timeout_s=300.0,
                input_schema={"type": "object", "properties": {}, "additionalProperties": False},
                output_schema={"type": "object"},
                limitations=(
                    "Catalog defaults only; dynamic command arguments are unsupported.",
                    "Requires a locally installed binary and explicit scope/approval.",
                    "Zero exit status is not independent vulnerability verification.",
                ),
            )
            registry.register(manifest)
            self._tool_by_provider[provider_id] = tool.id
            self._manifest_by_provider[provider_id] = manifest

    def inventory(self) -> list[dict]:
        """Live readiness is observational and never rewrites versioned manifests."""
        inventory = []
        for provider_id, expected in sorted(self._manifest_by_provider.items()):
            tool_id = self._tool_by_provider[provider_id]
            tool = self.catalog.get(tool_id)
            current = next((
                item for item in self.registry.list(expected.capability_id)
                if item.provider_id == provider_id
                and item.provider_version == expected.provider_version
            ), None)
            bound = current is not None and current.fingerprint == expected.fingerprint
            current_catalog = bool(
                tool is not None and _catalog_version(tool) == expected.provider_version
                and getattr(tool, "transport", "cli") == "cli"
            )
            installed = current_catalog and _tool_available(tool)
            inventory.append({
                "capability_id": expected.capability_id,
                "provider_id": provider_id,
                "provider_version": expected.provider_version,
                "manifest_fingerprint": expected.fingerprint,
                "transport": "local_process",
                "target_types": list(expected.target_types),
                "registry_digest": self.registry.digest,
                "registered": bound,
                "installed": installed,
                "executable": bound and installed,
                "readiness": "installed" if bound and installed else "registered" if bound else "blocked",
                "reason": (
                    "ready_for_local_execution" if bound and installed
                    else "manifest_binding_mismatch" if not bound
                    else "catalog_changed_requires_reload" if not current_catalog
                    else "binary_not_installed"
                ),
                "authorization_required": True,
                "smoke_tested": False,
                "lab_validated": False,
                "end_to_end_verified": False,
            })
        return inventory

    def resolve_task(self, task: WorkflowTask, *, require_installed: bool = False):
        """Resolve only the locally bound manifest, never a stored imposter."""
        if not isinstance(task, WorkflowTask):
            raise TypeError("provider task must be a WorkflowTask")
        if task.inputs:
            raise ValueError(
                "catalog adapter providers accept no dynamic inputs; use the approved catalog defaults"
            )
        provider_id = f"whaxon.adapter.{task.capability_id.removeprefix('tool.')}"
        expected = self._manifest_by_provider.get(provider_id)
        if expected is None or expected.capability_id != task.capability_id:
            raise CapabilityUnavailable(task.capability_id, ("no bound local adapter",))
        tool = self.catalog.get(self._tool_by_provider[provider_id])
        if tool is None or _catalog_version(tool) != expected.provider_version:
            raise CapabilityUnavailable(task.capability_id, (
                "catalog executable/argv changed since provider registration",))
        if getattr(tool, "transport", "cli") != "cli":
            raise CapabilityUnavailable(task.capability_id, ("local transport unavailable",))
        target_type = _target_type(task.target)
        if tool.id == "ffuf" and target_type == "url" and urlsplit(task.target).query:
            raise CapabilityUnavailable(task.capability_id, (
                "ffuf target query is incompatible with the /FUZZ template",))
        resolution = self.registry.resolve(
            task.capability_id,
            CapabilityRequirements(
                transport="local_process",
                target_type=target_type,
                required_permissions=tuple(task.permissions),
                maximum_impact=task.impact,
                allowed_providers=(provider_id,),
                allowed_versions=(expected.provider_version,),
                allowed_fingerprints=(expected.fingerprint,),
                allowed_side_effects=expected.side_effects,
            ),
        )
        if resolution.manifest.fingerprint != expected.fingerprint:
            raise CapabilityUnavailable(task.capability_id, ("unbound provider manifest",))
        if require_installed and not _tool_available(tool):
            raise RuntimeError(f"required tool is not installed: {tool.id}")
        return resolution

    async def dispatch(self, task: WorkflowTask) -> dict:
        resolution = self.resolve_task(task, require_installed=True)
        expected = resolution.manifest
        if set(task.permissions) != set(expected.permissions) or task.impact != expected.impact:
            raise CapabilityUnavailable(task.capability_id, (
                "task permission/impact differs from the bound provider contract",))
        tool_id = self._tool_by_provider[expected.provider_id]
        job_id = uuid.uuid4().hex[:12]
        timeout_s = min(float(task.timeout_s), expected.timeout_s)
        returned_id = await self.runner.run_tool(
            tool_id=tool_id,
            target=task.target,
            job_id=job_id,
            timeout_s=timeout_s,
            phase="workflow",
        )
        if returned_id != job_id:
            raise RuntimeError("provider runner returned a mismatched execution identity")
        # EventBus persistence is scheduled onto the bound Core event loop.
        await asyncio.sleep(0)
        job = self.store.get(job_id)
        if job is None:
            raise RuntimeError(f"tool execution {job_id} did not persist a job record")
        if (
            job.get("id") != job_id
            or job.get("tool") != tool_id
            or job.get("target") != task.target
        ):
            raise RuntimeError("persisted provider job identity does not match dispatched task")
        if job.get("error") == "timeout":
            raise TimeoutError(f"{tool_id} exceeded {timeout_s:g}s")
        if job.get("status") != "finished" or job.get("exit_code") != 0:
            raise RuntimeError(
                f"{tool_id} failed (status={job.get('status')}, exit_code={job.get('exit_code')})"
            )
        findings = self.store.get_findings(job_id)
        if not isinstance(findings, list):
            raise RuntimeError("provider findings could not be verified in durable store")
        return {
            "job_id": job_id,
            "tool_id": tool_id,
            "target": task.target,
            "exit_code": job["exit_code"],
            "duration_s": job.get("duration_s"),
            "findings": findings,
            "provider_id": expected.provider_id,
            "provider_version": expected.provider_version,
            "manifest_fingerprint": expected.fingerprint,
            "registry_digest": resolution.registry_digest,
            "transport": "local_process",
        }
