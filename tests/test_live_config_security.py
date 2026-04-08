from __future__ import annotations

import json
from pathlib import Path


def test_live_config_source_does_not_hardcode_user_specific_path():
    source = Path("src/exomind_minimax_mcp/live_config.py").read_text(encoding="utf-8")

    assert "C:\\Users\\starlin" not in source
    assert ".claude.json" in source


def test_load_live_settings_supports_explicit_config_path(monkeypatch, tmp_path):
    from exomind_minimax_mcp.live_config import load_live_settings

    config_path = tmp_path / "claude.json"
    config_path.write_text(
        json.dumps(
            {
                "mcpServers": {
                    "MiniMaxUnified": {
                        "env": {
                            "MINIMAX_API_HOST": "https://api.minimax.io",
                            "MINIMAX_TOKEN_PLAN_API_KEY": "token-plan-key",
                        }
                    }
                }
            }
        ),
        encoding="utf-8",
    )

    monkeypatch.delenv("MINIMAX_API_HOST", raising=False)
    monkeypatch.delenv("MINIMAX_TOKEN_PLAN_API_KEY", raising=False)
    monkeypatch.setenv("MINIMAX_CLAUDE_CONFIG_PATH", str(config_path))

    settings = load_live_settings()

    assert settings is not None
    assert settings.api_host == "https://api.minimax.io"
    assert settings.token_plan_key == "token-plan-key"
