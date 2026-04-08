from __future__ import annotations

import json


SAMPLE_QUOTA_RESPONSE = {
    "model_remains": [
        {
            "model_name": "MiniMax-M*",
            "current_interval_usage_count": 14822,
            "current_interval_total_count": 15000,
            "remains_time": 12600000,
            "current_weekly_usage_count": 148028,
            "current_weekly_total_count": 150000,
        },
        {
            "model_name": "speech-hd",
            "current_interval_usage_count": 19000,
            "current_interval_total_count": 20000,
            "remains_time": 45000000,
            "current_weekly_usage_count": 133000,
            "current_weekly_total_count": 140000,
        },
    ]
}


class StubQuotaClient:
    def fetch_remains(self) -> dict:
        return SAMPLE_QUOTA_RESPONSE


def test_get_token_plan_quota_formats_single_model_response():
    from exomind_minimax_mcp.tools.quota import get_token_plan_quota

    output = get_token_plan_quota(
        quota_client=StubQuotaClient(),
        model="MiniMax-M*",
    )

    assert "MiniMax-M2.7-highspeed" in output
    assert "14,822/15,000" in output
    assert "148,028/150,000" in output


def test_get_token_plan_quota_returns_json_when_requested():
    from exomind_minimax_mcp.tools.quota import get_token_plan_quota

    output = get_token_plan_quota(
        quota_client=StubQuotaClient(),
        raw_json=True,
    )

    parsed = json.loads(output)
    assert parsed["model_remains"][0]["model_name"] == "MiniMax-M*"
