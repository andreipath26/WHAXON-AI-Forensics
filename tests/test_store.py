import threading
import time

import pytest

from whaxon.core.store import JobStore


@pytest.fixture
def store(tmp_path):
    return JobStore(tmp_path / "test.db")

def test_create_and_get(store):
    store.create("abc")
    assert store.get("abc")["status"] == "starting"

def test_full_lifecycle(store):
    store.create("j1")
    store.set_started("j1", "nmap", "127.0.0.1")
    store.append_line("j1", "stdout", "a")
    store.append_line("j1", "stderr", "b")
    store.set_finished("j1", 0, 1.5)
    j = store.get("j1")
    assert j["status"] == "finished"
    assert len(j["lines"]) == 2

def test_findings_roundtrip(store):
    store.create("f1")
    store.append_finding("f1", {"kind": "open_port", "severity": "high", "source": "nmap",
                                "data": {"port": 22}, "raw_line": "22/tcp"}, 0)
    out = store.get_findings("f1")
    assert out[0]["severity"] == "high"
    assert out[0]["data"]["port"] == 22

def test_history_ordering(store):
    for i in range(3):
        store.create(f"h{i}")
        store.set_finished(f"h{i}", 0, 0.1)
        time.sleep(0.01)
    assert store.history()[0]["id"] == "h2"

def test_evidence_crud(store):
    store.create("e1")
    seq = store.add_evidence("e1", "note", "n", note="hi")
    store.add_evidence("e1", "file", "s.png", path="evidence/e1/s.png")
    assert len(store.list_evidence("e1")) == 2
    assert store.remove_evidence("e1", seq) is True

def test_concurrent_writes(store):
    def worker(jid):
        store.create(jid)
        for i in range(50):
            store.append_line(jid, "stdout", f"l{i}")
        store.set_finished(jid, 0, 1.0)
    ts = [threading.Thread(target=worker, args=(f"c{i}",)) for i in range(4)]
    for t in ts: t.start()
    for t in ts: t.join()
    for i in range(4):
        assert len(store.get(f"c{i}")["lines"]) == 50

def test_history_reports_finding_count_not_output_line_count(store):
    store.create("history-findings")
    store.set_started("history-findings", "nmap", "127.0.0.1")
    store.append_line("history-findings", "stdout", "tool output")
    store.append_finding(
        "history-findings",
        {"kind": "open_port", "severity": "medium", "source": "nmap",
         "data": {"port": 22}, "raw_line": "22/tcp open ssh"},
        0,
    )
    store.append_finding(
        "history-findings",
        {"kind": "open_port", "severity": "high", "source": "nmap",
         "data": {"port": 443}, "raw_line": "443/tcp open https"},
        1,
    )
    store.set_finished("history-findings", 0, 0.1)

    entry = next(row for row in store.history() if row["id"] == "history-findings")
    assert entry["line_count"] == 1
    assert entry["findings_count"] == 2

def test_findings_by_target_preserves_conflicting_path_observations(store):
    """Do not collapse different tools' status/size evidence into the first row."""
    target = "http://127.0.0.1:8080/"
    store.create("ffuf-job")
    store.set_started("ffuf-job", "ffuf", target)
    store.append_finding(
        "ffuf-job",
        {
            "kind": "found_path", "severity": "info", "source": "ffuf",
            "data": {"path": "/admin", "status": None, "size": None},
            "raw_line": "admin",
        },
        0,
    )
    store.create("gobuster-job")
    store.set_started("gobuster-job", "gobuster", target)
    store.append_finding(
        "gobuster-job",
        {
            "kind": "found_path", "severity": "info", "source": "gobuster",
            "data": {"path": "/admin", "status": 403, "size": 289},
            "raw_line": "/admin (Status: 403) [Size: 289]",
        },
        0,
    )

    grouped = store.findings_by_target()
    target_row = next(row for row in grouped if row["target"] == "127.0.0.1")
    observations = [f for f in target_row["findings"] if f["data"].get("path") == "/admin"]

    assert len(observations) == 2
    by_source = {finding["source"]: finding["data"] for finding in observations}
    assert by_source["ffuf"]["status"] is None
    assert by_source["gobuster"]["status"] == 403
    assert by_source["gobuster"]["size"] == 289
