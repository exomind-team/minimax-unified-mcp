from __future__ import annotations

import importlib
import asyncio


def test_importing_server_does_not_write_to_stdout(capsys):
    import exomind_minimax_mcp.server as server_module

    importlib.reload(server_module)
    captured = capsys.readouterr()

    assert captured.out == ""


def test_create_mcp_returns_app():
    from exomind_minimax_mcp.server import create_mcp

    app = create_mcp()

    assert app is not None


def test_understand_image_tool_matches_official_token_plan_schema():
    from exomind_minimax_mcp.server import create_mcp

    async def _get_schema():
        app = create_mcp()
        tools = await app.list_tools()
        for tool in tools:
            if tool.name == "understand_image_tool":
                return tool.inputSchema
        raise AssertionError("understand_image_tool not found")

    schema = asyncio.run(_get_schema())

    assert schema["required"] == ["prompt", "image_source"]
    assert schema["properties"]["image_source"]["type"] == "string"


def test_generate_video_tool_exposes_official_video_arguments():
    from exomind_minimax_mcp.server import create_mcp

    async def _get_schema():
        app = create_mcp()
        tools = await app.list_tools()
        for tool in tools:
            if tool.name == "generate_video_tool":
                return tool.inputSchema
        raise AssertionError("generate_video_tool not found")

    schema = asyncio.run(_get_schema())

    assert schema["required"] == ["prompt"]
    for key in ["model", "first_frame_image", "duration", "resolution", "output_directory", "async_mode"]:
        assert key in schema["properties"]


def test_generate_video_tool_description_mentions_first_frame_usage():
    from exomind_minimax_mcp.server import create_mcp

    async def _get_tool():
        app = create_mcp()
        tools = await app.list_tools()
        for tool in tools:
            if tool.name == "generate_video_tool":
                return tool
        raise AssertionError("generate_video_tool not found")

    tool = asyncio.run(_get_tool())

    assert "first_frame_image" in tool.description
    assert "MiniMax-Hailuo-2.3-Fast" in tool.description
    assert "URL" in tool.description
