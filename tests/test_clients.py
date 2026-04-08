from __future__ import annotations

import json
import subprocess
from types import SimpleNamespace

import requests


def test_quota_client_builds_required_cloudflare_headers():
    from exomind_minimax_mcp.clients.quota import TokenPlanQuotaClient

    client = TokenPlanQuotaClient(api_key="quota-key")
    headers = client.build_headers()

    assert headers["Authorization"] == "Bearer quota-key"
    assert headers["Content-Type"] == "application/json"
    assert headers["Accept"] == "application/json"
    assert headers["Referer"] == "https://www.minimax.io/"
    assert headers["Origin"] == "https://www.minimax.io"
    assert "Mozilla/5.0" in headers["User-Agent"]


def test_quota_client_uses_diary_remains_endpoint():
    from exomind_minimax_mcp.clients.quota import TOKEN_PLAN_REMAINS_URL, TokenPlanQuotaClient

    client = TokenPlanQuotaClient(api_key="quota-key")

    assert client.url == TOKEN_PLAN_REMAINS_URL


def test_quota_client_fetches_with_curl_when_available(monkeypatch):
    from exomind_minimax_mcp.clients import quota as quota_module
    from exomind_minimax_mcp.clients.quota import TokenPlanQuotaClient

    client = TokenPlanQuotaClient(api_key="quota-key")
    payload = {"model_remains": [{"model_name": "MiniMax-M*"}]}
    recorded: dict[str, object] = {}

    def fake_run(args, capture_output, text, timeout, input):
        recorded["args"] = args
        recorded["input"] = input
        return subprocess.CompletedProcess(args=args, returncode=0, stdout=json.dumps(payload), stderr="")

    monkeypatch.setattr(quota_module, "shutil", SimpleNamespace(which=lambda name: "curl.exe"), raising=False)
    monkeypatch.setattr(quota_module.subprocess, "run", fake_run)

    assert client.fetch_remains() == payload
    assert recorded["args"][0] == "curl"
    assert "--config" in recorded["args"]
    assert "-" in recorded["args"]
    assert not any("Authorization: Bearer quota-key" in item for item in recorded["args"])
    assert f'url = "{client.url}"' in recorded["input"]
    assert 'header = "Authorization: Bearer quota-key"' in recorded["input"]


def test_quota_client_falls_back_to_requests_when_curl_missing(monkeypatch):
    from exomind_minimax_mcp.clients import quota as quota_module
    from exomind_minimax_mcp.clients.quota import TokenPlanQuotaClient

    client = TokenPlanQuotaClient(api_key="quota-key")
    payload = {"model_remains": [{"model_name": "MiniMax-M*"}]}

    class DummyResponse:
        status_code = 200

        def raise_for_status(self):
            return None

        def json(self):
            return payload

    def fake_get(url, headers, timeout, proxies):
        assert url == client.url
        assert headers["Authorization"] == "Bearer quota-key"
        return DummyResponse()

    def unexpected_run(*args, **kwargs):
        raise AssertionError("curl should not run when curl is unavailable")

    monkeypatch.setattr(quota_module, "shutil", SimpleNamespace(which=lambda name: None), raising=False)
    monkeypatch.setattr(quota_module, "requests", SimpleNamespace(get=fake_get), raising=False)
    monkeypatch.setattr(quota_module.subprocess, "run", unexpected_run)

    assert client.fetch_remains() == payload
