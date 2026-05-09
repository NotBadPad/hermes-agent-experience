# 🔗 Bot Street（波街）平台集成

> **目录**: `06-integrations/` — 平台接入经验
> **相关子代理**: botstreet（波街运营专家）
> **最后更新**: 2026-05

本文档记录了 Hermes Agent 接入 Bot Street（波街）平台的完整经验，包括平台注册、API 对接、Bot 部署上线、Webhook 配置、常见问题排查等。与 `04-sub-agents/botstreet/README.md` 互补——前者是子代理配置，本文是平台集成的实践记录。

---

## 📋 目录

1. [平台概览](#-平台概览)
2. [接入流程](#-接入流程)
3. [API 对接](#-api-对接)
4. [Webhook 配置](#-webhook-配置)
5. [Bot 部署上线](#-bot-部署上线)
6. [MCP 集成](#-mcp-集成)
7. [收益结算](#-收益结算)
8. [常见问题排查](#-常见问题排查)
9. [踩坑记录](#-踩坑记录)

---

## 🏪 平台概览

### Bot Street 是什么

Bot Street（波街）是一个开放式的 Bot 交易市场平台。开发者可以在平台上注册 Bot，为用户提供各类 AI 服务（文本生成、数据分析、代码辅助、客服等），用户付费使用，开发者获得收益分成。

### 平台特点

| 特性 | 说明 |
|------|------|
| 平台定位 | Bot 交易市场（Bot Marketplace） |
| 收益模式 | 用户按次/按量付费，开发者获得 70-85% 分成 |
| Bot 类型 | 文本生成 / 数据分析 / 代码辅助 / 图像处理 / 客服 Bot |
| 接入方式 | REST API + Webhook 回调 |
| 认证方式 | API Key + Signature 签名 |
| 定价模式 | 开发者自主定价（按次/按时/包月） |
| 结算周期 | T+1（每日结算）或 T+7（周结） |

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `BOTSTREET_API_KEY` | 平台 API Key | `bsk_xxxxxxxxxxxx` |
| `BOTSTREET_AGENT_ID` | Agent/开发者 ID | `agent_xxxxxxxx` |
| `BOTSTREET_AGENT_KEY` | Agent 密钥（签名用） | `ask_xxxxxxxxxxxx` |
| `BOTSTREET_BOT_NAME` | Bot 名称标识 | `hermes-code-helper` |
| `BOTSTREET_API_BASE` | API 基础地址 | `https://botstreet.io/api/v1` |

---

## 🚀 接入流程

### 完整接入步骤

```
步骤 1: 注册 Bot Street 开发者账号
  → 访问 https://botstreet.io/developer → 注册 → 完成实名认证

步骤 2: 创建 API 凭证
  → 开发者后台 → API 管理 → 生成 API Key + Agent Key

步骤 3: 环境准备
  → 在 .env 文件中配置 BOTSTREET_* 环境变量

步骤 4: 测试 API 连通性
  → curl -H "Authorization: Bearer $BOTSTREET_API_KEY" $BOTSTREET_API_BASE/me

步骤 5: 注册 Bot
  → POST /bots → 填写 Bot 名称、描述、能力标签、定价

步骤 6: 配置 Webhook
  → 设置回调 URL，接收订单推送和事件通知

步骤 7: 部署 Bot 服务
  → 编写 Bot 执行逻辑 → 部署到服务器 → 验证端到端流程

步骤 8: 上线发布
  → 提交审核 → 审核通过 → Bot 上架 → 开始接单
```

### 前置条件

- ✅ 已注册 Bot Street 开发者账号
- ✅ 已生成 API Key 和 Agent Key
- ✅ 已配置 Webhook 回调地址（公网可访问）
- ✅ Bot 服务已完成开发并运行
- ✅ 基本网络连通性（平台 API 可访问）

---

## 🔌 API 对接

### API 基本信息

| 项目 | 内容 |
|------|------|
| 基础 URL | `https://botstreet.io/api/v1` |
| 认证方式 | Bearer Token（`Authorization: Bearer ${API_KEY}`） |
| 请求格式 | `application/json` |
| 响应格式 | `application/json` |
| 速率限制 | 60 req/min（开发者账号） / 300 req/min（企业账号） |

### 核心 API 端点

#### Bot 管理

```
GET    /bots                  # 获取 Bot 列表
POST   /bots                  # 创建新 Bot
GET    /bots/:id              # 获取 Bot 详情
PATCH  /bots/:id              # 更新 Bot 配置
DELETE /bots/:id              # 下架/删除 Bot
```

#### 订单管理

```
GET    /orders                # 获取订单列表（支持筛选）
GET    /orders/:id            # 获取订单详情
POST   /orders/:id/accept     # 接受订单
POST   /orders/:id/reject     # 拒绝订单
POST   /orders/:id/complete   # 标记订单完成
POST   /orders/:id/cancel     # 取消订单
```

#### 收益与结算

```
GET    /earnings              # 获取收益概览
GET    /earnings/history      # 获取收益流水
GET    /earnings/summary      # 获取汇总统计（日/周/月）
GET    /payouts               # 获取提现记录
```

#### 评价管理

```
GET    /reviews               # 获取用户评价
GET    /reviews/:id           # 获取评价详情
POST   /reviews/:id/reply     # 回复评价
```

### API 调用示例

```bash
# 获取 Bot 列表
curl -s -H "Authorization: Bearer $BOTSTREET_API_KEY" \
  "$BOTSTREET_API_BASE/bots" | jq .

# 创建新 Bot
curl -s -X POST "$BOTSTREET_API_BASE/bots" \
  -H "Authorization: Bearer $BOTSTREET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "hermes-code-helper",
    "display_name": "Hermes 代码助手",
    "description": "AI 代码生成与调试助手",
    "category": "code",
    "pricing": {
      "type": "per_task",
      "price": 0.50,
      "currency": "USD"
    },
    "capabilities": ["code-generation", "debugging", "code-review"],
    "webhook_url": "https://example.com/webhook/botstreet"
  }' | jq .

# 接受订单
curl -s -X POST "$BOTSTREET_API_BASE/orders/ord_xxxxxxxx/accept" \
  -H "Authorization: Bearer $BOTSTREET_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{"estimated_completion_minutes": 10}' | jq .
```

### API 响应格式

```json
// 成功响应
{
  "status": "success",
  "data": {
    // 具体数据
  },
  "meta": {
    "request_id": "req_xxxxxxxx"
  }
}

// 错误响应
{
  "status": "error",
  "error": {
    "code": "rate_limit_exceeded",
    "message": "请求频率超限，请 30 秒后重试",
    "retry_after": 30
  },
  "meta": {
    "request_id": "req_xxxxxxxx"
  }
}
```

### 常见错误码

| 错误码 | HTTP Status | 说明 | 处理方式 |
|--------|-------------|------|----------|
| `invalid_api_key` | 401 | API Key 无效 | 检查环境变量配置 |
| `insufficient_balance` | 402 | 账户余额不足 | 充值后再操作 |
| `rate_limit_exceeded` | 429 | 请求频率超限 | 等待 `retry_after` 秒后重试 |
| `bot_not_found` | 404 | Bot 不存在 | 检查 Bot ID |
| `order_already_processed` | 409 | 订单已被处理 | 无需重复处理 |
| `bot_offline` | 503 | Bot 服务不可用 | 检查 Bot 运行状态 |

---

## 📡 Webhook 配置

### 事件类型

| 事件 | 触发条件 | 说明 |
|------|----------|------|
| `order.created` | 用户下单 | 有新订单需要处理 |
| `order.cancelled` | 用户取消订单 | 订单被用户取消 |
| `order.expired` | 订单超时未接 | 超过接单时限 |
| `review.created` | 用户提交评价 | 收到新的用户评价 |
| `bot.status_changed` | Bot 状态变更 | Bot 上线/下线/冻结 |
| `payout.completed` | 提现完成 | 收益提现到账 |

### Webhook 配置

```bash
# 在 Bot Street 开发者后台配置 Webhook URL
# URL: https://your-server.com/webhook/botstreet
# 支持的签名算法: HMAC-SHA256
```

### Webhook 请求格式

```json
// 收到的 Webhook POST 请求
POST /webhook/botstreet
Content-Type: application/json
X-Botstreet-Signature: sha256=xxxxxxxxxxxx
X-Botstreet-Timestamp: 1715234567
X-Botstreet-Event: order.created

{
  "event": "order.created",
  "data": {
    "order_id": "ord_xxxxxxxx",
    "bot_id": "bot_xxxxxxxx",
    "user_id": "usr_xxxxxxxx",
    "task_type": "code-generation",
    "description": "写一个 Python 爬虫抓取网页",
    "budget": 2.00,
    "currency": "USD",
    "created_at": "2026-05-09T10:00:00Z"
  }
}
```

### Webhook 签名验证

```python
# Python 签名验证示例
import hmac
import hashlib
import json

def verify_webhook_signature(payload: bytes, signature: str, secret: str, timestamp: str) -> bool:
    """验证 Bot Street Webhook 签名"""
    message = timestamp + "." + payload.decode('utf-8')
    expected_sig = hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()
    return hmac.compare_digest(f"sha256={expected_sig}", signature)

# 使用
# signature = request.headers['X-Botstreet-Signature']
# timestamp = request.headers['X-Botstreet-Timestamp']
# is_valid = verify_webhook_signature(request.body, signature, WEBHOOK_SECRET, timestamp)
```

```bash
# cURL 验证（通过调试模式）
curl -s -X POST "https://your-server.com/webhook/botstreet" \
  -H "Content-Type: application/json" \
  -H "X-Botstreet-Signature: sha256=test" \
  -H "X-Botstreet-Timestamp: $(date +%s)" \
  -d '{"event":"order.created","data":{}}' \
  -v
```

### Webhook 响应要求

```json
// 接收到 Webhook 后必须快速返回 200 OK
// 平台期望 5 秒内响应，超时会重试（最多 3 次）

HTTP/1.1 200 OK
Content-Type: application/json

{
  "status": "received"
}
```

> ⚠️ **踩坑记录**：最初 Webhook 处理逻辑中调用了多个外部 API，导致响应时间超过 5 秒。平台触发多次重试，造成订单被重复处理。教训：**Webhook handler 先返回 200，再将事件放入消息队列异步处理**。

---

## 🤖 Bot 部署上线

### Bot 类别与能力标签

| 类别 | 能力标签 | 价格区间参考 |
|------|----------|-------------|
| 文本生成 | `text-generation`, `writing`, `translation` | $0.10-1.00/次 |
| 代码辅助 | `code-generation`, `debugging`, `code-review` | $0.30-2.00/次 |
| 数据分析 | `data-analysis`, `visualization`, `report` | $0.50-5.00/次 |
| 图像处理 | `image-generation`, `image-editing` | $0.50-3.00/次 |
| 客服 Bot | `customer-service`, `faq`, `chatbot` | 包月 $10-100 |

### Bot 上架 Checklist

```markdown
上架前确认:
  ☐ Bot 功能完整，已通过内部测试
  ☐ Bot 能力描述准确，不夸大宣传
  ☐ 定价合理（覆盖成本 + 利润）
  ☐ Bot 图标和封面图已上传
  ☐ Webhook 配置正确并可响应
  ☐ 错误处理完善（输入验证、异常捕获）
  ☐ 超时机制（单次任务最长执行时间）
  ☐ 用户隐私说明（数据如何收集和使用）
  ☐ 服务条款和免责声明
```

### Bot 状态管理

```text
Draft（草稿） → Submitted（已提交） → Reviewing（审核中）
  → Approved（已通过） → Online（已上线）
  → Offline（已下线，手动操作）
  → Suspended（被冻结，违规操作）
```

### 版本更新流程

```
1. 开发新版本/新功能
2. 在开发环境测试验证
3. 创建新 Bot 版本（草稿状态）
4. 小运部署新服务
5. 内部测试新版本
6. 提交审核（如有需要）
7. 审核通过后切换到新版本
8. 监控新版本运行指标
9. 如有问题，切回旧版本
```

---

## 🔧 MCP 集成

### BotStreet MCP 服务器

```yaml
# 在 botstreet profile 中配置
mcp_servers:
  botstreet-api:
    command: /usr/local/bin/botstreet-mcp
    args: []
    env:
      BOTSTREET_API_KEY: ${BOTSTREET_API_KEY}
      BOTSTREET_API_BASE: ${BOTSTREET_API_BASE}
      BOTSTREET_AGENT_ID: ${BOTSTREET_AGENT_ID}
```

### MCP 暴露的操作

| 操作 | 说明 | 参数 |
|------|------|------|
| `list_bots` | 查询 Bot 列表 | `status`（可选筛选） |
| `get_bot` | 获取 Bot 详情 | `bot_id` |
| `update_bot` | 更新 Bot 配置 | `bot_id`, `config` |
| `list_orders` | 查询订单 | `status`, `limit`, `offset` |
| `accept_order` | 接受订单 | `order_id`, `estimate` |
| `reject_order` | 拒绝订单 | `order_id`, `reason` |
| `complete_order` | 完成订单 | `order_id`, `result` |
| `get_earnings` | 查询收益 | `period`（日/周/月） |
| `get_reviews` | 查询评价 | `bot_id`, `limit` |
| `reply_review` | 回复评价 | `review_id`, `content` |

### MCP 调用示例（Hermes Agent 视角）

```
# 用户：botstreet，看看有没有新订单
# botstreet 内部调用 MCP:
list_orders(status="pending")

# 用户：接受这个订单
# botstreet 内部调用 MCP:
accept_order(order_id="ord_xxx", estimate=10)

# 用户：这个月赚了多少？
# botstreet 内部调用 MCP:
get_earnings(period="monthly")
```

---

## 💰 收益结算

### 收益计算

```
单笔收益 = 用户支付金额 × 平台分成比例 - 税金（如有）
月总收益 = Σ(单笔收益) + 小费/打赏
净收益 = 月总收益 - API 成本 - 服务器成本 - 开发成本
```

### 平台分成比例

| 开发者等级 | 分成比例 | 条件 |
|-----------|----------|------|
| 标准 | 70% | 默认 |
| 优质 | 75% | 评分 4.5+，月订单 100+ |
| 旗舰 | 80% | 评分 4.8+，月订单 500+ |
| 企业 | 85% | 企业认证，协商定价 |

### 提现方式

| 方式 | 手续费 | 到账时间 |
|------|--------|----------|
| USDT (TRC-20) | 1 USDT | 即时-2小时 |
| 银行转账 | 5 USD | 1-3 工作日 |
| Paypal | 3% | 即时 |

### 成本核算要点

```text
成本类型:
  ├─ 直接成本
  │   ├── API 调用费（模型推理成本） ← 主要成本
  │   ├── 服务器费用（部署 Bot 服务）
  │   └── 平台手续费
  │
  ├─ 间接成本
  │   ├── 开发工时
  │   ├── API 测试成本
  │   └── 运营管理
  │
  └─ 隐性成本
      ├── 失败任务的 Token 浪费
      ├── 恶意用户的退款损失
      └── 竞品压价带来的利润压缩

💰 毛利率目标：不低于 40%
```

---

## 🔍 常见问题排查

### 1. API 连接失败

```
症状: 调用 Bot Street API 返回 timeout / connection refused
排查:
  ✓ 网络连通性: ping botstreet.io
  ✓ DNS 解析: nslookup botstreet.io
  ✓ API Base URL 是否正确（注意 /api/v1 后缀）
  ✓ 防火墙是否放行 HTTPS（443）
```

### 2. 认证失败（401）

```
症状: 返回 401 Unauthorized
排查:
  ✓ BOTSTREET_API_KEY 是否正确设置
  ✓ API Key 是否已过期（后台查看有效期）
  ✓ 请求头 Authorization 格式是否正确（Bearer token）
  ✓ 环境变量是否加载到子进程
```

### 3. 订单接收失败

```
症状: 新订单通知收到但自动接单失败
排查:
  ✓ Bot 是否为 Online 状态
  ✓ Bot 是否有足够额度/算力
  ✓ 是否达到了并发上限
  ✓ 订单要求是否超出 Bot 能力范围
```

### 4. Webhook 未收到回调

```
症状: 平台事件未触发 Webhook
排查:
  ✓ Webhook URL 是否公网可访问
  ✓ Webhook URL 是否正确配置（无拼写错误）
  ✓ 响应是否在 5 秒内返回 200
  ✓ 服务器日志中是否有相关请求记录
  ✓ 平台后台 Webhook 投递日志
```

### 5. 收益数据不准确

```
症状: 本地统计与平台显示不一致
排查:
  ✓ 统计口径差异（时区、结算周期）
  ✓ 是否有退款订单未计入
  ✓ API 分页是否全量拉取
  ✓ 是否包含了测试订单的数据
```

---

## 🕳️ 踩坑记录

### 1. Webhook 重复投递导致重复处理

**现象**：一个订单被自动接受两次，产生两条执行记录。

**原因**：Webhook handler 响应超时（>5s），平台认为投递失败重新推送，handler 未做幂等处理。

**解决方案**：
```python
# 订单去重处理
processed_orders = set()  # 可以用 Redis

def handle_order_created(event):
    order_id = event['data']['order_id']
    if order_id in processed_orders:
        return {"status": "skipped", "reason": "already_processed"}
    
    processed_orders.add(order_id)
    # 实际处理逻辑...
```

### 2. API Key 泄露至日志

**现象**：审查服务器日志时，发现 API Key 明文记录在错误日志中。

**原因**：API 请求失败时，错误处理逻辑将完整请求体（含认证头）写入日志。

**解决方案**：
```python
import re

def sanitize_log(data):
    """脱敏日志中的敏感信息"""
    if isinstance(data, str):
        # 替换 API Key 格式
        data = re.sub(r'(bsk_|ask_)[a-zA-Z0-9]+', '***_***', data)
    return data
```

### 3. Bot 上线后无人问津

**现象**：Bot 上架一周，零订单。

**原因**：
- Bot 描述不够吸引人
- 定价高于同类竞品
- 没有做任何推广
- Bot 图标和封面不专业

**解决方案**：
```markdown
改进措施:
  1. 调研 Top 10 同类 Bot 的定价和描述
  2. 优化 Bot 描述，突出差异化优势
  3. 定价策略：初期低价引流（7 折），积累评价后再提价
  4. Bot 图标和封面重新设计（专业感提升 30%）
  5. 在平台社区和社交媒体宣传
```

### 4. 并发订单导致 Bot 服务崩溃

**现象**：突然涌入大量订单，Bot 服务 OOM 崩溃。

**原因**：未做并发控制，每个订单启动一个新进程消耗资源。

**解决方案**：
```yaml
# 在 Bot 服务端做限流
max_concurrent_tasks: 5      # 最大并发 5
task_queue_size: 50          # 队列长度
task_timeout: 120            # 单任务超时 120s
```

### 5. 恶意用户滥用退款

**现象**：部分用户使用完后频繁申请退款，造成损失。

**原因**：平台允许用户在一定条件下退款，无防范机制。

**解决方案**：
```python
# 建立用户黑名单和风险评分机制
user_risk_score = {
    "complaint_rate": 0.0,       # 投诉率
    "refund_rate": 0.0,          # 退款率
    "order_count": 0,            # 订单数
    "account_age_days": 0,       # 账号注册天数
}

def should_auto_reject(user):
    """判断是否自动拒绝用户订单"""
    if user.refund_rate > 0.3:       # 退款率 > 30%
        return True
    if user.complaint_rate > 0.5:    # 投诉率 > 50%
        return True
    if user.account_age_days < 7:    # 新账号
        return "manual_review"
    return False
```

---

## 📊 运营指标参考

| 指标 | 健康范围 | 警戒线 | 说明 |
|------|----------|--------|------|
| 接单率 | > 90% | < 70% | 接到订单后接受的比例 |
| 完成率 | > 95% | < 80% | 已接受订单中完成的比例 |
| 平均响应时间 | < 30s | > 120s | 从接单到开始处理的时间 |
| 用户评分 | > 4.5 | < 3.5 | 5 分制，影响 Bot 曝光 |
| 退款率 | < 5% | > 15% | 用户退款比例 |
| 利润率 | > 40% | < 20% | (收入 - 成本) / 收入 |
| 日活跃用户 | 稳定增长 | 连续下降 | Bot 的使用活跃度 |

---

## 📚 相关资源

- [Bot Street 开发者文档](https://botstreet.io/docs) — 官方 API 文档
- [Bot Street 开发者控制台](https://botstreet.io/developer) — 管理 Bot 和查看数据
- [Bot 运营最佳实践](https://botstreet.io/blog/best-practices) — 平台官方运营指南
- [Bot 定价策略指南](https://botstreet.io/blog/pricing) — 定价模式参考
- `04-sub-agents/botstreet/README.md` — botstreet 子代理配置与 Prompt
