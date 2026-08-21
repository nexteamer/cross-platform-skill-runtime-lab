from __future__ import annotations

import hashlib
from concurrent.futures import ThreadPoolExecutor, wait
from pathlib import Path
from typing import Any
from uuid import uuid4

from candidate_core.codex import probe_codex
from candidate_core.jsonio import write_json
from short_essay.db import connect, get_run, upsert_run, upsert_stage


def run_short_essay(
    text: str,
    *,
    data_root: Path,
    run_id: str | None = None,
    polish_candidates: int = 2,
    fail_candidates: list[int] | None = None,
    timeout: float | None = None,
    cancel: bool = False,
) -> dict[str, Any]:
    run_id = run_id or str(uuid4())
    fail_candidates = fail_candidates or []
    root = Path(data_root) / "runs" / run_id
    root.mkdir(parents=True, exist_ok=True)
    db_path = Path(data_root) / "short-essay.sqlite"
    db = connect(db_path)
    upsert_run(db, run_id, "running")
    artifacts: dict[str, str] = {}

    input_path = root / "input.txt"
    input_path.write_text(text, encoding="utf-8")
    artifacts["input"] = str(input_path)

    analysis = _call_codex(db, run_id, "analysis", "analyze this text", text, fail=False)
    write_json(root / "analysis.json", {"ok": analysis["ok"], "payload": analysis["payload"]})
    artifacts["analysis"] = str(root / "analysis.json")

    polish_results = _run_polish(
        db,
        run_id,
        text,
        root,
        polish_candidates=polish_candidates,
        fail_candidates=fail_candidates,
        timeout=timeout,
        cancel=cancel,
    )
    artifacts.update(polish_results["artifacts"])
    survivors = polish_results["survivors"]
    failures = polish_results["failures"]

    if polish_candidates > 0 and not survivors:
        upsert_run(db, run_id, "failed", {"category": "polish_failed", "message": "all polish candidates failed"})
        receipt = {"run_id": run_id, "status": "failed", "failures": failures}
        write_json(root / "receipt.json", receipt)
        _write_manifest(root, run_id, artifacts)
        db.close()
        return {
            "run_id": run_id,
            "status": "failed",
            "result": None,
            "artifacts": artifacts,
            "manifest": str(root / "manifest.json"),
            "failures": failures,
            "retried": False,
            "state": get_run(connect(db_path), run_id),
        }

    synthesis_input = survivors[0]["text"] if survivors else text
    synthesis = _call_codex(db, run_id, "synthesis", "synthesize candidates", synthesis_input, fail=False)
    (root / "synthesis.md").write_text(str(synthesis["payload"].get("text") or synthesis_input), encoding="utf-8")
    artifacts["synthesis"] = str(root / "synthesis.md")
    status = "partial_success" if failures else "passed"
    upsert_run(db, run_id, status)
    receipt = {
        "run_id": run_id,
        "status": status,
        "failures": failures,
        "survivors": [item["name"] for item in survivors],
        "retried": False,
    }
    write_json(root / "receipt.json", receipt)
    _write_manifest(root, run_id, artifacts)
    db.close()
    return {
        "run_id": run_id,
        "status": status,
        "result": (root / "synthesis.md").read_text(encoding="utf-8"),
        "artifacts": artifacts,
        "manifest": str(root / "manifest.json"),
        "failures": failures,
        "retried": False,
        "state": get_run(connect(db_path), run_id),
    }


def _run_polish(
    db,
    run_id: str,
    text: str,
    root: Path,
    *,
    polish_candidates: int,
    fail_candidates: list[int],
    timeout: float | None,
    cancel: bool,
) -> dict[str, Any]:
    artifacts: dict[str, str] = {}
    survivors: list[dict[str, Any]] = []
    failures: list[dict[str, Any]] = []
    if polish_candidates == 0:
        return {"artifacts": artifacts, "survivors": survivors, "failures": failures}

    def work(index: int) -> dict[str, Any]:
        name = f"polish-{index}"
        fail = index in fail_candidates
        thread_db = connect(Path(root).parents[1] / "short-essay.sqlite")
        try:
            return _call_codex(thread_db, run_id, name, f"polish candidate {index}", text, fail=fail)
        finally:
            thread_db.close()

    with ThreadPoolExecutor(max_workers=max(polish_candidates, 1)) as pool:
        futures = {pool.submit(work, index): index for index in range(1, polish_candidates + 1)}
        if cancel:
            pending = set(futures)
            done: set = set()
            for future in pending:
                future.cancel()
        else:
            done, pending = wait(list(futures), timeout=timeout)
            for future in pending:
                future.cancel()
                index = futures[future]
                failures.append({"name": f"polish-{index}", "category": "timeout"})
                upsert_stage(db, run_id, f"polish-{index}", "failed", "timeout")
        if cancel:
            for future, index in futures.items():
                failures.append({"name": f"polish-{index}", "category": "cancelled"})
                upsert_stage(db, run_id, f"polish-{index}", "failed", "cancelled")
        for future, index in futures.items():
            name = f"polish-{index}"
            path = root / f"{name}.md"
            if future.cancelled() or not future.done() or future.exception() is not None and future.cancelled():
                path.write_text("", encoding="utf-8")
                artifacts[name] = str(path)
                continue
            try:
                result = future.result()
            except Exception as exc:
                path.write_text("", encoding="utf-8")
                artifacts[name] = str(path)
                failures.append({"name": name, "category": "worker_failed", "message": str(exc)})
                continue
            path.write_text(str((result["payload"] or {}).get("text") or ""), encoding="utf-8")
            artifacts[name] = str(path)
            if result["ok"]:
                survivors.append({"name": name, "text": (result["payload"] or {}).get("text") or text})
            else:
                failures.append({"name": name, "category": result["category"], "stderr": result.get("stderr")})
    return {"artifacts": artifacts, "survivors": survivors, "failures": failures}


def _call_codex(db, run_id: str, name: str, model: str, text: str, *, fail: bool) -> dict[str, Any]:
    upsert_stage(db, run_id, name, "running")
    extra = ["--fail", "crash"] if fail else None
    probe = probe_codex(requested={"model": model, "transport": "fake-transport"}, extra_args=extra)
    if probe["status"] != "passed":
        upsert_stage(db, run_id, name, "failed", "codex_probe_failed")
        return {
            "ok": False,
            "category": "codex_probe_failed",
            "payload": {},
            "stderr": probe.get("stderr"),
            "retried": False,
        }
    parsed = probe.get("parsed") or {}
    parsed["text"] = parsed.get("text") or text
    upsert_stage(db, run_id, name, "passed")
    return {"ok": True, "category": None, "payload": parsed, "retried": False}


def _write_manifest(root: Path, run_id: str, artifacts: dict[str, str]) -> None:
    manifest = {
        "run_id": run_id,
        "artifacts": {
            name: {"path": path, "sha256": hashlib.sha256(Path(path).read_bytes()).hexdigest()}
            for name, path in artifacts.items()
            if Path(path).is_file()
        },
    }
    write_json(root / "manifest.json", manifest)
