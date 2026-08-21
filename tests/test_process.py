from __future__ import annotations

import sys
from pathlib import Path

from candidate_core.process import run_argv


def test_empty_argument_is_preserved() -> None:
    result = run_argv([sys.executable, "-c", "import sys,json; print(json.dumps(sys.argv[1:]))", "", "kept"])
    assert result.ok
    assert result.stderr == ""
    assert '"", "kept"' in result.stdout or '["", "kept"]' in result.stdout.replace(" ", "")


def test_stderr_does_not_fail_zero_exit() -> None:
    result = run_argv(
        [sys.executable, "-c", "import sys; sys.stderr.write('trace\\n'); sys.stdout.write('ok\\n')"]
    )
    assert result.ok
    assert result.returncode == 0
    assert "trace" in result.stderr
    assert "ok" in result.stdout
