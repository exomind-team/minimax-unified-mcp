# Release Guide

## Release Checklist

1. Ensure all tests pass
2. Update documentation if public behavior changed
3. Build distribution artifacts
4. Create or update release notes
5. Tag the release
6. Publish the GitHub release
7. Optionally publish to TestPyPI or PyPI

## Local Build

```powershell
python -m build
```

Artifacts will be written to `dist/`.

## Versioning

The package version is defined in `pyproject.toml`.

Recommended tag format:

- `v0.1.0`
- `v0.1.1`
- `v0.2.0`

## GitHub Release

If GitHub CLI is authenticated:

```powershell
gh release create v0.1.0 dist/* --title "v0.1.0" --notes-file docs/releases/v0.1.0.md
```

## PyPI Strategy

PyPI is not strictly required for this project to be usable.

Use GitHub Release only when:

- the primary users install from source or local wheel files
- the MCP is consumed mainly inside your own team workflow

Use PyPI when:

- you want `pip install minimax-unified-mcp`
- you want easier third-party adoption
- you want package-manager style version distribution

Recommended rollout:

1. Always create a GitHub Release first
2. Publish to TestPyPI manually
3. Verify install from TestPyPI
4. Publish to PyPI manually

## Publish Workflow

This repository includes a manual workflow:

- `.github/workflows/publish-pypi.yml`

It supports:

- `testpypi`
- `pypi`

The workflow:

1. runs tests
2. builds `sdist` and `wheel`
3. runs `twine check`
4. publishes via GitHub Trusted Publishing

## Trusted Publishing Setup

Before PyPI publishing works, configure the package on:

- TestPyPI
- PyPI

And grant this GitHub repository trusted publishing permission for each environment.

Suggested GitHub environments:

- `testpypi`
- `pypi`

## Suggested Release Notes Structure

- Highlights
- Added
- Changed
- Fixed
- Verification

## Current Scope

This repository is ready for:

- GitHub Releases with wheel and sdist artifacts
- manual TestPyPI publishing
- manual PyPI publishing after trusted publishing is configured
