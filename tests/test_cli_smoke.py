from __future__ import annotations

import runpy
from pathlib import Path


def test_module_entrypoint_delegates_to_main(monkeypatch):
    called: list[str] = []

    monkeypatch.setattr(
        "exomind_minimax_mcp.server.main",
        lambda: called.append("called"),
    )

    runpy.run_module("exomind_minimax_mcp.__main__", run_name="__main__")

    assert called == ["called"]


def test_live_matrix_script_exports_main():
    script_path = Path("scripts/run_live_api_matrix.py")

    assert script_path.exists()
