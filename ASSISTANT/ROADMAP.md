# ASSISTANT workstream under WHAXON master roadmap

This workstream is subordinate to the repository root WHAXON master product roadmap; it does not reorder Engine V2/UI V2 or their release gates.

- A1 Inventory: complete per-command JARVIS matrix, threats, license notices, WHAXON overlap and capability admission.
- A2 Provider abstraction: use existing WHAXON LLMBackend; support KILN, Ollama, OpenAI, Gemini, Claude, Mistral; test auth, errors, model readiness and no-cloud fallback.
- A3 Assistant domain: typed intents, capability discovery, optional conversation memory, system desktop helper; never raw shell execution from the model.
- A4 Voice: push-to-talk, transcription, optional TTS, confirmation UI, accessibility and no-microphone fallback.
- A5 UI/CLI integration: progressive disclosure with advanced WHAXON parameters retained; one execution policy boundary.
- A6 Acceptance: provider contract/failure tests, voice red-team tests, WHAXON regression, per-command retention, memory/privacy and performance budget tests.
- A7 Qualification: after agreed WHAXON implementation and internal tests, carry out the separately deferred real authorized-target and production qualifications.

Status: A1/A2 scaffolding started on a feature branch; no claim of a completed assistant or certified provider integration.
