# 近期 Agent 运行经验（2026-05-16）

> 记录一次 Hermes Agent 实战配置整理：模型路由清理、辅助模型降级、Gateway 重启定位、Bot Street 交付，以及文档归档边界。本文只保留可公开复用的经验，不包含 API Key、Token、密码、内网细节或私密凭据。

## 1. Opendoor 下移除 GPT 模型

### 背景

Opendoor provider 中曾保留多个 GPT 系模型别名，用于代码、写作和图像相关任务。后来路由策略调整：不再通过 Opendoor 使用 GPT 模型，只保留 Claude / Gemini 系模型。

### 操作要点

- 从主 Hermes 配置的 Opendoor provider 中删除 GPT 系模型块。
- 同步搜索并更新技能里的硬编码模型别名，避免后续路由继续指向已删除模型。
- 更新智能路由技能：写作/创意类从 GPT 路由切到 Claude Sonnet/Opus 系。
- 更新配置自动化技能：示例模型不要继续引用已弃用的 GPT 别名。

### 验证方法

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

### 经验

模型下线不能只改 `config.yaml`。如果技能、路由文档、子代理 profile 里还残留旧别名，Agent 会在后续任务中“复活”旧模型，造成难排查的 400/404 或路由失败。

## 2. 辅助模型统一切 DeepSeek

### 背景

部分辅助任务自动路由到了 MiMo 模型。MiMo 的多轮推理响应包含 `reasoning_content`，后续调用如果未按服务端协议回传历史 reasoning 内容，容易触发 HTTP 400。

### 决策

将 Hermes 的辅助模型任务统一切到 DeepSeek Flash，作为稳定、低成本、中文友好的后台任务模型。

### 操作要点

使用 Hermes 配置命令统一设置 auxiliary 相关项，而不是手动多处编辑：

```bash
hermes config set auxiliary.<task>.provider deepseek
hermes config set auxiliary.<task>.model deepseek-v4-flash
hermes config set auxiliary.<task>.base_url https://api.deepseek.com/v1
hermes config set auxiliary.<task>.api_key '${DEEPSEEK_API_KEY}'
```

实际 task 名以当前 Hermes 配置为准。设置后重启 gateway 并验证服务状态。

```bash
systemctl restart hermes-gateway
systemctl status hermes-gateway --no-pager
```

### 经验

- 辅助任务优先选“稳定、便宜、协议简单”的模型，不一定要选最强模型。
- 对有特殊推理字段的模型，要确认客户端是否完整支持多轮协议。
- 配置完成后要读回配置验证，不能只相信命令执行成功。

## 3. Gateway “总是重启”的排查方法

### 现象

用户观察到 Hermes Gateway 多次重启。

### 排查路径

```bash
systemctl status hermes-gateway --no-pager
journalctl -u hermes-gateway --since '2 hours ago' --no-pager
```

同时搜索本机脚本、cron、systemd 定时器中是否存在 restart 行为：

```bash
grep -R "restart hermes-gateway\|systemctl restart" ~/.hermes /etc/systemd/system 2>/dev/null || true
```

### 结论示例

本次定位到主要原因是：

1. 手动改模型配置期间主动重启。
2. 模型健康巡检在探测异常后触发过一次自动重启。

服务最终处于 active 状态，不是持续崩溃。

### 经验

“重启很多次”要先区分：

- 人为配置变更后的主动重启；
- watchdog / health-check 的自动重启；
- 进程崩溃导致 systemd restart。

三者修复策略完全不同。

## 4. Bot Street 任务执行与交付

### 当前运营模式

- 扫描新任务前，先核对本地已参与清单，避免重复申请。
- 发现新任务先汇报给主人确认，不自动扣火花申请。
- 被指派后的任务可以直接执行、发布交付物、提交 API。

### 交付物发布策略

优先使用公开可访问且低摩擦的平台：

1. `paste.rs`：适合 Markdown 文章，curl 一步发布。
2. GitHub 仓库 `articles/`：适合需要长期留存的交付物。

```bash
curl -s -X POST --data-binary @article.md https://paste.rs/
```

### 经验

- Bot Street API 认证不是 Bearer Token，而是 `x-agent-id` + `x-agent-key` 双头。
- `/tasks/my` 只显示已被指派的任务；待审核申请不一定在这里出现。
- 任务记录必须本地留痕：任务名、状态、交付链接、deliveryId、是否已申请。
- 自动巡检如果遇到消息平台限流，可以改为本地输出，避免噪声和失败重试。

## 5. 文档归档边界

### 背景

曾误把 Agent 运维经验文档放进业务项目仓库。后续已删除并迁移到专门的 Hermes 经验仓库。

### 规则

- 业务项目仓库只放业务项目相关代码与文档。
- Agent 配置、模型路由、运维经验、平台接入经验，统一放到 Hermes 经验仓库。
- 公共仓库文档必须脱敏：不写 API Key、Token、密码、真实后台账号、数据库凭据。
- 公开拓扑图隐藏 IP，对外展示机器名时使用约定命名，例如 `JTTI-HK`。

## 6. 提交前检查清单

```bash
# 1. 看暂存区
git diff --cached

# 2. 粗扫敏感信息
git diff --cached | grep -Ein 'ghp_[A-Za-z0-9_]+|sk-[A-Za-z0-9_-]{20,}|password\s*[:=]|secret\s*[:=]|token\s*[:=]|api[_-]?key\s*[:=]' || true

# 3. 确认没有误改业务仓库
git remote -v
git status --short
```

## 一句话总结

模型治理要“配置、技能、子代理、文档”一起改；Agent 经验要进 Agent 经验仓库，不要混进业务项目。
