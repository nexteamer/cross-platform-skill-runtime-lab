from __future__ import annotations

import json
import os
import sys
from pathlib import Path

from candidate_core.jsonio import load_json
from candidate_core.paths import default_data_root, resolve_data_root
from tests.conftest import run_productctl
from tests.helpers import write_payload


def _envelope(proc) -> dict:
    return json.loads(proc.stdout)


def test_install_promotes_to_final_path_and_keeps_receipt(
    tmp_path: Path, contract_path: Path
) -> None:
    payload = write_payload(tmp_path / "payload")
    prefix = tmp_path / "prefix"
    data_root = tmp_path / "data"
    proc = run_productctl(
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
    envelope = _envelope(proc)
    assert proc.returncode == 0, proc.stderr + proc.stdout
    receipt_path = prefix / "install" / "receipt.json"
    receipt = load_json(receipt_path)
    assert receipt["status"] == "installed"
    assert receipt["launched_from_staging"] is False
    python = Path(receipt["python"])
    assert python.is_file()
    assert "staging-" not in str(python)
    assert str(prefix / "install") in str(python)
    assert not list(prefix.glob("staging-*"))
    assert envelope["observations"]["smoke"]["launched_from_final"] is True

    again = run_productctl(
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
    assert again.returncode == 0, again.stdout
    assert _envelope(again)["observations"]["idempotent"] is True


def test_injected_staging_failure_rolls_back(tmp_path: Path, contract_path: Path) -> None:
    payload = write_payload(tmp_path / "payload")
    prefix = tmp_path / "prefix"
    proc = run_productctl(
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
        env={**os.environ, "PRODUCTCTL_FAIL_STAGE": "staging"},
    )
    envelope = _envelope(proc)
    assert proc.returncode == 2
    assert envelope["error"]["category"] == "install_staging_injected_failure"
    assert not (prefix / "install").exists()
    assert not list(prefix.glob("staging-*"))


def test_injected_promote_failure_rolls_back(tmp_path: Path, contract_path: Path) -> None:
    payload = write_payload(tmp_path / "payload")
    prefix = tmp_path / "prefix"
    first = run_productctl(
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
    )
    assert first.returncode == 0, first.stdout
    original = load_json(prefix / "install" / "receipt.json")
    original["payload_sha256"] = "ab" * 32
    (prefix / "install" / "receipt.json").write_text(json.dumps(original, indent=2) + "\n")
    proc = run_productctl(
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
        env={**os.environ, "PRODUCTCTL_FAIL_STAGE": "promote"},
    )
    envelope = _envelope(proc)
    assert proc.returncode == 2, proc.stdout
    assert envelope["error"]["category"] == "install_promote_injected_failure"
    assert (prefix / "install").exists()
    assert not list(prefix.glob("staging-*"))


def test_data_root_override_and_child_inheritance_beat_platformdirs(tmp_path: Path) -> None:
    override = tmp_path / "explicit-root"
    parent = resolve_data_root(
        "short-essay-lab",
        override=override,
        inherit_to_children=True,
    )
    assert parent == override
    receipt = {"data_root": str(parent)}
    child = resolve_data_root(
        "short-essay-lab",
        receipt=receipt,
        inherit_to_children=True,
    )
    assert child == parent
    independent = default_data_root("short-essay-lab")
    assert independent != parent
    spike = json.loads(
        (Path(__file__).resolve().parents[1] / "docs/spikes/platformdirs.json").read_text()
    )
    assert spike["status"] == "adopted"
    joined = " ".join(spike["constraints"]).lower()
    assert "override" in joined
    assert "inherit" in joined
