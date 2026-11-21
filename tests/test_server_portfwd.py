"""Legacy Metasploit port-forward endpoints cannot dispatch session commands."""
from __future__ import annotations

import pytest

from whaxon.core import Core
from whaxon.core import portfwd
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app


class _FakeMSF:
    def is_up(self):
        return True

    def sessions(self):
        return {"1": {"target_host": "127.0.0.1", "type": "shell"}}


def _make_app(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_DATA", str(tmp_path))
    monkeypatch.delenv("WHAXON_AUTH_USER", raising=False)
    monkeypatch.delenv("WHAXON_AUTH_PASS_HASH", raising=False)
    core = Core(data_dir=tmp_path)
    fake = _FakeMSF()
    monkeypatch.setattr(core, "msf", fake)
    core.store.upsert_session("1", "127.0.0.1", "shell", fake.sessions()["1"])
    app = create_app(core, JobRegistry(core), AsyncRunner(core))
    app.config["TESTING"] = True
    return app


@pytest.mark.parametrize("method,path,payload,operation", [
    ("get", "/api/msf/sessions/1/portfwd", None, "list_live"),
    ("post", "/api/msf/sessions/1/portfwd", {"lport": 8080, "rhost": "127.0.0.1", "rport": 80}, "add_forward"),
    ("delete", "/api/msf/sessions/1/portfwd", {"lport": 8080}, "remove_forward"),
])
def test_port_forward_operations_stay_blocked_with_stale_opt_in(
    tmp_path, monkeypatch, method, path, payload, operation,
):
    monkeypatch.setenv("WHAXON_LEGACY_MSF_EXECUTION_ENABLED", "true")
    calls = []
    monkeypatch.setattr(portfwd, operation, lambda *args, **kwargs: calls.append(args))
    app = _make_app(tmp_path, monkeypatch)

    response = getattr(app.test_client(), method)(path, json=payload)

    assert response.status_code == 410
    body = response.get_json()
    assert body["legacy_execution_enabled"] is False
    assert body["approval_granted"] is False
    assert body["execution_submitted"] is False
    assert calls == []
