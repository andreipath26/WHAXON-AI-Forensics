# Tool Catalog and Execution

The packaged catalog is maintained at `src/whaxon/data/tools.json`. It describes command-backed tools and session operations. The effective runtime catalog and availability should be checked through `GET /api/tools`; do not assume every catalog entry is installed or usable on every host.

## Catalog model

A command-backed entry may include:

- `id`: stable tool identifier used by the runner, API and adapters.
- `name`: display name.
- `category`: functional grouping.
- `binary`: executable name or path resolved by the runtime.
- `description`: operator-facing summary.
- `args`: argument template used by the adapter and runner.
- `package`: package hint; it is not by itself permission to install software.

Session-backed entries use a transport and command rather than a local executable. They operate through an existing session and are not standalone binaries. The tool catalog is not an authorization policy: scope checks and the execution path still govern whether an action can run.

## Catalog entries in the current main snapshot

The packaged catalog contains 24 entries:

| ID | Kind |
|---|---|
| `nmap` | Command |
| `nikto` | Command |
| `gobuster` | Command |
| `echo` | Test command |
| `sqlmap` | Command |
| `whois` | Command |
| `dig` | Command |
| `nuclei` | Command |
| `commix` | Command |
| `ffuf` | Command |
| `wpscan` | Command |
| `impacket` | Command |
| `theharvester` | Command |
| `dnsrecon` | Command |
| `msf_sysinfo` | Metasploit session |
| `msf_getuid` | Metasploit session |
| `msf_hashdump` | Metasploit session |
| `ssh_cmd` | SSH session |
| `smb_shares` | SMB session |
| `smb_ls` | SMB session |
| `netexec` | Command |
| `arjun` | Command |
| `wmi_exec` | Session operation |
| `hydra` | Command |

This list is a snapshot of the packaged catalog on 2026-11-02. The live API is authoritative for the runtime actually installed.

## Availability and installation

Use `GET /api/tools` to inspect tool IDs and current availability. A missing optional executable does not mean the WHAXON core is unavailable. Use `whaxon doctor` and the [dependency readiness guide](dependency-readiness.md) to diagnose dependencies and review an allowlisted installation plan. A catalog `package` value is not sufficient approval to invoke a package manager.

## Adding or changing a tool

1. Update the packaged catalog and any relevant adapter or provider registration.
2. Add or update parser, invocation, scope and failure-mode tests.
3. Confirm exact argv construction and that user-controlled values cannot bypass scope validation.
4. Update dependency diagnostics and installation policy separately where appropriate.
5. Verify the effective catalog through the API and run the relevant tests.

For output parsing, see [Writing an Adapter](adapters.md). For third-party adapter packages, see [Plugins](plugins.md).
