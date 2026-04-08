from __future__ import annotations

import runpy


def test_module_entrypoint_delegates_to_main(monkeypatch):
    called: list[str] = []

    monkeypatch.setattr(
        "exomind_minimax_mcp.server.main",
        lambda: called.append("called"),
    )

    runpy.run_module("exomind_minimax_mcp.__main__", run_name="__main__")

    assert called == ["called"]
