# Security Policy

## Supported Versions

Security fixes are applied to the latest branch on this repository.

## Reporting a Vulnerability

Please do not open a public issue for secrets, credential leaks, or exploitable bugs.

Instead, report privately to:

- `team@exomind.dev`

Include the following when possible:

- affected tool or module
- reproduction steps
- expected impact
- whether real MiniMax credentials are required to reproduce

## Sensitive Areas

Pay extra attention to:

- API key handling
- local file reads and path validation
- remote download limits
- MCP tool schemas and parameter validation
- generated file paths and artifact exposure

## Disclosure Process

1. We confirm receipt.
2. We reproduce and assess severity.
3. We prepare and test a fix.
4. We publish the fix and disclose the issue when appropriate.
