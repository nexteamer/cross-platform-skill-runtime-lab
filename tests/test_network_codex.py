from __future__ import annotations

import json
import os

from tests.conftest import run_productctl


def _envelope(proc) -> dict:
    return json.loads(proc.stdout)


def test_codex_probe_records_identity_streams_and_exit() -> None:
    proc = run_productctl(
        "--json",
        "codex",
        "probe",
        "--model",
        "requested-model",
        "--transport",
        "requested-transport",
    )
    envelope = _envelope(proc)
    assert proc.returncode == 0, proc.stdout
    obs = envelope["observations"]
    assert obs["requested"]["model"] == "requested-model"
    assert obs["resolved"]["model"] == "requested-model"
    assert obs["resolved"]["transport"] == "requested-transport"
    assert obs["launch"]["exit_category"] == "success"
    assert obs["stdout"]
    assert obs["silent_fallback"] is False
    assert "stderr" in obs


def test_codex_probe_nonzero_exit_keeps_streams() -> None:
    proc = run_productctl("--json", "codex", "probe", "--fail", "crash")
    envelope = _envelope(proc)
    assert proc.returncode == 2
    assert envelope["observations"]["launch"]["exit_category"] == "nonzero_exit"
    assert "boom" in envelope["observations"]["stderr"]


def test_network_probe_distinguishes_injected_layers() -> None:
    healthy = run_productctl("--json", "network", "probe")
    assert healthy.returncode == 0, healthy.stdout
    stages = [item["id"] for item in _envelope(healthy)["observations"]["stages"]]
    assert stages == ["route", "dns", "proxy", "tls", "crl", "target_http"]
    failed = run_productctl(
        "--json",
        "network",
        "probe",
        env={**os.environ, "PRODUCTCTL_NETWORK_FAIL": "tls"},
    )
    envelope = _envelope(failed)
    assert failed.returncode == 2
    assert envelope["error"]["category"] == "network_tls_failed"
    assert envelope["observations"]["failed_stage"] == "tls"
    assert envelope["observations"]["stages"][0]["status"] == "passed"
