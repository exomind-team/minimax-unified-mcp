"""Configuration helpers（配置辅助） for the unified MiniMax MCP server."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_API_HOST = "https://api.minimax.io"
DEFAULT_RESOURCE_MODE = "url"
DEFAULT_LOG_LEVEL = "WARNING"

# Path to the Claude Code global settings.json for fallback key resolution
_CLAUDE_SETTINGS_PATH = Path.home() / ".claude" / "settings.json"


def _read_claude_settings_key(key: str) -> str | None:
    """Read a value from Claude Code's global settings.json as fallback.

    Checks both the top-level ``env`` block and the ``mcpServers.MiniMaxUnified.env`` block.
    """
    try:
        raw = _CLAUDE_SETTINGS_PATH.read_text(encoding="utf-8")
        data = json.loads(raw)
    except (OSError, json.JSONDecodeError):
        return None

    # Top-level env
    top_env = data.get("env", {})
    if key in top_env:
        return top_env[key]

    # MCP server specific env
    mcp_servers = data.get("mcpServers", {})
    minimax = mcp_servers.get("MiniMaxUnified", {})
    mcp_env = minimax.get("env", {})
    if key in mcp_env:
        return mcp_env[key]

    return None


@dataclass(frozen=True)
class Settings:
    """Application settings（应用配置）."""

    api_host: str
    token_plan_api_key: str | None
    base_path: Path
    resource_mode: str
    log_level: str


def _expand_path(raw_path: str | None) -> Path:
    if not raw_path:
        return Path.home() / "Desktop"
    return Path(os.path.expanduser(raw_path))


def _env_or_claude(key: str, default: str | None = None) -> str | None:
    """Return settings.json value first, falling back to os.getenv then default.

    Claude Code sometimes caches stale MCP env vars; preferring the settings file
    ensures the MCP always uses the latest key.
    """
    val = _read_claude_settings_key(key)
    if val is not None:
        return val
    return os.getenv(key) or default


def load_settings() -> Settings:
    """Load settings from environment variables（从环境变量加载配置）."""

    token_plan_api_key = _env_or_claude("MINIMAX_TOKEN_PLAN_API_KEY")
    return Settings(
        api_host=_env_or_claude("MINIMAX_API_HOST", DEFAULT_API_HOST) or DEFAULT_API_HOST,
        token_plan_api_key=token_plan_api_key,
        base_path=_expand_path(_env_or_claude("MINIMAX_MCP_BASE_PATH")),
        resource_mode=_env_or_claude("MINIMAX_API_RESOURCE_MODE", DEFAULT_RESOURCE_MODE) or DEFAULT_RESOURCE_MODE,
        log_level=_env_or_claude("FASTMCP_LOG_LEVEL", DEFAULT_LOG_LEVEL) or DEFAULT_LOG_LEVEL,
    )
