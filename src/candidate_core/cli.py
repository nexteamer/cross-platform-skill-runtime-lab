from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

from candidate_core.acceptance import run_core
from candidate_core.context import CommandContext
from candidate_core.envelope import build_envelope, error_payload, stage
from candidate_core.errors import ProductctlError, UsageError
from candidate_core.jsonio import dumps


def main(argv: Sequence[str] | None = None) -> int:
    parser = _build_parser()
    try:
        args = parser.parse_args(list(argv) if argv is not None else None)
    except SystemExit as exc:
        code = exc.code if isinstance(exc.code, int) else 2
        return 64 if code == 2 else int(code or 0)

    as_json = bool(args.json)
    try:
        envelope = _dispatch(args)
    except UsageError as exc:
        envelope = _usage_envelope(exc)
        _emit(envelope, as_json=as_json)
        return 64
    except ProductctlError as exc:
        envelope = build_envelope(
            run_id="unassigned",
            command=_command_name(args),
            status="failed",
            stages=[
                stage(
                    "cli",
                    "failed",
                    error=error_payload(exc.category, exc.message),
                )
            ],
            error=error_payload(exc.category, exc.message),
        )
        _emit(envelope, as_json=as_json)
        return 2

    _emit(envelope, as_json=as_json)
    return 0 if envelope["status"] in {"passed", "partial_success"} else 2


def _dispatch(args: argparse.Namespace) -> dict[str, Any]:
    command = _command_name(args)
    ctx = CommandContext(command=command)
    if command == "acceptance.core":
        ctx.contract_path = Path(args.contract)
        if args.evidence_root:
            ctx.evidence_root = Path(args.evidence_root)
        return run_core(ctx)
    raise UsageError(f"unsupported command: {command}")


def _command_name(args: argparse.Namespace) -> str:
    group = getattr(args, "group", None)
    action = getattr(args, "action", None)
    if group and action:
        return f"{group}.{action}"
    return "unknown"


def _usage_envelope(exc: UsageError) -> dict[str, Any]:
    return build_envelope(
        run_id="unassigned",
        command="usage",
        status="failed",
        stages=[stage("cli", "failed", error=error_payload(exc.category, exc.message))],
        error=error_payload(exc.category, exc.message),
    )


def _emit(envelope: dict[str, Any], *, as_json: bool) -> None:
    if as_json:
        sys.stdout.write(dumps(envelope))
        return
    status = envelope["status"]
    run_id = envelope["run_id"]
    error = envelope.get("error")
    sys.stdout.write(f"{status} run_id={run_id}\n")
    if error:
        sys.stdout.write(f"{error['category']}: {error['message']}\n")


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="productctl")
    parser.add_argument("--json", action="store_true", help="emit a Control Envelope on stdout")
    sub = parser.add_subparsers(dest="group", required=True)

    acceptance = sub.add_parser("acceptance", help="acceptance seam")
    acceptance_sub = acceptance.add_subparsers(dest="action", required=True)
    core = acceptance_sub.add_parser("core", help="run core acceptance from a Product Contract")
    core.add_argument("--contract", required=True, help="path to productctl.contract.json")
    core.add_argument("--evidence-root", help="directory for owned run evidence")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
