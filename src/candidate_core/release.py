from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path
from typing import Any

from candidate_core import __version__
from candidate_core.jsonio import write_json

DEPENDENCIES = {
    "jsonschema": "4.19.2",
    "platformdirs": "4.3.6",
    "psutil": "7.2.2",
    "flask": "3.0.3",
}


def build_candidate(out_dir: Path, *, source_root: Path) -> dict[str, Any]:
    out_dir.mkdir(parents=True, exist_ok=True)
    wheel_name = f"candidate_core-{__version__}-py3-none-any.whl"
    wheel_path = out_dir / wheel_name
    package = source_root / "src" / "candidate_core"
    with zipfile.ZipFile(wheel_path, "w") as archive:
        for path in package.rglob("*"):
            if path.is_file() and "__pycache__" not in path.parts:
                archive.write(path, path.relative_to(source_root / "src").as_posix())
        archive.writestr(
            f"candidate_core-{__version__}.dist-info/METADATA",
            f"Metadata-Version: 2.1\nName: candidate-core\nVersion: {__version__}\n",
        )
        archive.writestr(
            f"candidate_core-{__version__}.dist-info/WHEEL",
            "Wheel-Version: 1.0\nGenerator: productctl\nRoot-Is-Purelib: true\nTag: py3-none-any\n",
        )
    digest = hashlib.sha256(wheel_path.read_bytes()).hexdigest()
    (out_dir / "SHA256SUMS").write_text(f"{digest}  {wheel_name}\n", encoding="utf-8")
    manifest = {
        "name": "candidate-core",
        "version": __version__,
        "wheel": wheel_name,
        "sha256": digest,
        "dependencies": DEPENDENCIES,
        "claims": {
            "hosted_ci": "not Real Lab Canary",
            "real_lab": "unproven",
            "desktop_e2e": "unproven",
        },
    }
    write_json(out_dir / "manifest.json", manifest)
    notice = (source_root / "NOTICE").read_text(encoding="utf-8") if (source_root / "NOTICE").is_file() else ""
    (out_dir / "NOTICE").write_text(notice, encoding="utf-8")
    write_json(out_dir / "DEPENDENCIES.json", DEPENDENCIES)
    return {"status": "passed", "wheel": str(wheel_path), "sha256": digest, "manifest": str(out_dir / "manifest.json")}


def verify_candidate(out_dir: Path) -> dict[str, Any]:
    manifest = __import__("json").loads((out_dir / "manifest.json").read_text(encoding="utf-8"))
    wheel = out_dir / manifest["wheel"]
    digest = hashlib.sha256(wheel.read_bytes()).hexdigest()
    if digest != manifest["sha256"]:
        return {"status": "failed", "category": "release_hash_mismatch"}
    sums = (out_dir / "SHA256SUMS").read_text(encoding="utf-8")
    if digest not in sums:
        return {"status": "failed", "category": "release_sums_mismatch"}
    if manifest["claims"]["hosted_ci"] == "Real Lab Canary":
        return {"status": "failed", "category": "release_claim_overreach"}
    return {"status": "passed", "version": manifest["version"], "sha256": digest}
