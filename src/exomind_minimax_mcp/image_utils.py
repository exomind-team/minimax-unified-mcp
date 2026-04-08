"""Image helpers（图片辅助） for Token Plan VLM tools."""

from __future__ import annotations

import base64
from pathlib import Path

import requests

from exomind_minimax_mcp.constants import DEFAULT_HTTP_TIMEOUT_SECONDS, DEFAULT_MAX_HTTP_DOWNLOAD_BYTES


def normalize_image_url(image_url: str) -> str:
    """Normalize image input（标准化图片输入） to a data URL."""

    if image_url.startswith("@"):
        image_url = image_url[1:]

    if image_url.startswith("data:"):
        return image_url

    if image_url.startswith(("http://", "https://")):
        response = requests.get(image_url, stream=True, timeout=DEFAULT_HTTP_TIMEOUT_SECONDS)
        try:
            response.raise_for_status()
            content_type = response.headers.get("content-type", "image/jpeg").lower()
            content_length = response.headers.get("content-length")
            if content_length and int(content_length) > DEFAULT_MAX_HTTP_DOWNLOAD_BYTES:
                raise ValueError("image is too large（图片体积过大）")

            body = bytearray()
            for chunk in response.iter_content(chunk_size=8192):
                if not chunk:
                    continue
                body.extend(chunk)
                if len(body) > DEFAULT_MAX_HTTP_DOWNLOAD_BYTES:
                    raise ValueError("image is too large（图片体积过大）")
            if "png" in content_type:
                image_format = "png"
            elif "webp" in content_type:
                image_format = "webp"
            else:
                image_format = "jpeg"
            encoded = base64.b64encode(bytes(body)).decode("utf-8")
            return f"data:image/{image_format};base64,{encoded}"
        finally:
            close = getattr(response, "close", None)
            if callable(close):
                close()

    path = Path(image_url).expanduser()
    if not path.exists():
        raise FileNotFoundError(f"Image file not found: {path}")

    if path.suffix.lower() == ".png":
        image_format = "png"
    elif path.suffix.lower() == ".webp":
        image_format = "webp"
    else:
        image_format = "jpeg"

    encoded = base64.b64encode(path.read_bytes()).decode("utf-8")
    return f"data:image/{image_format};base64,{encoded}"
