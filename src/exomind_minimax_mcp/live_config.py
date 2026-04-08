"""Live MiniMax credential loading（真实在线测试凭证加载） helpers."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass
from pathlib import Path

@dataclass(frozen=True)
class LiveTestSettings:
    api_host: str
    token_plan_key: str


def load_live_settings() -> LiveTestSettings | None:
    settings = _from_env()
    if settings is not None:
        return settings
    return _from_claude_config()


def _from_env() -> LiveTestSettings | None:
    api_host = os.getenv("MINIMAX_API_HOST")
    token_plan_key = os.getenv("MINIMAX_TOKEN_PLAN_API_KEY")
    if api_host and token_plan_key:
        return LiveTestSettings(api_host=api_host, token_plan_key=token_plan_key)
    return None


def _from_claude_config() -> LiveTestSettings | None:
    for config_path in _candidate_claude_config_paths():
        if not config_path.exists():
            continue

        data = json.loads(config_path.read_text(encoding="utf-8"))
        servers = data.get("mcpServers", {})
        unified = servers.get("MiniMaxUnified", {})
        token_plan = servers.get("MiniMax", {})

        unified_env = unified.get("env", {}) or {}
        token_plan_env = token_plan.get("env", {}) or {}

        api_host = unified_env.get("MINIMAX_API_HOST") or token_plan_env.get("MINIMAX_API_HOST")
        token_plan_key = unified_env.get("MINIMAX_TOKEN_PLAN_API_KEY") or token_plan_env.get("MINIMAX_TOKEN_PLAN_API_KEY")

        if api_host and token_plan_key:
            return LiveTestSettings(api_host=api_host, token_plan_key=token_plan_key)
    return None


def _candidate_claude_config_paths() -> list[Path]:
    explicit_path = os.getenv("MINIMAX_CLAUDE_CONFIG_PATH")
    paths: list[Path] = []
    if explicit_path:
        paths.append(Path(explicit_path).expanduser())

    default_path = Path.home() / ".claude.json"
    if default_path not in paths:
        paths.append(default_path)

    return paths
