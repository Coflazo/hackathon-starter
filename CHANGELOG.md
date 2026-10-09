# Changelog

All notable changes to this project are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and the project uses
[Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [1.0.0] - 2026-10-09

### Added

- `web/`: Next.js 16 app with one demo page, an API route, `lib/replay.ts` (record and replay with
  a fixture fallback) and `lib/llm.ts` (a primary and a fallback OpenAI-compatible provider).
- `api/`: FastAPI twin with `replay.py` and the same demo endpoint.
- `DEMO_MODE` and `RECORD` switches; sample answers are labelled "Sample data" on screen.
- Per-IP rate limit on `/demo`, `RECORD` ignored in production, generic client errors, strict
  fixture keys.
- Smoke tests: a Playwright demo-path test and five API tests.
- CI with build, smoke tests and gitleaks; `WRITEUP.md` submission template with a "what is proven"
  table.
- Theme-aware README banner designed in Figma, community files, issue forms, a pull request
  template, Dependabot and CodeQL.

### Security

- API dependencies updated: fastapi 0.143.0 and starlette 1.7.0 (starlette 0.38.6 had
  CVE-2024-47874, CVE-2025-54121 and five 2026 advisories), uvicorn 0.54.0 (h11 0.16.0 fixes
  CVE-2025-43859), pytest 9.1.1 (CVE-2025-71176). The API's outgoing call and the test client use
  httpx2, which Starlette 1.x expects.

[Unreleased]: https://github.com/Coflazo/hackathon-starter/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Coflazo/hackathon-starter/releases/tag/v1.0.0
