"""Shared identity rules for durable Engine V2 provider jobs."""
from __future__ import annotations

import uuid

SEMANTIC_OPERATION_TO_TOOL = {
    "network.services.discover": "nmap",
    "web.server.audit": "nikto",
    "web.directories.enumerate": "gobuster",
    "web.paths.fuzz": "ffuf",
    "web.templates.assess": "nuclei",
    "web.wordpress.audit": "wpscan",
    "web.sql_injection.assess": "sqlmap",
    "domain.registration.lookup": "whois",
    "dns.records.query": "dig",
    "osint.domain.contacts.search": "theharvester",
    "dns.records.enumerate": "dnsrecon",
    "web.parameters.discover": "arjun",
}


def provider_tool_id_for_capability(capability_id: str) -> str:
    """Resolve the persisted provider tool identity for a workflow capability."""
    if not isinstance(capability_id, str) or not capability_id:
        raise ValueError("workflow capability identity is required")
    if capability_id.startswith("tool."):
        return capability_id.removeprefix("tool.")
    return SEMANTIC_OPERATION_TO_TOOL.get(capability_id, capability_id)


def provider_execution_job_id(task) -> str:
    """Use a durable attempt ID for workflow jobs; keep direct calls random."""
    attempt_id = getattr(task, "_attempt_id", None)
    if attempt_id is None:
        return uuid.uuid4().hex[:12]
    if (
        not isinstance(attempt_id, str)
        or len(attempt_id) != 32
        or any(char not in "0123456789abcdef" for char in attempt_id)
        or getattr(task, "_provider_execution_id", None) != attempt_id
    ):
        raise ValueError("invalid durable V2 provider execution identity")
    return attempt_id
