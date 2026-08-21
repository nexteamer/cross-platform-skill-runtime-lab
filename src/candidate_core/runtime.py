from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any, Iterable

from importlib.resources import as_file, files

from candidate_core.process import run_argv

SUPPORTED_PYTHON = {"3.11", "3.12"}


def discover_runtimes(
    required_capabilities: Iterable[str],
    *,
    path: str | None = None,
    extra_executables: Iterable[str] | None = None,
) -> dict[str, Any]:
    required = list(required_capabilities)
    seen: set[str] = set()
    candidates: list[dict[str, Any]] = []
    selected: dict[str, Any] | None = None
    search_path = path if path is not None else os.environ.get("PATH", "")

    names = ["python3.12", "python3.11", "python3", "python"]
    found: list[str] = []
    for name in names:
        located = shutil.which(name, path=search_path)
        if located:
            found.append(located)
    if extra_executables:
        found.extend(str(item) for item in extra_executables)

    resource = files("candidate_core").joinpath("probes", "runtime_probe.py")
    with as_file(resource) as probe:
        for executable in found:
            resolved = str(Path(executable).resolve()) if Path(executable).exists() else executable
            if resolved in seen:
                continue
            seen.add(resolved)
            candidate = _probe_candidate(resolved, required, Path(probe))
            candidates.append(candidate)
            if selected is None and candidate["status"] == "selected":
                selected = candidate

    return {
        "selected": selected,
        "candidates": candidates,
        "required_capabilities": required,
        "supported_python": sorted(SUPPORTED_PYTHON),
    }


def _probe_candidate(executable: str, required: list[str], probe: Path) -> dict[str, Any]:
    reasons: list[dict[str, str]] = []
    result = run_argv([executable, str(probe)], timeout=5)
    observations = {
        "executable": executable,
        "returncode": result.returncode,
        "stderr_present": bool(result.stderr),
        "stderr_tail": result.stderr[-2000:],
        "stdout_tail": result.stdout[-2000:],
    }
    if result.returncode != 0:
        reasons.append(
            {
                "category": "runtime_probe_failed",
                "message": f"probe exited {result.returncode}",
            }
        )
        return _candidate(executable, "rejected", reasons, observations)

    try:
        payload = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        reasons.append({"category": "runtime_probe_unreadable", "message": str(exc)})
        return _candidate(executable, "rejected", reasons, observations)

    observations["probe"] = payload
    version = payload.get("version") or []
    if not (isinstance(version, list) and len(version) >= 2):
        reasons.append({"category": "runtime_version_unreadable", "message": "probe omitted version"})
        return _candidate(executable, "rejected", reasons, observations)

    series = f"{version[0]}.{version[1]}"
    observations["python_series"] = series
    if series not in SUPPORTED_PYTHON:
        reasons.append(
            {
                "category": "runtime_version_unsupported",
                "message": f"{series} is not in {sorted(SUPPORTED_PYTHON)}",
            }
        )

    capabilities = payload.get("capabilities") or {}
    missing = [name for name in required if not capabilities.get(name)]
    if missing:
        reasons.append(
            {
                "category": "runtime_capability_missing",
                "message": "missing required capabilities: " + ", ".join(missing),
            }
        )
    # base_pip is recorded and must not be a selection requirement
    observations["base_pip_present"] = bool(capabilities.get("base_pip"))
    observations["base_pip_required"] = False

    status = "selected" if not reasons else "rejected"
    return _candidate(executable, status, reasons, observations)


def _candidate(
    executable: str,
    status: str,
    reasons: list[dict[str, str]],
    observations: dict[str, Any],
) -> dict[str, Any]:
    return {
        "executable": executable,
        "status": status,
        "reasons": reasons,
        "observations": observations,
    }
