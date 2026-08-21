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
from candidate_core.install import InstallError, install_product
from candidate_core.lease import lease_release, lease_status
from candidate_core.locks import LockError
from candidate_core.codex import probe_codex, resolve_codex
from candidate_core.network import probe_network
from candidate_core.payload import current_platform, verify_payload
from candidate_core.process_probe import probe_pid
from candidate_core.runtime import discover_runtimes
from candidate_core.service import preflight, start_service, status_service, stop_service


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
        if getattr(args, "prefix", None):
            ctx.prefix = Path(args.prefix)
        if getattr(args, "python", None):
            ctx.python_executable = args.python
        return run_core(ctx)
    if command == "install.run":
        return _install(ctx, args)
    if command == "runtime.discover":
        return _runtime_discover(ctx, args)
    if command == "payload.verify":
        return _payload_verify(ctx, args)
    if command.startswith("service.") or command.startswith("lease."):
        return _service_or_lease(ctx, args, command)
    if command == "workflow.run":
        from short_essay.workflow import run_short_essay

        payload = run_short_essay(args.text, data_root=Path(args.data_root))
        ctx.add_stage(stage("workflow_run", "passed", observations=payload))
        return build_envelope(
            run_id=payload["run_id"],
            command=ctx.command,
            status="passed",
            stages=ctx.stages,
            observations=payload,
        )
    if command == "network.probe":
        result = probe_network(host=getattr(args, "host", "example.com"), url=getattr(args, "url", None))
        status = result["status"]
        error = None if status == "passed" else error_payload(result["category"], f"network probe failed at {result['failed_stage']}")
        ctx.add_stage(stage("network_probe", "passed" if status == "passed" else "failed", observations=result, error=error))
        return build_envelope(run_id=ctx.run_id, command=ctx.command, status=status, stages=ctx.stages, observations=result, error=error)
    if command == "codex.resolve":
        result = resolve_codex(
            requested={"model": args.model, "transport": args.transport},
        )
        ctx.add_stage(stage("codex_resolve", "passed", observations=result))
        return build_envelope(run_id=ctx.run_id, command=ctx.command, status="passed", stages=ctx.stages, observations=result)
    if command == "codex.probe":
        extra = ["--fail", args.fail] if getattr(args, "fail", None) else None
        result = probe_codex(
            requested={"model": args.model, "transport": args.transport},
            extra_args=extra,
        )
        status = result["status"]
        error = None if status == "passed" else error_payload("codex_probe_failed", result["launch"]["exit_category"])
        ctx.add_stage(stage("codex_probe", "passed" if status == "passed" else "failed", observations=result, error=error))
        return build_envelope(run_id=ctx.run_id, command=ctx.command, status=status, stages=ctx.stages, observations=result, error=error)
    if command == "process.probe":
        result = probe_pid(int(args.pid))
        status = result["status"]
        error = None if status == "passed" else error_payload(result.get("category") or "failed", result.get("category") or "process probe failed")
        ctx.add_stage(stage("process_probe", "passed" if status == "passed" else "failed", observations=result, error=error))
        return build_envelope(
            run_id=ctx.run_id,
            command=ctx.command,
            status=status,
            stages=ctx.stages,
            observations=result,
            error=error,
        )
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


def _install(ctx: CommandContext, args: argparse.Namespace) -> dict[str, Any]:
    ctx.contract_path = Path(args.contract)
    contract = load_and_validate_contract(ctx.contract_path)
    payload_root = Path(args.payload)
    try:
        result = install_product(
            prefix=Path(args.prefix),
            payload_root=payload_root,
            python_executable=args.python,
            app_id=contract["product"]["id"],
            run_id=ctx.run_id,
            data_root_override=getattr(args, "data_root", None),
            inherit_to_children=contract["data_roots"]["inherit_to_children"],
        )
    except InstallError as exc:
        ctx.add_stage(
            stage("install", "failed", error=error_payload(exc.category, exc.message))
        )
        return build_envelope(
            run_id=ctx.run_id,
            command=ctx.command,
            status="failed",
            stages=ctx.stages,
            error=error_payload(exc.category, exc.message),
        )
    ctx.add_stage(stage("install", "passed", observations=result))
    return build_envelope(
        run_id=ctx.run_id,
        command=ctx.command,
        status="passed",
        stages=ctx.stages,
        observations=result,
    )


def _service_or_lease(ctx: CommandContext, args: argparse.Namespace, command: str) -> dict[str, Any]:
    prefix = Path(args.prefix)
    run_id = getattr(args, "run_id", None) or ctx.run_id
    ctx.run_id = run_id
    try:
        if command == "service.preflight":
            result = preflight(prefix)
        elif command == "service.start":
            result = start_service(prefix, run_id=run_id, owner=args.owner)
        elif command == "service.status":
            result = status_service(prefix)
        elif command == "service.stop":
            result = stop_service(prefix, run_id=run_id)
        elif command == "lease.status":
            result = lease_status(prefix)
        elif command == "lease.release":
            result = lease_release(prefix, run_id=run_id)
        else:
            raise UsageError(f"unsupported command: {command}")
    except LockError as exc:
        ctx.add_stage(stage(command.replace(".", "_"), "failed", error=error_payload(exc.category, exc.message)))
        return build_envelope(
            run_id=ctx.run_id,
            command=ctx.command,
            status="failed",
            stages=ctx.stages,
            error=error_payload(exc.category, exc.message),
        )
    status = result.get("status", "passed")
    error = None
    if status != "passed":
        error = error_payload(result.get("category") or "failed", result.get("message") or status)
    ctx.add_stage(stage(command.replace(".", "_"), "passed" if status == "passed" else "failed", observations=result, error=error))
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

    install = sub.add_parser("install", help="transactional product install")
    install_sub = install.add_subparsers(dest="action", required=True)
    install_run = install_sub.add_parser("run", help="stage, promote, smoke, and receipt")
    install_run.add_argument("--contract", required=True)
    install_run.add_argument("--payload", required=True)
    install_run.add_argument("--prefix", required=True)
    install_run.add_argument("--python", required=True, help="absolute interpreter used to create the venv")
    install_run.add_argument("--data-root", dest="data_root")
    core.add_argument("--prefix", help="install prefix for acceptance")
    core.add_argument("--python", help="interpreter used when acceptance also installs")

    service = sub.add_parser("service", help="loopback service lifecycle")
    service_sub = service.add_subparsers(dest="action", required=True)
    for action in ("preflight", "start", "stop", "status"):
        parser_action = service_sub.add_parser(action)
        parser_action.add_argument("--prefix", required=True)
        parser_action.add_argument("--run-id", dest="run_id")
        if action == "start":
            parser_action.add_argument("--owner", default="short-essay-lab")

    workflow = sub.add_parser("workflow", help="product workflow")
    workflow_sub = workflow.add_subparsers(dest="action", required=True)
    workflow_run = workflow_sub.add_parser("run")
    workflow_run.add_argument("--text", required=True)
    workflow_run.add_argument("--data-root", dest="data_root", required=True)

    network = sub.add_parser("network", help="layered network probe")
    network_sub = network.add_subparsers(dest="action", required=True)
    network_probe = network_sub.add_parser("probe")
    network_probe.add_argument("--host", default="example.com")
    network_probe.add_argument("--url")

    codex = sub.add_parser("codex", help="fake or real Codex resolve/probe")
    codex_sub = codex.add_subparsers(dest="action", required=True)
    for action in ("resolve", "probe"):
        parser_action = codex_sub.add_parser(action)
        parser_action.add_argument("--model", default="fake-model")
        parser_action.add_argument("--transport", default="fake-transport")
        if action == "probe":
            parser_action.add_argument("--fail")

    process = sub.add_parser("process", help="process identity evidence")
    process_sub = process.add_subparsers(dest="action", required=True)
    process_probe = process_sub.add_parser("probe")
    process_probe.add_argument("--pid", required=True, type=int)

    lease = sub.add_parser("lease", help="service lease ownership")
    lease_sub = lease.add_subparsers(dest="action", required=True)
    for action in ("status", "release"):
        parser_action = lease_sub.add_parser(action)
        parser_action.add_argument("--prefix", required=True)
        parser_action.add_argument("--run-id", dest="run_id")
    return parser


if __name__ == "__main__":
    raise SystemExit(main())
