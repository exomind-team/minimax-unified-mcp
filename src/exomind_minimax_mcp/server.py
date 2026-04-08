"""Unified MiniMax MCP server entrypoint."""

from __future__ import annotations

from mcp.server.fastmcp import FastMCP

from exomind_minimax_mcp.config import load_settings
from exomind_minimax_mcp.constants import DEFAULT_SPEECH_MODEL, DEFAULT_T2V_MODEL
from exomind_minimax_mcp.tools.audio import (
    list_voices,
    play_audio,
    text_to_audio,
    text_to_audio_streaming,
    voice_clone,
)
from exomind_minimax_mcp.tools.generation import (
    generate_video,
    music_generation,
    query_video_generation,
    text_to_image,
    voice_design,
)
from exomind_minimax_mcp.tools.quota import get_token_plan_quota
from exomind_minimax_mcp.tools.token_plan import understand_image, web_search


def create_mcp() -> FastMCP:
    """Create FastMCP app（创建 FastMCP 应用）."""

    settings = load_settings()
    mcp = FastMCP("ExoMind MiniMax Unified", log_level=settings.log_level)

    @mcp.tool(
        description=(
            "Get MiniMax Token Plan quota（查询 MiniMax Token Plan 额度）. "
            "Supports filtered model output or raw JSON."
        )
    )
    def quota_tool(
        model: str = "MiniMax-M*",
        all_models: bool = False,
        raw_json: bool = False,
    ) -> str:
        return get_token_plan_quota(model=model, all_models=all_models, raw_json=raw_json)

    @mcp.tool(
        description="Perform official MiniMax Token Plan web search（官方网页搜索）."
    )
    def web_search_tool(query: str) -> str:
        return web_search(query=query)

    @mcp.tool(
        description=(
            "Analyze an image with official MiniMax Token Plan VLM（官方图片理解）. "
            "Use image_source（图片来源 / 本地路径 / data URL） exactly like the official Token Plan MCP. "
            "The source can be a local file path or HTTP/HTTPS URL（可传本地路径或 URL）."
        )
    )
    def understand_image_tool(
        prompt: str,
        image_source: str,
    ) -> str:
        return understand_image(prompt=prompt, image_source=image_source)

    @mcp.tool(description="Convert text to audio（文本转语音） with MiniMax speech models.")
    def text_to_audio_tool(
        text: str,
        output_directory: str | None = None,
        voice_id: str = "female-shaonv-jingpin",
        model: str = DEFAULT_SPEECH_MODEL,
        resource_mode: str | None = None,
        auto_play: bool = False,
        play_streaming: bool = True,
    ) -> str:
        return text_to_audio(
            text=text,
            output_directory=output_directory,
            voice_id=voice_id,
            model=model,
            resource_mode=resource_mode,
            auto_play=auto_play,
            play_streaming=play_streaming,
        )

    @mcp.tool(description="Low-latency text-to-speech streaming playback（低延迟 TTS 流式播放）.")
    def text_to_audio_streaming_tool(
        text: str,
        voice_id: str = "female-shaonv-jingpin",
        model: str = DEFAULT_SPEECH_MODEL,
    ) -> str:
        return text_to_audio_streaming(
            text=text,
            voice_id=voice_id,
            model=model,
        )

    @mcp.tool(description="List available voices（列出可用声音）.")
    def list_voices_tool(voice_type: str = "all") -> str:
        return list_voices(voice_type=voice_type)

    @mcp.tool(description="Clone a voice（克隆声音） from sample audio.")
    def voice_clone_tool(
        voice_id: str,
        file: str,
        text: str,
        output_directory: str | None = None,
        is_url: bool = False,
    ) -> str:
        return voice_clone(
            voice_id=voice_id,
            file=file,
            text=text,
            output_directory=output_directory,
            is_url=is_url,
        )

    @mcp.tool(description="Play audio from URL or local file（播放音频）.")
    def play_audio_tool(
        input_file_path: str,
        is_url: bool = False,
        streaming: bool = True,
    ) -> str:
        return play_audio(input_file_path=input_file_path, is_url=is_url, streaming=streaming)

    @mcp.tool(
        description=(
            "Generate a video（生成视频） with MiniMax video models. "
            "Use `MiniMax-Hailuo-2.3` for text-to-video by default. "
            "If you choose `MiniMax-Hailuo-2.3-Fast`, you should also provide "
            "`first_frame_image`（首帧图片） as a local path, URL, or data URL."
        )
    )
    def generate_video_tool(
        prompt: str,
        model: str = DEFAULT_T2V_MODEL,
        first_frame_image: str | None = None,
        duration: int | None = None,
        resolution: str | None = None,
        output_directory: str | None = None,
        async_mode: bool = False,
    ) -> str:
        return generate_video(
            prompt=prompt,
            model=model,
            first_frame_image=first_frame_image,
            duration=duration,
            resolution=resolution,
            output_directory=output_directory,
            async_mode=async_mode,
        )

    @mcp.tool(description="Query video generation status（查询视频生成状态）.")
    def query_video_generation_tool(task_id: str, output_directory: str | None = None) -> str:
        return query_video_generation(task_id=task_id, output_directory=output_directory)

    @mcp.tool(description="Generate images（生成图片） with MiniMax image models.")
    def text_to_image_tool(prompt: str, output_directory: str | None = None) -> str:
        return text_to_image(prompt=prompt, output_directory=output_directory)

    @mcp.tool(description="Generate music（生成音乐） with MiniMax music models.")
    def music_generation_tool(prompt: str, lyrics: str, output_directory: str | None = None) -> str:
        return music_generation(prompt=prompt, lyrics=lyrics, output_directory=output_directory)

    @mcp.tool(description="Design a voice（设计声音） with MiniMax voice design.")
    def voice_design_tool(
        prompt: str,
        preview_text: str,
        output_directory: str | None = None,
    ) -> str:
        return voice_design(prompt=prompt, preview_text=preview_text, output_directory=output_directory)

    return mcp


def main() -> None:
    """Start the MCP server（启动 MCP 服务）."""

    create_mcp().run()
