# Localization guide

[简体中文 / Source policy](../LOCALIZATION.md) | **English**

Simplified Chinese is the source language. English is maintained in the mirrored `en/` tree.

## Structure

```text
README.md                 Chinese entry point
AGENTS.md                 Chinese agent entry point
en/README.md              English entry point
en/AGENTS.md              English agent entry point
<module>/<document>.md    Chinese source
en/<module>/<document>.md English translation
```

Keep filenames and relative paths aligned across languages.

## Update rules

1. Update the Chinese source first.
2. Update the matching English file in the same pull request whenever possible.
3. Keep commands, paths, environment variables, API fields, model IDs, and product names exact.
4. Translate meaning and technical intent, not sentence shape.
5. Preserve redactions and placeholders.
6. Run `python3 scripts/check_docs.py` before committing.

## Adding another language

Create a top-level directory using an IETF-style code such as `ja`, `ko`, or `es`. Mirror the maintained tree and add the new language to both README entry points and the language-status table in the source policy.

A new language should start with a root README, an agent entry point, quick start, configuration overview, security policy, and a visible list of untranslated documents.
