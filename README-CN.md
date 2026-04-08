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
  - MCP 对齐官方 Token Plan 签名：必填 `image_source`（URL / 本地路径 / data URL）
- `text_to_audio`：文本转语音，默认模型 `speech-2.8-hd`
- `text_to_audio`：支持 `auto_play=true`，拿到 TTS 结果后立刻自动播放
- `text_to_audio_streaming`：专用低延迟 TTS 流式播放工具
- `generate_video`：默认模型 `MiniMax-Hailuo-2.3`
  - `MiniMax-Hailuo-2.3-Fast` 应配合 `first_frame_image` 使用，适合图生视频（image-to-video）
- `list_voices`：列出可用音色
- `voice_clone`：声音克隆
- `play_audio`：支持流式播放（streaming play，边下边播）
- `query_video_generation`：查询视频任务状态
- `text_to_image`：图片生成，默认模型 `image-01`
- `music_generation`：音乐生成，默认模型 `music-2.5`
- `voice_design`：声音设计

## 推荐使用方式

优先按下面这些工作流使用：

1. `web_search`
   - 用于查最新网页信息、文档、新闻、产品资料、外部知识。

```json
{
  "query": "MiniMax Token Plan 最新图片模型"
}
```

2. `understand_image`
   - 严格对齐官方 Token Plan MCP 用法：传 `prompt` + `image_source`
   - `image_source` 支持：
     - 本地路径，例如 `D:/images/demo.png`
     - HTTP / HTTPS 图片 URL
     - `data:` URL

```json
{
  "prompt": "描述这张截图里的界面结构",
  "image_source": "D:/images/screenshot.png"
}
```

3. `text_to_image` 后接 `understand_image`
   - 先生成图片
   - 从返回结果里复制一个图片 URL
   - 再把这个 URL 填进 `image_source` 做图片理解

4. `text_to_audio_streaming`
   - 如果你关心低体感延迟，优先直接用这个工具
   - 如果你需要更细的参数控制，比如 `resource_mode`、本地输出、自动播放，再用 `text_to_audio`

5. 本地落盘模式
   - 想把音频 / 图片 / 视频直接保存到本地时，设置 `MINIMAX_API_RESOURCE_MODE=local`
   - 同时配置 `MINIMAX_MCP_BASE_PATH`，把输出统一收口到固定目录

6. `generate_video`
   - 默认文生视频（text-to-video）路径使用 `MiniMax-Hailuo-2.3`
   - 如果你手动选择 `MiniMax-Hailuo-2.3-Fast`，需要同时传 `first_frame_image`
   - 图生视频示例：

```json
{
  "prompt": "一只可爱的橘猫在阳光下睡觉",
  "model": "MiniMax-Hailuo-2.3-Fast",
  "first_frame_image": "D:/images/cat.png",
  "async_mode": true
}
```

7. `music_generation`
   - 音乐生成通常比普通文本接口更慢
   - unified 版已经对这个接口放宽了请求超时，但真实耗时仍然取决于远端服务状态

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

## 开源说明

当前仓库使用 MIT License（MIT 许可证）。

- 项目许可证：[LICENSE](./LICENSE)
- 第三方声明：[THIRD_PARTY_NOTICES.md](./THIRD_PARTY_NOTICES.md)
- 贡献指南：[CONTRIBUTING.md](./CONTRIBUTING.md)
- 安全策略：[SECURITY.md](./SECURITY.md)

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

如果你想直接使用专用工具，也可以直接调用 `text_to_audio_streaming`，它内部固定采用这条低延迟链路。

当前自动化测试覆盖：
- 配置解析
- Token Plan 额度格式化
- Token Plan 搜索与图片理解 payload
- 音频 payload 与流式播放
- 视频、图片、音乐、声音设计的 payload 和本地落盘
- CLI / server 烟测

## 状态

这个仓库现在已经脱离 `uvx` 作为本地开发入口，统一运行时包位于 `src/exomind_minimax_mcp/`。真实在线矩阵测试可以通过 `scripts/run_live_api_matrix.py` 执行。
