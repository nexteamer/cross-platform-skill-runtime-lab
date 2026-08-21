from __future__ import annotations

import json
import sys
from pathlib import Path

from tests.conftest import run_productctl
from tests.helpers import write_payload, write_stub_codex


def test_doctor_passes_after_install(tmp_path: Path, contract_path: Path) -> None:
    payload = write_payload(tmp_path / "payload")
    prefix = tmp_path / "prefix"
    data_root = tmp_path / "data"
    installed = run_productctl(
        "--json",
        "install",
        "run",
        "--contract",
        str(contract_path),
        "--payload",
        str(payload),
        "--prefix",
        str(prefix),
        "--python",
        sys.executable,
        "--data-root",
        str(data_root),
    )
    assert installed.returncode == 0, installed.stdout
    proc = run_productctl(
        "--json",
        "doctor",
        "run",
        "--contract",
        str(contract_path),
        "--prefix",
        str(prefix),
    )
    envelope = json.loads(proc.stdout)
    assert proc.returncode == 0, proc.stdout
    assert envelope["status"] == "passed"
    ids = [stage["id"] for stage in envelope["observations"]["stages"]]
    assert "contract" in ids
    assert "install" in ids
    assert "data_root" in ids
    assert "codex" in ids


def test_doctor_fails_before_install(tmp_path: Path, contract_path: Path) -> None:
    proc = run_productctl(
        "--json",
        "doctor",
        "run",
        "--contract",
        str(contract_path),
        "--prefix",
        str(tmp_path / "missing"),
    )
    envelope = json.loads(proc.stdout)
    assert proc.returncode == 2
    assert envelope["observations"]["failed_stage"] == "install"


def test_doctor_real_codex_missing_fails_without_fallback(tmp_path: Path, contract_path: Path) -> None:
    empty = tmp_path / "empty-bin"
    empty.mkdir()
    proc = run_productctl(
        "--json",
        "doctor",
        "run",
        "--contract",
        str(contract_path),
        env={
            "PRODUCTCTL_ALLOW_REAL_CODEX": "1",
            "PRODUCTCTL_CODEX_MODEL": "lab-model",
            "PRODUCTCTL_CODEX_TRANSPORT": "chatgpt",
            "PATH": str(empty),
        },
    )
    envelope = json.loads(proc.stdout)
    assert proc.returncode == 2, proc.stdout
    assert envelope["observations"]["failed_stage"] == "codex"
    assert envelope["observations"]["stages"][-1]["category"] == "real_codex_missing"


def test_doctor_real_codex_present_passes(tmp_path: Path, contract_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    write_stub_codex(bin_dir)
    proc = run_productctl(
        "--json",
        "doctor",
        "run",
        "--contract",
        str(contract_path),
        env={
            "PRODUCTCTL_ALLOW_REAL_CODEX": "1",
            "PRODUCTCTL_CODEX_MODEL": "lab-model",
            "PRODUCTCTL_CODEX_TRANSPORT": "chatgpt",
            "PATH": str(bin_dir),
        },
    )
    envelope = json.loads(proc.stdout)
    assert proc.returncode == 0, proc.stdout
    assert envelope["status"] == "passed"
    assert envelope["observations"]["stages"][-1]["resolved"]["name"] == "codex"
