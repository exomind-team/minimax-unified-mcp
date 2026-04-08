"""Live API matrix runner（在线接口矩阵执行器） for real MiniMax checks."""

from __future__ import annotations

import json
import re
import struct
import time
import zlib
from dataclasses import asdict, dataclass
from pathlib import Path

from exomind_minimax_mcp.clients.base import MiniMaxBaseClient
from exomind_minimax_mcp.clients.quota import TokenPlanQuotaClient
from exomind_minimax_mcp.tools.audio import list_voices, play_audio, text_to_audio, voice_clone
from exomind_minimax_mcp.tools.generation import (
    generate_video,
    music_generation,
    query_video_generation,
    text_to_image,
    voice_design,
)
from exomind_minimax_mcp.tools.quota import get_token_plan_quota
from exomind_minimax_mcp.tools.token_plan import understand_image, web_search
from exomind_minimax_mcp.utils import is_installed


LIVE_TOOL_ORDER = [
    "get_token_plan_quota",
    "web_search",
    "understand_image",
    "text_to_audio",
    "list_voices",
    "voice_clone",
    "play_audio",
    "generate_video",
    "query_video_generation",
    "text_to_image",
    "music_generation",
    "voice_design",
]


@dataclass
class LiveCheckResult:
    tool: str
    status: str
    detail: str
    artifact: str | None = None
    elapsed_seconds: float | None = None


@dataclass
class _RunnerState:
    client: MiniMaxBaseClient
    quota_client: TokenPlanQuotaClient
    output_dir: Path
    generated_audio_path: Path | None = None
    video_task_id: str | None = None


def classify_live_failure(detail: str) -> str:
    lowered = detail.lower()
    if "timeout" in lowered or "timed out" in lowered:
        return "timeout"
    if "2061-" in lowered or "not support model" in lowered:
        return "unsupported"
    if "2056-" in lowered or "usage limit exceeded" in lowered:
        return "usage_limit_exceeded"
    if "1008-" in lowered or "insufficient balance" in lowered:
        return "insufficient_balance"
    if "2013-" in lowered or "invalid params" in lowered:
        return "invalid_params"
    if "ffplay" in lowered:
        return "skipped"
    return "error"


def create_live_png_fixture(path: Path, width: int = 32, height: int = 32) -> Path:
    def png_chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack("!I", len(data))
            + tag
            + data
            + struct.pack("!I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    signature = b"\x89PNG\r\n\x1a\n"
    ihdr = png_chunk(b"IHDR", struct.pack("!IIBBBBB", width, height, 8, 2, 0, 0, 0))
    row = b"\x00" + (b"\xff\x00\x00" * width)
    raw = row * height
    idat = png_chunk(b"IDAT", zlib.compress(raw, 9))
    iend = png_chunk(b"IEND", b"")
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(signature + ihdr + idat + iend)
    return path


def format_live_report_json(results: list[LiveCheckResult]) -> str:
    return json.dumps([asdict(item) for item in results], ensure_ascii=False, indent=2)


def format_live_report_text(results: list[LiveCheckResult]) -> str:
    lines = ["MiniMax Live API Matrix", ""]
    for item in results:
        suffix = f" | artifact={item.artifact}" if item.artifact else ""
        elapsed = f" | {item.elapsed_seconds:.2f}s" if item.elapsed_seconds is not None else ""
        lines.append(f"- {item.tool}: {item.status}{elapsed} | {item.detail}{suffix}")
    return "\n".join(lines)


def run_live_matrix(
    api_key: str,
    api_host: str,
    output_dir: str | Path | None = None,
    only: str | None = None,
    include_playback: bool = True,
) -> list[LiveCheckResult]:
    base_output_dir = Path(output_dir) if output_dir else Path.cwd() / "live-artifacts"
    base_output_dir.mkdir(parents=True, exist_ok=True)
    state = _RunnerState(
        client=MiniMaxBaseClient(api_key, api_host),
        quota_client=TokenPlanQuotaClient(api_key=api_key),
        output_dir=base_output_dir,
    )
    selected_tools = [tool for tool in LIVE_TOOL_ORDER if only in (None, tool)]
    return [_run_single_tool(tool, state, include_playback=include_playback) for tool in selected_tools]


def _run_single_tool(tool: str, state: _RunnerState, include_playback: bool) -> LiveCheckResult:
    start = time.time()
    try:
        if tool == "get_token_plan_quota":
            output = get_token_plan_quota(raw_json=True, quota_client=state.quota_client)
            parsed = json.loads(output)
            detail = f"returned {len(parsed.get('model_remains', []))} models"
            status = "passed"
            artifact = None
        elif tool == "web_search":
            output = web_search("MiniMax official site", api_client=state.client)
            parsed = json.loads(output)
            detail = f"returned {len(parsed.get('organic', []))} results"
            status = "passed"
            artifact = None
        elif tool == "understand_image":
            image_path = create_live_png_fixture(state.output_dir / "live-red-square-32.png")
            output = understand_image(
                prompt="Describe this image briefly in English.",
                image_url=str(image_path),
                api_client=state.client,
            )
            detail = output.strip() or "empty response"
            status = "passed" if output.strip() else "error"
            artifact = str(image_path)
        elif tool == "text_to_audio":
            output = text_to_audio(
                text="hello world from live matrix",
                output_directory=str(state.output_dir),
                resource_mode="local",
                api_client=state.client,
            )
            audio_path = _extract_saved_file(output)
            state.generated_audio_path = Path(audio_path) if audio_path else None
            detail = output
            status = "passed" if state.generated_audio_path and state.generated_audio_path.exists() else "error"
            artifact = str(state.generated_audio_path) if state.generated_audio_path else None
        elif tool == "list_voices":
            output = list_voices(api_client=state.client)
            detail = output[:300]
            status = "passed" if "System Voices" in output else "error"
            artifact = None
        elif tool == "voice_clone":
            if not state.generated_audio_path:
                return _build_result(tool, "skipped", "text_to_audio artifact missing", start)
            output = voice_clone(
                voice_id="token-plan-live-clone-test",
                file=str(state.generated_audio_path),
                text="hello world",
                resource_mode="url",
                api_client=state.client,
            )
            detail = output
            status = "passed"
            artifact = str(state.generated_audio_path)
        elif tool == "play_audio":
            if not include_playback:
                return _build_result(tool, "skipped", "playback disabled", start)
            if not state.generated_audio_path:
                return _build_result(tool, "skipped", "text_to_audio artifact missing", start)
            if not is_installed("ffplay"):
                return _build_result(tool, "skipped", "ffplay not installed", start)
            output = play_audio(input_file_path=str(state.generated_audio_path), is_url=False, streaming=False)
            detail = output
            status = "passed"
            artifact = str(state.generated_audio_path)
        elif tool == "generate_video":
            first_frame = create_live_png_fixture(state.output_dir / "live-video-first-frame.png")
            output = generate_video(
                prompt="a red ball rolling slowly on a white table",
                first_frame_image=str(first_frame),
                async_mode=True,
                api_client=state.client,
            )
            state.video_task_id = _extract_task_id(output)
            detail = output
            status = "passed" if state.video_task_id else "error"
            artifact = state.video_task_id or str(first_frame)
        elif tool == "query_video_generation":
            if not state.video_task_id:
                return _build_result(tool, "skipped", "video task id missing", start)
            output = query_video_generation(task_id=state.video_task_id, api_client=state.client)
            detail = output
            status = "processing" if "still processing" in output else "passed"
            artifact = state.video_task_id
        elif tool == "text_to_image":
            output = text_to_image(
                prompt="a tiny red cube icon on white background",
                resource_mode="url",
                api_client=state.client,
            )
            detail = output
            status = "passed" if "Image URLs" in output else "error"
            artifact = None
        elif tool == "music_generation":
            output = music_generation(
                prompt="gentle ambient piano",
                lyrics="hello world",
                resource_mode="url",
                api_client=state.client,
            )
            detail = output
            status = "passed"
            artifact = None
        elif tool == "voice_design":
            output = voice_design(
                prompt="warm calm young female narrator",
                preview_text="hello world",
                resource_mode="url",
                api_client=state.client,
            )
            detail = output
            status = "passed"
            artifact = None
        else:
            return _build_result(tool, "error", "unknown tool", start)
    except Exception as exc:
        detail = f"{type(exc).__name__}: {exc}"
        status = classify_live_failure(detail)
        artifact = None

    return _build_result(tool, status, detail, start, artifact)


def _build_result(
    tool: str,
    status: str,
    detail: str,
    start: float,
    artifact: str | None = None,
) -> LiveCheckResult:
    return LiveCheckResult(
        tool=tool,
        status=status,
        detail=detail,
        artifact=artifact,
        elapsed_seconds=round(time.time() - start, 2),
    )


def _extract_saved_file(message: str) -> str | None:
    match = re.search(r"File saved as: (.+?)(?:\. Voice used:|$)", message)
    return match.group(1) if match else None


def _extract_task_id(message: str) -> str | None:
    match = re.search(r"Task ID: ([0-9]+)", message)
    return match.group(1) if match else None
