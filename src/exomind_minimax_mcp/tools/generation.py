"""Generation tools（生成工具） for video, image, music, and voice design."""

from __future__ import annotations

from pathlib import Path

import requests

from exomind_minimax_mcp.constants import (
    DEFAULT_BITRATE,
    DEFAULT_FORMAT,
    DEFAULT_MUSIC_MODEL,
    DEFAULT_SAMPLE_RATE,
    DEFAULT_T2I_MODEL,
    DEFAULT_T2V_MODEL,
    RESOURCE_MODE_URL,
)
from exomind_minimax_mcp.image_utils import normalize_image_url
from exomind_minimax_mcp.tools.audio import _get_multimodal_client
from exomind_minimax_mcp.utils import build_output_file, build_output_path


def generate_video(
    prompt: str,
    model: str = DEFAULT_T2V_MODEL,
    first_frame_image: str | None = None,
    duration: int | None = None,
    resolution: str | None = None,
    output_directory: str | None = None,
    async_mode: bool = False,
    resource_mode: str = RESOURCE_MODE_URL,
    base_path: str | None = None,
    api_client=None,
) -> str:
    if not prompt:
        raise ValueError("prompt is required")

    client = _get_multimodal_client(api_client)
    payload = {"model": model, "prompt": prompt}
    if first_frame_image:
        payload["first_frame_image"] = normalize_image_url(first_frame_image)
    if duration:
        payload["duration"] = duration
    if resolution:
        payload["resolution"] = resolution

    response_data = client.post_json("/v1/video_generation", payload)
    task_id = response_data.get("task_id")
    if not task_id:
        raise ValueError("task_id missing in video generation response")

    if async_mode:
        return (
            "Success. Video generation task submitted: "
            f"Task ID: {task_id}. Please use `query_video_generation` to poll the result."
        )

    return query_video_generation(
        task_id=task_id,
        output_directory=output_directory,
        resource_mode=resource_mode,
        base_path=base_path,
        api_client=client,
    )


def query_video_generation(
    task_id: str,
    output_directory: str | None = None,
    resource_mode: str = RESOURCE_MODE_URL,
    base_path: str | None = None,
    api_client=None,
) -> str:
    client = _get_multimodal_client(api_client)
    response_data = client.get_json(f"/v1/query/video_generation?task_id={task_id}")
    status = response_data.get("status")
    if status == "Fail":
        return f"Video generation FAILED for task_id: {task_id}"
    if status != "Success":
        return f"Video generation task is still processing: Task ID: {task_id}"

    file_id = response_data.get("file_id")
    file_response = client.get_json(f"/v1/files/retrieve?file_id={file_id}")
    download_url = file_response.get("file", {}).get("download_url")
    if not download_url:
        raise ValueError("download_url missing in file retrieve response")
    if resource_mode == RESOURCE_MODE_URL:
        return f"Success. Video URL: {download_url}"

    output_path = build_output_path(output_directory, base_path)
    output_file = build_output_file("video", task_id, output_path, "mp4", True)
    Path(output_file).write_bytes(requests.get(download_url).content)
    return f"Success. Video saved as: {output_file}"


def text_to_image(
    prompt: str,
    model: str = DEFAULT_T2I_MODEL,
    aspect_ratio: str = "1:1",
    n: int = 1,
    prompt_optimizer: bool = True,
    output_directory: str | None = None,
    resource_mode: str = RESOURCE_MODE_URL,
    base_path: str | None = None,
    api_client=None,
) -> str:
    if not prompt:
        raise ValueError("prompt is required")

    client = _get_multimodal_client(api_client)
    response_data = client.post_json(
        "/v1/image_generation",
        {
            "model": model,
            "prompt": prompt,
            "aspect_ratio": aspect_ratio,
            "n": n,
            "prompt_optimizer": prompt_optimizer,
        },
    )

    image_urls = response_data.get("data", {}).get("image_urls", [])
    if resource_mode == RESOURCE_MODE_URL:
        return f"Success. Image URLs: {image_urls}"

    output_path = build_output_path(output_directory, base_path)
    output_files: list[Path] = []
    for index, image_url in enumerate(image_urls):
        output_file = build_output_file("image", f"{index}_{prompt}", output_path, "jpg")
        Path(output_file).write_bytes(requests.get(image_url).content)
        output_files.append(output_file)
    return f"Success. Images saved as: {output_files}"


def music_generation(
    prompt: str,
    lyrics: str,
    sample_rate: int = DEFAULT_SAMPLE_RATE,
    bitrate: int = DEFAULT_BITRATE,
    format: str = DEFAULT_FORMAT,
    output_directory: str | None = None,
    resource_mode: str = RESOURCE_MODE_URL,
    base_path: str | None = None,
    api_client=None,
) -> str:
    if not prompt or not lyrics:
        raise ValueError("prompt and lyrics are required")

    client = _get_multimodal_client(api_client)
    response_data = client.post_json(
        "/v1/music_generation",
        {
            "model": DEFAULT_MUSIC_MODEL,
            "prompt": prompt,
            "lyrics": lyrics,
            "audio_setting": {
                "sample_rate": sample_rate,
                "bitrate": bitrate,
                "format": format,
            },
            **({"output_format": "url"} if resource_mode == RESOURCE_MODE_URL else {}),
        },
    )
    audio_payload = response_data.get("data", {}).get("audio", "")
    if resource_mode == RESOURCE_MODE_URL:
        return f"Success. Music url: {audio_payload}"

    output_path = build_output_path(output_directory, base_path)
    output_file = build_output_file("music", prompt, output_path, format)
    Path(output_file).write_bytes(bytes.fromhex(audio_payload))
    return f"Success. Music saved as: {output_file}"


def voice_design(
    prompt: str,
    preview_text: str,
    voice_id: str | None = None,
    output_directory: str | None = None,
    resource_mode: str = RESOURCE_MODE_URL,
    base_path: str | None = None,
    api_client=None,
) -> str:
    if not prompt or not preview_text:
        raise ValueError("prompt and preview_text are required")

    client = _get_multimodal_client(api_client)
    payload = {"prompt": prompt, "preview_text": preview_text}
    if voice_id:
        payload["voice_id"] = voice_id

    response_data = client.post_json("/v1/voice_design", payload)
    generated_voice_id = response_data.get("voice_id", "")
    trial_audio_hex = response_data.get("trial_audio", "")
    if resource_mode == RESOURCE_MODE_URL:
        return f"Success. Voice ID generated: {generated_voice_id}, Trial Audio: {trial_audio_hex}"

    output_path = build_output_path(output_directory, base_path)
    output_file = build_output_file("voice_design", preview_text, output_path, "mp3")
    Path(output_file).write_bytes(bytes.fromhex(trial_audio_hex))
    return f"Success. File saved as: {output_file}. Voice ID generated: {generated_voice_id}"
