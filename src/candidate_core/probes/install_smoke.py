"""Final-path smoke probe. Must be launched with the installed interpreter."""

from __future__ import annotations

import json
import sys


def main() -> int:
    import candidate_core

    payload = {
        "executable": sys.executable,
        "candidate_core_version": candidate_core.__version__,
    }
    sys.stdout.write(json.dumps(payload, separators=(",", ":")) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
