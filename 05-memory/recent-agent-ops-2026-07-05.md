# 2026-07-05 Hermes 运维经验：服务器 IP 漂移与 NodeLite Agent 重绑

> 目录：`05-memory/`
> 主题：服务器资产信息更新、SSH key 重新部署、NodeLite 离线节点排查
> 安全：本文只记录方法和脱敏拓扑，不记录密码、token、私钥或完整敏感配置。

## 背景

一台已纳入 Hermes 管理的服务器更换了公网 IP。SSH 别名和 Agent 记忆仍指向旧 IP，NodeLite 面板中该节点显示离线。

本次经验适用于：

- VPS 重装 / 迁移 / 更换公网 IP 后，Hermes 还能连旧地址或无法免密登录。
- NodeLite 面板节点离线，但目标机器本身网络正常。
- NodeLite Agent 日志出现 `server notice unauthorized`。
- NodeLite Server 日志出现 `websocket authentication rejected ... error=Unauthorized`。

## 处理顺序

### 1. 先更新基础连接信息

不要直接认为服务坏了，先确认新 IP 的基础可达性：

```bash
nc -zv -w 5 <NEW_IP> 22 2>&1
ping -c 2 -W 3 <NEW_IP>
```

若 22 端口和 ping 都通，再更新本机 SSH config 中对应别名的 `HostName`。

```sshconfig
Host <node-alias>
    HostName <NEW_IP>
    User root
    Port 22
    IdentityFile ~/.ssh/<fleet-key>
    StrictHostKeyChecking accept-new
```

然后测试 key 登录：

```bash
ssh -o BatchMode=yes -o ConnectTimeout=8 <node-alias> 'hostname'
```

### 2. 如果新机器只允许密码登录，重新部署 fleet key

典型现象：

```text
Permission denied (password).
```

先用密码确认登录和主机身份，再部署公钥：

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

很多新 VPS 默认禁用公钥登录，需要检查并修复：

```bash
sshpass -p '<PASSWORD>' ssh root@<NEW_IP> \
  'grep -n "^PubkeyAuthentication" /etc/ssh/sshd_config /etc/ssh/sshd_config.d/*.conf 2>/dev/null || true'
```

如看到：

```text
PubkeyAuthentication no
```

改为 yes 并重启 sshd：

```bash
sshpass -p '<PASSWORD>' ssh root@<NEW_IP> \
  'sed -i "s/^PubkeyAuthentication no/PubkeyAuthentication yes/" /etc/ssh/sshd_config && systemctl restart sshd || systemctl restart ssh'
```

最后验证：

```bash
ssh -o BatchMode=yes <node-alias> 'echo SSH_KEY_OK; hostname; nproc; free -h | grep Mem; df -h / | tail -1'
```

### 3. NodeLite 离线时先看 Agent 和 Server 双侧日志

目标节点侧：

```bash
ssh <node-alias> 'systemctl status nodelite-agent --no-pager || true'
ssh <node-alias> 'journalctl -u nodelite-agent -n 80 --no-pager'
ssh <node-alias> 'curl -skI --connect-timeout 8 https://<nodelite-domain>/ | head -5'
```

NodeLite Server 侧：

```bash
systemctl status nodelite-server --no-pager || true
journalctl -u nodelite-server -n 120 --no-pager | grep -Ei '<node-id>|<NEW_IP>|websocket|unauthorized|rejected|agent'
```

如果 Agent 侧出现：

```text
server notice unauthorized
agent session ended; retrying after backoff
```

Server 侧出现：

```text
websocket authentication rejected client_ip=<NEW_IP> requested_node_id=<node-id> error=Unauthorized
websocket client disconnected reason=unauthorized
```

结论不是网络故障，而是：Agent 正在连面板，但本地 token 与服务端 registry token 不匹配。常见于机器重装、配置恢复、节点重新注册、IP 漂移后沿用旧配置。

### 4. 生成新 install session 并用完整 token 重绑 Agent

在 NodeLite Server 上生成新 install session：

```bash
/usr/local/bin/nodelite-server \
  --config /opt/nodelite/config/server.toml \
  install-agent \
  --node-id <node-id> \
  --node-label '<node-label>'
```

注意：命令打印的一键安装命令里的 token 可能被截断。不要直接复制 `***` 或省略号版本。读取完整 token：

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

然后在目标节点重新 bootstrap/install：

```bash
ssh <node-alias> "curl -fsSL 'https://<nodelite-domain>/install/install-agent.sh' -o /tmp/nodelite-install-agent.sh && chmod +x /tmp/nodelite-install-agent.sh && NODELITE_AGENT_INSTALL_TOKEN='<FULL_TOKEN>' /tmp/nodelite-install-agent.sh --bootstrap-url 'https://<nodelite-domain>/install/bootstrap' --base-url 'https://github.com/XiNian-dada/NodeLite/releases/latest/download'"
```

### 5. 验证上线

目标节点侧应出现：

```text
server notice authenticated
```

Server 侧应出现：

```text
node authenticated node_id=<node-id> node_label=<node-label>
recorded agent runtime log entries node_id=<node-id>
```

如果公网 `/api/nodes` 被 2FA 或 dashboard auth 拦住，可以直接在 NodeLite Server 读 snapshot：

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

期望结果：

```json
{
  "node_id": "<node-id>",
  "online": true,
  "remote_ip": "<NEW_IP>"
}
```

## 关键判断

| 现象 | 真实含义 | 处理 |
|---|---|---|
| SSH 端口通但 key 登录失败 | 新机器没有 fleet key，或 sshd 禁用公钥登录 | 用密码部署公钥，检查 `PubkeyAuthentication` |
| NodeLite Agent running 但面板离线 | 不能只看 systemd active | 查 Agent/Server 双侧日志 |
| `server notice unauthorized` | Agent 已连到服务端，但 token 不匹配 | 重新生成 install session 并重绑 |
| `/api/nodes` 返回 2FA 页面 | Dashboard/API 访问路径受交互式认证影响 | 用 server 本地 snapshot 和 journal 验证 |
| Docker netns `statvfs` warning | Agent 采集磁盘时跳过 Docker namespace 伪挂载 | 通常不影响节点在线，可暂时忽略 |

## 安全注意

- 不把 root 密码、install token、私钥写入文档或记忆。
- 记录经验时只保留节点别名、泛化命令和判断方法。
- 一键安装 token 有有效期，应现场生成、现场使用、用完不归档。
- 文档仓库可以记录“如何排查”，不要记录“可直接复制的真实凭据”。

## 复盘

这次 NodeLite 离线不是网络不可达，也不是服务进程没跑，而是 token mismatch。最省时间的排查路径是：

```text
连通性 → SSH key → agent systemd → agent 日志 → server 日志 → fresh install session → snapshot 验证
```

以后遇到“新 IP 后 NodeLite 离线”，优先搜索 server 日志里的：

```text
websocket authentication rejected
requested_node_id=<node-id>
error=Unauthorized
```

看到这组信号，直接走“重绑 agent”，不要在 Nginx、DNS、端口上绕圈。
