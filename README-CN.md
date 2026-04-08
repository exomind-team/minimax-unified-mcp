# MiniMax Unified MCP

这是 ExoMind Team 的统一版 MiniMax MCP（统一 MiniMax MCP）项目。

它把三类能力收进了一个本地可安装的 MCP 工具里：
- 官方多模态 MiniMax MCP
- 官方 Token Plan 工具：`web_search`、`understand_image`
- 来自团队日记线索的 Token Plan 额度查询（quota / 额度）

## 当前能力

- `get_token_plan_quota`：查询 Token Plan 额度
- `web_search`：官方网页搜索
- `understand_image`：官方图片理解
- `text_to_audio`：文本转语音，默认模型 `speech-2.8-hd`
- `text_to_audio`：支持 `auto_play=true`，拿到 TTS 结果后立刻自动播放
- `generate_video`：默认模型 `MiniMax-Hailuo-2.3-Fast`
- `list_voices`：列出可用音色
- `voice_clone`：声音克隆
- `play_audio`：支持流式播放（streaming play，边下边播）
- `query_video_generation`：查询视频任务状态
- `text_to_image`：图片生成，默认模型 `image-01`
- `music_generation`：音乐生成，默认模型 `music-2.5`
- `voice_design`：声音设计

## 安装

```powershell
cd <repo-root>
python -m pip install -e .
```

## 环境变量

参考 `.env.example`。

重点变量：
- `MINIMAX_TOKEN_PLAN_API_KEY`：Token Plan 专用 Key
- `MINIMAX_API_HOST`：接口地址，支持 `https://api.minimax.io` 或 `https://api.minimaxi.com`
- `MINIMAX_MCP_BASE_PATH`：本地输出目录
- `MINIMAX_API_RESOURCE_MODE`：资源模式，`url` 或 `local`

## MCP 配置示例

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

也可以直接看 [mcp_server_config_demo.json](./mcp_server_config_demo.json)。

## 测试

```powershell
python -m pytest -v
```

真实在线矩阵测试：

```powershell
python scripts/run_live_api_matrix.py --json
```

这个脚本会用 `MINIMAX_TOKEN_PLAN_API_KEY` 依次调用全部工具，并把结果归类成 `passed`、`unsupported`、`insufficient_balance`、`usage_limit_exceeded`、`timeout`、`invalid_params` 等状态。

## 低延迟 TTS 自动播放

如果要尽量降低体感等待时间，直接调用 `text_to_audio` 并传：

```json
{
  "text": "hello from MiniMax",
  "auto_play": true,
  "play_streaming": true
}
```

当你没有显式指定 `resource_mode` 时，这个调用会临时优先走 URL 输出，再把拿到的音频 URL 直接交给流式播放链路，实现“拿到 URL 就边下边播”。

当前自动化测试覆盖：
- 配置解析
- Token Plan 额度格式化
- Token Plan 搜索与图片理解 payload
- 音频 payload 与流式播放
- 视频、图片、音乐、声音设计的 payload 和本地落盘
- CLI / server 烟测

## 状态

这个仓库现在已经脱离 `uvx` 作为本地开发入口，统一运行时包位于 `src/exomind_minimax_mcp/`。真实在线矩阵测试可以通过 `scripts/run_live_api_matrix.py` 执行。
