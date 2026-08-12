# Lessons learned from operating Hermes Agent

[简体中文](../../05-memory/lessons-learned.md) | **English**

This page condenses recurring lessons from model configuration, specialist profiles, skills, prompts, MCP integrations, and public documentation.

## Keep responsibilities narrow

A focused profile is easier to reason about and safer to operate. Coding, finance, server operations, and marketplace operations need different tools, permissions, and failure policies. The main Hermes agent should coordinate cross-domain work and own the final user-facing answer.

## Verify providers in layers

A provider failure can come from credentials, endpoint routing, model aliases, protocol fields, rate limits, or WAF behavior. Test the smallest direct request first, then the Hermes adapter, then the full workflow. Do not treat a successful credential listing as proof that the model is visible or callable.

For custom providers, model discovery and credential pooling are separate concerns. The configuration that fills the model selector may differ from the store that rotates keys and tracks exhaustion.

## Respect protocol differences

Reasoning models may require fields such as `reasoning_content` to be returned on subsequent turns. Another OpenAI-compatible endpoint may reject the same field. Start a fresh session when switching incompatible providers, or configure a deliberate translation layer.

## Use deterministic automation for fixed checks

Disk, memory, API status, and simple model probes should use scripts when the logic is fixed. Empty stdout means normal and silent. Non-empty stdout is an actionable alert. A non-zero exit means the watchdog itself failed.

Let an LLM summarize rich input, but do not make it reinterpret a fixed threshold every hour.

## Separate execution from delivery

A scheduled job can run successfully while its message is rate-limited. Check scheduler state, stored output, silent-output rules, and platform logs separately. Never rerun a side-effecting task merely because the chat did not receive its report.

## Prompts need boundaries and evidence

Useful prompts state the goal, allowed tools, forbidden actions, expected format, and verification method. Avoid vague instructions such as "optimize it." Define a measurable outcome instead.

Do not ask agents to expose private chain-of-thought. Ask for concise rationale, assumptions, evidence, and verification results.

## Skills are software supply-chain components

Review external skills before installation. Check scripts, network access, credentials, file scope, dependencies, and obfuscated content. Version and maintain useful skills. Patch a skill when its commands or assumptions become outdated.

## Context is a budget

Load only the skills and files needed for the current task. Summarize stable decisions, keep temporary progress in the session or task list, and store only durable user preferences or environment facts in persistent memory.

## Public documentation requires a release check

Before publishing operational notes:

- replace private domains, IP addresses, account IDs, and emails;
- convert credentials to environment-variable references;
- remove raw logs that contain authorization headers or cookies;
- verify commands against current official docs;
- scan the staged diff for key-like values;
- confirm that the document belongs in this experience repository rather than a business application repo;
- check local links and fenced code blocks.

## Final rule

A plausible answer is not a completed task. Real work ends with a working artifact and fresh verification evidence.
