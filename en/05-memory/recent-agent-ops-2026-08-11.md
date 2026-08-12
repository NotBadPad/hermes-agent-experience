# Hermes Agent Operations Experience: Cron Jobs, Model Routing, and Health Checks (2026-08-11)

> This document organizes recent reusable Hermes Agent operations experience. Domains, Provider names, API Keys, task IDs, accounts, and server information in examples use generic placeholders, not containing real infrastructure or credentials.

## 1. Cron Jobs "No Message" Doesn't Mean "Not Executed"

Hermes Cron execution and message delivery are two independent phases. When troubleshooting, confirm in order:

1. Whether the scheduler triggered the task;
2. Whether output files were generated;
3. Whether output is `[SILENT]`;
4. Whether message platform delivery was rate-limited or rejected.

```bash
hermes cron list

# 查看指定任务的落盘结果
ls -la ~/.hermes/cron/output/<JOB_ID>/

# 查看执行与投递日志
grep -i '<JOB_ID>\|rate limited\|delivery error\|send failed' \
  ~/.hermes/logs/agent.log ~/.hermes/logs/errors.log | tail -50
```

Judgment criteria:

- Output file exists and task status is success: task was executed;
- Output is `[SILENT]`: task is designed to be silent, should not send messages;
- Output has content, but logs show platform rate limiting: execution successful, delivery failed;
- No output and scheduler status abnormal: then continue troubleshooting the scheduler itself.

When needing to ensure no results are lost during rate limiting, can temporarily change delivery target to local, then resend after platform recovery. Don't directly rerun tasks with side effects just because the chat window didn't receive a message.

## 2. Fixed Inspections Prioritize Deterministic Scripts

For disk, memory, interface, and model availability inspections, if judgment logic is fixed, prioritize:

- `no_agent=true`;
- Script handles complete judgment;
- Normal times stdout is empty;
- Only outputs directly deliverable alert content when abnormal;
- Non-zero exit code indicates inspection program itself is faulty.

This avoids having the model reinterpret the prompt each time, causing model aliases, parameters, or judgment thresholds to drift.

Script design recommendation:

```text
固定输入 → 执行探测 → 解析状态 →
  正常：不输出
  异常：输出告警
  程序错误：非零退出
```

Normal debug logs should be written to log files, not stdout, otherwise each round will trigger meaningless notifications.

## 3. Custom Provider "Visibility" and "Credential Pool" Are Two Mechanisms

Custom OpenAI-compatible services usually involve two independent configuration layers:

| Configuration Layer | Primary Responsibility |
|---|---|
| `custom_providers` / `model_catalog` | Define models, endpoints, and visibility in model selector |
| Credential Pool | Manage credential rotation, exhaustion status, and health records |

Common misconception: seeing credentials in `hermes auth list` assumes models will definitely appear in `/model`. In reality, with only credential pool but no model catalog configuration, the model selector may still be invisible.

`custom_providers` must be YAML list:

```yaml
custom_providers:
  - name: example-gateway
    base_url: https://gateway.example.com/v1
    api_key: ${EXAMPLE_GATEWAY_API_KEY}
    models:
      - example-model
```

Don't write as dictionary:

```yaml
# 错误示例
custom_providers:
  example-gateway:
    base_url: https://gateway.example.com/v1
```

After configuration, execute:

```bash
hermes config check
hermes auth list
```

Then open new session or restart relevant client to let model catalog reload. Public documents only keep environment variable names and example domains, don't write real Keys, gateway domains, or account group information.

## 4. Model Health Checks Must Prevent Client Fingerprinting False Failures

Certain CDN/WAF-protected OpenAI-compatible gateways reject Python `urllib` default request headers, returning 403 or similar security policy errors. At this time normal Hermes requests may succeed, but health scripts mistakenly report all models as offline.

Recommended diagnosis compares three probes:

1. `urllib` default request headers;
2. `urllib` with explicit `User-Agent`;
3. `requests` with explicit `User-Agent`.

Recommended pattern:

```python
import requests

headers = {
    "Authorization": "Bearer " + api_key,
    "Content-Type": "application/json",
    "User-Agent": "Mozilla/5.0 Hermes-ModelHealth/1.0",
}

response = requests.post(
    "https://gateway.example.com/v1/chat/completions",
    headers=headers,
    json={
        "model": "example-model",
        "messages": [{"role": "user", "content": "ping"}],
        "max_tokens": 8,
    },
    timeout=35,
)
```

Notes:

- When probing, use the raw model ID that the gateway actually accepts, don't use UI display aliases;
- Don't uniformly force `temperature`, some models only accept default values;
- If only default `urllib` returns 403, but requests with UA succeed, fix the probe, don't modify production routing;
- After fixing, both run script directly and manually trigger Cron once, reading latest disk results.

## 5. Clean Inference Fields When Switching Cross-Model Protocols

Some reasoning models return non-standard fields in historical messages, e.g., `reasoning_content`. If switching to OpenAI-compatible Providers that don't support this field in the same long session, complete history being resent may cause gateway to quickly return 400/403.

Typical characteristics:

- `/v1/models` normal;
- Minimal new conversation request normal;
- Request with old session history immediately fails;
- Failure occurs before upstream model actually reasons.

Processing order:

1. Create completely clean new session;
2. Switch to target Provider before sending message;
3. If controlling gateway, strip `reasoning_content` before forwarding to upstream that doesn't support this field;
4. Don't rotate API Key first—when Key is normal, rotating Key won't fix message format incompatibility.

Long-term solution is to do message normalization at Agent or gateway Provider boundaries, rather than relying on users to manually clean context each time.

## 6. Operations Changes Follow "Diagnose First, Then Minimal Change"

When model unavailable, Cron no message, or Gateway abnormal occurs, don't restart service as first step. Recommended order:

1. Read current configuration and task status;
2. Check disk output and logs;
3. Verify endpoint, model ID, and protocol with minimal request;
4. Modify single configuration layer or probe script;
5. Verify whether hot-reload or cache refresh is supported;
6. Only restart when confirmed no alternative;
7. Check service status and real requests again after restart.

This sequence reduces unnecessary interruptions, and avoids "temporarily recovers after restart, but root cause remains" false fixes.

## 7. Desensitization Checklist Before Public Experience Sync

Before submitting to public repository, at least check:

- API Key, Token, password, Cookie, private key;
- Real gateway domains, backend addresses, and database connection strings;
- Public/internal IPs, SSH accounts, and host lists;
- User emails, chat IDs, task IDs, and internal account groups;
- Credentials accidentally included in command output;
- Whether sensitive values already exist in Git history.

After staging, execute focused scan:

```bash
git diff --cached | grep -Ein \
  'ghp_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|password\s*[:=]|secret\s*[:=]|token\s*[:=]|api[_-]?key\s*[:=]' || true
```

After scan hits, need human judgment: security warning text and `${EXAMPLE_API_KEY}` placeholders can be kept, specific assignments, long random strings, and real auth headers must be deleted.

## Summary in One Sentence

First distinguish "execution, output, delivery" three layers, then distinguish "model catalog, credential pool, request protocol" three layers; health checks must verify the probe itself, public sync must do secondary desensitization in staging area.
