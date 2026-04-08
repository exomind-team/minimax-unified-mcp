# MiniMax Unified MCP

Unified MiniMax MCP server for ExoMind Team.

This project merges:
- Official multimodal MiniMax MCP capabilities
- Official Token Plan tools: `web_search` and `understand_image`
- Token Plan quota lookup via the remains endpoint recorded in the team diary

## Features

- `get_token_plan_quota`: query Token Plan quota / Token Plan 额度查询
- `web_search`: official Token Plan web search / 官方网页搜索
- `understand_image`: official Token Plan image understanding / 官方图片理解
- `text_to_audio`: speech generation with default `speech-2.8-hd`
- `text_to_audio` also supports `auto_play=true` for immediate playback after TTS response
- `text_to_audio_streaming`: dedicated low-latency TTS streaming playback tool
- `generate_video`: default model `MiniMax-Hailuo-2.3-Fast`
- `list_voices`
- `voice_clone`
- `play_audio` with streaming playback
- `query_video_generation`
- `text_to_image` with default model `image-01`
- `music_generation` with default model `music-2.5`
- `voice_design`

## Install

```powershell
cd <repo-root>
python -m pip install -e .
```

## Environment

See `.env.example`.

Key variables:
- `MINIMAX_TOKEN_PLAN_API_KEY`: Token Plan key
- `MINIMAX_API_HOST`: `https://api.minimax.io` or `https://api.minimaxi.com`
- `MINIMAX_MCP_BASE_PATH`: local output base path
- `MINIMAX_API_RESOURCE_MODE`: `url` or `local`

## Claude / Codex MCP Config

```json
{
  "mcpServers": {
    "MiniMaxUnified": {
      "command": "python",
      "args": ["-m", "exomind_minimax_mcp"],
      "env": {
        "MINIMAX_TOKEN_PLAN_API_KEY": "YOUR_TOKEN_PLAN_KEY",
        "MINIMAX_API_HOST": "https://api.minimax.io",
        "MINIMAX_MCP_BASE_PATH": "./output/minimax",
        "MINIMAX_API_RESOURCE_MODE": "local"
      }
    }
  }
}
```

See [mcp_server_config_demo.json](./mcp_server_config_demo.json).

## Tests

```powershell
python -m pytest -v
```

Real online matrix test（真实在线矩阵测试）:

```powershell
python scripts/run_live_api_matrix.py --json
```

The script executes every tool with `MINIMAX_TOKEN_PLAN_API_KEY` and returns classified statuses such as `passed`, `unsupported`, `insufficient_balance`, `usage_limit_exceeded`, `timeout`, and `invalid_params`.

## Low-latency TTS playback

For the lowest perceived delay, call `text_to_audio` with `auto_play=true`.
If you do not explicitly set `resource_mode`, the tool will temporarily prefer URL output and immediately hand the URL to the streaming playback path.

Example:

```json
{
  "text": "hello from MiniMax",
  "auto_play": true,
  "play_streaming": true
}
```

Dedicated MCP tool:

```json
{
  "text": "hello from MiniMax"
}
```

Call `text_to_audio_streaming` when you want the dedicated low-latency path directly.

Current automated coverage includes:
- config loading
- Token Plan quota formatting
- Token Plan search and image understanding payloads
- audio payloads and streaming playback
- video/image/music/voice-design payload and file handling
- CLI and server smoke tests

## Status

The unified package now runs from `src/exomind_minimax_mcp/` and no longer depends on `uvx` for local development. Real online matrix testing is available through `scripts/run_live_api_matrix.py`.
