from __future__ import annotations

import json
from pathlib import Path
from typing import Any


def dumps(data: Any) -> str:
    return json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n"


def load_json(path: Path) -> Any:
    raw = path.read_bytes()
    if raw.startswith(b"\xef\xbb\xbf"):
        raise ValueError(f"JSON at {path} has a UTF-8 BOM")
    return json.loads(raw.decode("utf-8"))


def write_json(path: Path, data: Any) -> None:
    encoded = dumps(data).encode("utf-8")
    if encoded.startswith(b"\xef\xbb\xbf"):
        raise ValueError("refusing to write JSON with a UTF-8 BOM")
    path.write_bytes(encoded)
