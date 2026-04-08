<div align="center">

# MiniMax Unified MCP

⚡ 面向 ExoMind 与通用 MCP 客户端的统一 MiniMax MCP 服务。

[![MIT License](https://img.shields.io/badge/license-MIT-2563eb.svg)](./LICENSE)
[![Python](https://img.shields.io/badge/python-3.10%2B-0f766e.svg)](./pyproject.toml)
[![Tests](https://img.shields.io/github/actions/workflow/status/exomind-team/minimax-unified-mcp/test.yml?branch=master&label=tests)](./.github/workflows/test.yml)
[![MCP](https://img.shields.io/badge/protocol-MCP-7c3aed.svg)](https://modelcontextprotocol.io/)
[![MiniMax](https://img.shields.io/badge/provider-MiniMax-f97316.svg)](https://www.minimax.io/)

[English](./README.md) | 简体中文

</div>

## ✨ 项目简介

`minimax-unified-mcp` 把三类能力统一进一个可安装的 MCP 服务：

- 官方多模态 MiniMax 生成能力
- 官方 Token Plan 工具：`web_search` 与 `understand_image`
- 面向 ExoMind 团队工作流的 Token Plan 额度查询

它适合本地优先地接入 Claude、Codex 以及其他兼容 MCP 的客户端。

## 🧰 当前工具

| 工具 | 作用 |
| --- | --- |
| `quota_tool` | 查询 Token Plan 额度与刷新窗口 |
| `web_search_tool` | 使用 Token Plan 做网页搜索 |
| `understand_image_tool` | 分析本地图片路径、远程 URL 或 `data:` URL |
| `text_to_audio_tool` | 文本转语音，支持本地或 URL 输出 |
| `text_to_audio_streaming_tool` | 低延迟 TTS 流式播放 |
| `list_voices_tool` | 查看可用音色 |
| `voice_clone_tool` | 基于样本音频克隆声音 |
| `play_audio_tool` | 播放本地或远程音频 |
| `generate_video_tool` | 文生视频或图生视频 |
| `query_video_generation_tool` | 查询视频生成状态 |
| `text_to_image_tool` | 图片生成 |
| `music_generation_tool` | 基于提示词和歌词生成音乐 |
| `voice_design_tool` | 声音设计 |

## 🚀 快速开始

### 1. 安装

```powershell
cd path/to/minimax-unified-mcp
python -m pip install -e ".[dev]"
```

### 2. 配置环境变量

把 `.env.example` 复制成 `.env`，再填入自己的配置。

关键变量：

- `MINIMAX_TOKEN_PLAN_API_KEY`：Token Plan API Key
- `MINIMAX_API_HOST`：`https://api.minimax.io` 或 `https://api.minimaxi.com`
- `MINIMAX_MCP_BASE_PATH`：本地落盘根目录
- `MINIMAX_API_RESOURCE_MODE`：`url` 或 `local`
- `FASTMCP_LOG_LEVEL`：日志级别，通常为 `WARNING` 或 `INFO`

### 3. 配置到 MCP 客户端

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

也可以直接参考 [mcp_server_config_demo.json](./mcp_server_config_demo.json)。

## 🧭 推荐使用方式

### 网页搜索

使用 `web_search_tool` 查询最新的外部信息。

```json
{
  "query": "MiniMax Token Plan 最新图片模型"
}
```

### 图片理解

严格对齐官方 Token Plan MCP 的签名：`prompt` + `image_source`。

`image_source` 支持：

- 本地路径，例如 `D:/images/demo.png`
- HTTP / HTTPS 图片 URL
- `data:` URL

```json
{
  "prompt": "描述这张截图里的界面结构",
  "image_source": "D:/images/screenshot.png"
}
```

### 先生成图，再理解图

1. 调用 `text_to_image_tool`
2. 复制返回结果中的一个图片 URL
3. 将该 URL 传入 `understand_image_tool.image_source`

### 低延迟 TTS

如果优先考虑体感延迟，优先用 `text_to_audio_streaming_tool`。

```json
{
  "text": "hello from MiniMax"
}
```

如果你需要更细的控制，比如 `resource_mode`、本地输出或自动播放，再用 `text_to_audio_tool`。

### 视频生成

- 默认文生视频路径使用 `MiniMax-Hailuo-2.3`
- 如果手动选择 `MiniMax-Hailuo-2.3-Fast`，必须同时传 `first_frame_image`
- `first_frame_image` 支持本地路径、URL 或 `data:` URL

```json
{
  "prompt": "一只可爱的橘猫在阳光下睡觉",
  "model": "MiniMax-Hailuo-2.3-Fast",
  "first_frame_image": "D:/images/cat.png",
  "async_mode": true
}
```

### 音乐生成

音乐生成通常比普通文本接口更慢。unified 版已经对该接口放宽了超时时间，但真实耗时仍然取决于上游服务状态。

## ⚙️ 文档导航

详细文档入口：

- [使用说明（中文）](./docs/USAGE-CN.md)
- [配置说明（中文）](./docs/CONFIGURATION-CN.md)
- [Usage Guide (English)](./docs/USAGE.md)
- [Configuration Guide (English)](./docs/CONFIGURATION.md)
- [Release Guide](./docs/RELEASE.md)

## 📦 输出模式

支持两种输出模式：

- `url`：直接返回远程资源 URL
- `local`：下载到 `MINIMAX_MCP_BASE_PATH`

如果你希望后续自动化流程稳定消费本地文件，建议使用 `local`。

## 🛡️ 错误与额度提示

统一客户端会保留上游错误，并对常见账户状态给出更清楚的提示：

- `1008 insufficient balance`：明确显示为余额不足
- `2056 usage limit exceeded`：明确显示为额度或用量已耗尽
- `2013 invalid params`：保留原始参数错误，例如视频模式与模型组合不支持

## ✅ 测试

运行完整测试：

```powershell
python -m pytest -v
```

运行真实在线矩阵：

```powershell
python scripts/run_live_api_matrix.py --json
```

在线矩阵会把结果归类成 `passed`、`unsupported`、`insufficient_balance`、`usage_limit_exceeded`、`timeout`、`invalid_params` 等状态。

## 🌍 开源说明

当前仓库使用 MIT License（MIT 许可证）。

- 许可证：[LICENSE](./LICENSE)
- 第三方声明：[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)
- 贡献指南：[CONTRIBUTING.md](./CONTRIBUTING.md)
- 安全策略：[SECURITY.md](./SECURITY.md)

## 📌 当前状态

当前运行时包位于 `src/exomind_minimax_mcp/`，本地开发已经不再依赖 `uvx`。仓库现在已经具备 GitHub Release 发布和持续维护的基础结构。
