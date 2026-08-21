from __future__ import annotations

import json
import os
from pathlib import Path

from tests.conftest import run_productctl
from tests.helpers import write_stub_codex


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


def test_real_codex_missing_does_not_fallback(tmp_path: Path) -> None:
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    proc = run_productctl(
        "--json",
        "codex",
        "resolve",
        "--model",
        "lab-model",
        "--transport",
        "chatgpt",
        env={
            "PRODUCTCTL_ALLOW_REAL_CODEX": "1",
            "PATH": str(empty),
        },
    )
    envelope = _envelope(proc)
    assert proc.returncode == 2, proc.stdout
    assert envelope["error"]["category"] == "real_codex_missing"
    assert envelope["observations"]["silent_fallback"] is False
    assert envelope["observations"]["resolved"] is None


def test_real_codex_requires_explicit_identity() -> None:
    proc = run_productctl(
        "--json",
        "codex",
        "resolve",
        env={"PRODUCTCTL_ALLOW_REAL_CODEX": "1", "PATH": ""},
    )
    envelope = _envelope(proc)
    assert proc.returncode == 2, proc.stdout
    assert envelope["error"]["category"] == "codex_identity_unspecified"
    assert envelope["observations"]["silent_fallback"] is False


def test_real_codex_probe_uses_exec_and_last_message(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    write_stub_codex(bin_dir, message="lab-ok")
    proc = run_productctl(
        "--json",
        "codex",
        "probe",
        "--model",
        "lab-model",
        "--transport",
        "chatgpt",
        env={
            "PRODUCTCTL_ALLOW_REAL_CODEX": "1",
            "PATH": str(bin_dir),
            "STUB_CODEX_TEXT": "lab-ok",
        },
    )
    envelope = _envelope(proc)
    assert proc.returncode == 0, proc.stdout
    obs = envelope["observations"]
    assert obs["resolved"]["name"] == "codex"
    assert obs["resolved"]["model"] == "lab-model"
    assert obs["resolved"]["transport"] == "chatgpt"
    assert "exec" in obs["launch"]["argv"]
    assert "--ignore-user-config" in obs["launch"]["argv"]
    assert obs["parsed"]["text"] == "lab-ok"
    assert obs["silent_fallback"] is False


def test_real_codex_auth_failure_is_visible(tmp_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    write_stub_codex(bin_dir)
    proc = run_productctl(
        "--json",
        "codex",
        "probe",
        "--model",
        "lab-model",
        "--transport",
        "chatgpt",
        env={
            "PRODUCTCTL_ALLOW_REAL_CODEX": "1",
            "PATH": str(bin_dir),
            "STUB_CODEX_FAIL": "auth",
        },
    )
    envelope = _envelope(proc)
    assert proc.returncode == 2, proc.stdout
    assert envelope["error"]["category"] == "codex_auth_missing"
    assert "not logged in" in envelope["observations"]["stderr"]
