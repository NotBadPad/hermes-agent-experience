# Hermes Agent Experience

[简体中文](../README.md) | **English**

A field-tested knowledge base for configuring and operating Hermes Agent. It covers setup, model providers, skills, specialist profiles, memory practices, integrations, and lessons learned from real deployments.

## Repository map

```text
hermes-agent-experience/
├── README.md              Chinese entry point
├── AGENTS.md              Chinese entry point for AI agents
├── LOCALIZATION.md        Translation policy and status
├── en/                    English documentation mirror
│   ├── README.md
│   ├── AGENTS.md
│   └── 01-quick-start/ ... 07-tips/
│
├── 01-quick-start/        Installation and first setup
├── 02-configuration/      Hermes configuration and environment templates
├── 03-skills/             Skill system and authoring notes
├── 04-sub-agents/         Specialist profiles and collaboration patterns
├── 05-memory/             Operational notes and lessons learned
├── 06-integrations/       External platform integrations
└── 07-tips/               Practical usage patterns
```

## Who this is for

- New Hermes users who want a practical starting point
- Agent developers building skills and specialist profiles
- Operators connecting Hermes to external platforms and services
- Teams that want reusable runbooks instead of one-off chat history

## Start here

| Topic | Document |
|---|---|
| Install and configure Hermes | [Quick start](01-quick-start/README.md) |
| Understand the main config | [Configuration](02-configuration/README.md) |
| Build and maintain skills | [Skills](03-skills/README.md) |
| Design specialist agents | [Sub-agents](04-sub-agents/xiao-kai/README.md) |
| Reuse operational lessons | [Memory and field notes](05-memory/README.md) |
| Connect external platforms | [Integrations](06-integrations/README.md) |
| Improve reliability and safety | [Tips and best practices](07-tips/README.md) |

## Recent field notes

- [Hermes operations: cron delivery, providers, and health checks](05-memory/recent-agent-ops-2026-08-11.md)
- [AI video generation: reference character to storyboard and video](05-memory/ai-video-generation-2026-07-08.md)
- [Server IP drift and monitoring-agent rebind](05-memory/recent-agent-ops-2026-07-05.md)
- [Model routing, gateway recovery, and platform delivery](05-memory/recent-agent-ops-2026-05-16.md)

## Language policy

Simplified Chinese is the source language. English is maintained in the mirrored `en/` tree. See the [English localization guide](LOCALIZATION.md) or the [source policy](../LOCALIZATION.md) for update rules and instructions for adding another language.

## Security

All examples are sanitized. IP addresses, private domains, credentials, personal email addresses, and internal identifiers must be replaced with placeholders or environment-variable references. Read the [security policy](SECURITY.md) before copying configuration examples.

## License

MIT. Reuse the material, adapt it to your environment, and send improvements back when useful.
