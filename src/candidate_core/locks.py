from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any

from candidate_core.errors import ProductctlError

try:
    import fcntl
except ImportError:  # pragma: no cover
    fcntl = None


class LockError(ProductctlError):
    pass


@dataclass
class LockRecord:
    path: Path
    payload: dict[str, Any]
    fd: int | None = None


def lock_path(prefix: Path) -> Path:
    return prefix / "install" / "service.lock"


def pid_alive(pid: int) -> bool:
    if pid <= 0:
        return False
    try:
        import psutil

        return psutil.Process(pid).is_running() and psutil.Process(pid).status() != psutil.STATUS_ZOMBIE
    except ImportError:
        pass
    except Exception:
        return False
    if os.name == "nt":
        return False
    try:
        os.kill(pid, 0)
    except ProcessLookupError:
        return False
    except PermissionError:
        return True
    except OSError:
        return False
    return True


def inspect_lock(path: Path) -> dict[str, Any]:
    if not path.exists():
        return {"status": "free", "category": None, "record": None}
    try:
        raw = path.read_bytes()
        record = json.loads(raw.decode("utf-8")) if raw.strip() else {}
    except PermissionError as exc:
        return {"status": "blocked", "category": "permission", "message": str(exc), "record": None}
    except ValueError:
        return {"status": "blocked", "category": "invalid_lock", "record": None}
    pid = int(record.get("pid") or 0)
    if pid and pid_alive(pid):
        return {"status": "busy", "category": "busy", "record": record}
    return {"status": "stale", "category": "stale", "record": record}


def acquire_lock(path: Path, payload: dict[str, Any]) -> LockRecord:
    path.parent.mkdir(parents=True, exist_ok=True)
    try:
        fd = os.open(path, os.O_RDWR | os.O_CREAT, 0o644)
    except PermissionError as exc:
        raise LockError(f"cannot open lock {path}", category="permission") from exc
    try:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
    except BlockingIOError as exc:
        os.close(fd)
        raise LockError("lock is held", category="busy") from exc

    raw = os.read(fd, 1_000_000)
    existing: dict[str, Any] | None = None
    if raw.strip():
        try:
            loaded = json.loads(raw.decode("utf-8"))
            existing = loaded if isinstance(loaded, dict) else None
        except ValueError:
            existing = None
    if existing:
        pid = int(existing.get("pid") or 0)
        same_prefix = existing.get("prefix") == payload.get("prefix")
        same_run = existing.get("run_id") == payload.get("run_id")
        if pid and pid_alive(pid) and same_run:
            return LockRecord(path=path, payload=existing, fd=fd)
        if pid and pid_alive(pid):
            os.close(fd)
            category = "busy" if same_prefix else "foreign_owner"
            raise LockError("live owner holds the lock", category=category)
        if not same_prefix:
            os.close(fd)
            raise LockError("unproved owner; refusing takeover", category="foreign_owner")

    encoded = (json.dumps(payload, indent=2) + "\n").encode("utf-8")
    os.lseek(fd, 0, os.SEEK_SET)
    os.ftruncate(fd, 0)
    os.write(fd, encoded)
    os.fsync(fd)
    return LockRecord(path=path, payload=payload, fd=fd)


def persist_lock(record: LockRecord) -> None:
    if record.fd is None:
        return
    encoded = (json.dumps(record.payload, indent=2) + "\n").encode("utf-8")
    os.lseek(record.fd, 0, os.SEEK_SET)
    os.ftruncate(record.fd, 0)
    os.write(record.fd, encoded)
    os.fsync(record.fd)
    if fcntl is not None:
        fcntl.flock(record.fd, fcntl.LOCK_UN)
    os.close(record.fd)
    record.fd = None


def release_lock(path: Path, *, expected_prefix: str, expected_run_id: str, fd: int | None = None) -> None:
    inspection = inspect_lock(path)
    held = inspection.get("record") or {}
    if not held:
        if fd is not None:
            os.close(fd)
        return
    if held.get("prefix") != expected_prefix or held.get("run_id") != expected_run_id:
        if fd is not None:
            os.close(fd)
        raise LockError("refusing to release an unproved lock", category="foreign_owner")
    if fd is not None:
        if fcntl is not None:
            fcntl.flock(fd, fcntl.LOCK_UN)
        os.close(fd)
    try:
        path.unlink()
    except FileNotFoundError:
        return
    except PermissionError as exc:
        raise LockError(f"cannot remove lock {path}", category="permission") from exc
