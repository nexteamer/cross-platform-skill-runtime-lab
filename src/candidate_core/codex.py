from __future__ import annotations

import json
import os
import shutil
import sys
from typing import Any

from candidate_core.process import run_argv


def resolve_codex(*, search_path: str | None = None, requested: dict[str, str] | None = None) -> dict[str, Any]:
    requested = requested or {"model": "fake-model", "transport": "fake-transport"}
    allow_real = os.environ.get("PRODUCTCTL_ALLOW_REAL_CODEX") == "1"
    names = ["fake-codex"]
    if allow_real:
        names.append("codex")
    candidates: list[dict[str, Any]] = []
    selected = None
    for name in names:
        located = shutil.which(name, path=search_path)
        if not located:
            continue
        item = {
            "path": located,
            "name": name,
            "status": "selected" if selected is None else "candidate",
            "reason": "contract-faithful fake on PATH" if name == "fake-codex" else "explicit real Codex allowed by PRODUCTCTL_ALLOW_REAL_CODEX",
        }
        candidates.append(item)
        if selected is None:
            selected = item
    real = shutil.which("codex", path=search_path)
    if real and not allow_real:
        candidates.append(
            {
                "path": real,
                "name": "codex",
                "status": "rejected",
                "reason": "real Codex is reserved for Real Lab/Desktop; Hosted CI uses the fake executable",
            }
        )
    if selected is None:
        candidates.append(
            {
                "path": f"{sys.executable} -m candidate_core.fake_codex",
                "name": "candidate_core.fake_codex",
                "status": "selected",
                "reason": "in-tree fake Codex module; not a silent model/transport fallback",
            }
        )
        selected = candidates[-1]
        argv = [sys.executable, "-m", "candidate_core.fake_codex"]
    else:
        argv = [selected["path"]]
    return {
        "requested": requested,
        "resolved": {
            "executable": selected["path"],
            "model": requested["model"],
            "transport": requested["transport"],
            "reason": selected["reason"],
        },
        "candidates": candidates,
        "argv": argv,
        "silent_fallback": False,
    }


def probe_codex(
    *,
    search_path: str | None = None,
    requested: dict[str, str] | None = None,
    extra_args: list[str] | None = None,
) -> dict[str, Any]:
    resolved = resolve_codex(search_path=search_path, requested=requested)
    argv = list(resolved["argv"])
    req = resolved["requested"]
    argv.extend(["--model", req["model"], "--transport", req["transport"]])
    if extra_args:
        argv.extend(extra_args)
    result = run_argv(argv, timeout=10)
    parsed = None
    if result.stdout.strip():
        try:
            parsed = json.loads(result.stdout.splitlines()[-1])
        except json.JSONDecodeError:
            parsed = None
    exit_category = "success" if result.ok else ("timeout" if result.returncode == 124 else "nonzero_exit")
    return {
        "requested": req,
        "resolved": resolved["resolved"],
        "launch": {
            "argv": result.argv,
            "returncode": result.returncode,
            "exit_category": exit_category,
        },
        "stdout": result.stdout,
        "stderr": result.stderr,
        "parsed": parsed,
        "candidates": resolved["candidates"],
        "silent_fallback": False,
        "status": "passed" if result.ok and parsed is not None else "failed",
    }
