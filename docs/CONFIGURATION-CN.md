# 配置说明

## 环境变量

### 必填项

- `MINIMAX_TOKEN_PLAN_API_KEY`
  - Token Plan API Key，统一工具和在线矩阵测试都会用到

- `MINIMAX_API_HOST`
  - 示例：`https://api.minimax.io`
  - 中国大陆环境也可以按实际情况使用 `https://api.minimaxi.com`

### 推荐项

- `MINIMAX_MCP_BASE_PATH`
  - 本地落盘模式下的输出根目录
  - 示例：`./output/minimax`

- `MINIMAX_API_RESOURCE_MODE`
  - `url`：直接返回远程资源 URL
  - `local`：下载并保存到本地

- `FASTMCP_LOG_LEVEL`
  - 推荐值：`WARNING`、`INFO`

## MCP 客户端配置示例

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

## 资源模式建议

适合使用 `url` 的情况：

- 直接把远程资源交给客户端消费
- 不需要保存本地文件

适合使用 `local` 的情况：

- 需要稳定的本地文件产物
- 下游自动化流程要继续处理文件
- 需要更方便地人工检查生成结果

## 默认模型说明

- 默认视频模型：`MiniMax-Hailuo-2.3`
- 默认图片模型：`image-01`
- 默认音乐模型：`music-2.5`
- 默认语音模型：`speech-2.8-hd`

## 安全建议

- 不要提交真实 API Key
- `.env` 只保留在本地
- `MINIMAX_MCP_BASE_PATH` 建议放在受控目录中
- 不要把生成文件输出到敏感目录
