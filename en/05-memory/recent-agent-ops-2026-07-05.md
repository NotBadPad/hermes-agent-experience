# 2026-07-05 Hermes Operations Experience: Server IP Drift and NodeLite Agent Rebind

> Directory: `05-memory/`
> Topics: Server asset information updates, SSH key redeployment, NodeLite offline node troubleshooting
> Security: This document only records methods and desensitized topology, not passwords, tokens, private keys, or complete sensitive configurations.

## Background

A server already managed by Hermes changed its public IP. SSH aliases and Agent memory still pointed to the old IP, and the node showed offline in the NodeLite dashboard.

This experience applies to:

- After VPS reinstallation / migration / public IP change, Hermes can still connect to the old address or cannot log in passwordlessly.
- NodeLite dashboard shows node offline, but the target machine's network is normal.
- NodeLite Agent logs show `server notice unauthorized`.
- NodeLite Server logs show `websocket authentication rejected ... error=Unauthorized`.

## Processing Order

### 1. Update Basic Connection Information First

Don't immediately assume the service is broken; first confirm basic reachability of the new IP:

```bash
nc -zv -w 5 <NEW_IP> 22 2>&1
ping -c 2 -W 3 <NEW_IP>
```

If port 22 and ping both work, then update the `HostName` for the corresponding alias in your local SSH config.

```sshconfig
Host <node-alias>
    HostName <NEW_IP>
    User root
    Port 22
    IdentityFile ~/.ssh/<fleet-key>
    StrictHostKeyChecking accept-new
```

Then test key login:

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 <node-alias> 'hostname'
```

### 2. If New Machine Only Allows Password Login, Redeploy Fleet Key

Typical symptom:

```text
Permission denied (password).
```

First confirm login and host identity with password, then deploy public key:

```bash
sshpass -p '<PASSWORD>' ssh \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -o StrictHostKeyChecking=accept-new \
  root@<NEW_IP> 'echo PASS_OK; hostname; mkdir -p ~/.ssh && chmod 700 ~/.ssh'

sshpass -p '<PASSWORD>' ssh-copy-id -f \
  -i ~/.ssh/<fleet-key>.pub \
  -o PreferredAuthentications=password \
  -o PubkeyAuthentication=no \
  -o StrictHostKeyChecking=accept-new \
  root@<NEW_IP>
```

Many new VPSs disable public key login by default; check and fix:

```bash
sshpass -p '<PASSWORD>' ssh root@<NEW_IP> \
  'grep -n "^PubkeyAuthentication" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null || true'
```

If you see:

```text
PubkeyAuthentication no
```

Change to yes and restart sshd:

```bash
sshpass -p '<PASSWORD>' ssh root@<NEW_IP> \
  'sed -i "s/^PubkeyAuthentication no/PubkeyAuthentication yes/" /etc/ssh/sshd_config && systemctl restart sshd || systemctl restart ssh'
```

Finally verify:

```bash
ssh -o BatchMode=yes <node-alias> 'echo SSH_KEY_OK; hostname; nproc; free -h | grep Mem; df -h / | tail -1'
```

### 3. When NodeLite is Offline, First Check Both Agent and Server Logs

Target node side:

```bash
ssh <node-alias> 'systemctl status nodelite-agent --no-pager || true'
ssh <node-alias> 'journalctl -u nodelite-agent -n 80 --no-pager'
ssh <node-alias> 'curl -skI --connect-timeout 8 https://<nodelite-domain>/ | head -5'
```

NodeLite Server side:

```bash
systemctl status nodelite-server --no-pager || true
journalctl -u nodelite-server -n 120 --no-pager | grep -Ei '<node-id>|<NEW_IP>|websocket|unauthorized|rejected|agent'
```

If Agent side shows:

```text
server notice unauthorized
agent session ended; retrying after backoff
```

Server side shows:

```text
websocket authentication rejected client_ip=<NEW_IP> requested_node_id=<node-id> error=Unauthorized
websocket client disconnected reason=unauthorized
```

The conclusion is not a network failure, but rather: the Agent is connecting to the dashboard, but the local token doesn't match the server registry token. Common after machine reinstallation, configuration restore, node re-registration, or IP drift with old configuration reused.

### 4. Generate New Install Session and Rebind Agent with Full Token

Generate new install session on NodeLite Server:

```bash
/usr/local/bin/nodelite-server \
  --config /opt/nodelite/config/server.toml \
  install-agent \
  --node-id <node-id> \
  --node-label '<node-label>'
```

Note: The one-click install command printed by the command may have the token truncated. Don't directly copy the `***` or ellipsis version. Read the full token:

```bash
python3 - <<'PY'
import json
p='/opt/nodelite/config/server.json'
data=json.load(open(p))
s=data['install_sessions'][-1]
print('node_id=', s.get('node_id'))
print('expires_at=', s.get('expires_at'))
print('token=', s.get('token'))
PY
```

Then bootstrap/install on the target node:

```bash
ssh <node-alias> "curl -fsSL 'https://<nodelite-domain>/install/install-agent.sh' -o /tmp/nodelite-install-agent.sh && chmod +x /tmp/nodelite-install-agent.sh && NODELITE_AGENT_INSTALL_TOKEN='<FULL_TOKEN>' /tmp/nodelite-install-agent.sh --bootstrap-url 'https://<nodelite-domain>/install/bootstrap' --base-url 'https://github.com/XiNian-dada/NodeLite/releases/latest/download'"
```

### 5. Verify Online Status

Target node side should show:

```text
server notice authenticated
```

Server side should show:

```text
node authenticated node_id=<node-id> node_label=<node-label>
recorded agent runtime log entries node_id=<node-id>
```

If public `/api/nodes` is blocked by 2FA or dashboard auth, you can directly read the snapshot on NodeLite Server:

```bash
python3 - <<'PY'
import json
p='/opt/nodelite/data/snapshot.json'
data=json.load(open(p))
nodes=data.get('nodes', data) if isinstance(data, dict) else data
for n in nodes:
    ident=n.get('identity', {})
    if ident.get('node_id') == '<node-id>':
        print(json.dumps({
            'node_id': ident.get('node_id'),
            'label': ident.get('node_label'),
            'online': n.get('online'),
            'remote_ip': n.get('remote_ip'),
            'last_seen': n.get('last_seen'),
            'latency_ms': n.get('latency_ms'),
        }, ensure_ascii=False, indent=2))
PY
```

Expected result:

```json
{
  "node_id": "<node-id>",
  "online": true,
  "remote_ip": "<NEW_IP>"
}
```

## Key Indicators

| Symptom | Real Meaning | Action |
|---|---|---|
| SSH port open but key login fails | New machine doesn't have fleet key, or sshd disables public key login | Deploy public key with password, check `PubkeyAuthentication` |
| NodeLite Agent running but dashboard offline | Cannot rely solely on systemd active | Check both Agent/Server logs |
| `server notice unauthorized` | Agent connected to server but token mismatch | Regenerate install session and rebind |
| `/api/nodes` returns 2FA page | Dashboard/API access path affected by interactive auth | Verify with server local snapshot and journal |
| Docker netns `statvfs` warning | Agent skips Docker namespace pseudo-mounts when collecting disk | Usually doesn't affect node online status, can temporarily ignore |

## Security Notes

- Don't write root passwords, install tokens, or private keys into documents or memory.
- When recording experience, only keep node aliases, generalized commands, and judgment methods.
- One-click install tokens have expiration dates; generate on-site, use on-site, don't archive after use.
- Documentation repositories can record "how to troubleshoot," don't record "directly copyable real credentials."

## Retrospective

This NodeLite offline incident was not network unreachable, nor was the service process not running, but token mismatch. The most time-saving troubleshooting path is:

```text
连通性 → SSH key → agent systemd → agent 日志 → server 日志 → fresh install session → snapshot 验证
```

When encountering "NodeLite offline after new IP" in the future, prioritize searching server logs for:

```text
websocket authentication rejected
requested_node_id=<node-id>
error=Unauthorized
```

Seeing these signals, directly proceed to "rebind agent," don't go in circles around Nginx, DNS, or ports.
