from __future__ import annotations

import hashlib
import json
import os
import sys
import zipfile
from pathlib import Path
from textwrap import dedent


def write_fake_python(
    path: Path,
    *,
    version: tuple[int, int, int] = (3, 12, 0),
    capabilities: dict[str, bool] | None = None,
) -> Path:
    caps = {
        "executable": True,
        "version": True,
        "venv": True,
        "ensurepip": True,
        "base_pip": False,
    }
    if capabilities:
        caps.update(capabilities)
    payload = {
        "executable": str(path),
        "version": list(version),
        "version_string": ".".join(str(part) for part in version),
        "platform": "linux",
        "capabilities": caps,
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    body = dedent(
        f"""\
        #!{sys.executable}
        import json
        import sys
        sys.stdout.write(json.dumps({payload!r}) + "\\n")
        """
    )
    if os.name == "nt":
        script = path.parent / f"{path.name}.py"
        script.write_text(body, encoding="utf-8")
        launcher = path.parent / f"{path.name}.cmd"
        launcher.write_text(f'@echo off\r\n"{sys.executable}" "{script}" %*\r\n', encoding="utf-8")
        return launcher
    path.write_text(body, encoding="utf-8")
    path.chmod(0o755)
    return path


def make_wheel(path: Path, members: dict[str, bytes] | None = None) -> str:
    payload = {
        "candidate_core-0.1.0.dist-info/METADATA": (
            b"Metadata-Version: 2.1\nName: candidate-core\nVersion: 0.1.0\n"
        ),
        "candidate_core-0.1.0.dist-info/WHEEL": (
            b"Wheel-Version: 1.0\nGenerator: tests\nRoot-Is-Purelib: true\nTag: py3-none-any\n"
        ),
        "candidate_core-0.1.0.dist-info/RECORD": b"candidate_core/__init__.py,,\n",
    }
    if members is None:
        payload["candidate_core/__init__.py"] = b'__version__ = "0.1.0"\n'
    else:
        payload.update(members)
    path.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(path, "w") as archive:
        for name, content in payload.items():
            archive.writestr(name, content)
    return hashlib.sha256(path.read_bytes()).hexdigest()


def write_payload(
    root: Path,
    *,
    filename: str = "wheels/candidate_core-0.1.0-py3-none-any.whl",
    tags: list[str] | None = None,
    marker: str | None = None,
    members: dict[str, bytes] | None = None,
    sha256: str | None = None,
    extra_files: list[dict] | None = None,
) -> Path:
    wheel_path = root / filename
    digest = make_wheel(
        wheel_path,
        members or {"candidate_core/__init__.py": b'__version__ = "0.1.0"\n'},
    )
    files = [
        {
            "path": filename,
            "sha256": sha256 or digest,
            "packaging_tags": tags or ["py3", "none", "any"],
            "environment_marker": marker,
            "required_members": ["candidate_core/__init__.py"],
        }
    ]
    if extra_files:
        files.extend(extra_files)
    root.mkdir(parents=True, exist_ok=True)
    (root / "manifest.json").write_text(
        json.dumps({"files": files}, indent=2) + "\n",
        encoding="utf-8",
    )
    return root


def path_with_bin(bin_dir: Path) -> str:
    return str(bin_dir)
