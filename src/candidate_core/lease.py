from __future__ import annotations

from pathlib import Path
from typing import Any

from candidate_core.locks import inspect_lock, lock_path, release_lock


def lease_status(prefix: Path) -> dict[str, Any]:
    inspection = inspect_lock(lock_path(prefix))
    category = inspection.get("category")
    status = "passed" if inspection["status"] in {"free", "stale", "busy"} else "failed"
    if category == "permission":
        status = "failed"
    return {
        "status": status,
        "category": category,
        "lock": inspection,
        "state": inspection["status"],
    }


def lease_release(prefix: Path, *, run_id: str) -> dict[str, Any]:
    path = lock_path(prefix)
    release_lock(path, expected_prefix=str(prefix.resolve()), expected_run_id=run_id)
    return {"status": "passed", "state": "free"}
