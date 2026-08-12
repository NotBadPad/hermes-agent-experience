# Quick Start

[简体中文](../../01-quick-start/README.md) | **English**

## Install Hermes

```bash
# Linux / macOS / WSL2 / Android (Termux)
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# Show version information
hermes --version
```

For Windows and Hermes Desktop, use the [official installation guide](https://hermes-agent.nousresearch.com/docs/getting-started/installation).

## Initial Setup

```bash
# Run the setup wizard
hermes setup

# Or create the base configuration directory manually
mkdir -p ~/.hermes
```

## Configure a Model Provider

### Choose a provider interactively

```bash
# Select and configure the provider and model interactively
hermes model
```

You can also run `hermes setup model`. Store API keys in `~/.hermes/.env`, never in the repository.

### OpenAI-Compatible Endpoint

```yaml
# config.yaml
model:
  default: your-model
  provider: custom
  base_url: https://your-api-endpoint/v1
  api_key: ${YOUR_API_KEY_ENV}
```

## Create Your First Profile

Hermes profiles are isolated instances with their own configuration, sessions, skills, and memory. Use the CLI to create the profile before editing its configuration.

```bash
# Create a profile
hermes profile create my-agent

# Open the profile directory, then edit its generated config.yaml as needed
cd ~/.hermes/profiles/my-agent

# Verify the profile
hermes profile list
```

## Common Commands

```bash
hermes chat -q "Your message"        # Ask a one-off question
hermes profile use my-agent          # Make the profile active
hermes                              # Start Hermes with the active profile
hermes gateway start                 # Start the Gateway service
hermes gateway status                # Check Gateway status
hermes update                        # Update Hermes
hermes model                         # Switch models
hermes profile list                  # List all profiles
```

## Managing Environment Variables

Store all secrets in the `.env` file or in system environment variables:

```bash
# ~/.hermes/.env
DEEPSEEK_API_KEY=<YOUR_DEEPSEEK_API_KEY>
OPENAI_API_KEY=<YOUR_OPENAI_API_KEY>
XIAOMI_API_KEY=<YOUR_XIAOMI_API_KEY>
```

> **Important:** Add `.env` to `.gitignore` and never commit it to the repository.
