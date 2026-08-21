from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import ROOT, run_productctl


def test_release_candidate_has_checksum_manifest_and_bounded_claims(tmp_path: Path) -> None:
    out = tmp_path / "dist"
    built = run_productctl("--json", "release", "candidate", "--out", str(out), "--source-root", str(ROOT))
    assert built.returncode == 0, built.stdout
    manifest = json.loads((out / "manifest.json").read_text(encoding="utf-8"))
    assert manifest["version"] == "0.1.0"
    assert manifest["sha256"]
    assert manifest["dependencies"]["jsonschema"] == "4.19.2"
    assert manifest["claims"]["hosted_ci"] == "not Real Lab Canary"
    assert manifest["claims"]["real_lab"] == "unproven"
    assert (out / "NOTICE").is_file()
    verified = run_productctl("--json", "release", "verify", "--out", str(out))
    assert verified.returncode == 0, verified.stdout
    assert json.loads(verified.stdout)["observations"]["sha256"] == manifest["sha256"]
