from __future__ import annotations

import os
from pathlib import Path
from typing import Any

from candidate_core.jsonio import load_json


APP_AUTHOR = "cross-platform-skill-runtime-lab"


def default_data_root(app_id: str) -> Path:
    try:
        import platformdirs

        return Path(platformdirs.user_data_dir(app_id, appauthor=APP_AUTHOR))
    except ImportError:
        return _stdlib_data_root(app_id)


def _stdlib_data_root(app_id: str) -> Path:
    if os.name == "nt":
        base = os.environ.get("LOCALAPPDATA") or str(Path.home() / "AppData" / "Local")
        return Path(base) / APP_AUTHOR / app_id
    xdg = os.environ.get("XDG_DATA_HOME")
    if xdg:
        return Path(xdg) / app_id
    return Path.home() / ".local" / "share" / app_id


def resolve_data_root(
    app_id: str,
    *,
    override: str | Path | None = None,
    receipt: dict[str, Any] | None = None,
    inherit_to_children: bool = True,
) -> Path:
    if override:
        return Path(override)
    if inherit_to_children and receipt and receipt.get("data_root"):
        return Path(receipt["data_root"])
    env_root = os.environ.get("PRODUCTCTL_DATA_ROOT")
    if inherit_to_children and env_root:
        return Path(env_root)
    return default_data_root(app_id)


def load_receipt(path: Path) -> dict[str, Any]:
    return load_json(path)


def venv_python(venv_root: Path) -> Path:
    if os.name == "nt":
        return venv_root / "Scripts" / "python.exe"
    return venv_root / "bin" / "python"
