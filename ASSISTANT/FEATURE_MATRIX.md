# JARVIS source feature retention inventory

Source: user-supplied JARVIS Kali Dragon Edition Python script and README. The original script is not vendored into WHAXON until licensing, correctness and security review. This inventory covers functional groups, not a promise that each advertised command works correctly upstream.

| Group | Examples | WHAXON ASSISTANT destination |
| --- | --- | --- |
| Dialogue | greetings, jokes, help, time/date, exit | Optional persona and deterministic intents |
| Desktop launching | browsers, editor, terminals, Kali GUI tools | Local desktop helper, least privilege |
| System observations | CPU/RAM/disk, processes, interfaces, root detection | Read-only diagnostics |
| Files | listing directories, opening folders, wordlists | Sandboxed local helper |
| Discovery | installable tool list, find executable, installation | WHAXON readiness for security tools; separately governed local app installs |
| Security tools | nmap, nikto, gobuster, wpscan, sqlmap, metasploit, wireshark, burp, searchsploit, hashcat, hydra, wireless tools | WHAXON capability provider only if in scope and supported; otherwise desktop launch/unsupported classification |
| Target context | set/show target, history | WHAXON scope/engagement/mission read and proposal services |
| Reporting | generate report templates | WHAXON evidence-backed reporting plus optional drafting helper |
| Preferences | aliases, favorite tools, work mode | Safe structured per-user preferences |
| Persistent history | conversation and memory | Structured opt-in encrypted/retention-managed data; no pickle |
| Web search | browser shortcuts and queries | URL-safe local opener; external network opt-in |
| Background execution | threads for interactive utilities | Supervised desktop jobs or WHAXON durable execution |
| Planned upstream | voice, plugin system, session recording, backup, Docker | Explicit development tasks, not represented as existing features |

Original code defects to address: import-time undefined USER_NAME in Config, shell=True target interpolation, pickle deserialization, missing KaliUtils.launch_security_tool_async, overlapping parser matches and inaccurate success status for detached processes.

Acceptance: expand this table into a per-command manifest with upstream invocation, exact behavior, destination, permission boundary, tests and supported/unsupported status before declaring feature-parity completion.
