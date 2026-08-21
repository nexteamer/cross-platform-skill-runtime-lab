from __future__ import annotations

import hashlib
import zipfile
from pathlib import Path
from typing import Any

from candidate_core.jsonio import load_json

PLATFORM_MARKERS = {
    "linux-x86_64": {"sys_platform": "linux"},
    "windows-x64": {"sys_platform": "win32"},
    "macos-arm64": {"sys_platform": "darwin"},
}

PLATFORM_TAGS = {
    "linux-x86_64": {"any", "linux_x86_64", "manylinux2014_x86_64", "manylinux_2_17_x86_64"},
    "windows-x64": {"any", "win_amd64"},
    "macos-arm64": {"any", "macosx_11_0_arm64", "macosx_12_0_arm64", "arm64"},
}

PYTHON_TAGS = {
    "3.11": {"py3", "py311", "cp311"},
    "3.12": {"py3", "py312", "cp312"},
}


def current_platform() -> str:
    import sys

    if sys.platform.startswith("linux"):
        return "linux-x86_64"
    if sys.platform == "win32":
        return "windows-x64"
    if sys.platform == "darwin":
        return "macos-arm64"
    raise ValueError(f"unsupported host platform {sys.platform}")


def verify_payload(
    payload_root: Path,
    *,
    target_platform: str,
    python_series: str,
) -> dict[str, Any]:
    manifest_path = payload_root / "manifest.json"
    candidates: list[dict[str, Any]] = []
    if not manifest_path.is_file():
        return {
            "status": "rejected",
            "selected": [],
            "candidates": [
                _file_result(
                    str(manifest_path),
                    "rejected",
                    [{"category": "payload_manifest_missing", "message": "manifest.json is required"}],
                    {},
                )
            ],
        }

    manifest = load_json(manifest_path)
    files = manifest.get("files") or []
    selected: list[dict[str, Any]] = []
    for item in files:
        result = _verify_file(payload_root, item, target_platform, python_series)
        candidates.append(result)
        if result["status"] == "selected":
            selected.append(result)

    required_rejected = [
        item
        for item in candidates
        if item["status"] == "rejected" and item["observations"].get("required") is True
    ]
    status = "selected" if files and not required_rejected else "rejected"
    if not files:
        status = "rejected"
        candidates.append(
            _file_result(
                str(manifest_path),
                "rejected",
                [{"category": "payload_empty", "message": "manifest lists no files"}],
                {"required": True},
            )
        )
    return {"status": status, "selected": selected, "candidates": candidates}


def _verify_file(
    payload_root: Path,
    item: dict[str, Any],
    target_platform: str,
    python_series: str,
) -> dict[str, Any]:
    rel = item.get("path")
    reasons: list[dict[str, str]] = []
    observations: dict[str, Any] = {
        "required": _required_for_target(item.get("environment_marker"), target_platform),
        "environment_marker": item.get("environment_marker"),
        "packaging_tags": item.get("packaging_tags") or [],
        "python_series": python_series,
        "target_platform": target_platform,
    }
    if not rel:
        reasons.append({"category": "payload_path_missing", "message": "file path omitted"})
        return _file_result("<missing>", "rejected", reasons, observations)

    path = payload_root / rel
    observations["path"] = str(path)
    required = observations["required"]
    if not required:
        return _file_result(str(path), "skipped", [], observations)
    if not path.is_file():
        reasons.append({"category": "payload_file_missing", "message": f"{rel} is missing"})
        return _file_result(str(path), "rejected", reasons, observations)

    digest = hashlib.sha256(path.read_bytes()).hexdigest()
    observations["sha256"] = digest
    expected = item.get("sha256")
    if expected and expected != digest:
        reasons.append({"category": "payload_hash_mismatch", "message": f"{rel} hash mismatch"})

    tags = [str(tag) for tag in item.get("packaging_tags") or []]
    if not _tags_compatible(tags, target_platform, python_series):
        reasons.append(
            {
                "category": "payload_incompatible_tag",
                "message": f"{rel} tags {tags} are incompatible with {target_platform}/{python_series}",
            }
        )

    required_members = [str(member) for member in item.get("required_members") or []]
    if required_members:
        missing_members = _missing_archive_members(path, required_members)
        observations["missing_members"] = missing_members
        if missing_members:
            reasons.append(
                {
                    "category": "payload_archive_member_missing",
                    "message": f"{rel} missing archive members: {', '.join(missing_members)}",
                }
            )

    status = "rejected" if reasons else "selected"
    return _file_result(str(path), status, reasons, observations)


def _required_for_target(marker: str | None, target_platform: str) -> bool:
    if not marker:
        return True
    expected = PLATFORM_MARKERS[target_platform]["sys_platform"]
    if "win32" in marker:
        return expected == "win32"
    if "darwin" in marker:
        return expected == "darwin"
    if "linux" in marker:
        return expected == "linux"
    return True


def _tags_compatible(tags: list[str], target_platform: str, python_series: str) -> bool:
    if not tags:
        return False
    lowered = {tag.lower() for tag in tags}
    python_ok = bool(lowered & {tag.lower() for tag in PYTHON_TAGS[python_series]})
    platform_ok = bool(lowered & {tag.lower() for tag in PLATFORM_TAGS[target_platform]})
    return python_ok and platform_ok


def _missing_archive_members(path: Path, required_members: list[str]) -> list[str]:
    try:
        with zipfile.ZipFile(path) as archive:
            names = set(archive.namelist())
    except zipfile.BadZipFile:
        return list(required_members)
    return [member for member in required_members if member not in names]


def _file_result(
    path: str,
    status: str,
    reasons: list[dict[str, str]],
    observations: dict[str, Any],
) -> dict[str, Any]:
    return {
        "path": path,
        "status": status,
        "reasons": reasons,
        "observations": observations,
    }
