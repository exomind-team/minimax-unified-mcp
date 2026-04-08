# 使用说明

## 推荐工具工作流

### 1. 查询最新信息

需要获取最新网页信息时，优先使用 `web_search_tool`。

示例：

```json
{
  "query": "MiniMax 最新视频模型文档"
}
```

### 2. 分析本地或远程图片

`understand_image_tool` 需要两个核心参数：

- `prompt`
- `image_source`

`image_source` 支持：

- 本地路径：`D:/images/ui.png`
- 远程 URL：`https://example.com/ui.png`
- data URL：`data:image/png;base64,...`

示例：

```json
{
  "prompt": "描述这张界面图的主要布局和可见控件",
  "image_source": "D:/images/ui.png"
}
```

### 3. 先生成图，再理解图

1. 调用 `text_to_image_tool`
2. 从返回结果里复制一个图片 URL
3. 把这个 URL 填到 `understand_image_tool.image_source`

### 4. 使用低延迟 TTS

如果优先考虑体感延迟，直接用 `text_to_audio_streaming_tool`。

如果你需要：

- 本地音频落盘
- 自动播放控制
- 自定义 `resource_mode`

则使用 `text_to_audio_tool`。

### 5. 正确生成视频

默认文生视频：

```json
{
  "prompt": "夜晚安静的赛博朋克街道"
}
```

使用 `MiniMax-Hailuo-2.3-Fast` 做图生视频：

```json
{
  "prompt": "一只橘猫在阳光里缓慢呼吸睡觉",
  "model": "MiniMax-Hailuo-2.3-Fast",
  "first_frame_image": "D:/images/cat.png",
  "async_mode": true
}
```

注意：

- `MiniMax-Hailuo-2.3` 是默认文生视频路径
- `MiniMax-Hailuo-2.3-Fast` 目前应视为图生视频路径
- 如果使用 `async_mode=true`，后续要调用 `query_video_generation_tool`

### 6. 生成音乐

音乐生成通常比较慢，unified 客户端已经为该接口配置了更长的请求超时。

示例：

```json
{
  "prompt": "温柔的氛围钢琴",
  "lyrics": "[Verse]\n清晨阳光落在地板上"
}
```

## 错误处理说明

- `1008 insufficient balance`：余额不足
- `2056 usage limit exceeded`：当前额度或用量窗口已耗尽
- `2013 invalid params`：参数和模型组合不合法

## 本地输出建议

当使用 `MINIMAX_API_RESOURCE_MODE=local` 时，建议始终设置 `MINIMAX_MCP_BASE_PATH`，把生成产物统一收口到一个可控目录里，便于检查和清理。
