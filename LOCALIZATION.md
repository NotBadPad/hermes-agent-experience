# Localization guide

This repository uses Simplified Chinese as the source language and English as the first maintained translation.

## Language layout

```text
README.md                 Chinese entry point
AGENTS.md                 Chinese agent entry point
en/README.md              English entry point
en/AGENTS.md              English agent entry point
<module>/<document>.md    Chinese source document
en/<module>/<document>.md English translation
```

The English tree mirrors the Chinese tree. Keep filenames and relative paths aligned so readers and agents can switch languages without learning a second structure.

## Translation status

| Language | Code | Status | Entry point |
|---|---|---|---|
| 简体中文 | `zh-CN` | Source language | [`README.md`](README.md) |
| English | `en` | Maintained | [`en/README.md`](en/README.md) |

## Maintenance rules

1. Update the Chinese source first when facts or procedures change.
2. Update the matching English file in the same pull request whenever possible.
3. Keep commands, paths, environment-variable names, API fields, and model IDs unchanged unless the translated document explains a platform-specific difference.
4. Translate prose for meaning rather than word for word. Keep the tone direct and technical.
5. Do not translate product names, project names, code identifiers, or public API names.
6. Preserve security redactions. Never replace placeholders with real infrastructure details or credentials.
7. If a translation temporarily falls behind, add a visible notice at the top linking to the newer source document.

## Adding another language

Use an IETF-style language code such as `ja`, `ko`, or `es` as the top-level directory name. Mirror the maintained document tree and add the language to the table above and to both repository entry points.

A new language does not need to translate every archived field note on day one, but it must include:

- a root README;
- an agent entry point;
- quick start;
- configuration overview;
- security policy;
- a translation-status page listing gaps.

## Verification

Run the documentation checks before committing:

```bash
python3 scripts/check_docs.py
```

The checker validates local Markdown links, balanced fenced code blocks, required language entry points, and English mirror coverage.
