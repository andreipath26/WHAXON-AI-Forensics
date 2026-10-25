import { useEffect, useState } from "react";
import { api } from "../api";

type Health = { ok?: boolean; status?: string; [key: string]: unknown };
type Tool = { id?: string; tool_id?: string; name?: string; description?: string };
type Scope = { [key: string]: unknown };

const navigation = [
  { id: "overview", label: "Overview" },
  { id: "scope", label: "Scope & targets" },
  { id: "run", label: "Run orchestration" },
  { id: "findings", label: "Findings" },
  { id: "evidence", label: "Evidence" },
];

export function App() {
  const [view, setView] = useState("overview");
  const [health, setHealth] = useState<"checking" | "online" | "offline">("checking");
  const [tools, setTools] = useState<Tool[]>([]);
  const [scope, setScope] = useState<Scope | null>(null);
  const [error, setError] = useState("");
  const [target, setTarget] = useState("");
  const [toolId, setToolId] = useState("");
  const [scopeResult, setScopeResult] = useState<unknown>(null);
  const [jobId, setJobId] = useState("");
  const [output, setOutput] = useState<string[]>([]);
  const [busy, setBusy] = useState(false);

  useEffect(() => {
    let alive = true;
    void Promise.all([
      api<Health>("/api/health"),
      api<Tool[]>("/api/tools"),
      api<Scope>("/api/scope"),
    ]).then(([h, t, s]) => {
      if (!alive) return;
      if (h.ok === false) throw new Error("WHAXON health check reported a failure");
      setHealth("online");
      setTools(Array.isArray(t) ? t : []);
      setScope(s);
      setToolId(String(t[0]?.id ?? t[0]?.tool_id ?? ""));
    }).catch((e: unknown) => {
      if (!alive) return;
      setHealth("offline");
      setError(e instanceof Error ? e.message : "Could not connect to WHAXON");
    });
    return () => { alive = false; };
  }, []);

  async function checkScope(event: React.FormEvent) {
    event.preventDefault();
    setBusy(true);
    setError("");
    try {
      setScopeResult(await api("/api/scope/check", {
        method: "POST",
        body: JSON.stringify({ target: target.trim() }),
      }));
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
    try {
      const result = await api<{ job_id?: string; id?: string }>("/api/run", {
        method: "POST",
        body: JSON.stringify({ tool_id: toolId, target: target.trim() }),
      });
      const id = String(result.job_id ?? result.id ?? "");
      if (!id) throw new Error("The server did not return a job identifier");
      setJobId(id);
      const stream = new EventSource(`/api/jobs/${encodeURIComponent(id)}/stream`);
      stream.onmessage = (event) => {
        try {
          const data = JSON.parse(event.data) as { text?: string; type?: string; error?: string };
          if (data.text) setOutput((lines) => [...lines, data.text!]);
          if (data.type === "failed") {
            setError(data.error ?? "Job failed");
            stream.close();
          }
          if (data.type === "finished") stream.close();
        } catch {
          setOutput((lines) => [...lines, event.data]);
        }
      };
      stream.onerror = () => {
        stream.close();
        setError("Live output connection ended. Check job history for its persisted result.");
      };
    } catch (e) {
      setError(e instanceof Error ? e.message : "Could not start the assessment");
    } finally {
      setBusy(false);
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
        {view === "overview" && <section className="panel"><p className="eyebrow">LIVE STATUS</p><h2>WHAXON security operations</h2><p>Connected status and available tools are read from the running backend. No sample findings or simulated telemetry are displayed.</p><div className="metric-row"><div><small>Backend</small><strong>{health === "online" ? "Connected" : health === "offline" ? "Unavailable" : "Checking"}</strong></div><div><small>Available tools</small><strong>{tools.length}</strong></div></div></section>}
        {view === "scope" && <section className="panel"><h2>Scope &amp; targets</h2><p>Check a target against the current server-side scope policy before starting work.</p><form onSubmit={checkScope}><label htmlFor="target-scope">Target</label><input id="target-scope" required value={target} onChange={(e) => setTarget(e.target.value)} placeholder="Target permitted by your configured scope" /><button disabled={busy || !target.trim()}>{busy ? "Checking…" : "Check scope"}</button></form><pre>{scopeResult ? JSON.stringify(scopeResult, null, 2) : scope ? JSON.stringify(scope, null, 2) : "Loading configured scope…"}</pre></section>}
        {view === "run" && <section className="panel"><h2>Run orchestration</h2><p>Only tools returned by the live backend catalog are selectable.</p><form onSubmit={runTool}><label htmlFor="run-target">Target</label><input id="run-target" required value={target} onChange={(e) => setTarget(e.target.value)} placeholder="Target permitted by configured scope" /><label htmlFor="run-tool">Tool</label><select id="run-tool" required value={toolId} onChange={(e) => setToolId(e.target.value)}>{tools.map((tool, index) => { const id = String(tool.id ?? tool.tool_id ?? ""); return <option key={id || index} value={id}>{tool.name ?? id}</option>; })}</select><button disabled={busy || !target.trim() || !toolId}>{busy ? "Starting…" : "Start assessment"}</button></form>{jobId && <><h3>Job {jobId}</h3><pre aria-live="polite">{output.join("\n") || "Waiting for persisted job output…"}</pre></>}</section>}
        {view === "findings" && <section className="panel"><h2>Findings</h2><p>Finding review is hidden until a selected persisted job and its finding lifecycle are fully integrated in this frontend.</p><p>Use the existing report workflow for findings until that integration is complete.</p></section>}
        {view === "evidence" && <section className="panel"><h2>Evidence</h2><p>Evidence operations remain hidden until job-bound listing, upload, note persistence, download, and deletion have complete acceptance coverage.</p></section>}
      </main>
    </div>
  );
}
