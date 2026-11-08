# WHAXON ASSISTANT

The dedicated home for the JARVIS-derived WHAXON assistant and its planned voice, local-desktop, and multi-LLM integrations.

**Status:** foundation work; this does not mean the assistant or voice controls are shipped. This directory does not supersede WHAXON Engine V2, UI V2, or their master roadmap.

## Principles
- Preserve every supported WHAXON professional feature and full-detail control.
- Inventory every original JARVIS capability, then rebuild it through governed WHAXON services or separately permissioned desktop helpers.
- Never create a second security execution engine; every security action passes WHAXON's existing scope, policy, approval, scheduler and audit controls.
- Use deterministic commands without an LLM; AI is optional.
- Local first. No provider auto-fallback or cloud transmission without affirmative configuration.
- Support voice input/output as another interface, never as approval authority.

## Files
- [ARCHITECTURE.md](ARCHITECTURE.md): system boundaries.
- [FEATURE_MATRIX.md](FEATURE_MATRIX.md): original JARVIS retention plan.
- [PROVIDERS.md](PROVIDERS.md): provider matrix, including KILN.
- [VOICE.md](VOICE.md): voice development and safety.
- [ROADMAP.md](ROADMAP.md): work sequence and gates.
- [provider_factory.py](provider_factory.py): initial provider selection using existing WHAXON adapters.
- [tests/test_provider_factory.py](tests/test_provider_factory.py): no-network configuration tests.

## Developer example

```python
from ASSISTANT.provider_factory import ProviderSettings, build_backend

# KILN runs locally at http://127.0.0.1:11435 by default.
backend = build_backend(ProviderSettings(provider="kiln", model="exact-active-model-name"))
ready, why = backend.available()
if ready:
    answer = backend.chat([{"role": "user", "content": "Hello"}])
```

A model must first be loaded in KILN. The example is not an execution permission, and a successful text response is not proof of suitability for planning. Use `cargo run -p kiln-cli -- serve` in the separate KILN checkout.

To run the initial tests from the WHAXON checkout: `python -m unittest discover -s ASSISTANT/tests -v`.
