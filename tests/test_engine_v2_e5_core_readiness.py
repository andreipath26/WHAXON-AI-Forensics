"""Engine V2 core readiness remains distinct from optional integration status."""
from types import SimpleNamespace

from whaxon.core import Core
from whaxon.interfaces.web.server import AsyncRunner, JobRegistry, create_app


def _client(tmp_path):
    core = Core(tmp_path)
    app = create_app(core, JobRegistry(core), AsyncRunner(core))
    app.config["TESTING"] = True
    return app.test_client(), core


def test_e5_optional_msf_outage_does_not_mark_durable_core_unready(tmp_path):
    client, core = _client(tmp_path)
    core.msf = SimpleNamespace(is_up=lambda: False)
    response = client.get("/api/health")
    assert response.status_code == 200
    state = response.get_json()
    assert state["status"] == "ok"
    assert state["core_ready"] is True
    assert state["checks"]["database"] == "ready"
    assert state["checks"]["data"] == "writable"
    assert state["checks"]["msf"] == "down"
    assert state["optional_degraded"] == ["msf"]


def test_e5_health_tests_core_data_dir_not_unrelated_environment_path(
    tmp_path, monkeypatch,
):
    client, core = _client(tmp_path)
    unrelated = tmp_path / "not-the-core-data"
    monkeypatch.setenv("WHAXON_DATA", str(unrelated))
    core.msf = SimpleNamespace(is_up=lambda: True)
    assert client.get("/api/health").status_code == 200
    assert not unrelated.exists()
    assert list(tmp_path.glob(".healthz*")) == []


def test_e5_database_failure_is_unready_even_when_msf_is_up(tmp_path, monkeypatch):
    client, core = _client(tmp_path)
    core.msf = SimpleNamespace(is_up=lambda: True)

    def fail_database():
        raise OSError("database must not leak full exception path")

    monkeypatch.setattr(core.store, "_conn", fail_database)
    response = client.get("/api/health")
    assert response.status_code == 503
    state = response.get_json()
    assert state["core_ready"] is False
    assert state["checks"]["database"] == "unavailable"
    assert "database must not leak" not in response.get_data(as_text=True)


def test_e5_data_directory_failure_is_unready(tmp_path):
    client, core = _client(tmp_path)
    core.msf = SimpleNamespace(is_up=lambda: True)
    non_directory = tmp_path / "not-a-directory"
    non_directory.write_text("file", encoding="utf-8")
    core.data_dir = non_directory
    response = client.get("/api/health")
    assert response.status_code == 503
    assert response.get_json()["core_ready"] is False
    assert response.get_json()["checks"]["data"] == "unavailable"


def test_e5_optional_msf_probe_exception_is_informational_not_service_failure(tmp_path):
    client, core = _client(tmp_path)

    def offline():
        raise RuntimeError("optional RPC offline")

    core.msf = SimpleNamespace(is_up=offline)
    response = client.get("/api/health")
    assert response.status_code == 200
    state = response.get_json()
    assert state["core_ready"] is True
    assert state["checks"]["msf"] == "unavailable"
    assert state["optional_degraded"] == ["msf"]
