"""Configuration helpers（配置辅助） for the unified MiniMax MCP server."""

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path


DEFAULT_API_HOST = "https://api.minimax.io"
DEFAULT_RESOURCE_MODE = "url"
DEFAULT_LOG_LEVEL = "WARNING"


@dataclass(frozen=True)
class Settings:
    """Application settings（应用配置）."""

    api_host: str
    default_api_key: str | None
    token_plan_api_key: str | None
    payg_api_key: str | None
    base_path: Path
    resource_mode: str
    log_level: str


def _expand_path(raw_path: str | None) -> Path:
    if not raw_path:
        return Path.home() / "Desktop"
    return Path(os.path.expanduser(raw_path))


def load_settings() -> Settings:
    """Load settings from environment variables（从环境变量加载配置）."""

    default_api_key = os.getenv("MINIMAX_API_KEY")
    token_plan_api_key = os.getenv("MINIMAX_TOKEN_PLAN_API_KEY") or default_api_key
    payg_api_key = os.getenv("MINIMAX_PAYG_API_KEY") or default_api_key

    return Settings(
        api_host=os.getenv("MINIMAX_API_HOST", DEFAULT_API_HOST),
        default_api_key=default_api_key,
        token_plan_api_key=token_plan_api_key,
        payg_api_key=payg_api_key,
        base_path=_expand_path(os.getenv("MINIMAX_MCP_BASE_PATH")),
        resource_mode=os.getenv("MINIMAX_API_RESOURCE_MODE", DEFAULT_RESOURCE_MODE),
        log_level=os.getenv("FASTMCP_LOG_LEVEL", DEFAULT_LOG_LEVEL),
    )
