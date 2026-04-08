from __future__ import annotations

from pathlib import Path


class StubGenerationClient:
    def __init__(self, post_responses: list[dict] | None = None, get_responses: list[dict] | None = None):
        self.post_responses = post_responses or []
        self.get_responses = get_responses or []
        self.post_calls: list[tuple[str, dict]] = []
        self.get_calls: list[str] = []

    def post_json(self, endpoint: str, payload: dict) -> dict:
        self.post_calls.append((endpoint, payload))
        return self.post_responses.pop(0)

    def get_json(self, endpoint: str) -> dict:
        self.get_calls.append(endpoint)
        return self.get_responses.pop(0)


def test_generate_video_async_returns_task_id():
    from exomind_minimax_mcp.tools.generation import generate_video

    client = StubGenerationClient(post_responses=[{"task_id": "task-123"}])

    output = generate_video(
        prompt="a robot walking in rain",
        async_mode=True,
        api_client=client,
    )

    assert client.post_calls[0][0] == "/v1/video_generation"
    assert client.post_calls[0][1]["prompt"] == "a robot walking in rain"
    assert client.post_calls[0][1]["model"] == "MiniMax-Hailuo-2.3-Fast"
    assert "task-123" in output


def test_text_to_image_saves_files_in_local_mode(tmp_path, monkeypatch):
    from exomind_minimax_mcp.tools.generation import text_to_image

    client = StubGenerationClient(
        post_responses=[{"data": {"image_urls": ["https://example.com/1.jpg", "https://example.com/2.jpg"]}}]
    )

    class FakeResponse:
        def __init__(self, content: bytes):
            self.headers = {"content-length": str(len(content))}
            self._content = content

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield self._content

        def close(self):
            return None

    contents = [b"img-one", b"img-two"]
    monkeypatch.setattr(
        "exomind_minimax_mcp.utils.requests.get",
        lambda *args, **kwargs: FakeResponse(contents.pop(0)),
    )

    output = text_to_image(
        prompt="a red moon",
        output_directory=str(tmp_path),
        base_path=str(tmp_path),
        resource_mode="local",
        api_client=client,
    )

    assert "Images saved as:" in output
    saved = list(tmp_path.glob("*.jpg"))
    assert len(saved) == 2


def test_music_generation_uses_default_music_model(tmp_path):
    from exomind_minimax_mcp.tools.generation import music_generation

    client = StubGenerationClient(post_responses=[{"data": {"audio": "41424344"}}])

    output = music_generation(
        prompt="sad piano",
        lyrics="[Verse]\nhello rain",
        output_directory=str(tmp_path),
        base_path=str(tmp_path),
        resource_mode="local",
        api_client=client,
    )

    assert client.post_calls[0][0] == "/v1/music_generation"
    assert client.post_calls[0][1]["model"] == "music-2.5"
    assert "Music saved as:" in output


def test_voice_design_saves_trial_audio(tmp_path):
    from exomind_minimax_mcp.tools.generation import voice_design

    client = StubGenerationClient(
        post_responses=[{"voice_id": "voice-demo", "trial_audio": "41424344"}]
    )

    output = voice_design(
        prompt="warm female narrator",
        preview_text="hello there",
        output_directory=str(tmp_path),
        base_path=str(tmp_path),
        resource_mode="local",
        api_client=client,
    )

    assert client.post_calls[0][0] == "/v1/voice_design"
    assert "voice-demo" in output
    assert list(tmp_path.glob("*.mp3"))
