from __future__ import annotations

import base64
from pathlib import Path

import pytest


def test_normalize_image_url_keeps_data_urls():
    from exomind_minimax_mcp.image_utils import normalize_image_url

    data_url = "data:image/png;base64,AAAA"

    assert normalize_image_url(data_url) == data_url


def test_normalize_image_url_loads_local_png(tmp_path):
    from exomind_minimax_mcp.image_utils import normalize_image_url

    image_path = tmp_path / "sample.png"
    image_path.write_bytes(b"png-bytes")

    normalized = normalize_image_url(str(image_path))

    assert normalized == f"data:image/png;base64,{base64.b64encode(b'png-bytes').decode('utf-8')}"


def test_normalize_image_url_downloads_remote_webp(monkeypatch):
    from exomind_minimax_mcp.image_utils import normalize_image_url

    class FakeResponse:
        headers = {"content-type": "image/webp", "content-length": "10"}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"webp-bytes"

    monkeypatch.setattr(
        "exomind_minimax_mcp.image_utils.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    normalized = normalize_image_url("https://example.com/sample.webp")

    assert normalized == f"data:image/webp;base64,{base64.b64encode(b'webp-bytes').decode('utf-8')}"


def test_normalize_image_url_rejects_oversized_remote_image(monkeypatch):
    from exomind_minimax_mcp.image_utils import normalize_image_url

    class FakeResponse:
        headers = {"content-type": "image/jpeg", "content-length": str(101 * 1024 * 1024)}

        def raise_for_status(self):
            return None

        def iter_content(self, chunk_size):
            yield b"x"

    monkeypatch.setattr(
        "exomind_minimax_mcp.image_utils.requests.get",
        lambda *args, **kwargs: FakeResponse(),
    )

    with pytest.raises(ValueError):
        normalize_image_url("https://example.com/huge.jpg")


def test_normalize_image_url_raises_for_missing_local_file(tmp_path):
    from exomind_minimax_mcp.image_utils import normalize_image_url

    missing_path = tmp_path / "missing.jpg"

    with pytest.raises(FileNotFoundError):
        normalize_image_url(str(missing_path))
