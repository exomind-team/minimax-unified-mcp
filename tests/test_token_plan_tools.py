from __future__ import annotations

import base64
import json


class StubApiClient:
    def __init__(self, response: dict):
        self.response = response
        self.calls: list[tuple[str, dict]] = []

    def post_json(self, endpoint: str, payload: dict) -> dict:
        self.calls.append((endpoint, payload))
        return self.response


def test_web_search_calls_official_coding_plan_search_endpoint():
    from exomind_minimax_mcp.tools.token_plan import web_search

    client = StubApiClient(
        {
            "organic": [{"title": "MiniMax result", "link": "https://www.minimax.io"}],
            "related_searches": [{"query": "MiniMax token plan"}],
        }
    )

    output = web_search("latest minimax token plan", api_client=client)
    parsed = json.loads(output)

    assert client.calls == [
        ("/v1/coding_plan/search", {"q": "latest minimax token plan"})
    ]
    assert parsed["organic"][0]["title"] == "MiniMax result"


def test_understand_image_accepts_local_file_and_url(tmp_path, monkeypatch):
    from exomind_minimax_mcp.tools.token_plan import understand_image

    image_path = tmp_path / "sample.png"
    image_bytes = b"fake-image-bytes"
    image_path.write_bytes(image_bytes)

    class FakeResponse:
        headers = {"content-type": "image/png", "content-length": "15"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"url-image-bytes"

    def fake_get(url: str, *args, **kwargs):
        assert url == "https://example.com/demo.png"
        return FakeResponse()

    monkeypatch.setattr("exomind_minimax_mcp.image_utils.requests.get", fake_get)

    local_client = StubApiClient({"content": "local ok"})
    url_client = StubApiClient({"content": "url ok"})

    local_result = understand_image(
        prompt="describe image",
        image_url=str(image_path),
        api_client=local_client,
    )
    url_result = understand_image(
        prompt="describe image",
        image_url="https://example.com/demo.png",
        api_client=url_client,
    )

    local_payload = local_client.calls[0][1]
    url_payload = url_client.calls[0][1]

    assert local_client.calls[0][0] == "/v1/coding_plan/vlm"
    assert local_result == "local ok"
    assert url_result == "url ok"
    assert local_payload["image_url"].startswith("data:image/png;base64,")
    assert base64.b64decode(local_payload["image_url"].split(",", 1)[1]) == image_bytes
    assert url_payload["image_url"].startswith("data:image/png;base64,")


def test_understand_image_accepts_official_image_source_alias(monkeypatch):
    from exomind_minimax_mcp.tools.token_plan import understand_image

    class FakeResponse:
        headers = {"content-type": "image/png", "content-length": "16"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"alias-image-bytes"

    monkeypatch.setattr(
        "exomind_minimax_mcp.image_utils.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    client = StubApiClient({"content": "alias ok"})

    result = understand_image(
        prompt="describe alias image",
        image_source="https://example.com/alias.png",
        api_client=client,
    )

    assert result == "alias ok"
    assert client.calls[0][0] == "/v1/coding_plan/vlm"
    assert client.calls[0][1]["image_url"].startswith("data:image/png;base64,")
