from __future__ import annotations

from pathlib import Path

from exomind_minimax_mcp.live_runner import LIVE_TOOL_ORDER, run_live_matrix
from tests.live_config import load_live_test_settings


def test_live_matrix_executes_every_tool_with_classified_statuses(tmp_path):
    settings = load_live_test_settings()

    results = run_live_matrix(
        api_key=settings.token_plan_key,
        api_host=settings.api_host,
        output_dir=tmp_path / "live-matrix-output",
    )

    result_map = {item.tool: item for item in results}

    assert [item.tool for item in results] == LIVE_TOOL_ORDER

    assert result_map["get_token_plan_quota"].status == "passed"
    assert result_map["web_search"].status == "passed"
    assert result_map["understand_image"].status == "passed"
    assert result_map["text_to_audio"].status == "passed"
    assert result_map["list_voices"].status == "passed"
    assert result_map["play_audio"].status == "passed"
    assert result_map["generate_video"].status in {"passed", "usage_limit_exceeded", "insufficient_balance", "unsupported"}
    assert result_map["query_video_generation"].status in {"passed", "processing", "skipped"}
    assert result_map["text_to_image"].status == "passed"

    assert result_map["music_generation"].status in {"passed", "unsupported", "timeout", "usage_limit_exceeded"}
    assert result_map["voice_design"].status in {"passed", "insufficient_balance", "unsupported", "timeout"}
    assert result_map["voice_clone"].status in {"passed", "invalid_params", "unsupported", "insufficient_balance", "timeout"}

    for item in results:
        assert item.status != "error", f"{item.tool} returned unclassified error: {item.detail}"
        assert item.detail.strip() != ""


def test_live_matrix_keeps_audio_artifact_for_followup_steps(tmp_path):
    settings = load_live_test_settings()

    results = run_live_matrix(
        api_key=settings.token_plan_key,
        api_host=settings.api_host,
        output_dir=tmp_path / "live-matrix-output",
        only="text_to_audio",
    )

    assert len(results) == 1
    assert results[0].tool == "text_to_audio"
    assert results[0].status == "passed"
    assert results[0].artifact is not None
    assert Path(results[0].artifact).exists()
