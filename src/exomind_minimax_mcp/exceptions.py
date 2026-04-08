"""Custom exceptions（自定义异常） for unified MiniMax MCP."""


class MiniMaxAPIError(Exception):
    """Base API exception（基础 API 异常）."""


class MiniMaxAuthError(MiniMaxAPIError):
    """Authentication error（鉴权异常）."""


class MiniMaxRequestError(MiniMaxAPIError):
    """Request error（请求异常）."""


class MiniMaxTimeoutError(MiniMaxAPIError):
    """Timeout error（超时异常）."""


class MiniMaxValidationError(MiniMaxAPIError):
    """Validation error（校验异常）."""


class MiniMaxMcpError(MiniMaxAPIError):
    """Local MCP error（本地 MCP 异常）."""
