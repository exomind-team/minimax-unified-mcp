from __future__ import annotations

import json
from pathlib import Path


def test_live_runner_declares_all_tool_checks():
    from exomind_minimax_mcp.live_runner import LIVE_TOOL_ORDER

    assert LIVE_TOOL_ORDER == [
        "get_token_plan_quota",
        "web_search",
        "understand_image",
        "text_to_audio",
        "list_voices",
        "voice_clone",
        "play_audio",
        "generate_video",
        "query_video_generation",
        "text_to_image",
        "music_generation",
        "voice_design",
    ]


def test_live_runner_classifies_known_account_limit_errors():
    from exomind_minimax_mcp.live_runner import classify_live_failure

    timeout = classify_live_failure("ReadTimeout: HTTPSConnectionPool(host='api.minimax.io', port=443): Read timed out")
    unsupported = classify_live_failure("API Error: 2061-your current token plan not support model")
    limit = classify_live_failure("API Error: 2056-usage limit exceeded")
    balance = classify_live_failure("API Error: 1008-insufficient balance")
    invalid = classify_live_failure("API Error: 2013-invalid params")
    other = classify_live_failure("some unexpected failure")

    assert timeout == "timeout"
    assert unsupported == "unsupported"
    assert limit == "usage_limit_exceeded"
    assert balance == "insufficient_balance"
    assert invalid == "invalid_params"
    assert other == "error"


def test_live_runner_writes_valid_png_fixture(tmp_path):
    from exomind_minimax_mcp.live_runner import create_live_png_fixture

    image_path = create_live_png_fixture(tmp_path / "sample.png")

    data = image_path.read_bytes()
    assert image_path.exists()
    assert data.startswith(b"\x89PNG\r\n\x1a\n")


def test_live_runner_formats_json_report():
    from exomind_minimax_mcp.live_runner import LiveCheckResult, format_live_report_json

    report = format_live_report_json(
        [
            LiveCheckResult(tool="web_search", status="passed", detail="ok"),
            LiveCheckResult(tool="music_generation", status="unsupported", detail="model not supported"),
        ]
    )

    parsed = json.loads(report)
    assert parsed[0]["tool"] == "web_search"
    assert parsed[1]["status"] == "unsupported"


def test_live_runner_resolves_relative_artifact_into_output_dir(tmp_path):
    from exomind_minimax_mcp.live_runner import _resolve_artifact_path

    artifact = _resolve_artifact_path("audio.mp3", tmp_path)

    assert artifact == tmp_path / "audio.mp3"
