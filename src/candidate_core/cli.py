from __future__ import annotations

import argparse
import sys
from pathlib import Path
from typing import Any, Sequence

from candidate_core.acceptance import run_core
from candidate_core.context import CommandContext
from candidate_core.contract import load_and_validate_contract
from candidate_core.envelope import build_envelope, error_payload, stage
from candidate_core.errors import ProductctlError, UsageError
from candidate_core.jsonio import dumps
from candidate_core.payload import current_platform, verify_payload
from candidate_core.runtime import discover_runtimes


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
        if getattr(args, "payload", None):
            ctx.payload_root = Path(args.payload)
        if getattr(args, "target_platform", None):
            ctx.target_platform = args.target_platform
        return run_core(ctx)
    if command == "runtime.discover":
        return _runtime_discover(ctx, args)
    if command == "payload.verify":
        return _payload_verify(ctx, args)
    raise UsageError(f"unsupported command: {command}")


def _runtime_discover(ctx: CommandContext, args: argparse.Namespace) -> dict[str, Any]:
    ctx.contract_path = Path(args.contract)
    contract = load_and_validate_contract(ctx.contract_path)
    result = discover_runtimes(contract["runtime"]["discovery"]["required_capabilities"])
    selected = result.get("selected")
    status = "passed" if selected is not None else "failed"
    error = None if status == "passed" else error_payload(
        "runtime_not_found",
        "no Python 3.11 or 3.12 candidate satisfied required capabilities",
    )
    ctx.add_stage(stage("runtime.discover", status if status == "passed" else "failed", observations=result, error=error))
    return build_envelope(
        run_id=ctx.run_id,
        command=ctx.command,
        status=status,
        stages=ctx.stages,
        observations=result,
        error=error,
    )


def _payload_verify(ctx: CommandContext, args: argparse.Namespace) -> dict[str, Any]:
    ctx.contract_path = Path(args.contract)
    contract = load_and_validate_contract(ctx.contract_path)
    payload_root = Path(args.payload) if args.payload else ctx.contract_path.parent / "payload"
    python_series = args.python or contract["platforms"]["python"][0]
    target_platform = args.target_platform or current_platform()
    result = verify_payload(payload_root, target_platform=target_platform, python_series=python_series)
    status = "passed" if result["status"] == "selected" else "failed"
    rejected = [item for item in result["candidates"] if item["status"] == "rejected" and item["reasons"]]
    category = rejected[0]["reasons"][0]["category"] if rejected else "payload_rejected"
    error = None if status == "passed" else error_payload(category, "payload verification rejected one or more required files")
    ctx.add_stage(stage("payload.verify", "passed" if status == "passed" else "failed", observations=result, error=error))
    return build_envelope(
        run_id=ctx.run_id,
        command=ctx.command,
        status=status,
        stages=ctx.stages,
        observations=result,
        error=error,
    )


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
    core.add_argument("--payload", help="payload directory containing manifest.json")
    core.add_argument("--target-platform", dest="target_platform", help="linux-x86_64, windows-x64, or macos-arm64")

    runtime = sub.add_parser("runtime", help="runtime discovery")
    runtime_sub = runtime.add_subparsers(dest="action", required=True)
    runtime_discover = runtime_sub.add_parser("discover", help="discover Python runtimes by capability")
    runtime_discover.add_argument("--contract", required=True)

    payload = sub.add_parser("payload", help="payload verification")
    payload_sub = payload.add_subparsers(dest="action", required=True)
    payload_verify = payload_sub.add_parser("verify", help="verify target-specific payload files")
    payload_verify.add_argument("--contract", required=True)
    payload_verify.add_argument("--payload", help="payload directory containing manifest.json")
    payload_verify.add_argument("--python", help="target Python series, such as 3.12")
    payload_verify.add_argument("--target-platform", dest="target_platform")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
