# Configuration Guide

## Environment Variables

### Required

- `MINIMAX_TOKEN_PLAN_API_KEY`
  - Token Plan API key used by Token Plan tools and unified online checks

- `MINIMAX_API_HOST`
  - Example: `https://api.minimax.io`
  - Mainland deployments may use `https://api.minimaxi.com`

### Recommended

- `MINIMAX_MCP_BASE_PATH`
  - Base directory used when tools save local artifacts
  - Example: `./output/minimax`

- `MINIMAX_API_RESOURCE_MODE`
  - `url`: return remote URLs
  - `local`: save artifacts locally

- `FASTMCP_LOG_LEVEL`
  - Suggested values: `WARNING`, `INFO`

## MCP Client Example

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

## Resource Mode Advice

Use `url` when:

- you want the client to consume remote assets directly
- you do not need local files

Use `local` when:

- you need stable local artifacts
- you want downstream automation to process generated files
- you want easier manual inspection

## Model Notes

- Default video model: `MiniMax-Hailuo-2.3`
- Default image model: `image-01`
- Default music model: `music-2.5`
- Default speech model: `speech-2.8-hd`

## Security Notes

- Never commit real API keys
- Keep `.env` local
- Use `MINIMAX_MCP_BASE_PATH` inside a controlled directory
- Avoid placing generated files in sensitive folders
