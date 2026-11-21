"""Tests for MSF endpoints in whaxon.interfaces.web.server.

Session 2 of 3 for server coverage. These endpoints call
`registry.core.msf.*`, so tests monkeypatch `core.msf` with a FakeMSF.

Session 3 will cover portfwd (which needs `client.connect().sessions.session(id)`
returning a write/read object — a deeper mock) and the AI + evidence routes.

FakeMSF implements only the methods server.py calls:
    is_up, config.display, version, module_counts, sessions, session_exec,
    connect (returns an object with .modules.exploits/.auxiliary/.post)
"""
from __future__ import annotations

from whaxon.core import Core
from whaxon.interfaces.web.server import (
    AsyncRunner,
    JobRegistry,
    create_app,
)

# ---------------------------------------------------------------- FakeMSF

class _FakeConfig:
    def __init__(self):
        self.display_value = "http://127.0.0.1:55553"

    def display(self):
        return self.display_value


class _FakeModules:
    def __init__(self):
        self.exploits = ["exploit/unix/ftp/vsftpd_234_backdoor",
                         "exploit/multi/samba/usermap_script"]
        self.auxiliary = ["auxiliary/scanner/ssh/ssh_login"]
        self.post = ["post/multi/gather/env"]


class _FakeConnected:
    def __init__(self):
        self.modules = _FakeModules()


class FakeMSF:
    """Minimal stand-in for whaxon.core.msf.MSFClient."""

    def __init__(self, up=True):
        self._up = up
        self._sessions = {}
        self.config = _FakeConfig()
        self.exec_calls = []
        self.exec_response = "uid=0(root) gid=0(root)"

    def is_up(self):
        return self._up

    def version(self):
        return "6.5.3-dev"

    def module_counts(self):
        return {"exploits": 2, "auxiliary": 1, "post": 1}

    def sessions(self):
        return dict(self._sessions)

    def session_exec(self, session_id, command, timeout=15.0):
        self.exec_calls.append((session_id, command, timeout))
        return self.exec_response

    def connect(self):
        return _FakeConnected()


# ---------------------------------------------------------------- helpers

def _make_app(tmp_path, monkeypatch, fake_msf=None):
    monkeypatch.setenv("WHAXON_DATA", str(tmp_path))
    monkeypatch.delenv("WHAXON_AUTH_USER", raising=False)
    monkeypatch.delenv("WHAXON_AUTH_PASS_HASH", raising=False)

    core = Core(data_dir=tmp_path)
    if fake_msf is not None:
        monkeypatch.setattr(core, "msf", fake_msf)
        # Model the tracker having persisted the initial live-session identity.
        for session_id, info in fake_msf.sessions().items():
            if isinstance(info, dict):
                host = info.get("target_host") or info.get("tunnel_peer") or info.get("host") or "?"
                core.store.upsert_session(
                    str(session_id), str(host), str(info.get("type") or "?"), info
                )
    registry = JobRegistry(core)
    runner = AsyncRunner(core)
    app = create_app(core, registry, runner)
    app.config["TESTING"] = True
    return app, core


# ---------------------------------------------------------------- /api/msf/status

def test_msf_status_up(tmp_path, monkeypatch):
    fake = FakeMSF(up=True)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/status")
    assert r.status_code == 200
    data = r.get_json()
    assert data["up"] is True
    assert data["config"] == "http://127.0.0.1:55553"
    assert data["version"] == "6.5.3-dev"
    assert data["modules"] == {"exploits": 2, "auxiliary": 1, "post": 1}


def test_msf_status_down(tmp_path, monkeypatch):
    fake = FakeMSF(up=False)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/status")
    assert r.status_code == 200
    data = r.get_json()
    assert data["up"] is False
    assert "version" not in data
    assert "modules" not in data


# ---------------------------------------------------------------- /api/msf/sessions

def test_msf_sessions_empty(tmp_path, monkeypatch):
    fake = FakeMSF(up=True)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/sessions")
    assert r.status_code == 200
    data = r.get_json()
    assert data["live"] == {}
    assert data["live_count"] == 0
    assert isinstance(data["stored"], list)


def test_msf_sessions_with_live(tmp_path, monkeypatch):
    fake = FakeMSF(up=True)
    fake._sessions = {"1": {"host": "10.0.0.5", "type": "shell"}}
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/sessions")
    assert r.status_code == 200
    data = r.get_json()
    assert data["live_count"] == 1
    assert "1" in data["live"]


def test_msf_sessions_when_down(tmp_path, monkeypatch):
    fake = FakeMSF(up=False)
    fake._sessions = {"1": {"host": "10.0.0.5"}}
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/sessions")
    assert r.status_code == 200
    data = r.get_json()
    # sessions() only called when up
    assert data["live"] == {}
    assert data["live_count"] == 0


# ---------------------------------------------------------------- /api/msf/sessions/<id>

def test_msf_session_info_found(tmp_path, monkeypatch):
    fake = FakeMSF(up=True)
    fake._sessions = {"5": {"host": "10.0.0.9", "target_host": "10.0.0.9", "type": "meterpreter"}}
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/sessions/5")
    assert r.status_code == 200
    data = r.get_json()
    assert data["id"] == "5"
    assert data["info"]["host"] == "10.0.0.9"


def test_msf_session_info_not_found(tmp_path, monkeypatch):
    fake = FakeMSF(up=True)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/sessions/99")
    assert r.status_code == 404


def test_msf_session_info_when_down(tmp_path, monkeypatch):
    fake = FakeMSF(up=False)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/sessions/1")
    assert r.status_code == 503


# ---------------------------------------------------------------- retired legacy execution
def test_msf_session_exec_stays_blocked_with_stale_opt_in(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_LEGACY_MSF_EXECUTION_ENABLED", "true")
    fake = FakeMSF(up=True)
    fake._sessions = {"1": {"target_host": "127.0.0.1", "type": "shell"}}
    app, _ = _make_app(tmp_path, monkeypatch, fake)

    response = app.test_client().post(
        "/api/msf/sessions/1/exec", json={"command": "id"},
    )

    assert response.status_code == 410
    body = response.get_json()
    assert body["legacy_execution_enabled"] is False
    assert body["approval_granted"] is False
    assert body["execution_submitted"] is False
    assert fake.exec_calls == []


# ---------------------------------------------------------------- /api/msf/modules/<type>

def test_msf_modules_exploit(tmp_path, monkeypatch):
    fake = FakeMSF(up=True)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/modules/exploit")
    assert r.status_code == 200
    data = r.get_json()
    assert len(data) == 2
    assert "vsftpd" in data[0]


def test_msf_modules_bad_type(tmp_path, monkeypatch):
    fake = FakeMSF(up=True)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/modules/nonsense")
    assert r.status_code == 400


def test_msf_modules_when_down(tmp_path, monkeypatch):
    fake = FakeMSF(up=False)
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    r = app.test_client().get("/api/msf/modules/exploit")
    assert r.status_code == 503


# ---------------------------------------------------------------- retired legacy launch
def test_msf_run_stays_blocked_with_stale_opt_in_without_creating_job(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_LEGACY_MSF_EXECUTION_ENABLED", "true")
    fake = FakeMSF(up=True)
    app, core = _make_app(tmp_path, monkeypatch, fake)
    before = core.store.history()

    response = app.test_client().post("/api/msf/run", json={
        "module_type": "exploit",
        "module_path": "multi/samba/usermap_script",
        "target": "127.0.0.1",
        "options": {"RHOSTS": "127.0.0.1"},
    })

    assert response.status_code == 410
    body = response.get_json()
    assert body["legacy_execution_enabled"] is False
    assert body["approval_granted"] is False
    assert body["execution_submitted"] is False
    assert core.store.history() == before


def test_pivot_candidates_stay_blocked_with_stale_opt_in(tmp_path, monkeypatch):
    monkeypatch.setenv("WHAXON_LEGACY_MSF_EXECUTION_ENABLED", "true")
    fake = FakeMSF(up=True)
    fake._sessions = {"1": {"target_host": "127.0.0.1", "type": "shell"}}
    app, _ = _make_app(tmp_path, monkeypatch, fake)
    calls = []

    from whaxon.core import autopivot
    monkeypatch.setattr(
        autopivot, "detect",
        lambda *args: calls.append(args) or [{"cidr": "10.0.0.0/24"}],
    )

    response = app.test_client().get("/api/pivot/candidates")

    assert response.status_code == 410
    body = response.get_json()
    assert body["legacy_execution_enabled"] is False
    assert body["approval_granted"] is False
    assert body["execution_submitted"] is False
    assert calls == []


