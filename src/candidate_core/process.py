from __future__ import annotations

import subprocess
from dataclasses import dataclass
from pathlib import Path
from typing import Mapping, Sequence


@dataclass
class ProcessResult:
    argv: list[str]
    returncode: int
    stdout: str
    stderr: str
    executable: str

    @property
    def ok(self) -> bool:
        return self.returncode == 0


def run_argv(
    argv: Sequence[str],
    *,
    cwd: Path | None = None,
    env: Mapping[str, str] | None = None,
    timeout: float | None = None,
    stdin: str | None = None,
    close_stdin: bool = False,
) -> ProcessResult:
    if not argv:
        raise ValueError("argv must not be empty")
    command = [str(part) for part in argv]
    try:
        completed = subprocess.run(
            command,
            cwd=cwd,
            env=dict(env) if env is not None else None,
            input=None if close_stdin else stdin,
            stdin=subprocess.DEVNULL if close_stdin else None,
            capture_output=True,
            text=True,
            timeout=timeout,
            check=False,
            shell=False,
        )
    except subprocess.TimeoutExpired as exc:
        stdout = exc.stdout.decode("utf-8") if isinstance(exc.stdout, bytes) else (exc.stdout or "")
        stderr = exc.stderr.decode("utf-8") if isinstance(exc.stderr, bytes) else (exc.stderr or "")
        return ProcessResult(
            argv=command,
            returncode=124,
            stdout=stdout,
            stderr=(stderr + f"\ntimeout after {timeout}s").strip(),
            executable=command[0],
        )
    return ProcessResult(
        argv=command,
        returncode=completed.returncode,
        stdout=completed.stdout or "",
        stderr=completed.stderr or "",
        executable=command[0],
    )
