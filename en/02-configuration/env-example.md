# Environment-Variable Template

[简体中文](../../02-configuration/env-example.md) | **English**

> Copy this template to `.env`, then replace every placeholder with the real value.

## Required

```bash
# DeepSeek API (v4-series models are recommended)
DEEPSEEK_API_KEY=«redacted:sk-…»

# OpenDoor API (access to GPT, Claude, and other models)
OPENDOOR_API_KEY=<YOUR_OPENDOOR_API_KEY>
```

## Optional

```bash
# Xiaomi MiMo API (for the mimo-v2.5-pro model)
XIAOMI_API_KEY=<YOUR_XIAOMI_API_KEY>

# Kimi API
KIMI_API_KEY=<YOUR_KIMI_API_KEY>

# Anthropic API (direct Claude access)
ANTHROPIC_API_KEY=«redacted:sk-…»

# GitHub token (for repository operations)
# Format: https://username:token@github.com

# Bot Street credentials
BOTSTREET_AGENT_ID=your-agent-id
BOTSTREET_AGENT_KEY=your-agent-key
BOTSTREET_BOT_NAME=your-bot-name
BOTSTREET_API_BASE=https://botstreet.io/api/v1

# Xia345
XIA345_API_BASE=https://xia345.com

# Gemini API
GEMINI_API_KEY=<YOUR_GEMINI_API_KEY>
GOOGLE_API_KEY=<YOUR_GOOGLE_API_KEY>
```

## Recommended `.gitignore`

```gitignore
# Environment variables
.env
*.env

# Keys and authentication data
*.key
*.pem
auth.json
credentials.json

# Dependencies
node_modules/
__pycache__/
*.pyc

# Build artifacts
dist/
build/

# Databases
*.db
*.sqlite

# Logs
*.log

# System files
.DS_Store
Thumbs.db
```

## Security Recommendations

1. **Never** commit `.env` to Git.
2. Reference secrets as `${VAR_NAME}` instead of hard-coding values.
3. Rotate API keys regularly.
4. Use separate keys for separate environments, such as development and production.
5. For GitHub, use a fine-grained personal access token with only the permissions required.
