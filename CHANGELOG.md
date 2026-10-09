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

[Unreleased]: https://github.com/Coflazo/hackathon-starter/compare/v1.0.0...HEAD
[1.0.0]: https://github.com/Coflazo/hackathon-starter/releases/tag/v1.0.0
