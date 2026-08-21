from __future__ import annotations

import json
import tarfile
from io import BytesIO
from pathlib import Path
from typing import Any

from candidate_core.jsonio import load_json, write_json

SECRET_KEYS = {"token", "authorization", "password", "secret", "credential"}


def sanitize(value: Any) -> Any:
    if isinstance(value, dict):
        return {
            key: "[redacted]" if key.lower() in SECRET_KEYS else sanitize(item)
            for key, item in value.items()
        }
    if isinstance(value, list):
        return [sanitize(item) for item in value]
    if isinstance(value, str) and any(word in value.lower() for word in ("token=", "sk-", "bearer ")):
        return "[redacted]"
    return value


def collect_diagnostics(run_dir: Path, envelope: dict[str, Any] | None = None) -> dict[str, Any]:
    first_failed = None
    stages = []
    if envelope:
        stages = envelope.get("stages") or []
        first_failed = next((stage for stage in stages if stage.get("status") == "failed"), None)
    bundle = {
        "run_dir": str(run_dir),
        "first_failed_stage": first_failed["id"] if first_failed else None,
        "stages": sanitize(stages),
        "receipt": sanitize(load_json(run_dir / "receipt.json") if (run_dir / "receipt.json").is_file() else {}),
    }
    bundle_path = run_dir / "diagnostics.json"
    write_json(bundle_path, bundle)
    tar_path = run_dir / "diagnostics.tar"
    with tarfile.open(tar_path, "w") as archive:
        data = json.dumps(bundle, indent=2).encode("utf-8")
        info = tarfile.TarInfo("diagnostics.json")
        info.size = len(data)
        archive.addfile(info, BytesIO(data))
    return {"status": "passed", "bundle": str(bundle_path), "archive": str(tar_path), "first_failed_stage": bundle["first_failed_stage"]}
