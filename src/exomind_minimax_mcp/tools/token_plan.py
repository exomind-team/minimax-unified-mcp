"""Official Token Plan tools（官方 Token Plan 工具）."""

from __future__ import annotations

import json

from exomind_minimax_mcp.clients.base import MiniMaxBaseClient
from exomind_minimax_mcp.config import load_settings
from exomind_minimax_mcp.image_utils import normalize_image_url


def _get_token_plan_client(api_client: MiniMaxBaseClient | None) -> MiniMaxBaseClient:
    if api_client is not None:
        return api_client

    settings = load_settings()
    if not settings.token_plan_api_key:
        raise ValueError("MINIMAX_TOKEN_PLAN_API_KEY or MINIMAX_API_KEY is required")
    return MiniMaxBaseClient(settings.token_plan_api_key, settings.api_host)


def web_search(query: str, api_client: MiniMaxBaseClient | None = None) -> str:
    """Official `web_search` tool（官方网页搜索工具）."""

    if not query:
        raise ValueError("query is required")

    client = _get_token_plan_client(api_client)
    payload = client.post_json("/v1/coding_plan/search", {"q": query})
    return json.dumps(payload, ensure_ascii=False, indent=2)


def understand_image(
    prompt: str,
    image_url: str | None = None,
    image_source: str | None = None,
    api_client: MiniMaxBaseClient | None = None,
) -> str:
    """Official `understand_image` tool（官方图片理解工具）."""

    if not prompt:
        raise ValueError("prompt is required")

    resolved_image = image_url or image_source
    if not resolved_image:
        raise ValueError("image_url is required")

    client = _get_token_plan_client(api_client)
    payload = client.post_json(
        "/v1/coding_plan/vlm",
        {
            "prompt": prompt,
            "image_url": normalize_image_url(resolved_image),
        },
    )
    return payload.get("content", "")
