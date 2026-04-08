"""Token Plan quota client（Token Plan 额度客户端）."""

from __future__ import annotations

import requests

TOKEN_PLAN_REMAINS_URL = "https://www.minimax.io/v1/api/openplatform/coding_plan/remains"


class TokenPlanQuotaClient:
    """HTTP client for Token Plan remains endpoint（额度查询客户端）."""

    def __init__(self, api_key: str, url: str = TOKEN_PLAN_REMAINS_URL):
        self.api_key = api_key
        self.url = url

    def build_headers(self) -> dict[str, str]:
        return {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
            "Accept": "application/json",
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/120.0.0.0 Safari/537.36"
            ),
            "Referer": "https://www.minimax.io/",
            "Origin": "https://www.minimax.io",
        }

    def fetch_remains(self) -> dict:
        response = requests.get(self.url, headers=self.build_headers(), timeout=15)
        response.raise_for_status()
        return response.json()
