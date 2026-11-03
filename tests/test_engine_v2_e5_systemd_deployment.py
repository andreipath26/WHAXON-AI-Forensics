"""E5 service-mode deployment must use the durable foreground worker."""
import configparser
import shlex
from pathlib import Path

from whaxon.interfaces.cli.workflow_cmd import _parser

ROOT = Path(__file__).resolve().parents[1]


def _unit(filename):
    parser = configparser.ConfigParser(interpolation=None)
    parser.read(ROOT / filename, encoding="utf-8")
    return parser


def test_systemd_worker_shares_web_identity_and_persistent_state():
    web = _unit("whaxon.service")["Service"]
    worker = _unit("whaxon-workflow-worker.service")["Service"]
    for key in (
        "User", "Group", "WorkingDirectory", "EnvironmentFile",
        "Environment", "ReadWritePaths", "StateDirectory",
        "StateDirectoryMode", "RequiresMountsFor",
    ):
        assert worker[key] == web[key], key
    assert worker["StateDirectory"] == "whaxon"
    assert worker["StateDirectoryMode"] == "0700"
    assert worker["RequiresMountsFor"] == "/var/lib/whaxon"
    assert worker["Type"] == "simple"
    assert worker["Restart"] == "on-failure"
    assert worker["NoNewPrivileges"] == "true"
    assert worker["ProtectSystem"] == "strict"
    assert worker["ProtectHome"] == "true"
    assert worker["UMask"] == "0077"
    assert worker["KillSignal"] == "SIGTERM"


def test_systemd_worker_invokes_supported_foreground_cli_not_api_thread():
    worker = _unit("whaxon-workflow-worker.service")["Service"]
    args = shlex.split(worker["ExecStart"])
    assert args[:4] == [
        "/opt/whaxon/.venv/bin/whaxon", "workflow", "plan", "serve-requests",
    ]
    parsed = _parser().parse_args(args[2:])
    assert parsed.plan_command == "serve-requests"
    assert parsed.poll_interval == 1
    assert parsed.max_runs_per_batch == 20
    assert "--daemon" not in args
    assert "gunicorn" not in args
    assert "0.0.0.0" not in worker["ExecStart"]


def test_web_unit_does_not_start_a_second_unfenced_worker():
    web = _unit("whaxon.service")["Service"]
    worker = _unit("whaxon-workflow-worker.service")["Service"]
    assert "gunicorn" in web["ExecStart"]
    assert "serve-requests" not in web["ExecStart"]
    assert "gunicorn" not in worker["ExecStart"]
    assert "WHAXON_DATA=/var/lib/whaxon/data" in worker["Environment"]


def test_both_service_units_are_in_release_artifact_manifests():
    import tomllib

    config = tomllib.loads((ROOT / "pyproject.toml").read_text(encoding="utf-8"))
    sdist = config["tool"]["hatch"]["build"]["targets"]["sdist"]["include"]
    wheel = config["tool"]["hatch"]["build"]["targets"]["wheel"]["force-include"]
    for unit in ("whaxon.service", "whaxon-workflow-worker.service"):
        assert unit in sdist
        assert wheel[unit] == f"whaxon/data/systemd/{unit}"
        assert (ROOT / unit).is_file()
