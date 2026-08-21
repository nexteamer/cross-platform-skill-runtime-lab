from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from typing import Any

from importlib.resources import as_file, files

from candidate_core.jsonio import load_json, write_json
from candidate_core.paths import resolve_data_root, venv_python
from candidate_core.process import run_argv
from candidate_core.fsync import sync_directory, sync_file


class InstallError(Exception):
    def __init__(self, category: str, message: str) -> None:
        super().__init__(message)
        self.category = category
        self.message = message


def install_product(
    *,
    prefix: Path,
    payload_root: Path,
    python_executable: str,
    app_id: str,
    run_id: str,
    data_root_override: str | None = None,
    inherit_to_children: bool = True,
    fail_stage: str | None = None,
) -> dict[str, Any]:
    prefix = prefix.resolve()
    final_dir = prefix / "install"
    staging_dir = prefix / f"staging-{run_id}"
    backup_dir = prefix / f"backup-{run_id}"
    receipt_path = final_dir / "receipt.json"
    injected = fail_stage or os.environ.get("PRODUCTCTL_FAIL_STAGE")

    payload = _selected_wheel(payload_root)
    if receipt_path.is_file():
        existing = load_json(receipt_path)
        if existing.get("payload_sha256") == payload["sha256"] and _smoke(final_dir)["ok"]:
            return {
                "status": "passed",
                "idempotent": True,
                "final_dir": str(final_dir),
                "receipt": existing,
                "python": str(venv_python(final_dir / "venv")),
            }

    if staging_dir.exists():
        shutil.rmtree(staging_dir)
    staging_dir.mkdir(parents=True)
    venv_dir = staging_dir / "venv"
    created = run_argv([python_executable, "-m", "venv", str(venv_dir)], timeout=60)
    if not created.ok:
        _cleanup(staging_dir)
        raise InstallError("install_venv_failed", created.stderr[-2000:])

    python = venv_python(venv_dir)
    pip = run_argv([str(python), "-m", "ensurepip", "--upgrade"], timeout=60)
    if not pip.ok:
        _cleanup(staging_dir)
        raise InstallError("install_ensurepip_failed", pip.stderr[-2000:])
    installed = run_argv(
        [str(python), "-m", "pip", "install", "--no-deps", payload["path"]],
        timeout=120,
    )
    if not installed.ok:
        _cleanup(staging_dir)
        raise InstallError("install_wheel_failed", installed.stderr[-2000:])

    data_root = resolve_data_root(
        app_id,
        override=data_root_override,
        inherit_to_children=inherit_to_children,
    )
    data_root.mkdir(parents=True, exist_ok=True)
    staging_receipt = {
        "run_id": run_id,
        "final_dir": str(final_dir),
        "python": str(venv_python(final_dir / "venv")),
        "payload_sha256": payload["sha256"],
        "data_root": str(data_root),
        "status": "staging",
    }
    write_json(staging_dir / "receipt.json", staging_receipt)
    sync_file(staging_dir / "receipt.json")
    sync_directory(staging_dir)
    if injected == "staging":
        _cleanup(staging_dir)
        raise InstallError("install_staging_injected_failure", "injected staging failure")

    if final_dir.exists():
        if backup_dir.exists():
            shutil.rmtree(backup_dir)
        final_dir.rename(backup_dir)
    try:
        staging_dir.rename(final_dir)
        _rewrite_pyvenv(final_dir / "venv")
        if injected == "promote":
            raise InstallError("install_promote_injected_failure", "injected promotion failure")
        smoke = _smoke(final_dir)
        if not smoke["ok"]:
            raise InstallError("install_final_path_smoke_failed", smoke.get("stderr", ""))
    except Exception:
        if final_dir.exists():
            shutil.rmtree(final_dir)
        if backup_dir.exists():
            backup_dir.rename(final_dir)
        _cleanup(staging_dir)
        raise

    _cleanup(backup_dir)
    receipt = {
        "run_id": run_id,
        "final_dir": str(final_dir),
        "python": str(venv_python(final_dir / "venv")),
        "payload_sha256": payload["sha256"],
        "data_root": str(data_root),
        "status": "installed",
        "launched_from_staging": False,
    }
    write_json(receipt_path, receipt)
    sync_file(receipt_path)
    return {
        "status": "passed",
        "idempotent": False,
        "final_dir": str(final_dir),
        "receipt": receipt,
        "python": receipt["python"],
        "smoke": smoke,
    }


def _selected_wheel(payload_root: Path) -> dict[str, str]:
    manifest = load_json(payload_root / "manifest.json")
    files_list = manifest.get("files") or []
    if not files_list:
        raise InstallError("payload_empty", "payload manifest lists no files")
    item = files_list[0]
    path = payload_root / item["path"]
    return {"path": str(path), "sha256": item["sha256"]}


def _rewrite_pyvenv(venv_dir: Path) -> None:
    cfg = venv_dir / "pyvenv.cfg"
    if not cfg.is_file():
        return
    lines = []
    home = str(venv_dir)
    for line in cfg.read_text(encoding="utf-8").splitlines():
        if line.startswith("home ="):
            lines.append(f"home = {home}")
        else:
            lines.append(line)
    cfg.write_text("\n".join(lines) + "\n", encoding="utf-8")


def _smoke(final_dir: Path) -> dict[str, Any]:
    python = venv_python(final_dir / "venv")
    resource = files("candidate_core").joinpath("probes", "install_smoke.py")
    with as_file(resource) as probe:
        result = run_argv([str(python), str(probe)], timeout=30)
    payload = {}
    if result.ok:
        try:
            payload = json.loads(result.stdout)
        except json.JSONDecodeError:
            payload = {}
    staging_in_path = "staging-" in str(python)
    return {
        "ok": result.ok and not staging_in_path,
        "returncode": result.returncode,
        "stderr": result.stderr[-2000:],
        "executable": payload.get("executable", str(python)),
        "launched_from_final": str(final_dir) in str(python) and not staging_in_path,
    }


def _cleanup(path: Path) -> None:
    if path.exists():
        shutil.rmtree(path, ignore_errors=True)
