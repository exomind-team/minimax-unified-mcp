# Live API Matrix Automation Implementation Plan

> **For Claude:** REQUIRED SUB-SKILL: Use superpowers:executing-plans to implement this plan task-by-task.

**Goal:** Build a real MiniMax live smoke runner that exercises every MCP tool with `MINIMAX_TOKEN_PLAN_API_KEY`, records per-interface outcomes, and is reusable from both CLI scripts and pytest.

**Architecture:** Add one shared live-runner module that owns credential loading, temporary fixture creation, per-tool execution, and structured result classification. Keep pytest thin by asserting over the runner's result matrix instead of duplicating endpoint logic across many tests.

**Tech Stack:** Python 3.14, pytest, requests, existing `exomind_minimax_mcp` tool modules.

---

### Task 1: Add failing tests for the live matrix runner

**Files:**
- Modify: `<repo-root>\tests\test_live_minimax_integration.py`
- Create: `<repo-root>\tests\test_live_runner.py`

**Step 1: Write the failing test**

Add tests that expect:
- a shared live runner can enumerate all tool names
- the live runner returns a structured result object per tool
- multimodal live checks use the Token Plan key path by default

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_live_runner.py -v`
Expected: FAIL because the runner module does not exist yet.

**Step 3: Write minimal implementation**

Create the runner module and only enough stubs/types to satisfy the failing imports.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_live_runner.py -v`
Expected: PASS

### Task 2: Implement the shared live runner

**Files:**
- Create: `<repo-root>\src\exomind_minimax_mcp\live_runner.py`
- Modify: `<repo-root>\tests\live_config.py`

**Step 1: Write the failing test**

Add tests for:
- temporary PNG/audio fixture helpers
- status classification for supported, unsupported, insufficient balance, invalid params
- per-tool result shape including tool name, status, detail, and optional artifacts

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_live_runner.py -v`
Expected: FAIL on missing helper behavior.

**Step 3: Write minimal implementation**

Implement:
- result dataclass / typed dict
- helper constructors for minimal fixtures
- one function per live tool scenario
- orchestration entrypoint returning a matrix list

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_live_runner.py -v`
Expected: PASS

### Task 3: Switch multimodal default key selection to Token Plan

**Files:**
- Modify: `<repo-root>\src\exomind_minimax_mcp\tools\audio.py`
- Modify: `<repo-root>\src\exomind_minimax_mcp\tools\generation.py`
- Modify: `<repo-root>\src\exomind_minimax_mcp\config.py`

**Step 1: Write the failing test**

Add tests asserting:
- multimodal helper resolves `MINIMAX_TOKEN_PLAN_API_KEY` by default
- default client creation works without `MINIMAX_PAYG_API_KEY`

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_audio_tools.py tests/test_config.py -v`
Expected: FAIL because the current helper requires the payg path.

**Step 3: Write minimal implementation**

Update the client resolution helper to use the Token Plan key as the default live key path.

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_audio_tools.py tests/test_config.py -v`
Expected: PASS

### Task 4: Add CLI automation script

**Files:**
- Create: `<repo-root>\scripts\run_live_api_matrix.py`
- Modify: `<repo-root>\README.md`
- Modify: `<repo-root>\README-CN.md`

**Step 1: Write the failing test**

Add a smoke test that imports the script entrypoint and expects JSON/text output modes.

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_cli_smoke.py tests/test_live_runner.py -v`
Expected: FAIL because the script entrypoint is missing.

**Step 3: Write minimal implementation**

Add the script with:
- `--json`
- `--only tool_name`
- `--output-dir`
- non-zero exit code only for execution crashes, not for classified account limitations

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_cli_smoke.py tests/test_live_runner.py -v`
Expected: PASS

### Task 5: Expand the real online pytest coverage

**Files:**
- Modify: `<repo-root>\tests\test_live_minimax_integration.py`

**Step 1: Write the failing test**

Replace narrow one-off live tests with matrix-based assertions over all tool scenarios:
- `quota`
- `web_search`
- `understand_image`
- `text_to_audio`
- `list_voices`
- `voice_clone`
- `play_audio`
- `generate_video`
- `query_video_generation`
- `text_to_image`
- `music_generation`
- `voice_design`

**Step 2: Run test to verify it fails**

Run: `python -m pytest tests/test_live_minimax_integration.py -v`
Expected: FAIL until the runner is wired in and the expectations are aligned.

**Step 3: Write minimal implementation**

Use the shared live runner, then assert:
- every tool gets executed
- passing tools must be explicitly marked `passed`
- known account-limited tools must return classified statuses instead of raw crashes

**Step 4: Run test to verify it passes**

Run: `python -m pytest tests/test_live_minimax_integration.py -v`
Expected: PASS or PASS+SKIP depending on local playback capabilities.

### Task 6: Final verification

**Files:**
- Verify only

**Step 1: Run focused verification**

Run: `python -m pytest tests/test_live_runner.py tests/test_live_minimax_integration.py -v`
Expected: PASS

**Step 2: Run full verification**

Run: `python -m pytest -v`
Expected: PASS with any explicitly documented skips only.

**Step 3: Capture actual live matrix**

Run: `python scripts/run_live_api_matrix.py --json`
Expected: JSON result containing all tool statuses and exact failure classifications.
