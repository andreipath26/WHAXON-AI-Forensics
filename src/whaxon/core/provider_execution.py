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

# Built-in first-party providers persist jobs with their capability ID as tool ID.
FIRST_PARTY_PROVIDER_CAPABILITY_IDS = frozenset({
    "recon.http",
    "dns.recon.passive",
    "dns.recon.full",
    "web.recon.passive",
    "web.recon.headers",
    "web.recon.robots",
    "web.recon.security_txt",
    "web.recon.redirect_observe",
    "tls.certificate.inspect",
    "lab.initial_access.samba_usermap",
})


def provider_capability_identity_is_known(capability_id: str) -> bool:
    """Whether capability ID carries an exact durable provider tool contract."""
    return (
        isinstance(capability_id, str)
        and (
            capability_id.startswith("tool.")
            or capability_id in SEMANTIC_OPERATION_TO_TOOL
            or capability_id in FIRST_PARTY_PROVIDER_CAPABILITY_IDS
        )
    )


# Positive recovery policy: additions require an explicit reviewed contract.
# Verification probes, SQL injection checks, the Samba lab provider and
# unknown tool aliases intentionally remain manual-reconciliation-only.
RESULT_ONLY_RECOVERY_CAPABILITY_IDS = frozenset({
    "tool.nmap", "tool.nikto", "tool.gobuster", "tool.ffuf", "tool.nuclei",
    "tool.wpscan", "tool.whois", "tool.dig", "tool.theharvester",
    "tool.dnsrecon", "tool.arjun",
    "network.services.discover", "web.server.audit", "web.directories.enumerate",
    "web.paths.fuzz", "web.templates.assess", "web.wordpress.audit",
    "domain.registration.lookup", "dns.records.query",
    "osint.domain.contacts.search", "dns.records.enumerate",
    "web.parameters.discover",
    "dns.recon.passive", "dns.recon.full", "web.recon.passive",
    "web.recon.headers", "web.recon.robots", "web.recon.security_txt",
    "web.recon.redirect_observe", "tls.certificate.inspect",
})


def provider_supports_result_only_recovery(capability_id: str) -> bool:
    """Whether this exact capability has an approved observational recovery contract."""
    return (
        isinstance(capability_id, str)
        and capability_id in RESULT_ONLY_RECOVERY_CAPABILITY_IDS
    )


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
