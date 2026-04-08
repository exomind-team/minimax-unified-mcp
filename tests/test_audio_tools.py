from __future__ import annotations

from pathlib import Path


class StubAudioClient:
    def __init__(self, response: dict):
        self.response = response
        self.calls: list[tuple[str, dict]] = []

    def post_json(self, endpoint: str, payload: dict) -> dict:
        self.calls.append((endpoint, payload))
        return self.response


class StubVoiceCloneClient:
    def __init__(self):
        self.calls: list[tuple[str, str]] = []

    def request_json(self, method: str, endpoint: str, **kwargs) -> dict:
        self.calls.append((method, endpoint))
        if endpoint == "/v1/files/upload":
            return {"file": {"file_id": "file-123"}}
        if endpoint == "/v1/voice_clone":
            return {"demo_audio": "https://example.com/demo.wav"}
        raise AssertionError(f"unexpected endpoint: {endpoint}")


def test_multimodal_client_uses_token_plan_key_by_default(monkeypatch):
    from exomind_minimax_mcp.tools.audio import _get_multimodal_client

    captured: dict[str, str] = {}

    class FakeClient:
        def __init__(self, api_key: str, base_url: str):
            captured["api_key"] = api_key
            captured["base_url"] = base_url

    monkeypatch.setenv("MINIMAX_TOKEN_PLAN_API_KEY", "token-plan-key")
    monkeypatch.setenv("MINIMAX_API_HOST", "https://api.minimax.io")
    monkeypatch.setattr("exomind_minimax_mcp.tools.audio.MiniMaxBaseClient", FakeClient)

    _get_multimodal_client(None)

    assert captured["api_key"] == "token-plan-key"
    assert captured["base_url"] == "https://api.minimax.io"


def test_text_to_audio_uses_speech_28_hd_default(tmp_path):
    from exomind_minimax_mcp.tools.audio import text_to_audio

    client = StubAudioClient({"data": {"audio": "41424344"}})

    output = text_to_audio(
        text="hello world",
        output_directory=str(tmp_path),
        base_path=str(tmp_path),
        resource_mode="local",
        api_client=client,
    )

    assert client.calls[0][0] == "/v1/t2a_v2"
    assert client.calls[0][1]["model"] == "speech-2.8-hd"
    assert "File saved as:" in output
    saved_files = list(tmp_path.glob("*.mp3"))
    assert len(saved_files) == 1
    assert saved_files[0].read_bytes() == b"ABCD"


def test_text_to_audio_auto_play_prefers_url_mode_for_low_latency(monkeypatch):
    from exomind_minimax_mcp.tools.audio import text_to_audio

    client = StubAudioClient({"data": {"audio": "https://example.com/live.mp3"}})
    recorded: dict[str, object] = {}

    def fake_play_audio(input_file_path: str, is_url: bool, streaming: bool) -> str:
        recorded["input_file_path"] = input_file_path
        recorded["is_url"] = is_url
        recorded["streaming"] = streaming
        return "played"

    monkeypatch.setenv("MINIMAX_API_RESOURCE_MODE", "local")
    monkeypatch.setattr("exomind_minimax_mcp.tools.audio.play_audio", fake_play_audio)

    output = text_to_audio(
        text="hello autoplay",
        auto_play=True,
        api_client=client,
    )

    assert client.calls[0][1]["output_format"] == "url"
    assert recorded == {
        "input_file_path": "https://example.com/live.mp3",
        "is_url": True,
        "streaming": True,
    }
    assert "Auto-play: played" in output


def test_text_to_audio_auto_play_can_use_local_artifact(tmp_path, monkeypatch):
    from exomind_minimax_mcp.tools.audio import text_to_audio

    client = StubAudioClient({"data": {"audio": "41424344"}})
    recorded: dict[str, object] = {}

    def fake_play_audio(input_file_path: str, is_url: bool, streaming: bool) -> str:
        recorded["input_file_path"] = input_file_path
        recorded["is_url"] = is_url
        recorded["streaming"] = streaming
        return "played-local"

    monkeypatch.setattr("exomind_minimax_mcp.tools.audio.play_audio", fake_play_audio)

    output = text_to_audio(
        text="hello local autoplay",
        output_directory=str(tmp_path),
        base_path=str(tmp_path),
        resource_mode="local",
        auto_play=True,
        api_client=client,
    )

    saved_files = list(tmp_path.glob("*.mp3"))
    assert len(saved_files) == 1
    assert recorded == {
        "input_file_path": str(saved_files[0]),
        "is_url": False,
        "streaming": True,
    }
    assert "Auto-play: played-local" in output


def test_text_to_audio_streaming_uses_dedicated_low_latency_wrapper(monkeypatch):
    from exomind_minimax_mcp.tools.audio import text_to_audio_streaming

    recorded: dict[str, object] = {}

    def fake_text_to_audio(**kwargs) -> str:
        recorded.update(kwargs)
        return "streaming-ok"

    monkeypatch.setattr("exomind_minimax_mcp.tools.audio.text_to_audio", fake_text_to_audio)

    output = text_to_audio_streaming(
        text="hello streaming tool",
        voice_id="voice-demo",
    )

    assert output == "streaming-ok"
    assert recorded["text"] == "hello streaming tool"
    assert recorded["voice_id"] == "voice-demo"
    assert recorded["auto_play"] is True
    assert recorded["play_streaming"] is True
    assert recorded["resource_mode"] == "url"


def test_play_audio_supports_streaming_iterators(monkeypatch):
    from exomind_minimax_mcp.utils import play

    writes: list[bytes] = []

    class FakeProc:
        def __init__(self):
            self.stdin = self
            self.closed = False

        def write(self, chunk: bytes):
            writes.append(chunk)

        def close(self):
            self.closed = True
            writes.append(b"<closed>")

        def wait(self):
            return 0

    monkeypatch.setattr("exomind_minimax_mcp.utils.is_installed", lambda _: True)
    monkeypatch.setattr("exomind_minimax_mcp.utils.subprocess.Popen", lambda **_: FakeProc())

    play(iter([b"abc", b"def"]))

    assert writes == [b"abc", b"def", b"<closed>"]


def test_voice_clone_uploads_file_and_saves_demo_audio(tmp_path, monkeypatch):
    from exomind_minimax_mcp.tools.audio import voice_clone

    sample_audio = tmp_path / "input.mp3"
    sample_audio.write_bytes(b"sample-audio")

    class FakeResponse:
        headers = {"content-length": "10"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"demo-audio"

        def close(self):
            return None

    monkeypatch.setattr(
        "exomind_minimax_mcp.utils.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    client = StubVoiceCloneClient()
    output = voice_clone(
        voice_id="voice-001",
        file=str(sample_audio),
        text="hello",
        output_directory=str(tmp_path),
        base_path=str(tmp_path),
        resource_mode="local",
        api_client=client,
    )

    assert client.calls == [("POST", "/v1/files/upload"), ("POST", "/v1/voice_clone")]
    assert "Voice cloned successfully" in output
    assert list(tmp_path.glob("*.wav"))
