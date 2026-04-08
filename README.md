<div align="center">

# MiniMax Unified MCP

⚡ Unified MiniMax MCP for multimodal generation, Token Plan search, and image understanding.

[![MIT License](https://img.shields.io/badge/license-MIT-2563eb.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-0f766e.svg)](./pyproject.toml)
[![Tests](https://img.shields.io/github/actions/workflow/status/exomind-team/minimax-unified-mcp/test.yml?branch=master&label=tests)](./.github/workflows/test.yml)
[![MCP](https://img.shields.io/badge/protocol-MCP-7c3aed.svg)](https://modelcontextprotocol.io/)
[![MiniMax](https://img.shields.io/badge/provider-MiniMax-f97316.svg)](https://www.minimax.io/)

English | [简体中文](./README-CN.md)

</div>

## ✨ Overview

`minimax-unified-mcp` merges three capability groups into one installable MCP server:

- Official multimodal MiniMax generation tools
- Official Token Plan tools: `web_search` and `understand_image`
- Token Plan quota lookup aligned with the ExoMind Team workflow

This repository is intended for local-first MCP usage in Claude, Codex, and compatible MCP clients.

## 🧰 Tools

| Tool | Purpose |
| --- | --- |
| `quota_tool` | Query Token Plan quota and refresh window |
| `web_search_tool` | Search the live web via Token Plan |
| `understand_image_tool` | Analyze a local image path, remote URL, or `data:` URL |
| `text_to_audio_tool` | Generate speech with configurable output mode |
| `text_to_audio_streaming_tool` | Low-latency speech playback path |
| `list_voices_tool` | List available voices |
| `voice_clone_tool` | Clone a voice from sample audio |
| `play_audio_tool` | Play local or remote audio |
| `generate_video_tool` | Generate text-to-video or image-to-video |
| `query_video_generation_tool` | Query video generation status |
| `text_to_image_tool` | Generate images |
| `music_generation_tool` | Generate music from prompt and lyrics |
| `voice_design_tool` | Design a new voice |

## 🚀 Quick Start

### 1. Install

```powershell
cd path/to/minimax-unified-mcp
python -m pip install -e ".[dev]"
```

### 2. Configure environment

Copy `.env.example` to `.env` and fill in your credentials.

Important variables:

- `MINIMAX_TOKEN_PLAN_API_KEY`: Token Plan API key
- `MINIMAX_API_HOST`: `https://api.minimax.io` or `https://api.minimaxi.com`
- `MINIMAX_MCP_BASE_PATH`: base path for local artifacts
- `MINIMAX_API_RESOURCE_MODE`: `url` or `local`
- `FASTMCP_LOG_LEVEL`: logging level, usually `WARNING` or `INFO`

### 3. Add to your MCP client

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
        "MINIMAX_API_RESOURCE_MODE": "local",
        "FASTMCP_LOG_LEVEL": "WARNING"
      }
    }
  }
}
```

See [mcp_server_config_demo.json](./mcp_server_config_demo.json) for a ready-to-copy example.

## 🧭 Recommended Usage

### Web search

Use `web_search_tool` for current external information.

```json
{
  "query": "MiniMax Token Plan latest image model"
}
```

### Image understanding

Follow the official Token Plan MCP signature: `prompt` + `image_source`.

`image_source` supports:

- local file path, such as `D:/images/demo.png`
- HTTP / HTTPS image URL
- `data:` URL

```json
{
  "prompt": "Describe the UI structure in this screenshot",
  "image_source": "D:/images/screenshot.png"
}
```

### Image generation then image understanding

1. Call `text_to_image_tool`
2. Copy one returned image URL
3. Pass that URL into `understand_image_tool.image_source`

### Low-latency TTS

Prefer `text_to_audio_streaming_tool` when perceived latency matters.

```json
{
  "text": "hello from MiniMax"
}
```

Use `text_to_audio_tool` when you need more control over `resource_mode`, local output, or autoplay.

### Quota field notes

`quota_tool` currently maps the upstream fields to their display semantics as follows:

- `current_interval_usage_count`: remaining in current interval（当前窗口剩余）
- `current_weekly_usage_count`: weekly remaining（本周剩余）

Note: even though the field name contains `usage_count`, this output is treated as remaining quota, not used quota.

### Video generation

- Default text-to-video path uses `MiniMax-Hailuo-2.3`
- If you choose `MiniMax-Hailuo-2.3-Fast`, also provide `first_frame_image`
- `first_frame_image` supports local path, URL, or `data:` URL

```json
{
  "prompt": "A cute orange cat sleeping in sunlight",
  "model": "MiniMax-Hailuo-2.3-Fast",
  "first_frame_image": "D:/images/cat.png",
  "async_mode": true
}
```

### Music generation

Music generation is slower than typical text APIs. The unified client uses an extended request timeout for this endpoint, but real latency still depends on upstream service status.

## ⚙️ Configuration

Detailed guides:

- [Usage Guide](./docs/USAGE.md)
- [Configuration Guide](./docs/CONFIGURATION.md)
- [Release Guide](./docs/RELEASE.md)
- [Chinese Usage Guide](./docs/USAGE-CN.md)
- [Chinese Configuration Guide](./docs/CONFIGURATION-CN.md)

## 📦 Output Modes

Two output modes are supported:

- `url`: return remote URLs directly
- `local`: download artifacts to `MINIMAX_MCP_BASE_PATH`

Use `local` when you want reproducible local files for downstream automation.

## 🛡️ Errors and Quota Signals

The unified client preserves upstream errors and improves readability for common account states:

- `1008 insufficient balance`: clearly reported as balance insufficient
- `2056 usage limit exceeded`: clearly reported as quota / usage exhausted
- `2013 invalid params`: preserved for bad payloads such as unsupported video mode combinations

## ✅ Testing

Run the full suite:

```powershell
python -m pytest -v
```

Run the live API matrix:

```powershell
python scripts/run_live_api_matrix.py --json
```

The live matrix classifies results into statuses such as `passed`, `unsupported`, `insufficient_balance`, `usage_limit_exceeded`, `timeout`, and `invalid_params`.

## 🌍 Open Source

This repository is released under the MIT License.

- License: [LICENSE](./LICENSE)
- Third-party attribution: [THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)
- Contributing: [CONTRIBUTING.md](./CONTRIBUTING.md)
- Security: [SECURITY.md](./SECURITY.md)

## 📌 Status

The package runs from `src/exomind_minimax_mcp/` and no longer depends on `uvx` for local development. It is ready for GitHub-based release packaging and ongoing MCP client integration.
