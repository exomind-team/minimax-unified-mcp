"""Base HTTP client（基础 HTTP 客户端） for MiniMax APIs."""

from __future__ import annotations

from typing import Any

import requests

from exomind_minimax_mcp.exceptions import MiniMaxAuthError, MiniMaxRequestError


class MiniMaxBaseClient:
    """Minimal shared API client（最小共享 API 客户端）."""

    def __init__(self, api_key: str, base_url: str):
        self.api_key = api_key
        self.base_url = base_url.rstrip("/")
        self.session = requests.Session()
        self.session.headers.update(
            {
                "Authorization": f"Bearer {api_key}",
                "Content-Type": "application/json",
                "MM-API-Source": "ExoMind-MiniMax-Unified-MCP",
            }
        )

    def post(self, endpoint: str, **kwargs: Any) -> requests.Response:
        return self.session.post(f"{self.base_url}{endpoint}", **kwargs)

    def request_json(
        self,
        method: str,
        endpoint: str,
        timeout: int = 30,
        **kwargs: Any,
    ) -> dict[str, Any]:
        response = self.session.request(method, f"{self.base_url}{endpoint}", timeout=timeout, **kwargs)
        return self._parse_json_response(response)

    def post_json(
        self,
        endpoint: str,
        payload: dict[str, Any],
        timeout: int = 30,
    ) -> dict[str, Any]:
        return self.request_json("POST", endpoint, json=payload, timeout=timeout)

    def get_json(self, endpoint: str, timeout: int = 30) -> dict[str, Any]:
        response = self.session.get(f"{self.base_url}{endpoint}", timeout=timeout)
        return self._parse_json_response(response)

    def _parse_json_response(self, response: requests.Response) -> dict[str, Any]:
        response.raise_for_status()
        data = response.json()
        base_resp = data.get("base_resp", {})
        if base_resp and base_resp.get("status_code") not in (None, 0):
            status_code = base_resp.get("status_code")
            status_msg = base_resp.get("status_msg", "")
            trace_id = response.headers.get("Trace-Id")
            if status_code == 1004:
                raise MiniMaxAuthError(
                    f"API Error: {status_msg}, please check your API key and API host. Trace-Id: {trace_id}"
                )
            if status_code == 1008:
                raise MiniMaxRequestError(
                    "API Error: insufficient balance（余额不足）. "
                    f"Upstream: {status_msg}. Trace-Id: {trace_id}"
                )
            if status_code == 2056:
                raise MiniMaxRequestError(
                    "API Error: usage limit exceeded（额度或用量已耗尽）. "
                    "Please wait for quota refresh or switch models / plans（请等待额度刷新或切换模型 / 套餐）. "
                    f"Upstream: {status_msg}. Trace-Id: {trace_id}"
                )
            raise MiniMaxRequestError(f"API Error: {status_code}-{status_msg} Trace-Id: {trace_id}")
        return data
