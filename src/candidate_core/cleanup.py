from __future__ import annotations

from pathlib import Path
from typing import Any

from candidate_core.jsonio import load_json


def cleanup_exact(run_dir: Path, *, run_id: str) -> dict[str, Any]:
    receipt_path = run_dir / "receipt.json"
    if not receipt_path.is_file():
        return {"status": "failed", "category": "cleanup_unowned_path", "removed": []}
    receipt = load_json(receipt_path)
    if receipt.get("run_id") != run_id:
        return {"status": "failed", "category": "cleanup_unowned_path", "removed": []}
    removed = []
    for path in sorted(run_dir.iterdir()):
        if path.is_file():
            path.unlink()
            removed.append(str(path))
    return {"status": "passed", "removed": removed, "run_id": run_id}
