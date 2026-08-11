# Hermes Agent 运维经验：定时任务、模型路由与健康检查（2026-08-11）

> 本文整理近期可复用的 Hermes Agent 运维经验。示例中的域名、Provider 名、API Key、任务 ID、账号和服务器信息均使用通用占位符，不包含真实基础设施或凭据。

## 1. 定时任务“没消息”不等于“没执行”

Hermes Cron 的执行和消息投递是两个独立阶段。排查时应依次确认：

1. 调度器是否触发任务；
2. 是否生成了输出文件；
3. 输出是否为 `[SILENT]`；
4. 消息平台投递是否被限流或拒绝。

```bash
hermes cron list

# 查看指定任务的落盘结果
ls -la ~/.hermes/cron/output/<JOB_ID>/

# 查看执行与投递日志
grep -i '<JOB_ID>\|rate limited\|delivery error\|send failed' \
  ~/.hermes/logs/agent.log ~/.hermes/logs/errors.log | tail -50
```

判断标准：

- 有输出文件且任务状态为成功：任务已经执行；
- 输出为 `[SILENT]`：任务按设计静默，不应发送消息；
- 输出有正文，但日志显示平台限流：执行成功、投递失败；
- 没有输出且调度状态异常：才继续排查调度器本身。

需要保证限流期间不丢结果时，可暂时将投递目标改为本地，待平台恢复后再补发。不要因为聊天窗口里没收到消息，就直接重跑有副作用的任务。

## 2. 固定巡检优先使用确定性脚本

磁盘、内存、接口和模型可用性巡检等任务，如果判断逻辑固定，优先采用：

- `no_agent=true`；
- 脚本负责完整判断；
- 正常时 stdout 为空；
- 只有异常时输出可直接投递的告警正文；
- 非零退出码表示巡检程序自身故障。

这样可以避免每次由模型重新解释 Prompt，导致模型别名、参数或判断阈值发生漂移。

脚本设计建议：

```text
固定输入 → 执行探测 → 解析状态 →
  正常：不输出
  异常：输出告警
  程序错误：非零退出
```

普通调试日志应写入日志文件，不要写到 stdout，否则每轮都会触发无意义通知。

## 3. 自定义 Provider 的“可见性”和“凭据池”是两套机制

自定义 OpenAI 兼容服务通常涉及两个独立配置层：

| 配置层 | 主要职责 |
|---|---|
| `custom_providers` / `model_catalog` | 定义模型、端点以及模型选择器中的可见性 |
| Credential Pool | 管理凭据轮换、耗尽状态和健康记录 |

常见误区是：`hermes auth list` 能看到凭据，就认为模型一定会出现在 `/model`。实际上，只有凭据池而没有模型目录配置时，模型选择器仍可能不可见。

`custom_providers` 必须是 YAML 列表：

```yaml
custom_providers:
  - name: example-gateway
    base_url: https://gateway.example.com/v1
    api_key: ${EXAMPLE_GATEWAY_API_KEY}
    models:
      - example-model
```

不要写成字典：

```yaml
# 错误示例
custom_providers:
  example-gateway:
    base_url: https://gateway.example.com/v1
```

配置后应执行：

```bash
hermes config check
hermes auth list
```

然后新开会话或重启相应客户端，让模型目录重新加载。公开文档中只保留环境变量名和示例域名，不写真实 Key、网关域名或账号组信息。

## 4. 模型健康检查要防止客户端指纹造成假故障

某些受 CDN/WAF 保护的 OpenAI 兼容网关会拒绝 Python `urllib` 的默认请求头，返回 403 或类似的安全策略错误。此时正常 Hermes 请求可能成功，健康脚本却把全部模型误报为离线。

建议诊断时对比三种探测：

1. `urllib` 默认请求头；
2. `urllib` 加明确的 `User-Agent`；
3. `requests` 加明确的 `User-Agent`。

推荐模式：

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

注意事项：

- 探测时使用网关实际接受的原始模型 ID，不要使用 UI 展示别名；
- 不要统一强塞 `temperature`，部分模型只接受默认值；
- 如果只有默认 `urllib` 返回 403，而带 UA 的请求成功，应修复探针，不要修改生产路由；
- 修复后既要直接运行脚本，也要手动触发一次 Cron，并读取最新落盘结果。

## 5. 跨模型协议切换时清理推理字段

部分推理模型会在历史消息中返回非标准字段，例如 `reasoning_content`。如果在同一长会话中切换到不支持该字段的 OpenAI 兼容 Provider，完整历史被重新发送后，网关可能快速返回 400/403。

典型特征：

- `/v1/models` 正常；
- 极简的新对话请求正常；
- 带旧会话历史的请求立即失败；
- 失败发生在上游模型真正推理之前。

处理顺序：

1. 新建完全干净的会话；
2. 在发送消息前切换到目标 Provider；
3. 如果控制网关，在转发到不支持该字段的上游前剥离 `reasoning_content`；
4. 不要先轮换 API Key——Key 正常时，换 Key 不会修复消息格式不兼容。

长期方案是在 Agent 或网关的 Provider 边界做消息规范化，而不是依赖用户每次手动清理上下文。

## 6. 运维变更遵循“先诊断，后最小变更”

出现模型不可用、Cron 无消息或 Gateway 异常时，不要第一步就重启服务。推荐顺序：

1. 读当前配置和任务状态；
2. 检查落盘输出与日志；
3. 用最小请求验证端点、模型 ID 和协议；
4. 修改单一配置层或探针脚本；
5. 验证是否支持热加载或缓存刷新；
6. 只有确认无替代方案时才重启；
7. 重启后再次检查服务状态和真实请求。

这套顺序能减少不必要中断，也能避免“重启后暂时恢复，但根因仍在”的假修复。

## 7. 公开经验同步前的脱敏清单

提交公开仓库前至少检查：

- API Key、Token、密码、Cookie、私钥；
- 真实网关域名、后台地址和数据库连接串；
- 公网/内网 IP、SSH 账号和主机清单；
- 用户邮箱、聊天 ID、任务 ID和内部账号组；
- 命令输出中意外带出的凭据；
- Git 历史中是否已有敏感值。

暂存后执行聚焦扫描：

```bash
git diff --cached | grep -Ein \
  'ghp_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|password\s*[:=]|secret\s*[:=]|token\s*[:=]|api[_-]?key\s*[:=]' || true
```

扫描命中后需要人工判断：安全警示文字和 `${EXAMPLE_API_KEY}` 占位符可以保留，具体赋值、长随机串和真实认证头必须删除。

## 一句话总结

先区分“执行、输出、投递”三层，再区分“模型目录、凭据池、请求协议”三层；健康检查必须验证探针本身，公开同步必须在暂存区做二次脱敏。
