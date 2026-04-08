from pathlib import Path


def test_load_config_prefers_explicit_token_plan_key(monkeypatch):
    from exomind_minimax_mcp.config import load_settings

    monkeypatch.setenv("MINIMAX_TOKEN_PLAN_API_KEY", "token-plan-key")
    monkeypatch.setenv("MINIMAX_API_HOST", "https://api.minimax.io")
    monkeypatch.setenv("MINIMAX_MCP_BASE_PATH", str(Path("./output")))

    settings = load_settings()

    assert settings.token_plan_api_key == "token-plan-key"
    assert settings.api_host == "https://api.minimax.io"


def test_load_config_does_not_use_legacy_api_key_for_token_plan(monkeypatch):
    from exomind_minimax_mcp.config import load_settings

    monkeypatch.delenv("MINIMAX_TOKEN_PLAN_API_KEY", raising=False)
    monkeypatch.setenv("MINIMAX_API_KEY", "legacy-key")

    settings = load_settings()

    assert settings.token_plan_api_key is None


def test_load_config_expands_base_path(monkeypatch):
    from exomind_minimax_mcp.config import load_settings

    monkeypatch.delenv("MINIMAX_TOKEN_PLAN_API_KEY", raising=False)
    monkeypatch.delenv("MINIMAX_API_KEY", raising=False)
    monkeypatch.setenv("MINIMAX_API_HOST", "https://api.minimaxi.com")
    monkeypatch.setenv("MINIMAX_MCP_BASE_PATH", "~/minimax-output")

    settings = load_settings()

    assert settings.base_path == Path.home() / "minimax-output"
