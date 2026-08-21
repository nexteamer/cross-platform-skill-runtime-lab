from __future__ import annotations

import json
from pathlib import Path

from jsonschema import Draft202012Validator

from candidate_core.resources import load_schema
from tests.conftest import run_productctl


def _envelope(proc) -> dict:
    return json.loads(proc.stdout)


def test_valid_contract_produces_control_envelope(tmp_path: Path, contract_path: Path) -> None:
    evidence = tmp_path / "evidence"
    proc = run_productctl(
        "--json",
        "acceptance",
        "core",
        "--contract",
        str(contract_path),
        "--evidence-root",
        str(evidence),
    )
    assert proc.returncode == 0, proc.stderr
    envelope = _envelope(proc)
    Draft202012Validator(load_schema("control-envelope.schema.json")).validate(envelope)
    assert envelope["status"] == "passed"
    assert envelope["run_id"]
    assert envelope["command"] == "acceptance.core"
    assert [stage["id"] for stage in envelope["stages"]] == [
        "contract.validate",
        "historical_failures.map",
        "acceptance.skeleton",
    ]
    assert all(stage["status"] == "passed" for stage in envelope["stages"])
    assert envelope["observations"]["product_id"] == "short-essay-lab"
    assert envelope["observations"]["process_launched"] is False
    assert envelope["observations"]["install_attempted"] is False
    assert envelope["evidence"]
    assert envelope["ownership"]["run_id"] == envelope["run_id"]
    receipt = evidence / envelope["run_id"] / "receipt.json"
    written = evidence / envelope["run_id"] / "envelope.json"
    assert receipt.is_file()
    assert written.is_file()
    assert not receipt.read_bytes().startswith(b"\xef\xbb\xbf")
    assert not written.read_bytes().startswith(b"\xef\xbb\xbf")


def test_invalid_contract_fails_before_mutation(tmp_path: Path) -> None:
    evidence = tmp_path / "evidence"
    contract = tmp_path / "bad.json"
    contract.write_text("{}\n", encoding="utf-8")
    before = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    proc = run_productctl(
        "--json",
        "acceptance",
        "core",
        "--contract",
        str(contract),
        "--evidence-root",
        str(evidence),
        cwd=tmp_path,
    )
    assert proc.returncode == 2, proc.stdout
    envelope = _envelope(proc)
    assert envelope["status"] == "failed"
    assert envelope["error"]["category"] in {"invalid_contract", "incomplete_contract"}
    assert envelope["ownership"]["mutations"] == []
    assert envelope["observations"]["process_launched"] is False
    assert not evidence.exists()
    after = {path.relative_to(tmp_path) for path in tmp_path.rglob("*")}
    assert after == before


def test_unconfirmed_contract_fails_before_mutation(tmp_path: Path, contract_path: Path) -> None:
    payload = json.loads(contract_path.read_text(encoding="utf-8"))
    payload["confirmed"] = False
    contract = tmp_path / "productctl.contract.json"
    contract.write_text(json.dumps(payload), encoding="utf-8")
    evidence = tmp_path / "evidence"
    proc = run_productctl(
        "--json",
        "acceptance",
        "core",
        "--contract",
        str(contract),
        "--evidence-root",
        str(evidence),
        cwd=tmp_path,
    )
    assert proc.returncode == 2
    envelope = _envelope(proc)
    assert envelope["error"]["category"] == "unconfirmed_contract"
    assert not evidence.exists()


def test_incomplete_contract_fails_before_mutation(tmp_path: Path) -> None:
    contract = tmp_path / "incomplete.json"
    contract.write_text(
        json.dumps({"contract_version": "0.1.0", "confirmed": True}),
        encoding="utf-8",
    )
    evidence = tmp_path / "evidence"
    proc = run_productctl(
        "--json",
        "acceptance",
        "core",
        "--contract",
        str(contract),
        "--evidence-root",
        str(evidence),
        cwd=tmp_path,
    )
    assert proc.returncode == 2
    envelope = _envelope(proc)
    assert envelope["error"]["category"] == "incomplete_contract"
    assert not evidence.exists()
