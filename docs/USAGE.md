# Usage Guide

## Recommended Tool Flows

### 1. Search current information

Use `web_search_tool` whenever you need current external information.

Example:

```json
{
  "query": "MiniMax latest video model documentation"
}
```

### 2. Analyze a local or remote image

Use `understand_image_tool` with:

- `prompt`
- `image_source`

Valid `image_source` formats:

- local path: `D:/images/ui.png`
- remote URL: `https://example.com/ui.png`
- data URL: `data:image/png;base64,...`

Example:

```json
{
  "prompt": "Describe the main layout and any visible controls",
  "image_source": "D:/images/ui.png"
}
```

### 3. Generate an image and inspect it

1. Call `text_to_image_tool`
2. Copy one generated image URL
3. Feed that URL into `understand_image_tool.image_source`

### 4. Generate speech with low latency

Use `text_to_audio_streaming_tool` for the fastest perceived response.

Use `text_to_audio_tool` when you need:

- local file output
- autoplay configuration
- custom `resource_mode`

### 5. Generate video correctly

Default text-to-video:

```json
{
  "prompt": "A calm cyberpunk street at night"
}
```

Image-to-video with `MiniMax-Hailuo-2.3-Fast`:

```json
{
  "prompt": "A sleepy orange cat breathing slowly in sunlight",
  "model": "MiniMax-Hailuo-2.3-Fast",
  "first_frame_image": "D:/images/cat.png",
  "async_mode": true
}
```

Important:

- `MiniMax-Hailuo-2.3` is the default text-to-video path
- `MiniMax-Hailuo-2.3-Fast` should be treated as image-to-video unless upstream changes
- if you use `async_mode=true`, follow up with `query_video_generation_tool`

### 6. Generate music

Music generation can be slow. The unified client uses a longer request timeout for this endpoint.

Example:

```json
{
  "prompt": "Gentle ambient piano",
  "lyrics": "[Verse]\nMorning light falls on the floor"
}
```

## Error Handling Notes

- `1008 insufficient balance`: account balance is insufficient
- `2056 usage limit exceeded`: quota or usage is exhausted for the current window
- `2013 invalid params`: payload and model combination is invalid

## Local Output Advice

When using `MINIMAX_API_RESOURCE_MODE=local`, always set `MINIMAX_MCP_BASE_PATH` to a controlled directory so generated artifacts remain easy to inspect and clean up.
