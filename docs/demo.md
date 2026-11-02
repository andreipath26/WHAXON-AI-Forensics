# Demo Script

A scripted walkthrough for a controlled lab. Use a Metasploitable2 VM or another target you own and have explicitly authorized. The example address below is illustrative; substitute the actual lab address and add it to the active scope before running any tool.

## 0:00 - Setup

```bash
cd WHAXON-AI-Forensics
source .venv/bin/activate
whaxon web
```

Open [http://127.0.0.1:5001/](http://127.0.0.1:5001/). The root route redirects to the canonical `/ui-v2` interface. Loopback requests use the local-peer authentication shortcut; if prompted, use locally configured credentials. Never expose default credentials remotely.

## 0:10 - Scope check

```bash
whaxon scope --show
whaxon scope --check 10.0.0.42
```

Confirm that the target is explicitly listed and authorized. Private addressing is not proof of authorization; scope checks are application-level preflight controls, not a network firewall.

## 0:20 - Run a tool

In the browser, select nmap, enter the explicitly authorized lab target, and submit the job. Review streamed output, persisted findings and evidence. Do not assume every nmap line becomes a finding; parser coverage and tool output determine what is recorded.

## 0:35 - Review findings

Open the job's findings and inspect the raw evidence and coverage. Correlation is data-dependent: only describe a correlated finding if the actual run produced one. Do not stage or imply a finding that was not observed.

## 0:45 - AI planner

AI planning is optional and provider-dependent. If enabled, use a lab target and review the proposed plan. A proposal is not authorization or execution evidence; only supported, approved actions can be executed.

## 1:05 - Reports

Export a report for the selected job. Review the coverage, verification state and limitations before presenting it as a client deliverable. Reports contain only the data actually persisted by the selected workflow.

## 1:20 - Cleanup

Stop the foreground server with Ctrl+C. If you deliberately started it as a daemon, use the PID file documented by the installed version and confirm the PID belongs to WHAXON before terminating it.

## Recording notes

- Use a lab target and show the active scope before execution.
- Do not fabricate findings or claim planner proposals were executed.
- Keep credentials, customer data and sensitive evidence out of screenshots and recordings.
