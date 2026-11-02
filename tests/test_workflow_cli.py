import json

import whaxon.interfaces.cli.workflow_cmd as workflow_cmd


class _FakeCore:
    def __init__(self, data_dir):
        self.data_dir = data_dir
        self.created = None
        self.saved = None
        self.initialized_with_drain = None
        self.capabilities = type("Registry", (), {"list": lambda self: []})()
        self.store = type("Store", (), {
            "get_workflow_plan": lambda self, plan_id: None,
            "list_workflow_tasks": lambda self, plan_id: [],
        })()

    def create_mission(self, mission_id, objective):
        self.created = (mission_id, objective)
        return True

    def save_workflow_plan(self, plan_id, plan):
        self.saved = (plan_id, plan)
        return True

    async def initialize(self, drain=True):
        self.initialized_with_drain = drain

    async def run_workflow_plan(self, plan_id, **kwargs):
        return {
            "complete": True,
            "tasks": [{"id": "scan", "status": "succeeded"}],
            "plan_id": plan_id,
        }


def test_workflow_cli_creates_mission(monkeypatch, capsys):
    monkeypatch.setattr(workflow_cmd, "Core", _FakeCore)
    assert workflow_cmd.main([
        "mission", "create", "--id", "mission-1", "--objective", "audit lab",
    ]) == 0
    assert json.loads(capsys.readouterr().out)["created"] is True


def test_workflow_cli_validates_and_persists_plan_file(tmp_path, monkeypatch, capsys):
    monkeypatch.setattr(workflow_cmd, "Core", _FakeCore)
    plan_file = tmp_path / "plan.json"
    plan_file.write_text(json.dumps({
        "mission_id": "mission-1",
        "tasks": [{
            "id": "scan", "capability_id": "tool.nmap", "target": "192.0.2.10",
            "permissions": ["network.scan"], "impact": "moderate",
        }],
    }), encoding="utf-8")
    assert workflow_cmd.main([
        "plan", "save", "--id", "plan-1", "--file", str(plan_file),
    ]) == 0
    result = json.loads(capsys.readouterr().out)
    assert result["plan_id"] == "plan-1"
    assert len(result["digest"]) == 64


def test_workflow_cli_runs_headless_without_draining_legacy_jobs(monkeypatch, capsys):
    monkeypatch.setattr(workflow_cmd, "Core", _FakeCore)
    assert workflow_cmd.main(["plan", "run", "--id", "plan-1"]) == 0
    capsys.readouterr()
