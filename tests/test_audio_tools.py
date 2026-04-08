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


def test_text_to_audio_uses_speech_28_hd_default(tmp_path):
    from exomind_minimax_mcp.tools.audio import text_to_audio

    client = StubAudioClient({"data": {"audio": "41424344"}})

    output = text_to_audio(
        text="hello world",
        output_directory=str(tmp_path),
        resource_mode="local",
        api_client=client,
    )

    assert client.calls[0][0] == "/v1/t2a_v2"
    assert client.calls[0][1]["model"] == "speech-2.8-hd"
    assert "File saved as:" in output
    saved_path = Path(output.split("File saved as: ", 1)[1].split(". Voice used:", 1)[0])
    assert saved_path.exists()
    assert saved_path.read_bytes() == b"ABCD"


def test_play_audio_supports_streaming_iterators(monkeypatch):
    from exomind_minimax_mcp.utils import play

    writes: list[bytes] = []

    class FakeProc:
        def __init__(self):
            self.stdin = self

        def write(self, chunk: bytes):
            writes.append(chunk)

        def close(self):
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
        content = b"demo-audio"

        def raise_for_status(self):
            return None

    monkeypatch.setattr(
        "exomind_minimax_mcp.tools.audio.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    client = StubVoiceCloneClient()
    output = voice_clone(
        voice_id="voice-001",
        file=str(sample_audio),
        text="hello",
        output_directory=str(tmp_path),
        resource_mode="local",
        api_client=client,
    )

    assert client.calls == [("POST", "/v1/files/upload"), ("POST", "/v1/voice_clone")]
    assert "Voice cloned successfully" in output
    assert list(tmp_path.glob("*.wav"))
