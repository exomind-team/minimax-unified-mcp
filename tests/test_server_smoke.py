from __future__ import annotations

import importlib


def test_importing_server_does_not_write_to_stdout(capsys):
    import exomind_minimax_mcp.server as server_module

    importlib.reload(server_module)
    captured = capsys.readouterr()

    assert captured.out == ""


def test_create_mcp_returns_app():
    from exomind_minimax_mcp.server import create_mcp

    app = create_mcp()

    assert app is not None
