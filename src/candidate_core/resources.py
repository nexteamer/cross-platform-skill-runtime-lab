from __future__ import annotations

import json
from importlib.resources import files
from typing import Any


def _read_json(*parts: str) -> dict[str, Any]:
    resource = files("candidate_core")
    for part in parts:
        resource = resource.joinpath(part)
    raw = resource.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"JSON resource {parts} has a UTF-8 BOM")
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"JSON resource {parts} must be an object")
    return payload


def load_schema(name: str) -> dict[str, Any]:
    return _read_json("schemas", name)


def load_registry_document() -> dict[str, Any]:
    return _read_json("data", "historical_failures.json")
