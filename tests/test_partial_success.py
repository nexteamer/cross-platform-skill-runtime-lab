from __future__ import annotations

import json
from pathlib import Path

from short_essay.workflow import run_short_essay
from tests.conftest import run_productctl


def test_zero_through_four_candidates(tmp_path: Path) -> None:
    for count in range(0, 5):
        result = run_short_essay("text", data_root=tmp_path / f"n{count}", polish_candidates=count)
        assert result["status"] == "passed"
        assert result["retried"] is False


def test_one_failed_candidate_is_partial_success(tmp_path: Path) -> None:
    result = run_short_essay(
        "text",
        data_root=tmp_path,
        polish_candidates=2,
        fail_candidates=[1],
    )
    assert result["status"] == "partial_success"
    assert result["result"]
    assert result["failures"]
    assert Path(result["artifacts"]["polish-1"]).is_file()
    assert result["retried"] is False


def test_two_failed_candidates_fail_without_retry(tmp_path: Path) -> None:
    result = run_short_essay(
        "text",
        data_root=tmp_path,
        polish_candidates=2,
        fail_candidates=[1, 2],
    )
    assert result["status"] == "failed"
    assert result["result"] is None
    assert result["retried"] is False
    assert len(result["failures"]) == 2


def test_timeout_and_cancel_fixtures(tmp_path: Path) -> None:
    timed = run_short_essay("text", data_root=tmp_path / "timeout", polish_candidates=2, timeout=0.0)
    assert timed["status"] in {"failed", "partial_success", "passed"}
    cancelled = run_short_essay("text", data_root=tmp_path / "cancel", polish_candidates=3, cancel=True)
    assert cancelled["status"] == "failed"
    assert cancelled["retried"] is False
    proc = run_productctl(
        "--json",
        "workflow",
        "run",
        "--text",
        "x",
        "--data-root",
        str(tmp_path / "cli"),
        "--fail-candidates",
        "1",
    )
    envelope = json.loads(proc.stdout)
    assert envelope["status"] == "partial_success"
