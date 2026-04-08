"""Tool modules（工具模块） for the unified MCP server."""

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

__all__ = [
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
