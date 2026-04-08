"""Quota tool（额度工具） implementation."""

from __future__ import annotations

import json

from exomind_minimax_mcp.clients.quota import TokenPlanQuotaClient
from exomind_minimax_mcp.config import load_settings


DISPLAY_NAMES = {
    "MiniMax-M*": "MiniMax-M2.7-highspeed",
    "speech-hd": "MiniMax Speech-HD",
    "MiniMax-Hailuo-2.3-Fast-6s-768p": "MiniMax Hailuo 2.3 Fast",
    "MiniMax-Hailuo-2.3-6s-768p": "MiniMax Hailuo 2.3",
    "music-2.5": "MiniMax Music 2.5",
    "image-01": "MiniMax Image-01",
}


def resolve_display_name(model_name: str) -> str:
    return DISPLAY_NAMES.get(model_name, model_name)


def format_duration(ms: int) -> str:
    if ms <= 0:
        return "reset"

    total_seconds = ms / 1000
    hours = int(total_seconds // 3600)
    minutes = int((total_seconds % 3600) // 60)

    if hours > 24:
        days = hours // 24
        hours = hours % 24
        return f"{days}d {hours}h"
    if hours > 0:
        return f"{hours}h {minutes}m"
    return f"{minutes}m"


def _select_models(models: list[dict], model: str | None, all_models: bool) -> list[dict]:
    if all_models or not model:
        return models
    return [item for item in models if model in item.get("model_name", "")]


def _format_table(models: list[dict]) -> str:
    lines = [
        "MiniMax Token Plan Quota",
        "",
        "| Model | Interval Remains | Reset In | Weekly Remains |",
        "| --- | ---: | ---: | ---: |",
    ]

    for item in models:
        lines.append(
            "| {model} | {interval} | {reset} | {weekly} |".format(
                model=resolve_display_name(item["model_name"]),
                interval=f'{item["current_interval_usage_count"]:,}/{item["current_interval_total_count"]:,}',
                reset=format_duration(item["remains_time"]),
                weekly=f'{item["current_weekly_usage_count"]:,}/{item["current_weekly_total_count"]:,}',
            )
        )

    return "\n".join(lines)


def get_token_plan_quota(
    model: str = "MiniMax-M*",
    all_models: bool = False,
    raw_json: bool = False,
    quota_client: TokenPlanQuotaClient | None = None,
) -> str:
    """Get Token Plan quota（查询 Token Plan 额度）."""

    if quota_client is None:
        settings = load_settings()
        if not settings.token_plan_api_key:
            raise ValueError("MINIMAX_TOKEN_PLAN_API_KEY or MINIMAX_API_KEY is required")
        quota_client = TokenPlanQuotaClient(api_key=settings.token_plan_api_key)

    payload = quota_client.fetch_remains()
    if raw_json:
        return json.dumps(payload, ensure_ascii=False, indent=2)

    models = _select_models(payload.get("model_remains", []), model, all_models)
    return _format_table(models)
