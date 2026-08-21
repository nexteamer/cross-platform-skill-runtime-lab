from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any
from uuid import uuid4

from candidate_core.codex import probe_codex
from candidate_core.jsonio import write_json
from short_essay.db import connect, get_run, upsert_run, upsert_stage


def run_short_essay(text: str, *, data_root: Path, run_id: str | None = None) -> dict[str, Any]:
    run_id = run_id or str(uuid4())
    root = Path(data_root) / "runs" / run_id
    root.mkdir(parents=True, exist_ok=True)
    db = connect(Path(data_root) / "short-essay.sqlite")
    upsert_run(db, run_id, "running")
    artifacts: dict[str, str] = {}

    input_path = root / "input.txt"
    input_path.write_text(text, encoding="utf-8")
    artifacts["input"] = str(input_path)

    analysis = _stage(db, run_id, "analysis", "analyze this text", text)
    write_json(root / "analysis.json", analysis)
    artifacts["analysis"] = str(root / "analysis.json")

    polish_one = _stage(db, run_id, "polish-1", "polish candidate one", text)
    (root / "polish-1.md").write_text(str(polish_one.get("text") or ""), encoding="utf-8")
    artifacts["polish-1"] = str(root / "polish-1.md")

    polish_two = _stage(db, run_id, "polish-2", "polish candidate two", text)
    (root / "polish-2.md").write_text(str(polish_two.get("text") or ""), encoding="utf-8")
    artifacts["polish-2"] = str(root / "polish-2.md")

    synthesis = _stage(db, run_id, "synthesis", "synthesize both candidates", text)
    (root / "synthesis.md").write_text(str(synthesis.get("text") or "final"), encoding="utf-8")
    artifacts["synthesis"] = str(root / "synthesis.md")

    manifest = {
        "run_id": run_id,
        "artifacts": {
            name: {"path": path, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
            for name, path in artifacts.items()
        },
    }
    write_json(root / "manifest.json", manifest)
    receipt = {"run_id": run_id, "status": "passed", "command": "workflow.run"}
    write_json(root / "receipt.json", receipt)
    upsert_run(db, run_id, "passed")
    db.close()
    return {
        "run_id": run_id,
        "status": "passed",
        "result": (root / "synthesis.md").read_text(encoding="utf-8"),
        "artifacts": artifacts,
        "manifest": str(root / "manifest.json"),
        "state": get_run(connect(Path(data_root) / "short-essay.sqlite"), run_id),
    }


def _stage(db, run_id: str, name: str, model: str, text: str) -> dict[str, Any]:
    upsert_stage(db, run_id, name, "running")
    probe = probe_codex(requested={"model": model, "transport": "fake-transport"})
    if probe["status"] != "passed":
        upsert_stage(db, run_id, name, "failed", "codex_probe_failed")
        upsert_run(db, run_id, "failed", {"category": "codex_probe_failed", "message": name})
        raise RuntimeError(name)
    parsed = probe.get("parsed") or {}
    parsed["text"] = parsed.get("text") or text
    upsert_stage(db, run_id, name, "passed")
    return parsed
