from __future__ import annotations

import os
from pathlib import Path
from typing import Any


def probe_pid(pid: int) -> dict[str, Any]:
    observations: dict[str, Any] = {"pid": pid}
    if pid <= 0:
        return {"status": "failed", "category": "invalid_pid", "owned": False, "observations": observations}
    psutil_probe = _psutil_probe(pid)
    if psutil_probe is not None:
        return psutil_probe
    proc_dir = Path("/proc") / str(pid)
    if not proc_dir.exists():
        return {"status": "passed", "category": "missing", "owned": False, "observations": observations}
    try:
        observations["executable"] = os.readlink(proc_dir / "exe")
    except PermissionError as exc:
        return {
            "status": "failed",
            "category": "access_denied",
            "owned": False,
            "observations": {**observations, "error": str(exc)},
        }
    except OSError as exc:
        return {
            "status": "failed",
            "category": "unreadable",
            "owned": False,
            "observations": {**observations, "error": str(exc)},
        }
    try:
        raw_cmd = (proc_dir / "cmdline").read_bytes()
        observations["argv"] = [part.decode("utf-8", "replace") for part in raw_cmd.split(b"\x00") if part]
    except PermissionError:
        observations["argv"] = []
        observations["argv_error"] = "access_denied"
    observations["starttime"] = _starttime(proc_dir)
    observations["children"] = _children(pid)
    observations.update(_psutil_extra(pid))
    return {"status": "passed", "category": None, "owned": None, "observations": observations}


def matches_identity(probe: dict[str, Any], *, executable: str | None, starttime: str | None) -> bool:
    obs = probe.get("observations") or {}
    if probe.get("category") in {"access_denied", "missing", "unreadable"}:
        return False
    if executable and obs.get("executable") and Path(obs["executable"]).resolve() != Path(executable).resolve():
        return False
    if starttime and obs.get("starttime") and str(obs["starttime"]) != str(starttime):
        return False
    return True


def _starttime(proc_dir: Path) -> str | None:
    try:
        stat = (proc_dir / "stat").read_text(encoding="utf-8")
        # After the comm field, starttime is field 22 in /proc/pid/stat.
        close = stat.rfind(")")
        fields = stat[close + 2 :].split()
        return fields[19] if len(fields) > 19 else None
    except OSError:
        return None


def _children(pid: int) -> list[int]:
    children: list[int] = []
    proc = Path("/proc")
    if not proc.exists():
        return children
    for entry in proc.iterdir():
        if not entry.name.isdigit():
            continue
        try:
            stat = (entry / "stat").read_text(encoding="utf-8")
            close = stat.rfind(")")
            fields = stat[close + 2 :].split()
            ppid = int(fields[1])
        except (OSError, ValueError, IndexError):
            continue
        if ppid == pid:
            children.append(int(entry.name))
    return sorted(children)


def _psutil_probe(pid: int) -> dict[str, Any] | None:
    try:
        import psutil
    except ImportError:
        return None
    try:
        proc = psutil.Process(pid)
        observations = {
            "pid": pid,
            "executable": proc.exe(),
            "argv": proc.cmdline(),
            "starttime": str(proc.create_time()),
            "children": [child.pid for child in proc.children()],
            "psutil": True,
            "create_time": proc.create_time(),
        }
        return {"status": "passed", "category": None, "owned": None, "observations": observations}
    except psutil.AccessDenied as exc:
        return {
            "status": "failed",
            "category": "access_denied",
            "owned": False,
            "observations": {"pid": pid, "psutil": True, "error": str(exc)},
        }
    except psutil.NoSuchProcess:
        return {"status": "passed", "category": "missing", "owned": False, "observations": {"pid": pid, "psutil": True}}


def _psutil_extra(pid: int) -> dict[str, Any]:
    try:
        import psutil
    except ImportError:
        return {"psutil": False}
    try:
        proc = psutil.Process(pid)
        return {
            "psutil": True,
            "create_time": proc.create_time(),
            "exe": proc.exe(),
            "cmdline": proc.cmdline(),
            "children_psutil": [child.pid for child in proc.children()],
        }
    except psutil.AccessDenied as exc:
        return {"psutil": True, "category": "access_denied", "error": str(exc)}
    except psutil.NoSuchProcess:
        return {"psutil": True, "category": "missing"}
