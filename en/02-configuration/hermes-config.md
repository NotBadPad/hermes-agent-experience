# Hermes Configuration in Detail

[简体中文](../../02-configuration/hermes-config.md) | **English**

## Configuration Paths

```
~/.hermes/
├── config.yaml        ← Main configuration file
├── .env               ← Environment variables (API keys and other secrets)
├── auth.json          ← Authentication data
├── skills/            ← Global skills directory
├── profiles/          ← Profile directories
│   ├── <name>/
│   │   ├── config.yaml
│   │   ├── .env
│   │   └── skills/
│   └── ...
├── cron/              ← Scheduled jobs
├── logs/              ← Logs
├── sessions/          ← Session history
└── memories/          ← Persistent memory
```

## Core Fields in `config.yaml`

### Model Configuration

```yaml
model:
  default: gpt-5.5                    # Default model (example; replace as needed)
  provider: custom:gateway-example  # Self-hosted gateway provider (example name)
  base_url: https://gateway.example.com/v1
providers: {}                          # Additional provider configuration
fallback_providers: []                 # Fallback providers
```

> The gateway URL above is sanitized. For auxiliary tasks, use a stable, inexpensive model such as DeepSeek Flash. This avoids silently routing background work to models whose protocols are not fully compatible.

### Agent Behavior

```yaml
agent:
  max_turns: 90                        # Maximum turns per session
  gateway_timeout: 1800                # Gateway timeout in seconds
  verbose: false                       # Enable verbose logs
  reasoning_effort: medium             # Reasoning effort (low/medium/high)
  tool_use_enforcement: auto           # Tool-use policy
```

### Toolsets

```yaml
toolsets:
- hermes-cli                           # CLI tools
# Profiles can add more toolsets
platform_toolsets:
  cli:
  - hermes-cli
  telegram:
  - hermes-telegram
  discord:
  - hermes-discord
```

### Terminal Configuration

```yaml
terminal:
  backend: local                        # Terminal backend (local/docker/ssh)
  cwd: .                                # Default working directory
  timeout: 180                          # Command timeout in seconds
  auto_source_bashrc: true              # Automatically source bashrc
```

### Memory

```yaml
memory:
  memory_enabled: true                  # Enable persistent memory
  user_profile_enabled: true            # Enable the user profile
  memory_char_limit: 2200               # Memory character limit
  user_char_limit: 1375                 # User-profile character limit
```

### Profile Configuration

A profile lives at `~/.hermes/profiles/<name>/config.yaml`. It uses the same structure as the main configuration, but normally contains only profile-specific overrides:

```yaml
model:
  default: gpt-5.5                      # Model used by this profile (example)
  provider: custom:gateway-example
  base_url: https://gateway.example.com/v1
  api_key: ${GATEWAY_API_KEY}
toolsets:
- hermes-cli
- terminal
- file
agent:
  max_turns: 90
display:
  personality: technical
memory:
  memory_enabled: true
  user_profile_enabled: false
```

Create and inspect profiles with `hermes profile create <name>` and `hermes profile show <name>` rather than creating profile directories by hand.

### Custom Model Providers

```yaml
custom_providers:
- name: mimo-v2.5-pro
  base_url: https://token-plan-sgp.xiaomimimo.com/v1
  api_key: ${XIAOMI_API_KEY}
  api_mode: chat_completions
  model: mimo-v2.5-pro
- name: opendoor
  base_url: https://ai.opendoor.cn/v1
  api_key: ${OPENDOOR_API_KEY}
  api_mode: chat_completions
  # Current policy: do not retain GPT-family aliases under OpenDoor; keep only Claude/Gemini routes.
```

`custom_providers` must be a YAML list, as shown above. Use environment-variable references for keys and keep the actual values in `~/.hermes/.env`.

### MCP Server Configuration

```yaml
mcp_servers:
  vibe-trading:
    command: vibe-trading-mcp
```

You can also manage MCP servers with `hermes mcp add`, `hermes mcp list`, `hermes mcp test`, and `hermes mcp remove`.

### Key Settings at a Glance

| Setting | Description | Default |
|---------|-------------|---------|
| `model.default` | Default model name | — |
| `model.provider` | Model provider | — |
| `agent.max_turns` | Maximum conversation turns | 90 |
| `agent.reasoning_effort` | Reasoning effort | medium |
| `terminal.backend` | Terminal backend | local |
| `terminal.cwd` | Working directory | . |
| `memory.memory_enabled` | Enable memory | true |
| `memory.memory_char_limit` | Memory limit | 2200 |
| `display.personality` | Response style | — |

Use `hermes config edit` to edit the active configuration, `hermes config set KEY VALUE` for individual values, and `hermes config check` to detect missing or outdated settings. For the authoritative current schema, see the [Hermes configuration documentation](https://hermes-agent.nousresearch.com/docs/user-guide/configuration).
