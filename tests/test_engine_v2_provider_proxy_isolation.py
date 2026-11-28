"""Catalog provider subprocesses must not inherit environment proxy routes."""
from __future__ import annotations

import pytest

from whaxon.core.providers import _provider_process_environment


@pytest.mark.parametrize(
    "name",
    (
        "HTTP_PROXY",
        "http_proxy",
        "HTTPS_PROXY",
        "https_proxy",
        "ALL_PROXY",
        "all_proxy",
        "FTP_PROXY",
        "ftp_proxy",
        "NO_PROXY",
        "no_proxy",
    ),
)
def test_provider_environment_strips_ambient_proxy_settings(monkeypatch, name):
    monkeypatch.setenv("PATH", "/fixture/bin")
    monkeypatch.setenv(name, "http://proxy.example:8080")

    environment = _provider_process_environment()

    assert environment.get("PATH") == "/fixture/bin"
    assert not any(key.upper() == name.upper() for key in environment)
