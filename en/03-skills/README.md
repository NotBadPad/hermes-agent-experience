# 🛠️ Hermes Skills

[简体中文](../../03-skills/README.md) | **English**

> A skill is a reusable procedure that gives Hermes specialized instructions, workflows, and domain knowledge. Toolsets provide callable tools, while skills teach the agent when and how to use its capabilities. This section documents the repository's capability organization, imported skills, and conventions for writing custom skills.

---

## Contents

- [Overview](#overview)
- [Core Capability Layers](#core-capability-layers)
- [Imported Skills (addyosmani/agent-skills)](#imported-skills)
- [Skill Structure](#skill-structure)
- [Writing a Custom Skill](#writing-a-custom-skill)
- [Best Practices](#best-practices)

---

## Overview

This repository organizes Hermes capabilities in layers:

```
Capabilities
├── General toolsets (available across sessions when enabled)
│   ├── terminal           — Command execution and filesystem operations
│   ├── file               — File reading, writing, and search
│   ├── web                — Web requests and extraction
│   └── memory             — Persistent memory access
│
├── Platform integrations (enabled for each connected platform)
│   ├── hermes-cli         — CLI interaction
│   ├── hermes-telegram    — Telegram
│   ├── hermes-discord     — Discord
│   └── hermes-wechat      — WeChat
│
├── Role-specific skills (enabled per profile)
│   ├── code-engineer      — Software development (Xiao Kai)
│   ├── financial-analysis — Financial analysis (Xiao Fu)
│   ├── server-ops         — Operations management (Xiao Yun)
│   └── bot-street         — Bot operations (botstreet)
│
└── Imported skills (22 imported from addyosmani/agent-skills on 2026-05-11)
    ├── Xiao Kai: 17 development skills (API design, code review, TDD, debugging, ...)
    ├── Xiao Yun: 2 operations skills (CI/CD and release management)
    └── Main agent: 3 general skills (context engineering, skill use, and idea refinement)
```

Toolsets and messaging adapters are not themselves Agent Skills in current Hermes terminology, but they form the runtime capability layers on which the skills in this repository depend.

### Skill Resolution

When skills with the same name exist in multiple locations, the more specific profile or user copy should take precedence over a more general installed copy. Keep names unique where possible and use `hermes skills list` and `hermes skills config` to inspect what is installed and enabled.

---

## Core Capability Layers

### 1. `terminal` — Command Execution

| Property | Value |
|----------|-------|
| Type | General toolset |
| Enabled by default | ✅ Yes |
| Purpose | Run shell commands and scripts; install dependencies |

---

### 2. `file` — File Operations

| Property | Value |
|----------|-------|
| Type | General toolset |
| Enabled by default | ✅ Yes |
| Purpose | Read and write files, search content, and manage directories |

---

### 3. `web` — Web Access

| Property | Value |
|----------|-------|
| Type | General toolset |
| Enabled by default | ✅ Yes |
| Purpose | Make HTTP requests, extract web content, and call APIs |

---

### 4. `memory` — Persistent Memory

| Property | Value |
|----------|-------|
| Type | General toolset |
| Enabled by default | ✅ Yes (can be disabled) |
| Purpose | Save and retrieve information across sessions |

---

### 5. `hermes-cli` — CLI Integration

| Property | Value |
|----------|-------|
| Type | Platform capability |
| Enabled by default | ✅ Yes in CLI mode |
| Purpose | Command-line input/output and pipeline handling |

---

### 6. Messaging Integrations

| Platform | Repository label | Description |
|----------|------------------|-------------|
| Telegram | `hermes-telegram` | Messaging, bot commands, and group handling |
| Discord | `hermes-discord` | Channel messages and slash commands |
| WeChat | `hermes-wechat` | WeChat message handling |

In current Hermes, configure messaging adapters through `hermes gateway setup`; these labels describe the repository's organization rather than skill packages installed through `hermes skills`.

---

## Imported Skills

### Source: [addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)

On 2026-05-11, 22 production engineering skills were imported from this repository and assigned by agent role.

### 🐉 Xiao Kai (Coding Specialist) — 17 Skills

| Skill | Description | Size |
|:------|:------------|:----:|
| `api-and-interface-design` | API and interface design guidance | 10K |
| `browser-testing-with-devtools` | Browser testing with DevTools | 12K |
| `code-review-and-quality` | Multi-axis code review | 14K |
| `code-simplification` | Code simplification and refactoring | 13K |
| `debugging-and-error-recovery` | Systematic root-cause debugging | 10K |
| `deprecation-and-migration` | Deprecation and migration management | 9K |
| `doubt-driven-development` | Doubt-driven development (high value) | **16K** |
| `frontend-ui-engineering` | Production-grade frontend UI engineering | 11K |
| `git-workflow-and-versioning` | Git workflow best practices | 10K |
| `incremental-implementation` | Incremental implementation strategy | 9K |
| `performance-optimization` | Performance-optimization methodology | 11K |
| `planning-and-task-breakdown` | Task breakdown and planning | 7K |
| `security-and-hardening` | Security hardening practices | 11K |
| `source-driven-development` | Source-driven development | 8K |
| `spec-driven-development` | Specification-driven development | 8K |
| `documentation-and-adrs` | Documentation and architecture decision records | 9K |
| `test-driven-development` | Test-driven development (merged edition) | — |

### 🛠️ Xiao Yun (Operations) — 2 Skills

| Skill | Description | Size |
|:------|:------------|:----:|
| `ci-cd-and-automation` | CI/CD automation pipelines | 11K |
| `shipping-and-launch` | Production releases and launches | 10K |

### 🧠 Main Hermes — 3 Skills

| Skill | Description | Size |
|:------|:------------|:----:|
| `context-engineering` | Context engineering and optimization | 11K |
| `using-agent-skills` | Skill discovery and invocation | 9K |
| `idea-refine` | Structured idea refinement | 8K |

### Notable Skills

- 🔥 **`doubt-driven-development`** — subjects each non-trivial decision to adversarial review to reduce hallucinations
- 🔥 **`code-review-and-quality`** — provides a more systematic, multi-axis code-review process
- 🔥 **`context-engineering`** — improves context management and reduces agent hallucinations

---

## Skill Structure

### Directory Convention

Each skill is a standalone directory under `skills/`:

```
skills/
└── <skill-name>/
    └── SKILL.md             ← Skill definition, including YAML frontmatter
```

### `SKILL.md` Format

```yaml
---
name: my-skill
description: "Skill description"
version: 1.0.0
---

# Skill Name

## Overview
Summary

## When to Use
Trigger conditions

## Steps
Execution steps
```

---

## Writing a Custom Skill

### Quick Creation

From an agent session with the skill-management tool available:

```bash
# Use the skill_manage tool
skill_manage(action='create', name='my-skill', content='...', category='devops')

# Or create the directory manually
mkdir -p ~/.hermes/skills/category/my-skill/
```

For hub-managed skills, the current CLI also supports discovery and installation through `hermes skills search`, `hermes skills inspect`, and `hermes skills install`.

### Writing Guidelines

1. **YAML frontmatter** — must include `name` and `description`.
2. **Trigger conditions** — define them clearly under `## When to Use`.
3. **Execution steps** — make them concrete and executable, with command examples.
4. **Known pitfalls** — record common problems under `## Pitfalls`.
5. **Verification** — explain how to confirm that the procedure succeeded.

---

## Best Practices

### 1. Keep Skills Focused

- A skill should do one thing and have a single responsibility.
- Do not mix unrelated workflows into one skill.

### 2. Isolate Profile-Specific Skills

- Load only skills relevant to each profile's role.
- A coding profile should not load financial-analysis skills unless the task requires them.
- Control skill availability per platform with `hermes skills config`, and use profile-local skill directories for role-specific isolation.

### 3. Maintain Skills

- If a problem appears while using a skill, patch it immediately with `skill_manage(action='patch')` from an agent session.
- An outdated skill is a liability, not an asset.
- Review skill content regularly to ensure it remains accurate.

---

## Skills Directory in This Repository

```
03-skills/
└── README.md                ← This document
```

> The actual runtime skill files live under `~/.hermes/skills/`. This document records the skill system and authoring conventions; it does not contain the runtime files.
