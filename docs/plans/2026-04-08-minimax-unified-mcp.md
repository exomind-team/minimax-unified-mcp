# MiniMax Unified MCP Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a single public MCP tool that unifies official MiniMax multimodal APIs, official Token Plan tools, and Token Plan quota querying into one locally installable Python server.

**Architecture:** Start from the patched local `minimax-mcp` codebase, rename the package to avoid `minimax_mcp` import collisions, and refactor the server into modular tool groups. Keep one shared HTTP client and one stdio MCP entrypoint, then add a dedicated quota client for the Token Plan remains endpoint. Expose one unified MCP server with stable environment variables and automated tests for config, payload building, response parsing, and tool behavior.

**Tech Stack:** Python 3.10+, `mcp[cli]`, `requests`, `python-dotenv`, `pytest`, `pytest-cov`, GitHub CLI

---

### Task 1: Repository Bootstrap

**Files:**
- Create: `docs/plans/2026-04-08-minimax-unified-mcp.md`
- Modify: `pyproject.toml`
- Modify: `setup.py`
- Modify: `README.md`
- Modify: `README-CN.md`
- Create: `src/exomind_minimax_mcp/__init__.py`
- Create: `src/exomind_minimax_mcp/__main__.py`
- Create: `src/exomind_minimax_mcp/server.py`
- Create: `src/exomind_minimax_mcp/config.py`

**Step 1: Write the failing metadata/import smoke test**

```python
def test_package_name_is_exomind_minimax_mcp():
    import exomind_minimax_mcp
    assert exomind_minimax_mcp.__name__ == "exomind_minimax_mcp"
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_package_smoke.py -v`
Expected: FAIL with `ModuleNotFoundError: No module named 'exomind_minimax_mcp'`

**Step 3: Write minimal implementation**

- Move runtime code under `src/exomind_minimax_mcp/`
- Update package metadata and console script to `minimax-unified-mcp`

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_package_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add pyproject.toml setup.py README.md README-CN.md src/exomind_minimax_mcp tests/test_package_smoke.py
git commit -m "chore: bootstrap minimax unified mcp package"
```

### Task 2: Shared Config And API Clients

**Files:**
- Create: `src/exomind_minimax_mcp/config.py`
- Create: `src/exomind_minimax_mcp/clients/base.py`
- Create: `src/exomind_minimax_mcp/clients/quota.py`
- Create: `tests/test_config.py`
- Create: `tests/test_clients.py`

**Step 1: Write the failing config tests**

```python
def test_load_config_prefers_explicit_token_plan_key():
    ...

def test_quota_client_builds_required_cloudflare_headers():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_config.py tests/test_clients.py -v`
Expected: FAIL because config/client modules do not exist

**Step 3: Write minimal implementation**

- Add shared config loader
- Add shared MiniMax API client
- Add quota client for `https://www.minimax.io/v1/api/openplatform/coding_plan/remains`

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_config.py tests/test_clients.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/exomind_minimax_mcp/config.py src/exomind_minimax_mcp/clients tests/test_config.py tests/test_clients.py
git commit -m "feat: add shared config and api clients"
```

### Task 3: Token Plan Quota Tool

**Files:**
- Create: `src/exomind_minimax_mcp/tools/quota.py`
- Modify: `src/exomind_minimax_mcp/server.py`
- Create: `tests/test_quota_tool.py`

**Step 1: Write the failing quota tool tests**

```python
def test_get_token_plan_quota_formats_single_model_response():
    ...

def test_get_token_plan_quota_returns_json_when_requested():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_quota_tool.py -v`
Expected: FAIL because quota tool is not registered

**Step 3: Write minimal implementation**

- Register `get_token_plan_quota`
- Reuse the diary-discovered endpoint and response semantics
- Support `model`, `all_models`, `raw_json`

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_quota_tool.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/exomind_minimax_mcp/tools/quota.py src/exomind_minimax_mcp/server.py tests/test_quota_tool.py
git commit -m "feat: add token plan quota tool"
```

### Task 4: Token Plan Search And Vision Tools

**Files:**
- Create: `src/exomind_minimax_mcp/tools/token_plan.py`
- Create: `src/exomind_minimax_mcp/image_utils.py`
- Modify: `src/exomind_minimax_mcp/server.py`
- Create: `tests/test_token_plan_tools.py`

**Step 1: Write the failing Token Plan tests**

```python
def test_web_search_calls_official_coding_plan_search_endpoint():
    ...

def test_understand_image_accepts_local_file_and_url():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_token_plan_tools.py -v`
Expected: FAIL because Token Plan tools are not implemented

**Step 3: Write minimal implementation**

- Add `web_search`
- Add `understand_image`
- Normalize `image_url` and keep `image_source` as compatibility alias

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_token_plan_tools.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/exomind_minimax_mcp/tools/token_plan.py src/exomind_minimax_mcp/image_utils.py src/exomind_minimax_mcp/server.py tests/test_token_plan_tools.py
git commit -m "feat: add token plan search and vision tools"
```

### Task 5: Multimodal Tool Migration

**Files:**
- Create: `src/exomind_minimax_mcp/tools/audio.py`
- Create: `src/exomind_minimax_mcp/tools/video.py`
- Create: `src/exomind_minimax_mcp/tools/image.py`
- Create: `src/exomind_minimax_mcp/tools/music.py`
- Create: `src/exomind_minimax_mcp/constants.py`
- Create: `src/exomind_minimax_mcp/utils.py`
- Create: `tests/test_audio_tools.py`
- Create: `tests/test_generation_tools.py`

**Step 1: Write the failing multimodal tests**

```python
def test_text_to_audio_uses_speech_28_hd_default():
    ...

def test_play_audio_supports_streaming_iterators():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_audio_tools.py tests/test_generation_tools.py -v`
Expected: FAIL because migrated tools are incomplete

**Step 3: Write minimal implementation**

- Migrate patched local multimodal code
- Preserve `speech-2.8-hd` default
- Preserve local resource mode
- Preserve streaming audio playback

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_audio_tools.py tests/test_generation_tools.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/exomind_minimax_mcp/tools src/exomind_minimax_mcp/constants.py src/exomind_minimax_mcp/utils.py tests/test_audio_tools.py tests/test_generation_tools.py
git commit -m "feat: migrate multimodal minimax tools"
```

### Task 6: MCP Transport And CLI Smoke Tests

**Files:**
- Modify: `src/exomind_minimax_mcp/server.py`
- Modify: `src/exomind_minimax_mcp/__main__.py`
- Create: `tests/test_server_smoke.py`
- Create: `tests/test_cli_smoke.py`

**Step 1: Write the failing transport tests**

```python
def test_server_startup_does_not_print_to_stdout():
    ...

def test_cli_entrypoint_exists():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_server_smoke.py tests/test_cli_smoke.py -v`
Expected: FAIL because startup behavior still pollutes stdout or CLI is missing

**Step 3: Write minimal implementation**

- Remove stdout startup prints
- Route logs to stderr
- Ensure `python -m exomind_minimax_mcp` starts the MCP server cleanly

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_server_smoke.py tests/test_cli_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add src/exomind_minimax_mcp/server.py src/exomind_minimax_mcp/__main__.py tests/test_server_smoke.py tests/test_cli_smoke.py
git commit -m "fix: clean stdio transport for mcp server"
```

### Task 7: Public Repo Readiness

**Files:**
- Modify: `README.md`
- Modify: `README-CN.md`
- Create: `.github/workflows/test.yml`
- Create: `.env.example`

**Step 1: Write the failing CI expectation test**

```python
def test_env_example_mentions_token_plan_and_payg_keys():
    ...
```

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_docs_smoke.py -v`
Expected: FAIL because docs/CI/env template are incomplete

**Step 3: Write minimal implementation**

- Add setup and usage docs
- Add CI for pytest
- Add GitHub-ready env template

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_docs_smoke.py -v`
Expected: PASS

**Step 5: Commit**

```bash
git add README.md README-CN.md .github/workflows/test.yml .env.example tests/test_docs_smoke.py
git commit -m "docs: prepare public repository and ci"
```

### Task 8: End-To-End Verification And Publish

**Files:**
- Modify: `.gitignore`
- Modify: `README.md`

**Step 1: Run full verification**

Run: `python -m pytest -v`
Expected: all tests PASS

**Step 2: Run packaging verification**

Run: `python -m pip install -e .`
Expected: editable install succeeds

**Step 3: Run MCP startup verification**

Run: `python -m exomind_minimax_mcp`
Expected: process starts without stdout pollution and waits for MCP stdio input

**Step 4: Publish repository**

Run: `gh repo create exomind-team/minimax-unified-mcp --public --source . --remote origin --push`
Expected: GitHub repository created and local branch pushed

**Step 5: Commit**

```bash
git add .
git commit -m "chore: release minimax unified mcp v0"
```
