from __future__ import annotations

import json
import os
import socket
from pathlib import Path

from candidate_core.jsonio import write_json
from candidate_core.process_probe import matches_identity, probe_pid
from candidate_core.service import preflight, service_receipt_path
from tests.conftest import run_productctl


def _envelope(proc) -> dict:
    return json.loads(proc.stdout)


def test_process_probe_reports_executable_and_children() -> None:
    proc = run_productctl("--json", "process", "probe", "--pid", str(os.getpid()))
    envelope = _envelope(proc)
    assert proc.returncode == 0, proc.stdout
    obs = envelope["observations"]["observations"]
    assert Path(obs["executable"]).exists()
    assert isinstance(obs["children"], list)


def test_pid_reuse_and_access_denied_fail_closed() -> None:
    probe = probe_pid(os.getpid())
    assert matches_identity(probe, executable=probe["observations"]["executable"], starttime=probe["observations"]["starttime"])
    assert not matches_identity(probe, executable=probe["observations"]["executable"], starttime="not-the-starttime")
    denied = probe_pid(1)
    if denied.get("category") == "access_denied":
        assert denied["owned"] is False
        assert "error" in denied["observations"]
    missing = probe_pid(999999)
    assert missing["owned"] is False
    assert not matches_identity(missing, executable="/bin/true", starttime="1")


def test_foreign_listener_is_reported_and_left_running(tmp_path: Path) -> None:
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    sock.bind(("127.0.0.1", 0))
    sock.listen(1)
    port = sock.getsockname()[1]
    prefix = tmp_path / "prefix"
    (prefix / "install").mkdir(parents=True)
    write_json(
        service_receipt_path(prefix),
        {"pid": 999999, "port": port, "bind": "127.0.0.1", "run_id": "x", "prefix": str(prefix), "owner": "lab"},
    )
    result = preflight(prefix)
    assert result["category"] == "foreign_owner"
    still = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    still.settimeout(0.2)
    still.connect(("127.0.0.1", port))
    still.close()
    sock.close()
    spike = json.loads((Path(__file__).resolve().parents[1] / "docs/spikes/psutil.json").read_text())
    assert spike["status"] == "adopted"
