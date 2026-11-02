
def test_tracker_restart_does_not_replace_open_session_identity(tmp_path):
    live = {"1": {"target_host": "10.0.0.5", "type": "shell"}}
    first, _, store, _ = _make(tmp_path, live_sessions=live)
    first._poll()

    # A fresh tracker has an empty in-memory known set, just like a service
    # restart. A reused ID with a changed host must not overwrite the record.
    restarted, _client, _, _ = _make(tmp_path, live_sessions={
        "1": {"target_host": "10.0.0.6", "type": "shell"}
    })
    restarted._store = store
    restarted._poll()
    assert store.get_session("1")["host"] == "10.0.0.5"