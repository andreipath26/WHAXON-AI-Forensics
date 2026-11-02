# AI Planning and Execution

WHAXON's optional AI subsystem separates **planning** from **execution**. The provider proposes one typed action at a time. The deterministic executor validates the proposal and, when allowed, invokes the existing tool runner. The model itself does not own a process runner, database or scope manager.

AI is disabled by default. With the default `null` provider, a run stops without invoking tools.

## Configuration

Set the master switch and select a provider explicitly:

```bash
export WHAXON_AI_ENABLED=true
export WHAXON_AI_PROVIDER=ollama   # null, rules, ollama, openai, anthropic, google
export WHAXON_AI_MODEL=qwen2.5:1.5b
whaxon ai "assess the explicitly authorized lab target"
```

Provider credentials and model settings are backend-specific:

- Ollama uses `WHAXON_OLLAMA_HOST` (default `http://127.0.0.1:11434`).
- OpenAI uses `OPENAI_API_KEY` and optionally `WHAXON_OPENAI_HOST`.
- Anthropic uses `ANTHROPIC_API_KEY`.
- Google uses `GOOGLE_API_KEY` or `GEMINI_API_KEY`.

`WHAXON_AI_PROVIDER=rules` selects a deterministic rules provider, not an LLM. Unknown provider names fall back to the null provider. Default model names are defined in `src/whaxon/core/ai_bridge.py`; they can change and are not model compatibility guarantees.

## Safety boundary

The planner returns a typed `Action`; it cannot directly invoke a tool. The executor is the only AI path that turns an action into a tool invocation. It checks the catalog and current scope before calling the runner, and records action results. Human questions and stop actions do not invoke tools.

This boundary does not make autonomous execution risk-free. The operator remains responsible for explicit authorization, scope configuration, provider choice, model quality, credentials and review of results. A proposal is not proof that a scan ran; persisted job state and evidence are the record of execution.

## Limits and controls

- `WHAXON_AI_MAX_STEPS` sets the step budget (default 12).
- `WHAXON_AI_MIN_CONFIDENCE` sets the confidence floor for tool proposals (default 0.55).
- The executor also applies a wall-clock limit and deterministic validation.
- Provider responses can be malformed, inaccurate or based on hallucinated targets; validation must reject actions that do not pass policy.
- A cloud provider receives the prompt and context sent to it. Do not send client data to a provider unless the engagement permits it.
- The AI run event stream is available through `GET /api/ai/runs/<run_id>/stream`; this is run-event streaming, not a guarantee that the underlying model streams token-by-token output.

## Audit trail

AI run and step records are persisted in SQLite (`ai_runs` and `ai_run_steps`). The API exposes:

- `GET /api/ai/runs`
- `GET /api/ai/runs/<run_id>`
- `GET /api/ai/pending`
- `POST /api/ai/runs/<run_id>/answer`
- `GET /api/ai/runs/<run_id>/stream`

See the source under `src/whaxon/ai/` and `src/whaxon/core/ai_bridge.py` for the current planner/executor contract.
