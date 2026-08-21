from __future__ import annotations

import json
import os
import stat
from pathlib import Path

from candidate_core.jsonio import write_json
from candidate_core.locks import acquire_lock, inspect_lock, lock_path
from tests.conftest import run_productctl


def _envelope(proc) -> dict:
    return json.loads(proc.stdout)


def test_service_start_status_stop_is_idempotent(tmp_path: Path) -> None:
    prefix = tmp_path / "prefix"
    (prefix / "install").mkdir(parents=True)
    start = run_productctl("--json", "service", "start", "--prefix", str(prefix), "--run-id", "run-a")
    assert start.returncode == 0, start.stdout + start.stderr
    first = _envelope(start)
    port = first["observations"]["receipt"]["port"]
    again = run_productctl("--json", "service", "start", "--prefix", str(prefix), "--run-id", "run-a")
    assert again.returncode == 0
    assert _envelope(again)["observations"]["idempotent"] is True
    status = run_productctl("--json", "service", "status", "--prefix", str(prefix))
    assert status.returncode == 0
    assert _envelope(status)["observations"]["owned"] is True
    lease = run_productctl("--json", "lease", "status", "--prefix", str(prefix))
    assert _envelope(lease)["observations"]["state"] == "busy"
    stop = run_productctl("--json", "service", "stop", "--prefix", str(prefix), "--run-id", "run-a")
    assert stop.returncode == 0, stop.stdout
    stopped = run_productctl("--json", "service", "status", "--prefix", str(prefix))
    assert _envelope(stopped)["observations"]["owned"] is False
    assert port > 0


def test_foreign_and_stale_locks_fail_closed(tmp_path: Path) -> None:
    prefix = tmp_path / "ours"
    foreign = tmp_path / "theirs"
    (prefix / "install").mkdir(parents=True)
    (foreign / "install").mkdir(parents=True)
    write_json(
        lock_path(prefix),
        {"pid": os.getpid(), "run_id": "foreign-run", "prefix": str(foreign.resolve()), "owner": "other"},
    )
    start = run_productctl("--json", "service", "start", "--prefix", str(prefix), "--run-id", "run-a")
    envelope = _envelope(start)
    assert start.returncode == 2
    assert envelope["error"]["category"] == "foreign_owner"

    write_json(
        lock_path(prefix),
        {"pid": 999999, "run_id": "old", "prefix": str(foreign.resolve()), "owner": "other"},
    )
    stale_foreign = run_productctl("--json", "service", "start", "--prefix", str(prefix), "--run-id", "run-a")
    assert stale_foreign.returncode == 2
    assert _envelope(stale_foreign)["error"]["category"] == "foreign_owner"

    write_json(
        lock_path(prefix),
        {"pid": 999999, "run_id": "old-same", "prefix": str(prefix.resolve()), "owner": "short-essay-lab"},
    )
    stale_same = run_productctl("--json", "service", "start", "--prefix", str(prefix), "--run-id", "run-a")
    assert stale_same.returncode == 0, stale_same.stdout
    run_productctl("--json", "service", "stop", "--prefix", str(prefix), "--run-id", "run-a")


def test_permission_is_not_reported_as_busy(tmp_path: Path) -> None:
    prefix = tmp_path / "prefix"
    install = prefix / "install"
    install.mkdir(parents=True)
    lock = lock_path(prefix)
    write_json(lock, {"pid": 1, "run_id": "x", "prefix": str(prefix), "owner": "x"})
    if os.name == "nt":
        # chmod 0 still leaves the file readable for the owner on Windows.
        inspection = inspect_lock(lock)
        assert inspection["category"] != "busy"
        return
    os.chmod(lock, 0)
    try:
        inspection = inspect_lock(lock)
        assert inspection["category"] == "permission"
        lease = run_productctl("--json", "lease", "status", "--prefix", str(prefix))
        envelope = _envelope(lease)
        assert envelope["error"]["category"] == "permission"
    finally:
        os.chmod(lock, stat.S_IRUSR | stat.S_IWUSR)
