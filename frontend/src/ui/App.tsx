import { useEffect, useRef, useState } from "react";
import { api } from "../api";

type Health = { ok?: boolean; status?: string; [key: string]: unknown };
type Tool = { id?: string; tool_id?: string; name?: string; description?: string; available?: boolean; adapter_available?: boolean };
type Scope = { [key: string]: unknown };
type ScopeCheck = { allowed?: boolean; reason?: string; [key: string]: unknown };

const navigation = [
  { id: "overview", label: "Overview" },
  { id: "scope", label: "Scope & targets" },
  { id: "run", label: "Run orchestration" },
];

export function App() {
  const [view, setView] = useState("overview");
  const [health, setHealth] = useState<"checking" | "online" | "offline">("checking");
  const [tools, setTools] = useState<Tool[]>([]);
  const [scope, setScope] = useState<Scope | null>(null);
  const [error, setError] = useState("");
  const [target, setTarget] = useState("");
  const [toolId, setToolId] = useState("");
  const [scopeResult, setScopeResult] = useState<ScopeCheck | null>(null);
  const [jobId, setJobId] = useState("");
  const [output, setOutput] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);
  const [jobStatus, setJobStatus] = useState<"idle" | "running" | "cancelling" | "finished" | "failed">("idle");
  const streamRef = useRef<EventSource | null>(null);

  useEffect(() => {
    let alive = true;
    void Promise.all([
      api<Health>("/api/health"),
      api<Tool[]>("/api/tools"),
      api<Scope>("/api/scope"),
    ]).then(([h, t, s]) => {
      if (!alive) return;
      if (h.ok === false) throw new Error("WHAXON health check reported a failure");
      const availableTools = Array.isArray(t) ? t.filter((tool) => tool.available === true && tool.adapter_available === true) : [];
      setHealth("online");
      setTools(availableTools);
      setScope(s);
      setToolId(String(availableTools[0]?.id ?? availableTools[0]?.tool_id ?? ""));
    }).catch((e: unknown) => {
      if (!alive) return;
      setHealth("offline");
      setError(e instanceof Error ? e.message : "Could not connect to WHAXON");
    });
    return () => { alive = false; streamRef.current?.close(); streamRef.current = null; };
  }, []);

  async function checkScopeFor(targetValue: string): Promise<ScopeCheck> {
    return api<ScopeCheck>("/api/scope/check", {
      method: "POST",
      body: JSON.stringify({ target: targetValue }),
    });
  }

  async function checkScope(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setScopeResult(null);
    try {
      setScopeResult(await checkScopeFor(target.trim()));
    } catch (e) {
      setError(e instanceof Error ? e.message : "Scope check failed");
    } finally {
      setBusy(false);
    }
  }

  async function runTool(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    setOutput([]);
    setJobStatus("idle");
    streamRef.current?.close();
    streamRef.current = null;
    setScopeResult(null);
    try {
      const checked = await checkScopeFor(target.trim());
      setScopeResult(checked);
      if (checked.allowed !== true) {
        throw new Error("The target was not confirmed in scope. No assessment was started.");
      }
      const result = await api<{ job_id?: string; id?: string }>("/api/run", {
        method: "POST",
        body: JSON.stringify({ tool_id: toolId, target: target.trim() }),
      });
      const id = String(result.job_id ?? result.id ?? "");
      if (!id) throw new Error("The server did not return a job identifier");
      setJobId(id);
      setJobStatus("running");
      const stream = new EventSource(`/api/jobs/${encodeURIComponent(id)}/stream`);
      streamRef.current = stream;
      stream.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as { text?: string; type?: string; error?: string };
          if (data.text) setOutput((lines) => [...lines, data.text!]);
          if (data.type === "failed") {
            setJobStatus("failed");
            setError(data.error ?? "Job failed");
            stream.close();
            if (streamRef.current === stream) streamRef.current = null;
          }
          if (data.type === "finished") {
            setJobStatus("finished");
            stream.close();
            if (streamRef.current === stream) streamRef.current = null;
          }
        } catch {
          setOutput((lines) => [...lines, event.data]);
        }
      };
      stream.onerror = () => {
        stream.close();
        if (streamRef.current === stream) streamRef.current = null;
        setError("Live output connection ended. Check job history for its persisted result.");
      };
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start the assessment");
    } finally {
      setBusy(false);
    }
  }

  async function cancelJob() {
    if (!jobId || jobStatus !== "running") return;
    setJobStatus("cancelling");
    setError("");
    try {
      const result = await api<{ ok?: boolean }>(`/api/jobs/${encodeURIComponent(jobId)}/cancel`, {
        method: "POST",
        body: JSON.stringify({}),
      });
      if (result.ok) {
        setOutput((lines) => [...lines, "Cancellation requested from the server."]);
      } else {
        setJobStatus("running");
        setError("The server could not cancel this job; it may already have finished.");
      }
    } catch (e) {
      setJobStatus("running");
      setError(e instanceof Error ? e.message : "Cancellation request failed");
    }
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <a className="brand" href="/" aria-label="WHAXON home"><span className="brand-mark">W</span><span><strong>WHAXON</strong><small>OBSIDIAN KINETIC</small></span></a>
        <p className="side-label">OPERATIONS</p>
        <nav aria-label="Main navigation">
          {navigation.map((item) => <button key={item.id} className={view === item.id ? "nav-item active" : "nav-item"} onClick={() => setView(item.id)}>{item.label}</button>)}
        </nav>
        <div className="sidebar-status"><span className={health === "online" ? "dot online" : "dot"} />{health === "online" ? "Backend connected" : health === "offline" ? "Backend unavailable" : "Connecting…"}</div>
      </aside>
      <main className="main">
        <header className="topbar"><div><p className="eyebrow">SECURITY OPERATIONS</p><h1>{navigation.find((item) => item.id === view)?.label ?? "Overview"}</h1></div><span className={health === "online" ? "status online" : "status"}>{health.toUpperCase()}</span></header>
        {error && <div className="alert" role="alert"><strong>Operation failed</strong><p>{error}</p><button onClick={() => setError("")}>Dismiss</button></div>}
        {view === "overview" && <section className="panel"><p className="eyebrow">LIVE STATUS</p><h2>WHAXON security operations</h2><p>Connected status and available tools are read from the running backend. No sample findings or simulated telemetry are displayed.</p><div className="metric-row"><div><small>Backend</small><strong>{health === "online" ? "Connected" : health === "offline" ? "Unavailable" : "Checking"}</strong></div><div><small>Runnable tools</small><strong>{tools.length}</strong></div></div><p>{tools.length ? "Only installed tools with detected WHAXON adapters are offered for execution." : "No installed, adapter-supported tools are currently available to run."}</p></section>}
        {view === "scope" && <section className="panel"><h2>Scope &amp; targets</h2><p>Check a target against the current server-side scope policy before starting work.</p><form onSubmit={checkScope}><label htmlFor="target-scope">Target</label><input id="target-scope" required value={target} onChange={(e) => { setTarget(e.target.value); setScopeResult(null); }} placeholder="Target permitted by your configured scope" /><button disabled={busy || !target.trim()}>{busy ? "Checking…" : "Check scope"}</button></form><pre>{scopeResult ? JSON.stringify(scopeResult, null, 2) : scope ? JSON.stringify(scope, null, 2) : "Loading configured scope…"}</pre></section>}
        {view === "run" && <section className="panel"><h2>Run orchestration</h2><p>Each submission first checks scope in the UI. The backend independently enforces authorization before execution.</p><form onSubmit={runTool}><label htmlFor="run-target">Target</label><input id="run-target" required value={target} onChange={(e) => { setTarget(e.target.value); setScopeResult(null); }} placeholder="Target permitted by configured scope" /><label htmlFor="run-tool">Tool</label><select id="run-tool" required value={toolId} onChange={(e) => setToolId(e.target.value)}>{tools.map((tool, index) => { const id = String(tool.id ?? tool.tool_id ?? ""); return <option key={id || index} value={id}>{tool.name ?? id}</option>; })}</select><button disabled={busy || !target.trim() || !toolId}>{busy ? "Checking scope / starting…" : "Start assessment"}</button>{!tools.length && <p role="status">No runnable tools are available. Install a supported tool and adapter before starting a job.</p>}</form>{scopeResult && <pre aria-live="polite">{JSON.stringify(scopeResult, null, 2)}</pre>}{jobId && <><h3>Job {jobId}</h3><p role="status">Status: {jobStatus.toUpperCase()}</p><pre aria-live="polite">{output.join("\n") || "Waiting for live job output…"}</pre>{(jobStatus === "running" || jobStatus === "cancelling") && <button onClick={() => void cancelJob()} disabled={jobStatus !== "running"}>{jobStatus === "cancelling" ? "Cancellation requested…" : "Cancel job"}</button>}</>}</section>}
      </main>
    </div>
  );
}
