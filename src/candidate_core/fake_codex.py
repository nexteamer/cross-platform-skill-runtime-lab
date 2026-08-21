"""Contract-faithful fake Codex executable for Hosted CI."""

from __future__ import annotations

import argparse
import json
import os
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(prog="fake-codex")
    parser.add_argument("--model", default="fake-model")
    parser.add_argument("--transport", default="fake-transport")
    parser.add_argument("--fail", default=os.environ.get("FAKE_CODEX_FAIL"))
    args = parser.parse_args(argv)
    if args.fail == "stderr-success":
        sys.stderr.write("warning: noisy stderr\n")
    event = {
        "type": "result",
        "model": args.model,
        "transport": args.transport,
        "text": "ok",
    }
    if args.fail == "timeout":
        sys.stderr.write("timeout\n")
        return 124
    if args.fail == "crash":
        sys.stderr.write("boom\n")
        return 1
    if args.fail == "malformed":
        sys.stdout.write("{not-json\n")
        return 0
    sys.stdout.write(json.dumps(event) + "\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
