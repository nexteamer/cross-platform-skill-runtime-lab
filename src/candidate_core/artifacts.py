from __future__ import annotations

import hashlib
import re
from pathlib import Path
from typing import Any

from candidate_core.jsonio import load_json, write_json


def unique_name(title: str, index: int, suffix: str) -> str:
    slug = re.sub(r"[^a-zA-Z0-9]+", "-", title).strip("-").lower() or "untitled"
    return f"{index:02d}-{slug}{suffix}"


def inventory(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    manifest = load_json(manifest_path) if manifest_path.is_file() else {"artifacts": {}}
    items = []
    for name, meta in (manifest.get("artifacts") or {}).items():
        path = Path(meta["path"])
        items.append({"name": name, "path": str(path), "exists": path.is_file()})
    return {"run_dir": str(run_dir), "items": items}


def verify_artifacts(run_dir: Path) -> dict[str, Any]:
    manifest_path = run_dir / "manifest.json"
    if not manifest_path.is_file():
        return {"status": "failed", "category": "manifest_missing", "problems": []}
    manifest = load_json(manifest_path)
    problems = []
    for name, meta in (manifest.get("artifacts") or {}).items():
        path = Path(meta["path"])
        if not path.is_file():
            problems.append({"name": name, "category": "missing", "path": str(path)})
            continue
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest != meta.get("sha256"):
            problems.append({"name": name, "category": "changed", "path": str(path)})
    return {
        "status": "passed" if not problems else "failed",
        "category": problems[0]["category"] if problems else None,
        "problems": problems,
    }


def write_unique_outputs(run_dir: Path, titles: list[str], body: str = "x") -> list[str]:
    names = []
    for index, title in enumerate(titles, start=1):
        name = unique_name(title, index, ".md")
        path = run_dir / name
        path.write_text(body, encoding="utf-8")
        names.append(name)
    return names
