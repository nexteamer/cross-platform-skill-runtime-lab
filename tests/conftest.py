from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "products" / "short-essay" / "productctl.contract.json"


def run_productctl(*args: str, cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
    env = os.environ.copy()
    src = str(ROOT / "src")
    env["PYTHONPATH"] = src + os.pathsep + env.get("PYTHONPATH", "")
    return subprocess.run(
        [sys.executable, "-m", "candidate_core", *args],
        cwd=cwd or ROOT,
        capture_output=True,
        text=True,
        check=False,
        env=env,
    )


@pytest.fixture
def contract_path() -> Path:
    return CONTRACT
