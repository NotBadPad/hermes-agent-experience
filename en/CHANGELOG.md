# Changelog

[简体中文](../CHANGELOG.md) | **English**

## [2.1.0] - 2026-09-19

### Added
- Added `05-memory/recent-agent-ops-2026-09-19.md` covering safe Hermes upgrades, semantic porting after local-patch conflicts, config migration, and Gateway restart verification.
- Added layered diagnosis for OpenAI-compatible gateway reachability, authentication, and model scheduling, plus disk-full failures disguised as auth rate limiting.
- Added health-probe rules for HTTP status classification, WAF fingerprints, and stale process environments after key rotation.

### Changed
- Updated the Chinese and English README, AGENTS, and memory indexes.

## [2.0.0] - 2026-08-12

### Added
- Added a maintained English mirror under `en/` alongside the Simplified Chinese source documents.
- Added `LOCALIZATION.md` with source-language, directory-mirroring, translation-sync, and new-language rules.
- Added `scripts/check_docs.py` to validate local Markdown links, fenced code blocks, language entry points, and English mirror coverage.
- Added a GitHub Actions workflow that runs the documentation checks on relevant pushes and pull requests.

### Changed
- Added language switching to README, AGENTS, and SECURITY.
- Reorganized navigation so human readers and AI agents can move through the same structure in either language.
- Updated the quick-start commands to match the current Hermes CLI and official installation path.

For earlier releases, see the [Simplified Chinese changelog](../CHANGELOG.md).
