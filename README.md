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
  - MCP follows the official Token Plan signature: required `image_source` (`URL / local path / data URL`) / MCP 对齐官方 Token Plan 签名：必填 `image_source`（链接 / 本地路径 / data URL）
- `text_to_audio`: speech generation with default `speech-2.8-hd`
- `text_to_audio` also supports `auto_play=true` for immediate playback after TTS response
- `text_to_audio_streaming`: dedicated low-latency TTS streaming playback tool
- `generate_video`: default model `MiniMax-Hailuo-2.3`
  - `MiniMax-Hailuo-2.3-Fast` should be used with `first_frame_image` for image-to-video workflows
- `list_voices`
- `voice_clone`
- `play_audio` with streaming playback
- `query_video_generation`
- `text_to_image` with default model `image-01`
- `music_generation` with default model `music-2.5`
- `voice_design`

## Recommended Usage

Use these workflows first when integrating the MCP in Claude, Codex, or other MCP clients:

1. `web_search`
   - Use for up-to-date external information, news, docs, product lookups, and web research.
   - Example:

```json
{
  "query": "MiniMax Token Plan latest image model"
}
```

2. `understand_image`
   - Follow the official Token Plan MCP signature: pass `prompt` + `image_source`.
   - `image_source` accepts:
     - local file path, such as `D:/images/demo.png`
     - HTTP/HTTPS URL
     - `data:` URL
   - Example:

```json
{
  "prompt": "Describe the UI layout in this screenshot",
  "image_source": "D:/images/screenshot.png"
}
```

3. `text_to_image` then `understand_image`
   - Generate first.
   - Copy one returned image URL into `image_source`.
   - Analyze it with `understand_image`.

4. `text_to_audio_streaming`
   - Prefer this when low perceived latency matters.
   - Use `text_to_audio` when you need full control over `resource_mode`, local outputs, or autoplay behavior.

5. Local-output workflows
   - Set `MINIMAX_API_RESOURCE_MODE=local` when you want audio / image / video artifacts saved to disk.
   - Set `MINIMAX_MCP_BASE_PATH` to keep all generated files under a controlled output directory.

6. `generate_video`
   - Default text-to-video path uses `MiniMax-Hailuo-2.3`.
   - If you choose `MiniMax-Hailuo-2.3-Fast`, also provide `first_frame_image`.
   - Example image-to-video call:

```json
{
  "prompt": "A cute orange cat sleeping in sunlight",
  "model": "MiniMax-Hailuo-2.3-Fast",
  "first_frame_image": "D:/images/cat.png",
  "async_mode": true
}
```

7. `music_generation`
   - Music generation can take longer than standard text APIs.
   - The unified client now uses a longer request timeout for this endpoint, but live generation still depends on remote service latency.

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

## Open Source

This repository is released under the MIT License.

- Project license: [LICENSE](./LICENSE)
- Third-party notices: [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)
- Contributing guide: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Security policy: [SECURITY.md](./SECURITY.md)

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
