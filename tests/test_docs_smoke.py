from __future__ import annotations

from pathlib import Path


def test_env_example_mentions_token_plan_and_payg_keys():
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "MINIMAX_TOKEN_PLAN_API_KEY" in env_example
    assert "MINIMAX_PAYG_API_KEY" in env_example
    assert "MINIMAX_API_RESOURCE_MODE" in env_example
