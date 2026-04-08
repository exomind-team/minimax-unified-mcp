from __future__ import annotations

from pathlib import Path


def test_env_example_mentions_required_token_plan_settings():
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "MINIMAX_TOKEN_PLAN_API_KEY" in env_example
    assert "MINIMAX_API_RESOURCE_MODE" in env_example


def test_examples_no_longer_use_legacy_minimax_api_key_name():
    example_files = [
        Path(".env.example"),
        Path("README.md"),
        Path("README-CN.md"),
        Path("mcp_server_config_demo.json"),
    ]

    for path in example_files:
        text = path.read_text(encoding="utf-8")
        assert "MINIMAX_API_KEY" not in text, f"{path} still references legacy MINIMAX_API_KEY"
