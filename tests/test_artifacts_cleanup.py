from __future__ import annotations

import json
from pathlib import Path

from candidate_core.artifacts import unique_name, write_unique_outputs
from candidate_core.diagnostics import collect_diagnostics, sanitize
from candidate_core.jsonio import write_json
from tests.conftest import run_productctl


def test_duplicate_titles_keep_unique_names_and_verify_detects_moves(tmp_path: Path) -> None:
    names = write_unique_outputs(tmp_path, ["Intro", "Intro"])
    assert names[0] != names[1]
    assert unique_name("Intro", 1, ".png").startswith("01-")
    write_json(
        tmp_path / "manifest.json",
        {
            "artifacts": {
                "one": {"path": str(tmp_path / names[0]), "sha256": "abc"},
            }
        },
    )
    (tmp_path / names[0]).write_text("changed", encoding="utf-8")
    proc = run_productctl("--json", "artifacts", "verify", "--run-dir", str(tmp_path))
    envelope = json.loads(proc.stdout)
    assert proc.returncode == 2
    assert envelope["observations"]["category"] in {"changed", "missing"}
    (tmp_path / names[0]).unlink()
    missing = run_productctl("--json", "artifacts", "verify", "--run-dir", str(tmp_path))
    assert json.loads(missing.stdout)["observations"]["category"] == "missing"


def test_diagnostics_redact_secrets_and_cleanup_is_ownership_bounded(tmp_path: Path) -> None:
    write_json(tmp_path / "receipt.json", {"run_id": "run-1", "token": "secret-value"})
    bundle = collect_diagnostics(
        tmp_path,
        envelope={"stages": [{"id": "payload.verify", "status": "failed", "token": "abc"}]},
    )
    data = json.loads(Path(bundle["bundle"]).read_text(encoding="utf-8"))
    assert data["first_failed_stage"] == "payload.verify"
    assert data["receipt"]["token"] == "[redacted]"
    assert "secret-value" not in Path(bundle["bundle"]).read_text(encoding="utf-8")
    outsider = tmp_path.parent / "unrelated.txt"
    outsider.write_text("keep", encoding="utf-8")
    refused = run_productctl(
        "--json", "cleanup", "exact", "--run-dir", str(tmp_path), "--run-id", "someone-else"
    )
    assert json.loads(refused.stdout)["error"]["category"] == "cleanup_unowned_path"
    assert (tmp_path / "receipt.json").is_file()
    ok = run_productctl("--json", "cleanup", "exact", "--run-dir", str(tmp_path), "--run-id", "run-1")
    assert ok.returncode == 0, ok.stdout
    assert not (tmp_path / "receipt.json").exists()
    assert outsider.read_text(encoding="utf-8") == "keep"
    assert sanitize({"token": "x", "ok": 1})["token"] == "[redacted]"
