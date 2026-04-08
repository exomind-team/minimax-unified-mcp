"""Audio tools（音频工具） migrated into the unified MCP package."""

from __future__ import annotations

from pathlib import Path
from typing import Iterator

import requests

from exomind_minimax_mcp.clients.base import MiniMaxBaseClient
from exomind_minimax_mcp.config import load_settings
from exomind_minimax_mcp.constants import (
    DEFAULT_HTTP_TIMEOUT_SECONDS,
    DEFAULT_BITRATE,
    DEFAULT_CHANNEL,
    DEFAULT_EMOTION,
    DEFAULT_FORMAT,
    DEFAULT_LANGUAGE_BOOST,
    DEFAULT_PITCH,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_SPEED,
    DEFAULT_SPEECH_MODEL,
    DEFAULT_VOLUME,
    DEFAULT_VOICE_ID,
    RESOURCE_MODE_LOCAL,
    RESOURCE_MODE_URL,
)
from exomind_minimax_mcp.utils import (
    build_output_file,
    build_output_path,
    describe_path,
    download_bytes,
    download_to_file,
    play,
    process_input_file,
)


def _get_multimodal_client(api_client: MiniMaxBaseClient | None) -> MiniMaxBaseClient:
    if api_client is not None:
        return api_client

    settings = load_settings()
    api_key = settings.token_plan_api_key
    if not api_key:
        raise ValueError("MINIMAX_TOKEN_PLAN_API_KEY is required")
    return MiniMaxBaseClient(api_key, settings.api_host)


def text_to_audio(
    text: str,
    output_directory: str | None = None,
    voice_id: str = DEFAULT_VOICE_ID,
    model: str = DEFAULT_SPEECH_MODEL,
    speed: float = DEFAULT_SPEED,
    vol: float = DEFAULT_VOLUME,
    pitch: int = DEFAULT_PITCH,
    emotion: str = DEFAULT_EMOTION,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    bitrate: int = DEFAULT_BITRATE,
    channel: int = DEFAULT_CHANNEL,
    format: str = DEFAULT_FORMAT,
    language_boost: str = DEFAULT_LANGUAGE_BOOST,
    resource_mode: str | None = None,
    base_path: str | None = None,
    auto_play: bool = False,
    play_streaming: bool = True,
    api_client: MiniMaxBaseClient | None = None,
) -> str:
    """Convert text to audio（文本转语音）."""

    if not text:
        raise ValueError("text is required")

    settings = load_settings()
    requested_resource_mode = resource_mode or settings.resource_mode
    effective_resource_mode = RESOURCE_MODE_URL if auto_play and resource_mode is None else requested_resource_mode
    effective_base_path = base_path or str(settings.base_path)
    client = _get_multimodal_client(api_client)

    payload = {
        "model": model,
        "text": text,
        "voice_setting": {
            "voice_id": voice_id,
            "speed": speed,
            "vol": vol,
            "pitch": pitch,
            "emotion": emotion,
        },
        "audio_setting": {
            "sample_rate": sample_rate,
            "bitrate": bitrate,
            "format": format,
            "channel": channel,
        },
        "language_boost": language_boost,
    }
    if effective_resource_mode == RESOURCE_MODE_URL:
        payload["output_format"] = "url"

    response_data = client.post_json("/v1/t2a_v2", payload)
    audio_data = response_data.get("data", {}).get("audio", "")
    if not audio_data:
        raise ValueError("audio payload is empty")

    if effective_resource_mode == RESOURCE_MODE_URL:
        output = f"Success. Audio URL: {audio_data}"
        if auto_play:
            play_result = play_audio(audio_data, is_url=True, streaming=play_streaming)
            return f"{output}. Auto-play: {play_result}"
        return output

    audio_bytes = bytes.fromhex(audio_data)
    output_path = build_output_path(output_directory, effective_base_path)
    output_file = build_output_file("t2a", text, output_path, format)
    Path(output_file).parent.mkdir(parents=True, exist_ok=True)
    Path(output_file).write_bytes(audio_bytes)
    output = f"Success. File saved as: {describe_path(output_file, output_path)}. Voice used: {voice_id}"
    if auto_play:
        play_result = play_audio(str(output_file), is_url=False, streaming=play_streaming)
        return f"{output}. Auto-play: {play_result}"
    return output


def text_to_audio_streaming(
    text: str,
    voice_id: str = DEFAULT_VOICE_ID,
    model: str = DEFAULT_SPEECH_MODEL,
    speed: float = DEFAULT_SPEED,
    vol: float = DEFAULT_VOLUME,
    pitch: int = DEFAULT_PITCH,
    emotion: str = DEFAULT_EMOTION,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    bitrate: int = DEFAULT_BITRATE,
    channel: int = DEFAULT_CHANNEL,
    format: str = DEFAULT_FORMAT,
    language_boost: str = DEFAULT_LANGUAGE_BOOST,
    api_client: MiniMaxBaseClient | None = None,
) -> str:
    """Low-latency TTS + streaming playback（低延迟 TTS 流式播放） wrapper."""

    return text_to_audio(
        text=text,
        voice_id=voice_id,
        model=model,
        speed=speed,
        vol=vol,
        pitch=pitch,
        emotion=emotion,
        sample_rate=sample_rate,
        bitrate=bitrate,
        channel=channel,
        format=format,
        language_boost=language_boost,
        resource_mode=RESOURCE_MODE_URL,
        auto_play=True,
        play_streaming=True,
        api_client=api_client,
    )


def list_voices(
    voice_type: str = "all",
    api_client: MiniMaxBaseClient | None = None,
) -> str:
    """List available voices（列出可用声音）."""

    client = _get_multimodal_client(api_client)
    response_data = client.post_json("/v1/get_voice", {"voice_type": voice_type})
    system_voices = response_data.get("system_voice", []) or []
    voice_cloning_voices = response_data.get("voice_cloning", []) or []
    system_voice_list = [f"Name: {voice.get('voice_name')}, ID: {voice.get('voice_id')}" for voice in system_voices]
    cloning_voice_list = [
        f"Name: {voice.get('voice_name')}, ID: {voice.get('voice_id')}" for voice in voice_cloning_voices
    ]
    return f"Success. System Voices: {system_voice_list}, Voice Cloning Voices: {cloning_voice_list}"


def voice_clone(
    voice_id: str,
    file: str,
    text: str,
    output_directory: str | None = None,
    is_url: bool = False,
    resource_mode: str | None = None,
    base_path: str | None = None,
    api_client: MiniMaxBaseClient | None = None,
) -> str:
    """Clone a voice（克隆声音） from local audio or URL."""

    settings = load_settings()
    effective_resource_mode = resource_mode or settings.resource_mode
    effective_base_path = base_path or str(settings.base_path)
    client = _get_multimodal_client(api_client)

    if is_url:
        response = requests.get(file, stream=True, timeout=DEFAULT_HTTP_TIMEOUT_SECONDS)
        response.raise_for_status()
        try:
            upload_response = client.request_json(
                "POST",
                "/v1/files/upload",
                files={"file": ("audio_file.mp3", response.raw, "audio/mpeg")},
                data={"purpose": "voice_clone"},
            )
        finally:
            response.close()
    else:
        path = Path(file)
        if not path.exists():
            raise FileNotFoundError(f"Local audio file not found: {file}")
        with open(path, "rb") as file_handle:
            upload_response = client.request_json(
                "POST",
                "/v1/files/upload",
                files={"file": file_handle},
                data={"purpose": "voice_clone"},
            )

    file_id = upload_response.get("file", {}).get("file_id")
    if not file_id:
        raise ValueError("file_id missing from upload response")

    payload = {"file_id": file_id, "voice_id": voice_id}
    if text:
        payload["text"] = text
        payload["model"] = DEFAULT_SPEECH_MODEL

    response_data = client.request_json("POST", "/v1/voice_clone", json=payload)
    demo_audio = response_data.get("demo_audio")
    if not demo_audio:
        return f"Voice cloned successfully: Voice ID: {voice_id}"
    if effective_resource_mode == RESOURCE_MODE_URL:
        return f"Success. Demo audio URL: {demo_audio}"

    output_path = build_output_path(output_directory, effective_base_path)
    output_file = build_output_file("voice_clone", text, output_path, "wav")
    download_to_file(demo_audio, output_file)
    return (
        "Voice cloned successfully: "
        f"Voice ID: {voice_id}, demo audio saved as: {describe_path(output_file, output_path)}"
    )


def play_audio(
    input_file_path: str,
    is_url: bool = False,
    streaming: bool = True,
) -> str:
    """Play audio from URL or local file（播放远端或本地音频）."""

    if is_url:
        if streaming:
            response = requests.get(input_file_path, stream=True, timeout=DEFAULT_HTTP_TIMEOUT_SECONDS)
            response.raise_for_status()
            try:
                play(response.iter_content(chunk_size=8192))
            finally:
                response.close()
        else:
            play(download_bytes(input_file_path))
        return f"Successfully played audio file: {input_file_path}"

    file_path = process_input_file(input_file_path)
    if streaming:
        def file_iterator() -> Iterator[bytes]:
            with open(file_path, "rb") as file_handle:
                while True:
                    chunk = file_handle.read(8192)
                    if not chunk:
                        break
                    yield chunk

        play(file_iterator())
    else:
        play(Path(file_path).read_bytes())
    return f"Successfully played audio file: {Path(file_path).name}"
