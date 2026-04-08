from __future__ import annotations

from pathlib import Path


def test_env_example_mentions_required_token_plan_settings():
    env_example = Path(".env.example").read_text(encoding="utf-8")

    assert "MINIMAX_TOKEN_PLAN_API_KEY" in env_example
    assert "MINIMAX_API_RESOURCE_MODE" in env_example


def test_examples_no_longer_use_legacy_minimax_api_key_name():
    example_files = [
        Path(".env.example"),
        Path("README.md"),
        Path("README-CN.md"),
        Path("mcp_server_config_demo.json"),
    ]

    for path in example_files:
        text = path.read_text(encoding="utf-8")
        assert "MINIMAX_API_KEY" not in text, f"{path} still references legacy MINIMAX_API_KEY"


def test_open_source_docs_and_license_markers_exist():
    assert Path("CONTRIBUTING.md").exists()
    assert Path("SECURITY.md").exists()
    assert Path("THIRD_PARTY_NOTICES.md").exists()
    assert Path("docs/USAGE.md").exists()
    assert Path("docs/USAGE-CN.md").exists()
    assert Path("docs/CONFIGURATION.md").exists()
    assert Path("docs/CONFIGURATION-CN.md").exists()
    assert Path("docs/RELEASE.md").exists()
    assert Path(".github/workflows/publish-pypi.yml").exists()

    readme = Path("README.md").read_text(encoding="utf-8")
    readme_cn = Path("README-CN.md").read_text(encoding="utf-8")
    release_doc = Path("docs/RELEASE.md").read_text(encoding="utf-8")

    assert "MIT" in readme
    assert "MIT" in readme_cn
    assert '<div align="center">' in readme
    assert '<div align="center">' in readme_cn
    assert "PyPI" in release_doc


def test_public_docs_do_not_contain_local_machine_paths():
    checked_files = [
        Path("README.md"),
        Path("README-CN.md"),
        Path("mcp_server_config_demo.json"),
        Path("docs/CONFIGURATION.md"),
        Path("docs/CONFIGURATION-CN.md"),
        Path("THIRD_PARTY_NOTICES.md"),
    ]

    forbidden_fragments = [
        "<workspace>/",
        "D:\\project\\",
        "C:/Users/starlin",
        "C:\\Users\\starlin",
    ]

    for path in checked_files:
        text = path.read_text(encoding="utf-8")
        for fragment in forbidden_fragments:
            assert fragment not in text, f"{path} still exposes local path fragment: {fragment}"
