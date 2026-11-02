# Writing an Adapter

An adapter parses tool output into structured `Finding` objects. The runner executes the tool; the adapter must not launch a second process.

**Adding an adapter inside WHAXON:** use this guide. **Shipping an adapter as a separate Python package:** use [Plugins](plugins.md).

## Adapter contract

`whaxon.adapters.base.Adapter` is an abstract base class with one required method, `parse`:

```python
from whaxon.adapters.base import Adapter
from whaxon.core.findings import Finding


class MyAdapter(Adapter):
    tool_id = "mytool"  # must match the catalog tool id

    def parse(self, lines, ctx=None) -> list[Finding]:
        findings = []
        for stream, text in lines:
            if stream != "stdout":
                continue
            # Parse the line and append Finding(...) objects.
        return findings
```

The runner supplies `lines` as a list of `(stream, text)` tuples; `stream` is `"stdout"` or `"stderr"`. The optional `ctx` dictionary may contain `tool_id`, `target`, `extra_args` and the executed `argv`.

## Finding fields

The `Finding` dataclass accepts:

- `kind`, `severity`, `source`, `data` — required structured fields.
- `raw_line` — original source line; the dataclass does not impose a universal truncation limit.
- `remediation`, `impact`, `cvss`, `cwe`, `references` — optional enrichment.
- `lookup_hint` — optional search hint for a later lookup.
- `request_context` — optional request context used by deterministic validation and retest flows.

Keep raw evidence useful but minimize unnecessary sensitive data. Do not assume the persistence or report layer will scrub secrets from a finding.

## Registration

Built-in adapters are imported by `src/whaxon/adapters/registry.py` and self-register by tool ID. To add an in-repository adapter:

1. Implement the adapter in `src/whaxon/adapters/`.
2. Add its module to the registry's built-in autoload list.
3. Ensure its tool ID exists in the effective catalog.
4. Add parser and runner integration tests.

Third-party packages use the `whaxon.adapters` Python entry-point group; see [Plugins](plugins.md). The runtime registry is available through `whaxon.adapters.list_adapters()`.

## Using context

Context can distinguish subcommands that share one catalog tool ID. For example:

```python
def parse(self, lines, ctx=None):
    ctx = ctx or {}
    extra = (ctx.get("extra_args") or "").strip()
    argv = ctx.get("argv") or []
    subtool = extra.split()[0] if extra else (argv[1] if len(argv) > 1 else "")

    if subtool == "secretsdump":
        return self._parse_secretsdump(lines)
    return []
```

See `src/whaxon/adapters/impacket.py` for a concrete multi-command adapter.

## Testing

Test parsers against representative captured output; parser tests should not spawn the external tool.

```bash
python -m pytest tests/test_myadapter.py -v
```

## Built-in adapter modules

The registry's built-in loader currently includes Nmap, Nikto, Burp, SQLmap, Gobuster, ffuf, Nuclei, WPScan, Hashcat, WHOIS, dig, WhatWeb, theHarvester, DNSRecon, Hydra, Metasploit, generic session, SMB session, NetExec, Arjun, WMI session and Commix adapters. The Impacket adapter is imported by the adapters package. The effective registry may skip an adapter whose import fails; inspect `list_adapters()` at runtime rather than treating this source list as proof that every adapter loaded.

## Anti-patterns

- Do not spawn the tool from `parse()`; the runner already executed it.
- Do not mutate the supplied `lines` list.
- Do not swallow parser exceptions or silently turn parse failures into empty findings.
- Do not put credentials or other secrets into finding payloads.
