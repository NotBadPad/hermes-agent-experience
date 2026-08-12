# Recent Agent Operations Experience (2026-05-16)

> Recording a practical Hermes Agent configuration session: model routing cleanup, auxiliary model downgrade, Gateway restart investigation, Bot Street delivery, and documentation archival boundaries. This document contains only publicly reusable experience, excluding API Keys, Tokens, passwords, internal network details, or private credentials.

## 1. Removing GPT Models from Opendoor

### Background

The Opendoor provider previously retained multiple GPT model aliases for coding, writing, and image-related tasks. Later, the routing strategy was adjusted: GPT models would no longer be used through Opendoor, keeping only Claude / Gemini family models.

### Key Operations

- Delete GPT model blocks from the Opendoor provider in the main Hermes configuration.
- Synchronously search and update hardcoded model aliases in skills to prevent subsequent routing from pointing to deleted models.
- Update intelligent routing skills: switch writing/creative tasks from GPT routing to Claude Sonnet/Opus family.
- Update configuration automation skills: example models should not continue to reference deprecated GPT aliases.

### Verification Methods

```bash
# 查主配置和技能目录里是否仍有旧模型别名
grep -R "opendoor-gpt\|gpt-5\.4\|gpt-4o-image" ~/.hermes/config.yaml ~/.hermes/skills || true

# 重新读取配置，确认 opendoor 只剩目标模型
python3 - <<'PY'
import yaml
from pathlib import Path
cfg = yaml.safe_load(Path('~/.hermes/config.yaml').expanduser().read_text())
for p in cfg.get('custom_providers', []):
    if p.get('name') == 'opendoor':
        print(p)
PY
```

### Lessons Learned

Taking models offline cannot be done by only modifying `config.yaml`. If skills, routing documents, or sub-agent profiles still retain old aliases, the Agent will "resurrect" old models in subsequent tasks, causing hard-to-debug 400/404 or routing failures.

## 2. Unifying Auxiliary Models to DeepSeek

### Background

Some auxiliary tasks were automatically routed to MiMo models. MiMo's multi-turn reasoning responses include `reasoning_content`, and subsequent calls that don't properly return historical reasoning content according to the server protocol can easily trigger HTTP 400.

### Decision

Switch Hermes auxiliary model tasks uniformly to DeepSeek Flash as a stable, low-cost, Chinese-friendly background task model.

### Key Operations

Use Hermes configuration commands to uniformly set auxiliary-related items instead of manually editing multiple places:

```bash
hermes config set auxiliary.<task>.provider deepseek
hermes config set auxiliary.<task>.model deepseek-v4-flash
hermes config set auxiliary.<task>.base_url https://api.deepseek.com/v1
hermes config set auxiliary.<task>.api_key '${DEEPSEEK_API_KEY}'
```

Actual task names depend on the current Hermes configuration. After setting, restart the gateway and verify service status.

```bash
systemctl restart hermes-gateway
systemctl status hermes-gateway --no-pager
```

### Lessons Learned

- For auxiliary tasks, prioritize models that are "stable, cheap, and simple in protocol" rather than necessarily the strongest model.
- For models with special reasoning fields, confirm whether the client fully supports the multi-turn protocol.
- After configuration, read back the configuration to verify; don't just trust that the command executed successfully.

## 3. Troubleshooting Gateway "Always Restarting"

### Symptoms

User observed multiple restarts of Hermes Gateway.

### Investigation Path

```bash
systemctl status hermes-gateway --no-pager
journalctl -u hermes-gateway --since '2 hours ago' --no-pager
```

Simultaneously search for restart behavior in local scripts, cron, and systemd timers:

```bash
grep -R "restart hermes-gateway\|systemctl restart" ~/.hermes /etc/systemd/system 2>/dev/null || true
```

### Example Conclusion

The main causes identified this time were:

1. Active restarts during manual model configuration changes.
2. Model health checks triggered an automatic restart after detecting anomalies.

The service ultimately remained in active status, not continuously crashing.

### Lessons Learned

"Restarted many times" requires distinguishing between:

- Active restarts after human configuration changes;
- Automatic restarts by watchdog / health-check;
- systemd restarts due to process crashes.

The three have completely different remediation strategies.

## 4. Bot Street Task Execution and Delivery

### Current Operating Model

- Before scanning for new tasks, verify against local participation list to avoid duplicate applications.
- Upon discovering new tasks, report to the owner for confirmation first; do not automatically deduct sparks to apply.
- Tasks after being assigned can be directly executed, deliverables published, and API submitted.

### Deliverable Publishing Strategy

Prioritize platforms that are publicly accessible and low-friction:

1. `paste.rs`: Suitable for Markdown articles, one-step curl publishing.
2. GitHub repository `articles/`: Suitable for deliverables requiring long-term retention.

```bash
curl -s -X POST --data-binary @article.md https://paste.rs/
```

### Lessons Learned

- Bot Street API authentication is not Bearer Token, but `x-agent-id` + `x-agent-key` dual headers.
- `/tasks/my` only displays assigned tasks; pending review applications may not appear here.
- Task records must be kept locally: task name, status, delivery link, deliveryId, whether applied.
- If automatic checks encounter message platform rate limiting, can switch to local output to avoid noise and failed retries.

## 5. Documentation Archival Boundaries

### Background

Agent operations experience documents were mistakenly placed in business project repositories. These have since been deleted and migrated to the dedicated Hermes experience repository.

### Rules

- Business project repositories only contain business project-related code and documents.
- Agent configuration, model routing, operations experience, and platform integration experience are uniformly placed in the Hermes experience repository.
- Public repository documents must be desensitized: no API Keys, Tokens, passwords, real backend accounts, or database credentials.
- Public topology diagrams hide IPs; when displaying machine names externally, use agreed naming conventions, e.g., `JTTI-HK`.

## 6. Pre-Commit Checklist

```bash
# 1. 看暂存区
git diff --cached

# 2. 粗扫敏感信息
git diff --cached | grep -Ein 'ghp_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|password\s*[:=]|secret\s*[:=]|token\s*[:=]|api[_-]?key\s*[:=]' || true

# 3. 确认没有误改业务仓库
git remote -v
git status --short
```

## Summary in One Sentence

Model governance requires changing "configuration, skills, sub-agents, and documents" together; Agent experience should go into the Agent experience repository, don't mix it into business projects.
