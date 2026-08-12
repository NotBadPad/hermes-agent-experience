# AGENTS.md — Hermes Agent Experience

[简体中文](../AGENTS.md) | **English**

This file is the short entry point for AI agents working with this repository.

## Repository purpose

This repository records practical Hermes Agent configuration, skills, specialist-profile design, external integrations, and operational lessons. Treat it as a reusable field guide, not as the live runtime configuration of any specific machine.

## Navigation

- Start with [`README.md`](README.md)
- Setup instructions: [`01-quick-start/`](01-quick-start/)
- Configuration: [`02-configuration/`](02-configuration/)
- Skills: [`03-skills/`](03-skills/)
- Specialist profiles: [`04-sub-agents/`](04-sub-agents/)
- Operational notes: [`05-memory/`](05-memory/)
- Integrations: [`06-integrations/`](06-integrations/)
- Reliability and usage tips: [`07-tips/`](07-tips/)

## Documentation rules

1. Simplified Chinese is the source language. The English tree mirrors it.
2. Keep commands, paths, API fields, environment-variable names, and model IDs exact.
3. Never add real credentials, private IP addresses, private domains, internal account IDs, or personal email addresses.
4. Verify current Hermes commands against the official documentation before changing setup procedures.
5. Record durable reasoning and runbooks. Do not dump raw memory files or transient task logs.
6. When a Chinese source document changes, update its English mirror in the same change whenever possible.
7. Run `python3 scripts/check_docs.py` before committing.

## Collaboration pattern documented here

The example setup separates responsibilities into focused profiles:

- coding and software delivery;
- market and financial research;
- server operations;
- platform and task-market operations;
- general coordination by the main Hermes agent.

These names and model choices are examples from one deployment. Readers should choose models, permissions, and toolsets that fit their own environment.

## High-value field notes

- [`05-memory/recent-agent-ops-2026-08-11.md`](05-memory/recent-agent-ops-2026-08-11.md): separating cron execution, stored output, and message delivery; deterministic watchdogs; custom-provider visibility; credential pools; WAF false negatives; cross-model protocol fields; public redaction.
- [`05-memory/ai-video-generation-2026-07-08.md`](05-memory/ai-video-generation-2026-07-08.md): reference-character extraction, storyboard generation, segmented image-to-video, frame checks, and audio mixing.
- [`05-memory/recent-agent-ops-2026-07-05.md`](05-memory/recent-agent-ops-2026-07-05.md): SSH recovery after IP drift and monitoring-agent token rebind.

For localization policy, read [`../LOCALIZATION.md`](../LOCALIZATION.md).
