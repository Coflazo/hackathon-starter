# Security policy

## Supported versions

| Version | Supported |
| --- | --- |
| 1.x | Yes |

## Reporting a vulnerability

Report security problems privately through GitHub: open the repository's **Security** tab and choose
**Report a vulnerability**. Do not open a public issue. You can expect an acknowledgement within 7 days.

## What the starter already defends against

A hackathon demo is deployed in public for a weekend, so the defaults assume hostile visitors.

| Risk | Default |
| --- | --- |
| A visitor burns your LLM quota | `/demo` is rate-limited per IP (`DEMO_RATE_LIMIT`, default 20 a minute; in memory, per instance) |
| A visitor overwrites the demo fixture | `RECORD` is ignored in production builds |
| A fixture key reaches the file system | Keys are checked against a strict pattern; path-like keys are refused |
| An error leaks internals | Clients get a generic message; details stay in the server log |
| A key lands in git | `.env` and `.env.local` are ignored, and gitleaks runs in CI on every push and pull request |

The in-memory rate limit resets on restart and is per instance. Put a shared limit (for example an
edge rule) in front of anything that runs longer than an event.
