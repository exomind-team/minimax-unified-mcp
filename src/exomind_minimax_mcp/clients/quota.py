"""Token Plan quota client（Token Plan 额度客户端）."""

from __future__ import annotations

import json
import os
import shutil
import subprocess

import requests


TOKEN_PLAN_REMAINS_URL = "https://www.minimax.io/v1/api/openplatform/coding_plan/remains"


def _get_proxy() -> str | None:
    """Read proxy from env（读取代理环境变量） for curl/requests."""

    for var in ("http_proxy", "HTTP_PROXY", "https_proxy", "HTTPS_PROXY"):
        value = os.environ.get(var)
        if value:
            return value
    return None


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

    def _proxy_args(self) -> list[str]:
        proxy = _get_proxy()
        if proxy:
            return ["-x", proxy]
        return []

    def _fetch_with_curl(self) -> dict:
        args = ["curl", "-sS", "--fail", "--location", *self._proxy_args()]
        for key, value in self.build_headers().items():
            args.extend(["-H", f"{key}: {value}"])
        args.append(self.url)

        result = subprocess.run(args, capture_output=True, text=True, timeout=20)
        if result.returncode != 0:
            stderr = (result.stderr or "").strip()
            raise RuntimeError(f"curl failed ({result.returncode}): {stderr[:200]}")

        return json.loads(result.stdout)

    def _fetch_with_requests(self) -> dict:
        proxies = None
        proxy = _get_proxy()
        if proxy:
            proxies = {"http": proxy, "https": proxy}

        response = requests.get(
            self.url,
            headers=self.build_headers(),
            timeout=20,
            proxies=proxies,
        )
        response.raise_for_status()
        return response.json()

    def fetch_remains(self) -> dict:
        # Cloudflare blocks Python requests for this endpoint in real usage;
        # curl is the reliable path, with requests kept as a fallback.
        if shutil.which("curl"):
            return self._fetch_with_curl()
        return self._fetch_with_requests()
