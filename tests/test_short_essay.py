from __future__ import annotations

import json
from pathlib import Path

from short_essay.app import create_app
from short_essay.db import connect, get_run
from tests.conftest import run_productctl


def _envelope(proc) -> dict:
    return json.loads(proc.stdout)


def test_page_and_api_share_workflow_and_sqlite(tmp_path: Path) -> None:
    app = create_app(tmp_path)
    client = app.test_client()
    page = client.post("/", data={"text": "hello from page"})
    assert page.status_code == 200
    assert b"run" in page.data
    created = client.post("/api/runs", json={"text": "hello from api"})
    assert created.status_code == 200
    payload = created.get_json()
    assert payload["status"] == "passed"
    fetched = client.get(f"/api/runs/{payload['run_id']}")
    assert fetched.status_code == 200
    assert fetched.get_json()["status"] == "passed"
    reopened = get_run(connect(tmp_path / "short-essay.sqlite"), payload["run_id"])
    assert reopened is not None
    assert reopened["status"] == "passed"
    assert {stage["name"] for stage in reopened["stages"]} >= {"analysis", "polish-1", "polish-2", "synthesis"}


def test_cli_workflow_writes_run_artifact_set(tmp_path: Path) -> None:
    proc = run_productctl(
        "--json",
        "workflow",
        "run",
        "--text",
        "a short essay",
        "--data-root",
        str(tmp_path),
    )
    envelope = _envelope(proc)
    assert proc.returncode == 0, proc.stdout
    artifacts = envelope["observations"]["artifacts"]
    for name in ("input", "analysis", "polish-1", "polish-2", "synthesis"):
        assert Path(artifacts[name]).is_file()
    manifest = json.loads(Path(envelope["observations"]["manifest"]).read_text(encoding="utf-8"))
    assert manifest["artifacts"]["input"]["sha256"]
    receipt = Path(artifacts["synthesis"]).parent / "receipt.json"
    assert receipt.is_file()
    db_state = envelope["observations"]["state"]
    assert db_state["status"] == "passed"
