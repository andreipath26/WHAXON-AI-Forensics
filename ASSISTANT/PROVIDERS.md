# LLM provider compatibility

Provider selection must be independent of the WHAXON security execution engine. Reuse the existing `src/whaxon/ai/providers/backends` interfaces, avoid parallel security planners, and expose provider readiness and the selected model visibly.

| Selection | Transport | Current basis | Notes |
| --- | --- | --- | --- |
| `kiln` | KILN local Ollama-compatible `/api/chat` and `/api/tags` | Verified in [KILN](https://github.com/andreipath26/KILN) source | Experimental local inference; explicit active-model match; port 11435 |
| `ollama` | Local `/api/chat` | Existing WHAXON Ollama backend | Port 11434 by default |
| `openai` | OpenAI API | Existing WHAXON OpenAI backend | API key required |
| `gemini` | Google Gemini API | Existing WHAXON Google backend | API key required |
| `claude` | Anthropic API | Existing WHAXON Anthropic backend | API key required |
| `mistral` | Mistral OpenAI-compatible chat completions | Existing WHAXON OpenAI transport with Mistral endpoint | API key required; provider-specific behavior needs contract tests |

ChatGPT and Claude consumer subscriptions are not interchangeable with API credentials; configure an approved API account and model. Additional local OpenAI-compatible servers may be added after endpoint validation and allowlisting.

## KILN findings (inspected current main, 2026-11-08)
KILN's `crates/kiln-api/src/server.rs` exposes `POST /api/chat`, `POST /api/generate`, `GET /api/tags` and `GET /api/version`. `crates/kiln-api/src/types.rs` implements the Ollama-shaped message and nonstreaming response envelopes. `cargo run -p kiln-cli -- serve` binds locally, default port 11435; optional `KILN_MODEL_PATH` selects the startup GGUF.

The current chat route uses role-prefixed text; model-specific chat-template application is not yet exposed by the shim. KILN's README warns that the runtime and end-to-end MoE streaming remain in development. Test model-specific prompt quality, structured action output, latency, watchdog behavior and token/context limits before allowing assistant planning tasks. The initial adapter can provide chat only; it is not proof of instruction-following parity with a hosted model.

## Privacy / resilience
- Default to an explicitly selected provider. No silent cloud fallback.
- Show local/remote and provider/model identity before sending any assessment context.
- Require opt-in for external data transfer; minimize and redact targets, findings, credentials and evidence by policy.
- Keep keys in environment/secret-store, never commit or log them.
- Validate allowed local endpoints; remote/custom URLs require separate trusted-host policy and TLS.
- Apply timeout, budget, cancellation, output size and error handling limits; do not claim production readiness from a configuration factory.
- A model may propose actions only. Scope/policy/approval services decide execution.
