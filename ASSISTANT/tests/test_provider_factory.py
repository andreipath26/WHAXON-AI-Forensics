"""Configuration-only tests: never connect to any model provider."""
import unittest
from unittest.mock import patch

from ASSISTANT.provider_factory import (
    KilnBackend, MistralBackend, ProviderSettings, build_backend,
)


class ProviderFactoryTests(unittest.TestCase):
    def test_kiln_is_loopback_and_has_correct_name(self):
        b = build_backend(ProviderSettings(provider="kiln", model="test.gguf"))
        self.assertIsInstance(b, KilnBackend)
        self.assertEqual(b.host, "http://127.0.0.1:11435")
        self.assertEqual(b.name, "kiln")

    def test_kiln_rejects_remote_host(self):
        with self.assertRaises(ValueError):
            build_backend(ProviderSettings(provider="kiln", model="x", host="https://example.org"))

    def test_mistral_endpoint(self):
        b = build_backend(ProviderSettings(provider="mistral", model="mistral-small", api_key="test"))
        self.assertIsInstance(b, MistralBackend)
        self.assertEqual(b.host, "https://api.mistral.ai")
        self.assertEqual(b.name, "mistral")

    def test_all_provider_names(self):
        cases = ("ollama", "openai", "gemini", "claude", "mistral", "kiln")
        for p in cases:
            with self.subTest(p=p):
                self.assertIsNotNone(build_backend(ProviderSettings(provider=p, model="test", api_key="test")))

    def test_unknown_and_empty_model(self):
        with self.assertRaises(ValueError):
            build_backend(ProviderSettings(provider="unsupported", model="test"))
        with self.assertRaises(ValueError):
            build_backend(ProviderSettings(provider="kiln", model="  "))

    def test_no_api_key_is_visible_for_mistral(self):
        with patch.dict("os.environ", {"MISTRAL_API_KEY": ""}):
            b = build_backend(ProviderSettings(provider="mistral", model="test"))
            ok, reason = b.available()
            self.assertFalse(ok)
            self.assertIn("MISTRAL_API_KEY", reason)


if __name__ == "__main__":
    unittest.main()
