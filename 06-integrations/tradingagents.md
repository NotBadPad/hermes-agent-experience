# 🤖 TradingAgents 平台集成

> **目录**: `06-integrations/` — 平台接入经验
> **相关子代理**: 小富（金融分析 & 交易执行）
> **最后更新**: 2026-05

本文档记录了 Hermes Agent 接入 TradingAgents 平台的经验，包括平台介绍、API 对接、策略部署、自动交易执行、风控配置及踩坑记录。

---

## 📋 目录

1. [平台概览](#-平台概览)
2. [接入流程](#-接入流程)
3. [API 对接](#-api-对接)
4. [策略部署](#-策略部署)
5. [交易执行](#-交易执行)
6. [风控体系](#-风控体系)
7. [MCP 集成](#-mcp-集成)
8. [常见问题排查](#-常见问题排查)
9. [踩坑记录](#-踩坑记录)

---

## 🏪 平台概览

### TradingAgents 是什么

TradingAgents 是一个面向 AI Agent 的量化交易执行平台。与传统的交易所 API 不同，TradingAgents 提供了**策略托管**、**自动执行**、**组合管理**和**风控引擎**一体化服务——小富（金融分析专家）给出交易信号后，TradingAgents 负责执行落地。

### 平台定位

| 维度 | 说明 |
|------|------|
| 核心功能 | 策略托管、自动交易执行、组合管理、风控 |
| 支持的交易所 | Binance, OKX, Bybit, Coinbase, Kraken 等 10+ |
| 交易品种 | 现货 / 合约 / 期权 / 外汇（受限于交易所支持） |
| 策略类型 | 网格、趋势跟踪、套利、均值回归、自定义 |
| 风控能力 | 止损/止盈、仓位限制、回撤控制、黑天鹅保护 |
| 接入方式 | REST API + WebSocket（实时行情 & 成交推送） |
| 结算模式 | 按交易量收费（0.01%-0.05%）或月费制 |

### 与 Vibe Trading MCP 的关系

```
TradingAgents ↔ 策略层 & 执行层（多交易所支持）
Vibe Trading MCP ↔ 直接执行层（单交易所连接）

使用场景：
  - 简单执行 → Vibe Trading MCP（快，直接）
  - 策略托管 + 多交易所 + 风控 → TradingAgents（全功能）
```

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `TRADINGAGENTS_API_KEY` | API Key | `tag_xxxxxxxxxxxx` |
| `TRADINGAGENTS_API_SECRET` | API 签名密钥 | `***` |
| `TRADINGAGENTS_API_BASE` | API 基础地址 | `https://api.tradingagents.io/v1` |
| `TRADINGAGENTS_AGENT_ID` | Agent 标识 | `agent_xxxxxxxx` |

---

## 🚀 接入流程

### 完整接入步骤

```
步骤 1: 注册 TradingAgents 账号
  → 访问 https://tradingagents.io → 注册开发者 → 完成 KYC 认证

步骤 2: 绑定交易所 API
  → 账户管理 → 交易所连接 → 添加 API Key（建议只读 + 交易权限）

步骤 3: 创建 Agent
  → Agent 管理 → 创建新的 Agent → 获取 API 凭证

步骤 4: 配置小富的子代理 profile
  → 在 xiao-fu 的 profile 中添加 TradingAgents MCP

步骤 5: 编写策略
  → 使用 TradingAgents DSL 或通过 API 注册策略逻辑

步骤 6: 回测验证
  → 在测试网或历史数据上运行策略 → 确认表现

步骤 7: 实盘运行
  → 分配资金 → 启用自动交易 → 设置风控参数

步骤 8: 监控与调整
  → 实时监控策略表现 → 根据市场变化调整参数
```

### 前置条件

- ✅ 已完成 KYC 实名认证
- ✅ 已绑定至少一个交易所 API（API + Secret）
- ✅ 交易账户中有足够的资金
- ✅ 已设定止损和风控参数

> ⚠️ **安全提醒**：交易所 API 建议**仅开启交易权限**，关闭提现权限。TradingAgents 无法转出资金，但 API 泄露可能导致未授权交易。

---

## 🔌 API 对接

### API 基本信息

| 项目 | 内容 |
|------|------|
| 基础 URL | `https://api.tradingagents.io/v1` |
| 认证方式 | API Key + HMAC-SHA256 签名 |
| 请求格式 | `application/json` |
| 响应格式 | `application/json` |
| 速率限制 | 30 req/min（标准）/ 120 req/min（专业） |
| WebSocket | `wss://ws.tradingagents.io/v1` |

### 签名算法

```python
import hmac
import hashlib
import time
import requests

def sign_request(method: str, path: str, body: str, secret: str, timestamp: int) -> str:
    """TradingAgents 请求签名（与 TradingAgents 格式一致）"""
    message = f"{timestamp}{method}{path}{body}"
    return hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def api_call(method, path, body=None):
    timestamp = int(time.time() * 1000)  # 毫秒时间戳
    body_str = json.dumps(body) if body else ""
    signature = sign_request(method, path, body_str, TRADINGAGENTS_API_SECRET, timestamp)
    
    headers = {
        "X-Api-Key": TRADINGAGENTS_API_KEY,
        "X-Timestamp": str(timestamp),
        "X-Signature": signature,
        "Content-Type": "application/json"
    }
    
    resp = requests.request(
        method, f"{TRADINGAGENTS_API_BASE}{path}",
        headers=headers, data=body_str
    )
    return resp.json()
```

### 核心 API 端点

#### Agent & 账户管理

```
GET    /agents                      # 获取 Agent 列表
POST   /agents                      # 创建新 Agent
GET    /agents/:id                  # 获取 Agent 详情
PATCH  /agents/:id                  # 更新 Agent 配置
DELETE /agents/:id                  # 删除 Agent
GET    /agents/:id/balance          # 查询 Agent 账户余额
```

#### 策略管理

```
GET    /strategies                  # 获取策略列表
POST   /strategies                  # 注册新策略
GET    /strategies/:id              # 获取策略详情
PATCH  /strategies/:id              # 更新策略配置
DELETE /strategies/:id              # 删除策略
POST   /strategies/:id/backtest     # 运行回测
GET    /strategies/:id/backtests    # 获取回测结果
POST   /strategies/:id/deploy       # 部署策略到实盘
POST   /strategies/:id/undeploy     # 停止策略
GET    /strategies/:id/performance  # 获取策略表现
```

#### 订单管理

```
GET    /orders                      # 获取订单列表
POST   /orders                      # 创建订单
GET    /orders/:id                  # 获取订单详情
DELETE /orders/:id                  # 取消订单
GET    /orders/history              # 历史订单
GET    /positions                   # 当前持仓
```

#### 风控管理

```
GET    /risk/rules                  # 获取风控规则
POST   /risk/rules                  # 创建风控规则
PATCH  /risk/rules/:id              # 更新风控规则
DELETE /risk/rules/:id              # 删除风控规则
GET    /risk/events                 # 风控事件日志
POST   /risk/circuit-breaker        # 手动触发熔断
```

### API 调用示例

```bash
# 1. 注册策略
curl -s -X POST "$TRADINGAGENTS_API_BASE/strategies" \
  -H "X-Api-Key: $TRADINGAGENTS_API_KEY" \
  -H "X-Timestamp: $(date +%s%3N)" \
  -H "X-Signature: $(python3 -c "
import hmac,hashlib,time
t = int(time.time()*1000)
msg = f'{t}POST/strategies{\"name\":\"ma-cross\",\"type\":\"custom\"}'
sig = hmac.new(b'$TRADINGAGENTS_API_SECRET', msg.encode(), hashlib.sha256).hexdigest()
print(sig)
")" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ma-cross",
    "display_name": "MA 金叉死叉策略",
    "type": "custom",
    "description": "基于 MA20 和 MA50 的金叉死叉策略",
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "timeframe": "1h",
    "parameters": {
      "fast_ma": 20,
      "slow_ma": 50,
      "position_size_pct": 0.1,
      "stop_loss_pct": 0.02
    }
  }' | jq .

# 2. 运行回测
curl -s -X POST "$TRADINGAGENTS_API_BASE/strategies/strat_xxx/backtest" \
  -H "X-Api-Key: $TRADINGAGENTS_API_KEY" \
  -H "X-Timestamp: $(date +%s%3N)" \
  -H "X-Signature: $SIGNATURE" \
  -H "Content-Type: application/json" \
  -d '{
    "start_time": "2026-01-01T00:00:00Z",
    "end_time": "2026-05-01T00:00:00Z",
    "initial_capital": 10000,
    "symbols": ["BTCUSDT", "ETHUSDT"]
  }' | jq .

# 3. 部署策略到实盘
curl -s -X POST "$TRADINGAGENTS_API_BASE/strategies/strat_xxx/deploy" \
  -H "X-Api-Key: $TRADINGAGENTS_API_KEY" \
  -H "X-Timestamp: $(date +%s%3N)" \
  -H "X-Signature: $SIGNATURE" \
  -H "Content-Type: application/json" \
  -d '{
    "exchange": "binance",
    "symbol": "BTCUSDT",
    "allocated_capital": 5000,
    "risk_profile_id": "risk_normal"
  }' | jq .
```

### API 响应格式

```json
// 成功响应
{
  "code": 0,
  "message": "success",
  "data": {
    "strategy_id": "strat_xxxxxxxx",
    "status": "deployed",
    "deployed_at": "2026-05-09T10:00:00Z"
  },
  "request_id": "req_xxxxxxxx"
}

// 错误响应
{
  "code": 4003,
  "message": "风控规则触发：单笔亏损超过 2% 上限",
  "data": {
    "rule_id": "risk_xxx",
    "trigger_value": 0.025,
    "threshold": 0.02,
    "action": "reject_order"
  },
  "request_id": "req_xxxxxxxx"
}
```

### 错误码表

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| 0 | 成功 | - |
| 4001 | 签名验证失败 | 检查签名算法和时间戳格式 |
| 4002 | API Key 无效 | 检查凭据 |
| 4003 | 风控规则触发 | 查看 rule 详情调整参数 |
| 4004 | 请求频率超限 | 等待后重试 |
| 4005 | 参数校验失败 | 检查请求参数 |
| 5001 | 交易所连接异常 | 检查交易所 API 状态 |
| 5002 | 账户余额不足 | 充值或降低仓位 |
| 5003 | 市场关闭（非交易时间） | 等待市场开放 |
| 6001 | 策略执行异常 | 检查策略逻辑 |
| 6002 | 回测数据不足 | 扩大回测时间范围 |

---

## 📋 策略部署

### 策略结构规范

```python
# tradingagent_strategy.py — 策略代码示例

class MACrossStrategy:
    """MA 金叉死叉策略模板"""
    
    def __init__(self, params: dict):
        self.fast_ma = params.get("fast_ma", 20)
        self.slow_ma = params.get("slow_ma", 50)
        self.position_size = params.get("position_size_pct", 0.1)
        self.stop_loss = params.get("stop_loss_pct", 0.02)
        
        self.fast_values = []
        self.slow_values = []
        self.position = 0  # 0: 空仓, 1: 多头, -1: 空头
    
    def on_candle(self, candle: dict) -> dict:
        """每根 K 线回调，返回交易信号"""
        close_price = candle["close"]
        timestamp = candle["timestamp"]
        
        # 计算 MA
        self.fast_values.append(close_price)
        self.slow_values.append(close_price)
        
        if len(self.fast_values) < self.fast_ma:
            return {"action": "hold"}
        if len(self.slow_values) < self.slow_ma:
            return {"action": "hold"}
        
        fast_ma = sum(self.fast_values[-self.fast_ma:]) / self.fast_ma
        slow_ma = sum(self.slow_values[-self.slow_ma:]) / self.slow_ma
        
        signal = {"action": "hold"}
        
        # 金叉（快线上穿慢线）→ 开多
        if fast_ma > slow_ma and self.position <= 0:
            signal = {
                "action": "buy",
                "size": self.position_size,
                "stop_loss": close_price * (1 - self.stop_loss),
                "reason": f"金叉: MA{self.fast_ma}={fast_ma:.2f} > MA{self.slow_ma}={slow_ma:.2f}"
            }
            self.position = 1
        
        # 死叉（快线下穿慢线）→ 开空
        elif fast_ma < slow_ma and self.position >= 0:
            signal = {
                "action": "sell",
                "size": self.position_size,
                "stop_loss": close_price * (1 + self.stop_loss),
                "reason": f"死叉: MA{self.fast_ma}={fast_ma:.2f} < MA{self.slow_ma}={slow_ma:.2f}"
            }
            self.position = -1
        
        return signal
    
    def get_parameters(self) -> dict:
        """返回当前策略参数（用于 UI 展示）"""
        return {
            "fast_ma": self.fast_ma,
            "slow_ma": self.slow_ma,
            "position_size_pct": self.position_size,
            "stop_loss_pct": self.stop_loss
        }
```

### 策略部署流程

```
┌─────────────────────────────────────────────────────────────┐
│                   策略生命周期                               │
│                                                             │
│  Draft（草稿）                                               │
│    ↓ 提交                                                    │
│  Backtesting（回测中）                                        │
│    ↓ 回测完成                                                │
│  Reviewed（已审查）— 查看回测报告，决定是否实盘               │
│    ↓ 部署                                                    │
│  Deploying（部署中）                                          │
│    ↓ 就绪                                                    │
│  Running（运行中）— 正常执行信号                              │
│    ↓ 手动/风控                                                │
│  Paused（已暂停）— 策略暂停但不销毁状态                       │
│    ↓ 停止                                                    │
│  Stopped（已停止）— 策略已停止，持仓已处理                    │
│    ↓ 归档                                                    │
│  Archived（已归档）— 历史策略                                 │
└─────────────────────────────────────────────────────────────┘
```

### 实盘部署前检查清单

```markdown
实盘部署 Checklist:
  ☐ 回测周期 ≥ 6 个月，包含不同市场环境（牛/熊/震荡）
  ☐ 回测收益率为正，夏普比率 > 1.0
  ☐ 最大回撤在可接受范围内（建议 < 20%）
  ☐ 策略逻辑清晰，无过拟合迹象
  ☐ 风控参数配置完成（止损/止盈/仓位限制）
  ☐ 分配给该策略的资金 ≤ 总资金 20%
  ☐ 在小额测试网先行运行 24-48 小时
  ☐ 设置告警通知（策略异常/风控触发）
  ☐ 确认交易所 API 权限正确（交易权限已开启）
```

---

## ⚡ 交易执行

### 订单类型

| 类型 | 说明 | 使用场景 |
|------|------|----------|
| `market` | 市价单，立即成交 | 快速进出场 |
| `limit` | 限价单，指定价格 | 网格交易、支撑位买入 |
| `stop_market` | 止损市价单 | 止损平仓 |
| `stop_limit` | 止损限价单 | 精确止损 |
| `take_profit` | 止盈限价单 | 目标位止盈 |
| `trailing_stop` | 追踪止损 | 保护利润同时让利润奔跑 |

### 交易执行工作流

```
小富:
  1. 监控市场数据（通过 TradingAgents WebSocket）
  2. 策略条件满足 → 生成交易信号
  3. 信号经过 TradingAgents 风控引擎检查
  4. 风控通过 → 提交订单到交易所
  5. 订单成交 → 更新持仓记录
  6. 设置止损/止盈订单
  7. 监控持仓状态

小富 → 主 Hermes:
  报告: "BTCUSDT 金叉信号触发，已开多单。
         开仓价: 85000 USDT, 仓位: 10%, 止损: 83300 USDT"
```

### 批量订单示例

```python
# 通过 TradingAgents API 批量创建订单
def place_strategy_orders(orders: list, strategy_id: str):
    """批量提交策略订单"""
    # 每个订单经过风控引擎检查
    results = []
    for order in orders:
        # 风控预检
        risk_check = api_call("POST", f"/risk/check-order", order)
        if risk_check["code"] != 0:
            results.append({
                "order": order,
                "status": "rejected",
                "reason": risk_check["message"]
            })
            continue
        
        # 提交订单
        resp = api_call("POST", "/orders", {
            **order,
            "strategy_id": strategy_id
        })
        results.append(resp["data"])
    
    return results
```

---

## 🛡️ 风控体系

### 风控层级

```
Level 1: 策略级风控
  ├── 单笔最大亏损（如 2%）
  ├── 单策略最大仓位（如 20%）
  ├── 每日最大交易次数（如 10 次）
  └── 策略暂停条件（如连续 3 次亏损）

Level 2: Agent 级风控
  ├── 总资金最大回撤（如 15%）
  ├── 单币种最大敞口（如 30%）
  ├── 杠杆限制（如 ≤ 3x）
  └── 每日最大亏损额（如 1000 USDT）

Level 3: 账户级风控
  ├── 全局熔断（总回撤 > 20% 时停止所有策略）
  ├── 黑天鹅保护（极端波动时自动减仓）
  ├── 连接异常保护（交易所失联时如何处理）
  └── 穿仓保护（负余额自动注入或清算）
```

### 风控规则配置

```yaml
# 风控规则配置示例
risk_profiles:
  # 保守型
  conservative:
    max_drawdown: 0.10           # 最大回撤 10%
    max_leverage: 1.0            # 不做合约
    max_single_order_pct: 0.05   # 单笔订单 ≤ 5% 资金
    max_position_pct: 0.15       # 单策略 ≤ 15% 资金
    daily_loss_limit: 500        # 每日最大亏损 500 USDT
    stop_loss_default: 0.03      # 默认止损 3%
    circuit_breaker:
      enabled: true
      trigger: total_drawdown > 0.15  # 总回撤 > 15% 熔断
      cooldown: 3600                  # 冷却 1 小时
  
  # 均衡型  
  balanced:
    max_drawdown: 0.20
    max_leverage: 2.0
    max_single_order_pct: 0.10
    max_position_pct: 0.25
    daily_loss_limit: 2000
    stop_loss_default: 0.05
    circuit_breaker:
      enabled: true
      trigger: total_drawdown > 0.25
      cooldown: 1800
  
  # 激进型
  aggressive:
    max_drawdown: 0.35
    max_leverage: 3.0
    max_single_order_pct: 0.20
    max_position_pct: 0.40
    daily_loss_limit: 5000
    stop_loss_default: 0.08
    circuit_breaker:
      enabled: true
      trigger: total_drawdown > 0.40
      cooldown: 900
```

### 风控事件告警

| 事件 | 告警级别 | 处理方式 |
|------|----------|----------|
| 单笔亏损超限 | ⚠️ 警告 | 拒绝该订单，通知小富 |
| 策略连续亏损 | ⚠️ 警告 | 暂停策略，小富重新评估 |
| 总回撤接近上限 | 🔴 严重 | 通知主 Hermes，考虑减仓 |
| 熔断触发 | 🚨 紧急 | 停止所有策略，全员通知 |
| 交易所 API 错误 | ⚠️ 警告 | 重试，失败后暂停相关策略 |
| 黑天鹅检测 | 🚨 紧急 | 执行应急计划（减仓/对冲） |

> ⚠️ **踩坑记录**：早期未设置每日最大亏损限额，一次异常行情导致单日亏损超 5000 USDT。教训：**实盘必须设置多层风控，特别是每日亏损上限和全局熔断**。

---

## 🔧 MCP 集成

### TradingAgents MCP 服务器

```yaml
# 在小富（xiao-fu）profile 中配置
mcp_servers:
  tradingagents-api:
    command: /usr/local/bin/tradingagents-mcp
    args: []
    env:
      TRADINGAGENTS_API_KEY: ${TRADINGAGENTS_API_KEY}
      TRADINGAGENTS_API_SECRET: ${TRADINGAGENTS_API_SECRET}
      TRADINGAGENTS_API_BASE: ${TRADINGAGENTS_API_BASE}
      TRADINGAGENTS_AGENT_ID: ${TRADINGAGENTS_AGENT_ID}
```

### MCP 暴露的操作

| 操作 | 说明 | 参数 |
|------|------|------|
| `list_strategies` | 查询策略列表 | `status`（可选筛选） |
| `create_strategy` | 注册新策略 | `name`, `type`, `parameters` |
| `deploy_strategy` | 部署策略到实盘 | `strategy_id`, `exchange`, `capital` |
| `stop_strategy` | 停止策略 | `strategy_id` |
| `backtest_strategy` | 运行回测 | `strategy_id`, `start`, `end` |
| `get_strategy_performance` | 查询策略表现 | `strategy_id`, `period` |
| `list_positions` | 查看当前持仓 | `strategy_id`（可选） |
| `place_order` | 手动下单 | `symbol`, `side`, `type`, `size` |
| `cancel_order` | 取消订单 | `order_id` |
| `get_balance` | 查询账户余额 | 无参数 |
| `get_risk_events` | 查看风控事件 | `severity`, `limit` |
| `trigger_circuit_breaker` | 手动触发熔断 | `reason` |

### MCP 调用示例（Hermes Agent 视角）

```
# 用户：小富，部署我写的那个 MA 金叉策略试试
# 小富内部调用 MCP:
create_strategy(name="ma-cross-btc", type="custom", parameters={...})
backtest_strategy(strategy_id="strat_xxx", start="2026-01-01", end="2026-05-01")
# 查看回测结果...
deploy_strategy(strategy_id="strat_xxx", exchange="binance", capital=5000)

# 用户：今天策略表现怎么样？
get_strategy_performance(strategy_id="strat_xxx", period="today")

# 用户：风控有没有问题？
get_risk_events(severity="warning", limit=10)
```

---

## 🔍 常见问题排查

### 1. 回测结果不准确

```
症状: 回测收益率很高，但实盘表现差
排查:
  ✓ 检查回测是否包含滑点和手续费
  ✓ 确认回测数据质量（有无缺失/异常 K 线）
  ✓ 检查过拟合（在样本外数据验证）
  ✓ 检查未来函数（是否使用了未来数据）
  ✓ 确认回测时间段是否包含当前市场环境类型
```

### 2. 策略部署后不执行

```
症状: 策略显示 Running 但没有产生任何订单
排查:
  ✓ 检查策略条件是否满足（行情是否触发信号）
  ✓ 检查交易所连接状态
  ✓ 检查风控规则是否拒绝了所有信号
  ✓ 查看策略日志（logs/strategy_xxx.log）
  ✓ 确认分配资金是否足够
```

### 3. 交易所 API 连接失败

```
症状: 返回 5001 交易所连接异常
排查:
  ✓ 检查交易所 API Key 是否过期
  ✓ 确认交易所 IP 白名单包含 TradingAgents 出口 IP
  ✓ 检查交易所是否在进行维护
  ✓ 确认 API 权限设置正确
  ✓ 尝试在 TradingAgents 后台手动测试连接
```

### 4. 风控频繁触发

```
症状: 大部分订单被 4003 风控拒绝
排查:
  ✓ 检查当前市场波动率是否异常
  ✓ 调整风控参数（可能过于严格）
  ✓ 检查策略仓位计算是否有 bug（如 size 异常大）
  ✓ 查看风控事件日志了解具体被拒原因
  ✓ 考虑在市场波动增大时临时放宽风控
```

---

## 🕳️ 踩坑记录

### 1. 滑点导致回测盈利实盘亏损

**现象**：MA 金叉策略回测年化 45%，实盘运行一个月仅 12%。

**原因**：回测配置中未设置滑点（slippage）和手续费，实盘交易中高频策略的滑点损耗远超预期。

**解决方案**：
```yaml
# 回测配置增加滑点和手续费
backtest_config:
  slippage: 0.001          # 0.1% 滑点模拟
  maker_fee: 0.0002        # 挂单费 0.02%
  taker_fee: 0.0004        # 吃单费 0.04%
  # 建议：回测时用保守参数，
  # 如果保守参数下仍有正收益，再考虑实盘
```

### 2. 策略过拟合——历史靓丽，未来拉跨

**现象**：花了大量时间优化的策略，在样本外测试和实盘中表现远不如回测。

**原因**：参数过度优化（过拟合），策略学会了"记住"历史数据中的噪声而非真实规律。

**解决方案**：
```text
1. 回测周期至少包含牛、熊、震荡三种市场
2. 保留 20% 数据作为样本外测试（不回测时使用）
3. 限制参数范围，避免极端值
4. 不同参数组合下的表现应相对稳定
5. 优先选择简单策略（Occam's Razor）
```

### 3. 黑天鹅行情的穿仓风险

**现象**：某次极端行情（BTC 单日 -30%）中，合约策略未及时止损，触发穿仓。

**原因**：止损单在极端行情下未能成交（滑点远超出止损价），且风控熔断响应不及时。

**解决方案**：
```yaml
# 黑天鹅保护方案
black_swan_protection:
  # 1. 硬止损（市价单止损，接受滑点）
  hard_stop: true
  
  # 2. 价格波动率检测
  volatility_detector:
    enabled: true
    lookback: 60           # 60 根 K 线
    threshold: 3.0         # 3 倍标准差
    
  # 3. 减仓策略
  when_volatility_high:
    action: reduce_position
    reduce_by: 0.5         # 减半仓位
    if_volatility_gt: 4.0  # 4 倍标准差时
  
  # 4. 组合对冲
  hedging:
    enabled: true
    hedge_asset: "USDC"    # 极端行情时转向稳定币
```

### 4. 多策略同时运行的资金竞争

**现象**：两个策略同时产生信号，但账户余额不足以同时开仓，导致订单被拒。

**原因**：未设置策略间的资金分配和优先级，多个策略竞争同一笔资金。

**解决方案**：
```yaml
# 资金分配策略
funds_allocation:
  mode: dedicated              # 专用模式：每个策略固定资金
  # 或: mode: pooled (共享池 + 优先级)
  
  strategies:
    - id: strat_ma
      allocated_capital: 5000   # 固定分配 5000 USDT
      max_risk: 0.15            # 单策略最大亏损 15%
    
    - id: strat_grid
      allocated_capital: 3000
      max_risk: 0.10
    
    - id: strat_arb
      allocated_capital: 2000
      max_risk: 0.05
```

### 5. WebSocket 断连导致信号延迟

**现象**：行情 WebSocket 断连后未自动重连，策略在数分钟内未产生任何信号，错过了最佳入场点。

**原因**：WebSocket 连接在长时间运行后断开，客户端未实现自动重连和心跳保活。

**解决方案**：
```python
# WebSocket 自动重连实现
class TradingAgentsWS:
    def __init__(self, symbols, on_candle):
        self.symbols = symbols
        self.on_candle = on_candle
        self.ws = None
        self.reconnect_count = 0
        self.max_reconnect = 10
    
    def connect(self):
        """连接并订阅行情"""
        url = "wss://ws.tradingagents.io/v1"
        params = {
            "api_key": TRADINGAGENTS_API_KEY,
            "symbols": self.symbols,
            "channels": ["candle"]
        }
        # ... 连接逻辑 ...
        # 启动心跳
        self._start_heartbeat()
    
    def _start_heartbeat(self):
        """每 30 秒发送心跳"""
        def ping():
            self.ws.send(json.dumps({"type": "ping"}))
        self.heartbeat_timer = set_interval(ping, 30000)
    
    def on_close(self):
        """断连后自动重连"""
        if self.reconnect_count < self.max_reconnect:
            delay = min(2 ** self.reconnect_count, 60)  # 指数退避
            time.sleep(delay)
            self.reconnect_count += 1
            self.connect()
        else:
            # 通知小富切换备用数据源
            self._notify_fallback()
```

---

## 📝 总结

| 项目 | 建议 |
|------|------|
| 接入准备 | 完成 KYC，绑定交易所 API（仅交易权限） |
| 策略开发 | 简单优先，过拟合比参数不足更危险 |
| 回测验证 | 包含滑点/手续费，保留样本外数据 |
| 实盘部署 | 从小额开始，逐步加仓 |
| 风控 | 三层风控（策略→Agent→账户），每日亏损上限必设 |
| 监控 | WebSocket 心跳保活，告警通知到位 |
| 协作 | 小富出信号 → TradingAgents 执行 → 数据回 Graphify 展示 |

> **TradingAgents 是小富的\"手\"**——策略分析再厉害，最终要通过执行验证。风控是交易的生命线，永远不要在高风险下运行未经充分测试的策略。
