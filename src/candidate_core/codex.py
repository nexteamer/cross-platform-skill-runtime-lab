from __future__ import annotations

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path
from typing import Any

from candidate_core.process import run_argv

FAKE_MODEL = "fake-model"
FAKE_TRANSPORT = "fake-transport"
AUTH_MARKERS = (
    "not logged in",
    "not authenticated",
    "authentication required",
    "sign in",
    "unauthorized",
    "401",
)


def default_requested() -> dict[str, str]:
    return {
        "model": os.environ.get("PRODUCTCTL_CODEX_MODEL") or FAKE_MODEL,
        "transport": os.environ.get("PRODUCTCTL_CODEX_TRANSPORT") or FAKE_TRANSPORT,
    }


def resolve_codex(*, search_path: str | None = None, requested: dict[str, str] | None = None) -> dict[str, Any]:
    requested = requested or default_requested()
    allow_real = os.environ.get("PRODUCTCTL_ALLOW_REAL_CODEX") == "1"
    candidates: list[dict[str, Any]] = []
    if allow_real:
        return _resolve_real(search_path=search_path, requested=requested, candidates=candidates)
    return _resolve_fake(search_path=search_path, requested=requested, candidates=candidates)


def probe_codex(
    *,
    search_path: str | None = None,
    requested: dict[str, str] | None = None,
    extra_args: list[str] | None = None,
    prompt: str | None = None,
    timeout: float | None = None,
) -> dict[str, Any]:
    resolved = resolve_codex(search_path=search_path, requested=requested)
    if resolved.get("status") != "passed":
        return {
            "requested": resolved["requested"],
            "resolved": resolved.get("resolved"),
            "launch": None,
            "stdout": "",
            "stderr": "",
            "parsed": None,
            "candidates": resolved.get("candidates") or [],
            "silent_fallback": False,
            "status": "failed",
            "category": resolved.get("category") or "codex_resolve_failed",
        }
    req = resolved["requested"]
    name = (resolved.get("resolved") or {}).get("name")
    if name == "codex":
        return _probe_real(resolved, prompt=prompt, timeout=timeout)
    return _probe_fake(resolved, extra_args=extra_args, timeout=timeout or 10)


def _resolve_real(*, search_path: str | None, requested: dict[str, str], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    fake = shutil.which("fake-codex", path=search_path)
    if fake:
        candidates.append(
            {
                "path": fake,
                "name": "fake-codex",
                "status": "rejected",
                "reason": "fake-codex ignored because PRODUCTCTL_ALLOW_REAL_CODEX=1",
            }
        )
    if requested.get("model") in {None, "", FAKE_MODEL} or requested.get("transport") in {None, "", FAKE_TRANSPORT}:
        candidates.append(
            {
                "path": None,
                "name": "codex",
                "status": "rejected",
                "reason": "Real Lab requires PRODUCTCTL_CODEX_MODEL and PRODUCTCTL_CODEX_TRANSPORT; fake defaults are not a silent fallback",
            }
        )
        return _failed_resolve("codex_identity_unspecified", requested, candidates)
    located = shutil.which("codex", path=search_path)
    if not located:
        candidates.append(
            {
                "path": None,
                "name": "codex",
                "status": "missing",
                "reason": "real Codex executable not on PATH; no silent fake fallback",
            }
        )
        return _failed_resolve("real_codex_missing", requested, candidates)
    selected = {
        "path": located,
        "name": "codex",
        "status": "selected",
        "reason": "explicit real Codex allowed by PRODUCTCTL_ALLOW_REAL_CODEX",
    }
    candidates.append(selected)
    return {
        "status": "passed",
        "category": None,
        "requested": requested,
        "resolved": {
            "executable": located,
            "name": "codex",
            "model": requested["model"],
            "transport": requested["transport"],
            "reason": selected["reason"],
        },
        "candidates": candidates,
        "argv": [located],
        "silent_fallback": False,
    }


def _resolve_fake(*, search_path: str | None, requested: dict[str, str], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    selected = None
    located = shutil.which("fake-codex", path=search_path)
    if located:
        selected = {
            "path": located,
            "name": "fake-codex",
            "status": "selected",
            "reason": "contract-faithful fake on PATH",
        }
        candidates.append(selected)
    real = shutil.which("codex", path=search_path)
    if real:
        candidates.append(
            {
                "path": real,
                "name": "codex",
                "status": "rejected",
                "reason": "real Codex is reserved for Real Lab/Desktop; Hosted CI uses the fake executable",
            }
        )
    if selected is None:
        selected = {
            "path": f"{sys.executable} -m candidate_core.fake_codex",
            "name": "candidate_core.fake_codex",
            "status": "selected",
            "reason": "in-tree fake Codex module; not a silent model/transport fallback",
        }
        candidates.append(selected)
        argv = [sys.executable, "-m", "candidate_core.fake_codex"]
    else:
        argv = [selected["path"]]
    return {
        "status": "passed",
        "category": None,
        "requested": requested,
        "resolved": {
            "executable": selected["path"],
            "name": selected["name"],
            "model": requested["model"],
            "transport": requested["transport"],
            "reason": selected["reason"],
        },
        "candidates": candidates,
        "argv": argv,
        "silent_fallback": False,
    }


def _failed_resolve(category: str, requested: dict[str, str], candidates: list[dict[str, Any]]) -> dict[str, Any]:
    return {
        "status": "failed",
        "category": category,
        "requested": requested,
        "resolved": None,
        "candidates": candidates,
        "argv": None,
        "silent_fallback": False,
    }


def _probe_fake(
    resolved: dict[str, Any],
    *,
    extra_args: list[str] | None,
    timeout: float,
) -> dict[str, Any]:
    argv = list(resolved["argv"])
    req = resolved["requested"]
    argv.extend(["--model", req["model"], "--transport", req["transport"]])
    if extra_args:
        argv.extend(extra_args)
    result = run_argv(argv, timeout=timeout)
    return _probe_result(resolved, result, parsed=_parse_json_line(result.stdout), require_parsed=True)


def _probe_real(
    resolved: dict[str, Any],
    *,
    prompt: str | None,
    timeout: float | None,
) -> dict[str, Any]:
    req = resolved["requested"]
    timeout = timeout if timeout is not None else float(os.environ.get("PRODUCTCTL_CODEX_TIMEOUT") or 180)
    with tempfile.TemporaryDirectory(prefix="productctl-codex-") as tmp:
        last = Path(tmp) / "last-message.txt"
        argv = [
            resolved["argv"][0],
            "exec",
            "--json",
            "--skip-git-repo-check",
            "--ephemeral",
            "--color",
            "never",
            "-s",
            "read-only",
            "-m",
            req["model"],
            "--output-last-message",
            str(last),
            prompt or "Reply with a single word: ok",
        ]
        result = run_argv(argv, timeout=timeout)
        text = last.read_text(encoding="utf-8").strip() if last.is_file() else ""
    parsed = {
        "type": "result",
        "model": req["model"],
        "transport": req["transport"],
        "text": text or _jsonl_text(result.stdout),
    }
    category = None
    combined = f"{result.stderr}\n{result.stdout}".lower()
    if any(marker in combined for marker in AUTH_MARKERS):
        category = "codex_auth_missing"
    status_ok = result.ok and bool(parsed["text"]) and category is None
    payload = _probe_result(resolved, result, parsed=parsed, require_parsed=False)
    payload["status"] = "passed" if status_ok else "failed"
    if category:
        payload["category"] = category
    elif not status_ok:
        payload["category"] = payload["launch"]["exit_category"]
    return payload


def _probe_result(
    resolved: dict[str, Any],
    result: Any,
    *,
    parsed: dict[str, Any] | None,
    require_parsed: bool,
) -> dict[str, Any]:
    exit_category = "success" if result.ok else ("timeout" if result.returncode == 124 else "nonzero_exit")
    passed = result.ok and (parsed is not None if require_parsed else True)
    return {
        "requested": resolved["requested"],
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
        "status": "passed" if passed else "failed",
        "category": None if passed else exit_category,
    }


def _parse_json_line(stdout: str) -> dict[str, Any] | None:
    for line in reversed(stdout.splitlines()):
        line = line.strip()
        if not line:
            continue
        try:
            parsed = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(parsed, dict):
            return parsed
    return None


def _jsonl_text(stdout: str) -> str:
    for line in reversed(stdout.splitlines()):
        try:
            event = json.loads(line)
        except json.JSONDecodeError:
            continue
        if not isinstance(event, dict):
            continue
        item = event.get("item") if event.get("type") == "item.completed" else event
        if isinstance(item, dict):
            text = item.get("text") or item.get("message")
            if text:
                return str(text)
        if event.get("type") == "result" and event.get("text"):
            return str(event["text"])
    return ""
