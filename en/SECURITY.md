# Security and redaction

[简体中文](../SECURITY.md) | **English**

Every configuration example in this repository must be safe to publish. Do not copy live credentials or private infrastructure details into documentation.

## Replace these placeholders before local use

| Placeholder | Meaning |
|---|---|
| `YOUR_API_KEY` | Your local API key, stored outside Git |
| `SERVER_IP` | Your server address |
| `example.com` | Your domain |
| `your-agent-id` | An identifier issued by an external platform |

## Never commit

- `.env` files;
- API keys, access tokens, passwords, or session secrets;
- SSH private keys, TLS private keys, or certificate bundles containing private material;
- browser cookies or exported sessions;
- private authentication JSON files;
- private IP addresses, internal hostnames, or personal email addresses unless the repository explicitly requires and approves them.

## Safe configuration pattern

```yaml
model:
  api_key: ${PROVIDER_API_KEY}
  base_url: https://api.example.com/v1
```

```bash
# Store locally in ~/.hermes/.env, not in this repository.
PROVIDER_API_KEY=replace-me-locally
```

## Review checklist

- [ ] Credentials are environment-variable references, not concrete values.
- [ ] IP addresses and domains are public examples or placeholders.
- [ ] Personal email addresses and internal identifiers are absent.
- [ ] Logs and screenshots do not expose tokens, authorization headers, or cookies.
- [ ] `.env`, keys, certificates, and session exports are ignored by Git.
- [ ] The staged diff has been scanned before commit.

A focused staged-diff scan:

```bash
git diff --cached | grep -Ein 'ghp_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|password\s*[:=]|secret\s*[:=]|token\s*[:=]|api[_-]?key\s*[:=]' || true
```

A match is a reason to inspect the line, not automatic proof of a leak. Safe placeholders and explanatory prose are allowed; real assigned values are not.
