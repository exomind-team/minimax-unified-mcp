# Contributing Guide

Thanks for contributing to `minimax-unified-mcp`.

## Before You Start

- Read [README.md](./README.md) or [README-CN.md](./README-CN.md) first.
- Use English in code, config keys, and test names.
- Keep Chinese notes in documentation when bilingual clarification is useful.
- Do not commit real API keys, tokens, or local absolute secrets.

## Local Setup

```powershell
python -m pip install -e ".[dev]"
Copy-Item .env.example .env
```

Then fill in your own environment variables in `.env`.

## Development Workflow

1. Create a focused branch.
2. Add or update tests before changing behavior.
3. Keep changes small and reviewable.
4. Update docs when public behavior, config, or tool signatures change.
5. Run the full test suite before opening a PR.

## Test Commands

```powershell
python -m pytest -v
python scripts/run_live_api_matrix.py --json
```

Notes:
- The live matrix script calls real MiniMax APIs and may consume quota.
- Use it only when you intend to verify real online behavior.

## Tool Compatibility Rules

- Keep `understand_image` aligned with the official Token Plan MCP signature.
- Preserve backward compatibility only when it does not make the MCP schema misleading.
- When adding new MCP tools, document the intended usage in both English and Chinese READMEs.

## Pull Requests

Please include:

- what changed
- why it changed
- how you tested it
- whether real API quota was used

If your change affects outputs, include a short example request and response.

## License

By contributing to this repository, you agree that your contributions are released under the MIT License in [LICENSE](./LICENSE).
