from __future__ import annotations

import pytest
from exomind_minimax_mcp.live_config import LiveTestSettings, load_live_settings


def load_live_test_settings() -> LiveTestSettings:
    settings = load_live_settings()
    if settings is None:
        pytest.skip("No live MiniMax credentials found in env or Claude config")
    return settings
