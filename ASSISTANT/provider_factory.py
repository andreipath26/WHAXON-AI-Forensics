"""Initial provider selector for WHAXON ASSISTANT; no security tool execution.

Reuse WHAXON LLMBackend adapters. KILN offers Ollama-shaped local chat,
but is separately named to make the selected inference runtime explicit.
"""
from __future__ import annotations

import os
from dataclasses import dataclass

from whaxon.ai.providers.backends.anthropic import AnthropicBackend
from whaxon.ai.providers.backends.google import GoogleBackend
from whaxon.ai.providers.backends.ollama import OllamaBackend
from whaxon.ai.providers.backends.openai import OpenAIBackend

KILN_URL = "http://127.0.0.1:11435"
MISTRAL_URL = "https://api.mistral.ai"


@dataclass(frozen=True)
class ProviderSettings:
    provider: str
    model: str
    host: str | None = None
    api_key: str | None = None


class KilnBackend(OllamaBackend):
    """KILN's verified Ollama-compatible local /api/chat and /api/tags API."""

    name = "kiln"

    def __init__(self, model: str, **options):
        host = options.pop("host", None) or KILN_URL
        # Prevent a misleading 'local' label from silently routing to the internet.
        if host not in (KILN_URL, "http://localhost:11435", "http://[::1]:11435"):
            raise ValueError("KILN is loopback-only; remote endpoints need a separately reviewed transport")
        super().__init__(model=model, host=host, **options)


class MistralBackend(OpenAIBackend):
    """Mistral's OpenAI-compatible chat-completions transport."""

    name = "mistral"

    def __init__(self, model: str, api_key: str | None = None, **options):
        key = api_key or os.environ.get("MISTRAL_API_KEY")
        super().__init__(model=model, host=MISTRAL_URL, api_key=key, **options)
        # Do not accidentally borrow OPENAI_API_KEY when Mistral is unconfigured.
        self.api_key = key or ""

    def available(self):
        if not self.api_key:
            return False, "MISTRAL_API_KEY not set"
        return True, ""


def build_backend(settings: ProviderSettings):
    """Return a backend; does not send data or authorize any activity."""
    provider = settings.provider.strip().lower()
    model = settings.model.strip()
    if not model:
        raise ValueError("model must be set explicitly")
    if provider == "kiln":
        return KilnBackend(model=model, host=settings.host)
    if provider == "ollama":
        if settings.host is not None and settings.host not in (
            "http://127.0.0.1:11434", "http://localhost:11434", "http://[::1]:11434"):
            raise ValueError("Ollama remote host requires separately reviewed transport")
        return OllamaBackend(model=model, host=settings.host)
    if provider in ("openai", "chatgpt"):
        if settings.host:
            raise ValueError("custom OpenAI host requires reviewed transport")
        return OpenAIBackend(model=model, api_key=settings.api_key)
    if provider in ("gemini", "google"):
        if settings.host:
            raise ValueError("custom Gemini host requires reviewed transport")
        return GoogleBackend(model=model, api_key=settings.api_key)
    if provider in ("claude", "anthropic"):
        if settings.host:
            raise ValueError("custom Anthropic host requires reviewed transport")
        return AnthropicBackend(model=model, api_key=settings.api_key)
    if provider == "mistral":
        if settings.host:
            raise ValueError("custom Mistral host requires reviewed transport")
        return MistralBackend(model=model, api_key=settings.api_key)
    raise ValueError("unknown provider: " + provider)
