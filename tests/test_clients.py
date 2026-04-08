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
