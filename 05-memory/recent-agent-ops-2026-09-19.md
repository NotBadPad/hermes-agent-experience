# Hermes Agent 运维经验：安全升级、配置迁移与网关排障（2026-09-19）

> 本文整理一次跨版本升级和关联故障排查中可复用的方法。示例使用通用域名、路径、进程名和环境变量，不包含真实服务器、账号或凭据。

## 1. 升级前先记录“版本、来源、工作树、服务”

升级是否安全，不只取决于当前版本，还取决于安装方式和本地改动。Git 安装可能带有未提交的平台适配、脚本或补丁；直接更新可能触发自动 stash、冲突或行为丢失。

```bash
command -v hermes
hermes --version
hermes config path

git -C ~/.hermes/hermes-agent rev-parse --short HEAD
git -C ~/.hermes/hermes-agent status --short
git -C ~/.hermes/hermes-agent remote -v

hermes status --all
```

升级前至少保留两层恢复点：

1. 对已跟踪文件保存 `git diff`；
2. 将重要未跟踪脚本复制到仓库外的时间戳目录。

```bash
backup="$HOME/hermes-preupdate-$(date +%Y%m%d-%H%M%S)"
mkdir -p "$backup"
git -C ~/.hermes/hermes-agent diff > "$backup/local.patch"
cp ~/.hermes/hermes-agent/path/to/local-script.py "$backup/"
```

不要只依赖更新器的自动 stash。显式备份便于在自动恢复冲突、stash 引用变化或仓库重置后独立恢复。

## 2. 自动更新成功，不代表本地补丁已经恢复

`hermes update` 可能完成以下动作：

- 拉取新代码；
- 自动 stash 本地修改；
- 更新 Python/Node 依赖；
- 构建 Web UI；
- 同步 Skills；
- 尝试恢复本地改动。

最后一步可能冲突。此时应区分三个事实：

- 新版本代码是否已经安装；
- 工作树是否干净；
- 本地功能是否已经恢复。

```bash
hermes --version
git -C ~/.hermes/hermes-agent log -1 --oneline --decorate
git -C ~/.hermes/hermes-agent status --short
git -C ~/.hermes/hermes-agent stash list
```

如果上游对同一文件做了大规模重构，不要机械执行 `git stash apply` 后接受整段冲突。更稳妥的做法是：

1. 阅读旧补丁，提炼它的行为契约；
2. 在新版代码中找到新的入口；
3. 按新版结构重新实现最小改动；
4. 保留原始 patch 和 stash，直到验证完成。

这种“语义移植”比逐行合并更可靠，尤其适用于消息平台适配器、Provider 路由和 Gateway 生命周期代码。

## 3. 配置迁移是升级的一部分，但要审阅副作用

升级后运行：

```bash
hermes doctor
hermes doctor --fix
hermes config check
```

`doctor --fix` 可能不只更新配置版本，还会调整新默认值、启用新工具、修改并发额度或修复状态库。执行后应阅读输出，不要把它视为无条件的黑盒修复。

核对重点：

- 配置版本是否迁移到最新版；
- 默认模型和 Provider 是否保持预期；
- Delegation 并发与迭代上限是否符合成本预算；
- 新启用的 Toolset 是否满足依赖；
- 旧 `custom_providers` 是否被提示迁移到新版 `providers`；
- 状态数据库是否过大或需要停机压缩。

配置迁移成功和外部 Provider 可用是两回事。`hermes config check` 通过，只说明配置结构有效，不代表每个 API Key、模型或上游账户池都健康。

## 4. 重启命令超时，不等于服务重启失败

Gateway 会优雅等待正在执行的任务退出。调用端可能先达到超时，但 systemd 已完成切换。因此不要凭命令退出码直接判断服务失败，应读取真实服务状态：

```bash
hermes gateway restart

systemctl is-active hermes-gateway
systemctl show hermes-gateway \
  -p MainPID -p SubState -p ActiveEnterTimestamp --no-pager
journalctl -u hermes-gateway --since '-5 minutes' --no-pager
```

可靠的成功标准是：

- `is-active` 返回 `active`；
- `SubState=running`；
- PID 或启动时间发生变化；
- 新 PID 的日志出现平台初始化信息；
- 没有持续的 traceback 或崩溃重启。

日志中旧 PID 在停机前打印的 API 错误，不应误判为新进程启动失败。查看日志时要结合 PID 和时间边界。

## 5. 网关可访问、API 可认证、模型可调度是三层状态

OpenAI 兼容网关“访问不了”至少应拆成三层：

| 层级 | 最小验证 | 典型结果 |
|---|---|---|
| 站点/反向代理 | `GET /` | `200` 表示入口正常 |
| API 鉴权 | `GET /v1/models`（不带 Key） | `401` 说明 API 路由活着且要求认证 |
| 模型调度 | `POST /v1/chat/completions` | `200` 才证明指定 Key、分组和模型可用 |

```bash
curl -I https://gateway.example.com/
curl -o /dev/null -w '%{http_code}\n' \
  https://gateway.example.com/v1/models
```

如果首页是 `200`、模型列表端点返回预期的 `401`，但聊天请求返回 `503`，优先检查账户池、Key 分组、模型映射和冷却状态。类似 `pool=0` 或 `no available accounts supporting model` 的日志属于调度配置问题，重启服务通常无效。

## 6. 认证“限流”可能只是磁盘满的外观

登录接口显示 `Too many requests`，不一定真是限流。磁盘写满时可能出现这条链路：

```text
根分区 100%
→ PostgreSQL 无法写 WAL/临时文件
→ 数据库进入恢复或拒绝连接
→ 登录查询失败
→ 应用返回通用限流/认证错误
→ 错误日志持续增长，进一步吃满磁盘
```

排查认证错误时先检查基础依赖：

```bash
df -h /
free -h
systemctl is-active postgresql redis-server nginx
journalctl -u postgresql --since '-30 minutes' --no-pager
```

修复顺序应是：

1. 释放明确安全的空间；
2. 确认 PostgreSQL 恢复接受连接；
3. 再测试登录接口；
4. 用“无效凭据返回 401，而不是 429/500”验证认证链路已经恢复；
5. 最后处理日志轮转和容量预警，避免错误风暴复发。

不要在数据库不可用时反复重置密码或修改限流配置。

## 7. 模型健康脚本要区分“活着”和“可用”

健康检查不能把所有非 `200` 都视为“服务在线”：

- `400`：参数或模型不兼容；
- `401/403`：凭据、权限或 WAF 问题；
- `404`：端点或模型不存在；
- `429`：通常是临时限流，可按策略保留为“服务活着”；
- `5xx`：当前路由不可用，应允许故障切换；
- 连接超时：网络或上游不可达。

同时注意两个容易造成假故障的细节：

1. CDN/WAF 可能拒绝默认 `urllib` 指纹，探针应使用明确 `User-Agent` 并与真实客户端对比；
2. Key 轮换后，长生命周期 Gateway 的进程环境可能仍持有旧值。确定性健康脚本可以优先读取最新 `.env`，再把进程环境作为回退。

自动切换配置时只写环境变量引用：

```yaml
model:
  api_key: ${EXAMPLE_GATEWAY_API_KEY}
```

不要把解析后的明文 Key 写回 `config.yaml`、日志或 Cron 输出。

## 8. 升级后的验证矩阵

一次升级至少覆盖以下验证：

```bash
# 版本和源码
hermes --version
git -C ~/.hermes/hermes-agent status --short

# 配置和依赖
hermes config check
hermes doctor

# 服务
systemctl is-active hermes-gateway
systemctl show hermes-gateway -p MainPID -p SubState --no-pager

# 本地定制代码
~/.hermes/hermes-agent/venv/bin/python -m py_compile \
  ~/.hermes/hermes-agent/path/to/modified_adapter.py

# 上游 API：使用无敏感输出的最小请求
curl -o /dev/null -w '%{http_code}\n' https://gateway.example.com/
```

对本地补丁还应运行一个最小功能 Smoke Test，而不仅是语法检查。例如，文件兜底功能要实际创建临时文件、执行发布函数，并检查目标文件和返回 URL 的一致性。

## 一句话总结

Hermes 升级要同时管理四条线：上游版本、本地补丁、配置迁移和运行中服务；故障排查则要把入口、认证、模型调度与底层数据库分层验证，避免用重启掩盖配置或容量根因。
