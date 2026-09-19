# Hermes Agent Operations: Safe Upgrades, Config Migration, and Gateway Diagnosis (2026-09-19)

> This note captures reusable methods from a cross-version upgrade and related incident diagnosis. All examples use generic domains, paths, process names, and environment variables; no live infrastructure or credentials are included.

## 1. Record version, source, working tree, and services before upgrading

Upgrade safety depends on more than the installed version. A Git installation may contain uncommitted platform adapters, scripts, or patches. Updating directly can trigger an automatic stash, merge conflicts, or silent loss of local behavior.

```bash
command -v hermes
hermes --version
hermes config path

git -C ~/.hermes/hermes-agent rev-parse --short HEAD
git -C ~/.hermes/hermes-agent status --short
git -C ~/.hermes/hermes-agent remote -v

hermes status --all
```

Keep at least two recovery layers:

1. Save `git diff` for tracked files.
2. Copy important untracked scripts to a timestamped directory outside the checkout.

```bash
backup="$HOME/hermes-preupdate-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
git -C ~/.hermes/hermes-agent diff > "$backup/local.patch"
cp ~/.hermes/hermes-agent/path/to/local-script.py "$backup/"
```

Do not rely only on the updater's automatic stash. An explicit backup remains usable if stash restoration conflicts, references move, or the checkout is reset.

## 2. A successful updater run does not prove local patches were restored

`hermes update` may fetch code, stash local changes, update Python and Node dependencies, build the Web UI, sync Skills, and then restore local changes. The last step can conflict.

After updating, verify three separate facts:

- Was the new release installed?
- Is the working tree in a known state?
- Was the local behavior restored?

```bash
hermes --version
git -C ~/.hermes/hermes-agent log -1 --oneline --decorate
git -C ~/.hermes/hermes-agent status --short
git -C ~/.hermes/hermes-agent stash list
```

If upstream heavily refactored the same file, do not blindly apply the stash and accept a large conflict. Prefer semantic porting:

1. Read the old patch and identify its behavioral contract.
2. Locate the new extension point in the updated code.
3. Reimplement the smallest equivalent change against the new structure.
4. Keep the original patch and stash until verification is complete.

This is safer than line-by-line conflict resolution for messaging adapters, Provider routing, and Gateway lifecycle code.

## 3. Config migration is part of the upgrade, but review its side effects

Run:

```bash
hermes doctor
hermes doctor --fix
hermes config check
```

`doctor --fix` may do more than bump a config version. It can adopt new defaults, enable tools, change concurrency budgets, or repair state databases. Read its output instead of treating it as an opaque repair command.

Review:

- whether the config reached the latest version;
- whether the default model and Provider stayed correct;
- whether Delegation concurrency and iteration limits fit the cost budget;
- whether newly enabled Toolsets have their dependencies;
- whether legacy `custom_providers` entries need migration to `providers`;
- whether the state database needs offline compaction.

A valid config does not prove an external Provider works. `hermes config check` validates structure, not every API key, model, or upstream account pool.

## 4. A restart command timeout does not prove restart failure

The Gateway can wait gracefully for in-flight work. The caller may time out while systemd has already completed the transition. Read actual service state:

```bash
hermes gateway restart

systemctl is-active hermes-gateway
systemctl show hermes-gateway \
  -p MainPID -p SubState -p ActiveEnterTimestamp --no-pager
journalctl -u hermes-gateway --since '-5 minutes' --no-pager
```

Reliable success criteria:

- `is-active` returns `active`;
- `SubState=running`;
- PID or activation timestamp changed;
- the new PID logged platform initialization;
- no persistent traceback or crash loop appears.

API errors printed by the old PID during shutdown should not be attributed to the new process. Always read logs with PID and time boundaries.

## 5. Reachability, authentication, and model scheduling are different layers

An OpenAI-compatible gateway being “down” should be split into at least three checks:

| Layer | Minimal check | Interpretation |
|---|---|---|
| Site/reverse proxy | `GET /` | `200` means the entry point is alive |
| API authentication | `GET /v1/models` without a key | `401` means routing is alive and authentication is enforced |
| Model scheduling | `POST /v1/chat/completions` | Only `200` proves that key, group, and model are usable |

```bash
curl -I https://gateway.example.com/
curl -o /dev/null -w '%{http_code}\n' \
  https://gateway.example.com/v1/models
```

If the homepage returns `200`, the model endpoint returns the expected `401`, but chat returns `503`, inspect account pools, API-key groups, model mappings, and cooldown state first. Logs such as `pool=0` or `no available accounts supporting model` describe scheduling configuration; restarting usually does not fix them.

## 6. Authentication “rate limiting” can be a disk-full symptom

`Too many requests` during login is not always a real rate limit. A full disk can create this chain:

```text
root filesystem reaches 100%
→ PostgreSQL cannot write WAL or temporary files
→ database enters recovery or rejects connections
→ login query fails
→ application returns a generic auth/rate-limit error
→ error logs grow rapidly and consume even more disk
```

Check dependencies before changing auth settings:

```bash
df -h /
free -h
systemctl is-active postgresql redis-server nginx
journalctl -u postgresql --since '-30 minutes' --no-pager
```

Recovery order:

1. Free clearly safe space.
2. Confirm PostgreSQL accepts connections again.
3. Retest login.
4. Verify that invalid credentials now return `401`, not `429` or `500`.
5. Fix log rotation and capacity monitoring to prevent recurrence.

Do not repeatedly reset passwords or tune rate limits while the database is unavailable.

## 7. Model health checks must distinguish “alive” from “usable”

A probe should not classify every non-`200` response as healthy:

- `400`: incompatible parameters or model;
- `401/403`: credentials, authorization, or WAF;
- `404`: missing endpoint or model;
- `429`: often temporary rate limiting and may count as “service alive” by policy;
- `5xx`: current route unavailable and should permit failover;
- connection timeout: network or upstream unavailable.

Two details often create false failures:

1. A CDN/WAF may reject default `urllib` fingerprints. Use an explicit `User-Agent` and compare with the real client.
2. After key rotation, a long-lived Gateway process may still hold the old environment value. A deterministic health script can read the current `.env` first and use process environment only as fallback.

When automation switches models, write only an environment-variable reference:

```yaml
model:
  api_key: ${EXAMPLE_GATEWAY_API_KEY}
```

Never write the resolved key back to `config.yaml`, logs, or Cron output.

## 8. Post-upgrade verification matrix

Cover at least:

```bash
# Version and source
hermes --version
git -C ~/.hermes/hermes-agent status --short

# Config and dependencies
hermes config check
hermes doctor

# Service
systemctl is-active hermes-gateway
systemctl show hermes-gateway -p MainPID -p SubState --no-pager

# Locally customized code
~/.hermes/hermes-agent/venv/bin/python -m py_compile \
  ~/.hermes/hermes-agent/path/to/modified_adapter.py

# Upstream API with a minimal, non-sensitive response
curl -o /dev/null -w '%{http_code}\n' https://gateway.example.com/
```

For local patches, run a minimal functional smoke test in addition to syntax checks. For example, a file fallback should create a temporary source file, call the publishing function, then verify the destination bytes and returned URL agree.

## One-sentence summary

A safe Hermes upgrade manages four tracks at once—upstream version, local patches, config migration, and the running service—while diagnosis separates entry point, authentication, model scheduling, and database health instead of using restarts to hide configuration or capacity failures.
