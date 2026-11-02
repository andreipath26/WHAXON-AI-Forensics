# Scope

WHAXON enforces scope fail-closed. A missing or broken config never silently permits everything.

## Default config

If data/scope.json does not exist at Core.__init__, ScopeManager.load() writes:

    {
      engagement: default,
      enabled: true,
      in_scope: [
        127.0.0.0/8,
        10.0.0.0/8,
        172.16.0.0/12,
        192.168.0.0/16,
        ::1,
        fe80::/10,
        fc00::/7
      ],
      out_of_scope: [],
      notes: Auto-generated default scope. Loopback and RFC1918 only.
    }

Covers:

- IPv4 loopback 127.0.0.0/8
- RFC1918 (10/8, 172.16/12, 192.168/16)
- IPv6 loopback ::1
- IPv6 link-local fe80::/10
- IPv6 unique-local fc00::/7

Does NOT cover 169.254.0.0/16 (link-local / cloud metadata) - treating that as an accidental target would be a mistake.

## Precedence

check(target) returns a result with .allowed and .reason. Order:

1. enabled == false -> allowed (operator opt-out, explicit).
2. out_of_scope match -> denied, regardless of in_scope.
3. in_scope match -> allowed.
4. No match -> denied.

## CLI

    whaxon scope --show                # Print the current config
    whaxon scope --check <target>      # Exit 0 allowed / 1 denied
    whaxon scope --set scope.json      # Replace config from file
    whaxon scope --enable              # Set enabled=true
    whaxon scope --disable             # Set enabled=false
    whaxon scope --clear               # Delete file (default rewritten next load)

## HTTP API

- GET  /api/scope             - current config
- POST /api/scope/check       - body: {target: ...} -> {allowed, reason}
- POST /api/scope/override    - body: {target, reason} -> allow once, logged to data/scope_overrides.log

## Explicit scope overrides

The normal execution path rejects targets outside the configured scope. There are deliberately separate, explicit override paths:

- CLI: `whaxon run ... --allow-out-of-scope` requests a per-run override. Use only when the engagement authorization explicitly covers the target; review the command's output and persisted job record.
- Web API: `POST /api/scope/override` records a target and reason for a one-time override. The subsequent run must use the matching recorded override; a request parameter alone cannot bypass scope.
- Python integrations: the runner exposes a per-call `allow_out_of_scope=True` option to trusted calling code.

These are not substitutes for authorization, and they do not provide network-level containment. Keep scope enforcement enabled by default. Setting `enabled: false` disables the application-level scope guard globally and should be reserved for deliberately isolated labs.

## AI scope expansion

The AI planner obeys the same fail-closed scope checker as everything else. `WHAXON_AI_SCOPE_EXPANSION` selects the policy for how discovered hosts are treated:

| Value | Behavior | Status |
| --- | --- | --- |
| `strict` | Only explicitly-listed targets. Discovered hosts are never automatically in scope. The agent may *propose* adding one via `ask_human`, but the executor refuses any action against an out-of-scope target regardless of the human's answer. | **v1 default and only implemented policy.** |
| `inherited` | Any host that resolves from an in-scope domain, and any host in the same RFC1918 subnet as an in-scope host, would be in scope. | Documented; **not implemented in v1**. Selecting it logs a warning and falls back to `strict`. |
| `recommended` | As inherited, but every auto-expansion is logged and the human can veto before the first action against the discovered host. | Documented; **not implemented in v1**. Selecting it logs a warning and falls back to `strict`. |

**Why strict for v1.** Scope enforcement is the safety property the whole tool rests on. Starting strict and moving to looser is a small change. Starting loose and trying to tighten is a rewrite. The design (`docs/agent-architecture.md` §9) makes this explicit.

**Env var default:** unset = `strict`. Any value other than `strict` warns at startup and uses `strict`.

## Failure modes

- File missing: strict default written, enforcement enabled
- File unreadable / malformed JSON: RuntimeError at Core.__init__ - WHAXON refuses to start
- enabled key missing: defaults to true (fail-closed)
- in_scope missing: empty list; everything denied

## Tests

Scope behavior is covered by the `tests/test_scope*.py` suite and execution-boundary regressions, including default loopback/private ranges, IPv6 local ranges, out-of-scope precedence, malformed/missing configuration, DNS resolution failure, unsafe target arguments and explicit override handling. Run:

```bash
python -m pytest tests/test_scope*.py tests/test_validator_security_regressions.py -q
```

The test suite is evidence for the exercised cases only; it is not proof of connection-time network containment.

## Broad CIDR warning

An enabled scope containing `0.0.0.0/0` or `::/0` emits a warning when loaded because it effectively permits every IPv4 or IPv6 address in that family. WHAXON does not silently rewrite an explicitly configured rule, but operators should treat it as a global-scope decision and verify that the engagement authorization truly covers that reach.

## DNS and connection-time enforcement limits

When the scope contains IP/CIDR rules, hostname checks resolve the hostname and compare the current A/AAAA answers against the configured rules. Resolution errors fail closed, and an out-of-scope address overrides an allow rule. This is a **preflight check**, not a guarantee about the address ultimately contacted: DNS answers can change between the check and a tool's connection, and many external tools resolve the hostname independently.

For any deployment, do not treat the scope checker as a network firewall or as complete DNS-rebinding protection.

- Run tests in an isolated lab/VM or container with outbound network access restricted to the approved target ranges.
- Use a dedicated test engagement and a written target allowlist; review redirects, proxy settings, VPN routes, and pivot/port-forward paths.
- Do not use the default scope as authorization to scan arbitrary public hosts. It is intentionally limited to loopback and private ranges.
- Do not expose WHAXON to untrusted users or allow untrusted users to edit scope, configure tools, or invoke runner APIs.
- Keep `enabled: true`. Disabling scope removes this application-level guard and should only be considered in a deliberately isolated lab.
- Before production use, enforce destination IP policy at connection/egress level for each execution path (including external tools and pivoted sessions), then add integration tests proving that the actual connection cannot escape the allowlist.

A successful `whaxon scope --check` means the target passed the current application-level policy check. It does **not** prove that a later network connection is pinned to the checked address.
