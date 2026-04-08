# Release Guide

## Release Checklist

1. Ensure all tests pass
2. Update documentation if public behavior changed
3. Build distribution artifacts
4. Create or update release notes
5. Tag the release
6. Publish the GitHub release

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

## Suggested Release Notes Structure

- Highlights
- Added
- Changed
- Fixed
- Verification

## Current Scope

This repository is ready for GitHub Releases with wheel and sdist artifacts. Publishing to PyPI should be added only after package publishing credentials and ownership are finalized.
