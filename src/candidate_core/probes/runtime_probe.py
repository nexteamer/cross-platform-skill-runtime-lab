"""Read-only runtime capability probe. Invoked as an argument-vector script."""

from __future__ import annotations

import json
import sys


def _can_import(name: str) -> bool:
    try:
        __import__(name)
    except Exception:
        return False
    return True


def main() -> int:
    version = sys.version_info
    payload = {
        "executable": sys.executable,
        "version": [version.major, version.minor, version.micro],
        "version_string": f"{version.major}.{version.minor}.{version.micro}",
        "platform": sys.platform,
        "capabilities": {
            "executable": True,
            "version": True,
            "venv": _can_import("venv"),
            "ensurepip": _can_import("ensurepip"),
            "base_pip": _can_import("pip"),
        },
    }
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
