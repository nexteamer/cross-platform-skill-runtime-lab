from __future__ import annotations

import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from typing import Any

from candidate_core.jsonio import load_json, write_json
from candidate_core.locks import (
    LockError,
    acquire_lock,
    inspect_lock,
    lock_path,
    persist_lock,
    pid_alive,
    release_lock,
)


class ServiceError(LockError):
    pass


def service_receipt_path(prefix: Path) -> Path:
    return prefix / "install" / "service.json"


def listener_owner(bind: str, port: int) -> dict[str, Any]:
    probe = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    probe.settimeout(0.2)
    try:
        probe.connect((bind, port))
        connected = True
    except OSError:
        connected = False
    finally:
        probe.close()
    return {"bind": bind, "port": port, "occupied": connected}


def preflight(prefix: Path, bind: str = "127.0.0.1") -> dict[str, Any]:
    receipt_file = service_receipt_path(prefix)
    lock = inspect_lock(lock_path(prefix))
    occupied = None
    if receipt_file.exists():
        receipt = load_json(receipt_file)
        occupied = listener_owner(bind, int(receipt["port"]))
        if occupied["occupied"] and lock["status"] != "busy":
            return {
                "status": "failed",
                "category": "foreign_owner",
                "lock": lock,
                "listener": occupied,
                "message": "listener is occupied without a proved owner",
            }
    return {"status": "passed", "lock": lock, "listener": occupied}


def start_service(
    prefix: Path,
    *,
    run_id: str,
    owner: str,
    bind: str = "127.0.0.1",
) -> dict[str, Any]:
    prefix = prefix.resolve()
    install = prefix / "install"
    install.mkdir(parents=True, exist_ok=True)
    current = status_service(prefix, bind=bind)
    if current["status"] == "passed" and current.get("owned"):
        return {**current, "idempotent": True}
    if current.get("category") in {"busy", "foreign_owner", "permission"}:
        raise ServiceError(current.get("message") or "service is not startable", category=current["category"])

    payload = {
        "pid": os.getpid(),
        "run_id": run_id,
        "prefix": str(prefix),
        "owner": owner,
    }
    record = acquire_lock(lock_path(prefix), payload)
    port_file = install / "service.port"
    if port_file.exists():
        port_file.unlink()
    worker_script = Path(__file__).with_name("service_worker.py")
    log_path = install / "service.worker.log"
    env = os.environ.copy()
    worker = [
        sys.executable,
        "-u",
        str(worker_script),
        "--bind",
        bind,
        "--port-file",
        str(port_file),
    ]
    with log_path.open("w", encoding="utf-8") as log:
        proc = subprocess.Popen(worker, stdout=log, stderr=log, env=env)
    try:
        port = _wait_for_port_file(port_file, timeout=15.0)
    except Exception:
        proc.kill()
        raise
    receipt = {
        "pid": proc.pid,
        "port": port,
        "bind": bind,
        "run_id": run_id,
        "prefix": str(prefix),
        "owner": owner,
    }
    write_json(service_receipt_path(prefix), receipt)
    record.payload["pid"] = proc.pid
    persist_lock(record)
    return {"status": "passed", "idempotent": False, "receipt": receipt, "owned": True}


def status_service(prefix: Path, bind: str = "127.0.0.1") -> dict[str, Any]:
    lock = inspect_lock(lock_path(prefix))
    receipt_file = service_receipt_path(prefix)
    if not receipt_file.exists():
        return {"status": "passed", "owned": False, "lock": lock, "state": "stopped"}
    try:
        receipt = load_json(receipt_file)
    except PermissionError as exc:
        return {"status": "failed", "category": "permission", "message": str(exc), "owned": False}
    alive = pid_alive(int(receipt.get("pid") or 0))
    listener = listener_owner(bind, int(receipt["port"]))
    owned = (
        alive
        and lock.get("record")
        and lock["record"].get("run_id") == receipt.get("run_id")
        and lock["record"].get("prefix") == str(prefix.resolve())
    )
    if listener["occupied"] and not owned:
        return {
            "status": "failed",
            "category": "foreign_owner",
            "owned": False,
            "lock": lock,
            "receipt": receipt,
            "listener": listener,
            "message": "foreign listener is present",
        }
    if not alive:
        return {
            "status": "failed" if lock["status"] != "free" else "passed",
            "category": lock.get("category"),
            "owned": False,
            "lock": lock,
            "receipt": receipt,
            "state": "stopped",
        }
    return {"status": "passed", "owned": True, "lock": lock, "receipt": receipt, "listener": listener, "state": "running"}


def stop_service(prefix: Path, *, run_id: str) -> dict[str, Any]:
    current = status_service(prefix)
    receipt = current.get("receipt")
    if not receipt:
        return {"status": "passed", "idempotent": True, "state": "stopped"}
    if receipt.get("run_id") != run_id or receipt.get("prefix") != str(prefix.resolve()):
        raise ServiceError("refusing to stop an unproved owner", category="foreign_owner")
    pid = int(receipt.get("pid") or 0)
    if pid_alive(pid):
        os.kill(pid, 15)
        for _ in range(20):
            if not pid_alive(pid):
                break
            time.sleep(0.05)
    release_lock(lock_path(prefix), expected_prefix=str(prefix.resolve()), expected_run_id=run_id)
    receipt_file = service_receipt_path(prefix)
    if receipt_file.exists():
        receipt_file.unlink()
    return {"status": "passed", "idempotent": False, "state": "stopped"}


def _wait_for_port_file(path: Path, timeout: float = 15.0) -> int:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if path.is_file() and path.read_text(encoding="utf-8").strip():
            return int(path.read_text(encoding="utf-8").strip())
        time.sleep(0.05)
    raise ServiceError("service did not publish a port", category="service_start_timeout")
