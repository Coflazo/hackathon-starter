"""Smoke test of the demo path; runs offline in DEMO_MODE."""
import os

os.environ["DEMO_MODE"] = "1"

from fastapi.testclient import TestClient  # noqa: E402

from main import app  # noqa: E402

client = TestClient(app)


def test_demo_path_answers_from_fixture():
    r = client.post("/demo", json={"input": "What does this do?"})
    assert r.status_code == 200
    assert r.json()["source"] == "fixture" and "Sample answer" in r.json()["output"]


def test_empty_input_rejected():
    assert client.post("/demo", json={"input": ""}).status_code == 422


def test_live_failure_without_fixture_is_a_clear_error(tmp_path, monkeypatch):
    import replay
    monkeypatch.setenv("DEMO_MODE", "0")
    monkeypatch.setattr(replay, "FIXTURES", tmp_path)
    r = client.post("/demo", json={"input": "hi"})
    assert r.status_code == 502 and "unavailable" in r.json()["detail"]


def test_fixture_keys_cannot_be_paths():
    import pytest
    from replay import ReplayError, with_replay
    with pytest.raises(ReplayError):
        with_replay("../../etc/passwd", lambda: "x")


def test_rate_limit(monkeypatch):
    import main
    monkeypatch.setattr(main, "MAX_PER_MINUTE", 2)
    main._hits.clear()
    codes = [client.post("/demo", json={"input": "x"}).status_code for _ in range(3)]
    assert codes[-1] == 429
