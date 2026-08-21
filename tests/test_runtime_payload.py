from __future__ import annotations

import json
from pathlib import Path

from tests.conftest import run_productctl
from tests.helpers import make_wheel, path_with_bin, write_fake_python, write_payload


def _envelope(proc) -> dict:
    return json.loads(proc.stdout)


def test_runtime_selects_capability_match_without_base_pip(
    tmp_path: Path, contract_path: Path
) -> None:
    bin_dir = tmp_path / "bin"
    write_fake_python(bin_dir / "python3.12", capabilities={"base_pip": False, "venv": True, "ensurepip": True})
    write_fake_python(
        bin_dir / "python3.11",
        version=(3, 11, 0),
        capabilities={"base_pip": True, "venv": False, "ensurepip": False},
    )
    proc = run_productctl(
        "--json",
        "runtime",
        "discover",
        "--contract",
        str(contract_path),
        env={"PATH": path_with_bin(bin_dir)},
    )
    envelope = _envelope(proc)
    assert proc.returncode == 0, envelope
    selected = envelope["observations"]["selected"]
    assert selected["status"] == "selected"
    assert selected["observations"]["python_series"] == "3.12"
    assert selected["observations"]["base_pip_present"] is False
    rejected = [item for item in envelope["observations"]["candidates"] if item["status"] == "rejected"]
    assert rejected
    assert any(
        reason["category"] == "runtime_capability_missing" for reason in rejected[0]["reasons"]
    )


def test_runtime_rejects_unsupported_version(tmp_path: Path, contract_path: Path) -> None:
    bin_dir = tmp_path / "bin"
    write_fake_python(bin_dir / "python3", version=(3, 14, 4))
    proc = run_productctl(
        "--json",
        "runtime",
        "discover",
        "--contract",
        str(contract_path),
        env={"PATH": str(bin_dir)},
    )
    envelope = _envelope(proc)
    assert proc.returncode == 2
    assert envelope["error"]["category"] == "runtime_not_found"
    assert envelope["observations"]["candidates"][0]["reasons"][0]["category"] == "runtime_version_unsupported"


def test_payload_verifies_markers_hashes_and_archive_members(
    tmp_path: Path, contract_path: Path
) -> None:
    payload = write_payload(tmp_path / "good")
    proc = run_productctl(
        "--json",
        "payload",
        "verify",
        "--contract",
        str(contract_path),
        "--payload",
        str(payload),
        "--python",
        "3.12",
        "--target-platform",
        "linux-x86_64",
    )
    assert proc.returncode == 0, proc.stdout
    assert _envelope(proc)["status"] == "passed"


def test_payload_rejects_missing_windows_marker_and_bad_hash(
    tmp_path: Path, contract_path: Path
) -> None:
    root = tmp_path / "payload"
    write_payload(root)
    win_name = "wheels/windows_only-0.1.0-cp312-none-win_amd64.whl"
    digest = make_wheel(
        root / win_name,
        {"candidate_core/__init__.py": b"ok\n", "windows_only.pth": b""},
    )
    manifest = json.loads((root / "manifest.json").read_text(encoding="utf-8"))
    manifest["files"].append(
        {
            "path": win_name,
            "sha256": "0" * 64,
            "packaging_tags": ["cp312", "none", "win_amd64"],
            "environment_marker": "sys_platform == 'win32'",
            "required_members": ["windows_only.pth"],
        }
    )
    (root / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n", encoding="utf-8")

    linux = run_productctl(
        "--json",
        "payload",
        "verify",
        "--contract",
        str(contract_path),
        "--payload",
        str(root),
        "--python",
        "3.12",
        "--target-platform",
        "linux-x86_64",
    )
    assert linux.returncode == 0, linux.stdout

    windows = run_productctl(
        "--json",
        "payload",
        "verify",
        "--contract",
        str(contract_path),
        "--payload",
        str(root),
        "--python",
        "3.12",
        "--target-platform",
        "windows-x64",
    )
    envelope = _envelope(windows)
    assert windows.returncode == 2
    assert envelope["error"]["category"] == "payload_hash_mismatch"
    assert digest != "0" * 64


def test_payload_rejects_missing_archive_member(tmp_path: Path, contract_path: Path) -> None:
    root = tmp_path / "payload"
    write_payload(root, members={"unrelated.txt": b"nope\n"})
    proc = run_productctl(
        "--json",
        "payload",
        "verify",
        "--contract",
        str(contract_path),
        "--payload",
        str(root),
        "--python",
        "3.12",
        "--target-platform",
        "linux-x86_64",
    )
    envelope = _envelope(proc)
    assert proc.returncode == 2
    assert envelope["error"]["category"] == "payload_archive_member_missing"
