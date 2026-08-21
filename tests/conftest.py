from __future__ import annotations

import os
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "products" / "short-essay" / "productctl.contract.json"


def run_productctl(
    *args: str,
    cwd: Path | None = None,
    env: dict[str, str] | None = None,
) -> subprocess.CompletedProcess[str]:
    merged = os.environ.copy()
    if env:
        merged.update(env)
    src = str(ROOT / "src")
    merged["PYTHONPATH"] = src + os.pathsep + merged.get("PYTHONPATH", "")
    env = merged
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
