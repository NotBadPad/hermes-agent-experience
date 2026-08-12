# 🤖 TradingAgents Platform Integration

> **Directory**: `06-integrations/` — Platform integration experience
> **Related Sub-agent**: Xiao Fu (Financial Analysis & Trading Execution)
> **Last Updated**: 2026-05

This document records the experience of integrating the Hermes Agent with the TradingAgents platform, including platform overview, API integration, strategy deployment, automated trading execution, risk control configuration, and lessons learned.

---

## 📋 Table of Contents

1. [Platform Overview](#-platform-overview)
2. [Integration Process](#-integration-process)
3. [API Integration](#-api-integration)
4. [Strategy Deployment](#-strategy-deployment)
5. [Trade Execution](#-trade-execution)
6. [Risk Control System](#-risk-control-system)
7. [MCP Integration](#-mcp-integration)
8. [Troubleshooting](#-troubleshooting)
9. [Lessons Learned](#-lessons-learned)

---

## 🏪 Platform Overview

### What is TradingAgents

TradingAgents is a quantitative trading execution platform for AI Agents. Unlike traditional exchange APIs, TradingAgents provides an integrated service for **strategy hosting**, **automated execution**, **portfolio management**, and **risk control engine**—after Xiao Fu (financial analysis expert) generates trading signals, TradingAgents handles the execution.

### Platform Positioning

| Dimension | Description |
|-----------|-------------|
| Core Features | Strategy hosting, automated trading execution, portfolio management, risk control |
| Supported Exchanges | Binance, OKX, Bybit, Coinbase, Kraken, and 10+ others |
| Trading Instruments | Spot / Futures / Options / Forex (limited by exchange support) |
| Strategy Types | Grid, trend following, arbitrage, mean reversion, custom |
| Risk Control Capabilities | Stop-loss/take-profit, position limits, drawdown control, black swan protection |
| Integration Methods | REST API + WebSocket (real-time quotes & trade push) |
| Pricing Model | Volume-based (0.01%-0.05%) or monthly subscription |

### Relationship with Vibe Trading MCP

```
TradingAgents ↔ Strategy layer & Execution layer (multi-exchange support)
Vibe Trading MCP ↔ Direct execution layer (single exchange connection)

Usage scenarios:
  - Simple execution → Vibe Trading MCP (fast, direct)
  - Strategy hosting + multi-exchange + risk control → TradingAgents (full-featured)
```

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `TRADINGAGENTS_API_KEY` | API Key | `tag_xxxxxxxxxxxx` |
| `TRADINGAGENTS_API_SECRET` | API signature key | `***` |
| `TRADINGAGENTS_API_BASE` | API base URL | `https://api.tradingagents.io/v1` |
| `TRADINGAGENTS_AGENT_ID` | Agent identifier | `agent_xxxxxxxx` |

---

## 🚀 Integration Process

### Complete Integration Steps

```
Step 1: Register TradingAgents account
  → Visit https://tradingagents.io → Register as developer → Complete KYC verification

Step 2: Bind exchange API
  → Account management → Exchange connections → Add API Key (read-only + trading permissions recommended)

Step 3: Create Agent
  → Agent management → Create new Agent → Obtain API credentials

Step 4: Configure Xiao Fu's sub-agent profile
  → Add TradingAgents MCP to xiao-fu's profile

Step 5: Write strategy
  → Use TradingAgents DSL or register strategy logic via API

Step 6: Backtest validation
  → Run strategy on testnet or historical data → Confirm performance

Step 7: Live trading
  → Allocate funds → Enable automated trading → Set risk control parameters

Step 8: Monitoring and adjustment
  → Real-time strategy performance monitoring → Adjust parameters based on market changes
```

### Prerequisites

- ✅ KYC identity verification completed
- ✅ At least one exchange API bound (API + Secret)
- ✅ Sufficient funds in trading account
- ✅ Stop-loss and risk control parameters set

> ⚠️ **Security reminder**: Exchange API should **only have trading permissions**, withdraw permissions disabled. TradingAgents cannot transfer funds out, but API leaks may lead to unauthorized trading.

---

## 🔌 API Integration

### API Basic Information

| Item | Content |
|------|---------|
| Base URL | `https://api.tradingagents.io/v1` |
| Authentication | API Key + HMAC-SHA256 signature |
| Request format | `application/json` |
| Response format | `application/json` |
| Rate limit | 30 req/min (Standard) / 120 req/min (Pro) |
| WebSocket | `wss://ws.tradingagents.io/v1` |

### Signature Algorithm

```python
import hmac
import hashlib
import time
import requests

def sign_request(method: str, path: str, body: str, secret: str, timestamp: int) -> str:
    """TradingAgents request signature (consistent with TradingAgents format)"""
    message = f"{timestamp}{method}{path}{body}"
    return hmac.new(
        secret.encode('utf-8'),
        message.encode('utf-8'),
        hashlib.sha256
    ).hexdigest()

def api_call(method, path, body=None):
    timestamp = int(time.time() * 1000)  # millisecond timestamp
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

### Core API Endpoints

#### Agent & Account Management

```
GET    /agents                      # Get Agent list
POST   /agents                      # Create new Agent
GET    /agents/:id                  # Get Agent details
PATCH  /agents/:id                  # Update Agent configuration
DELETE /agents/:id                  # Delete Agent
GET    /agents/:id/balance          # Query Agent account balance
```

#### Strategy Management

```
GET    /strategies                  # Get strategy list
POST   /strategies                  # Register new strategy
GET    /strategies/:id              # Get strategy details
PATCH  /strategies/:id              # Update strategy configuration
DELETE /strategies/:id              # Delete strategy
POST   /strategies/:id/backtest     # Run backtest
GET    /strategies/:id/backtests    # Get backtest results
POST   /strategies/:id/deploy       # Deploy strategy to live trading
POST   /strategies/:id/undeploy     # Stop strategy
GET    /strategies/:id/performance  # Get strategy performance
```

#### Order Management

```
GET    /orders                      # Get order list
POST   /orders                      # Create order
GET    /orders/:id                  # Get order details
DELETE /orders/:id                  # Cancel order
GET    /orders/history              # Historical orders
GET    /positions                   # Current positions
```

#### Risk Control Management

```
GET    /risk/rules                  # Get risk control rules
POST   /risk/rules                  # Create risk control rule
PATCH  /risk/rules/:id              # Update risk control rule
DELETE /risk/rules/:id              # Delete risk control rule
GET    /risk/events                 # Risk control event logs
POST   /risk/circuit-breaker        # Manually trigger circuit breaker
```

### API Call Examples

```bash
# 1. Register strategy
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
    "display_name": "MA Golden Cross/Death Cross Strategy",
    "type": "custom",
    "description": "Golden cross/death cross strategy based on MA20 and MA50",
    "symbols": ["BTCUSDT", "ETHUSDT"],
    "timeframe": "1h",
    "parameters": {
      "fast_ma": 20,
      "slow_ma": 50,
      "position_size_pct": 0.1,
      "stop_loss_pct": 0.02
    }
  }' | jq .

# 2. Run backtest
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

# 3. Deploy strategy to live trading
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

### API Response Format

```json
// Success response
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

// Error response
{
  "code": 4003,
  "message": "Risk control rule triggered: single trade loss exceeds 2% limit",
  "data": {
    "rule_id": "risk_xxx",
    "trigger_value": 0.025,
    "threshold": 0.02,
    "action": "reject_order"
  },
  "request_id": "req_xxxxxxxx"
}
```

### Error Code Reference

| Error Code | Description | Resolution |
|------------|-------------|------------|
| 0 | Success | - |
| 4001 | Signature verification failed | Check signature algorithm and timestamp format |
| 4002 | Invalid API Key | Check credentials |
| 4003 | Risk control rule triggered | View rule details and adjust parameters |
| 4004 | Request rate limit exceeded | Wait and retry |
| 4005 | Parameter validation failed | Check request parameters |
| 5001 | Exchange connection error | Check exchange API status |
| 5002 | Insufficient account balance | Deposit or reduce position |
| 5003 | Market closed (non-trading hours) | Wait for market open |
| 6001 | Strategy execution error | Check strategy logic |
| 6002 | Insufficient backtest data | Expand backtest time range |

---

## 📋 Strategy Deployment

### Strategy Structure Specification

```python
# tradingagent_strategy.py — Strategy code example

class MACrossStrategy:
    """MA golden cross/death cross strategy template"""

    def __init__(self, params: dict):
        self.fast_ma = params.get("fast_ma", 20)
        self.slow_ma = params.get("slow_ma", 50)
        self.position_size = params.get("position_size_pct", 0.1)
        self.stop_loss = params.get("stop_loss_pct", 0.02)

        self.fast_values = []
        self.slow_values = []
        self.position = 0  # 0: flat, 1: long, -1: short

    def on_candle(self, candle: dict) -> dict:
        """Callback for each candle, returns trading signal"""
        close_price = candle["close"]
        timestamp = candle["timestamp"]

        # Calculate MA
        self.fast_values.append(close_price)
        self.slow_values.append(close_price)

        if len(self.fast_values) < self.fast_ma:
            return {"action": "hold"}
        if len(self.slow_values) < self.slow_ma:
            return {"action": "hold"}

        fast_ma = sum(self.fast_values[-self.fast_ma:]) / self.fast_ma
        slow_ma = sum(self.slow_values[-self.slow_ma:]) / self.slow_ma

        signal = {"action": "hold"}

        # Golden cross (fast MA crosses above slow MA) → go long
        if fast_ma > slow_ma and self.position <= 0:
            signal = {
                "action": "buy",
                "size": self.position_size,
                "stop_loss": close_price * (1 - self.stop_loss),
                "reason": f"Golden cross: MA{self.fast_ma}={fast_ma:.2f} > MA{self.slow_ma}={slow_ma:.2f}"
            }
            self.position = 1

        # Death cross (fast MA crosses below slow MA) → go short
        elif fast_ma < slow_ma and self.position >= 0:
            signal = {
                "action": "sell",
                "size": self.position_size,
                "stop_loss": close_price * (1 + self.stop_loss),
                "reason": f"Death cross: MA{self.fast_ma}={fast_ma:.2f} < MA{self.slow_ma}={slow_ma:.2f}"
            }
            self.position = -1

        return signal

    def get_parameters(self) -> dict:
        """Return current strategy parameters (for UI display)"""
        return {
            "fast_ma": self.fast_ma,
            "slow_ma": self.slow_ma,
            "position_size_pct": self.position_size,
            "stop_loss_pct": self.stop_loss
        }
```

### Strategy Deployment Workflow

```
┌─────────────────────────────────────────────────────────────┐
│                   Strategy Lifecycle                         │
│                                                             │
│  Draft                                                       │
│    ↓ Submit                                                  │
│  Backtesting                                                 │
│    ↓ Backtest complete                                       │
│  Reviewed — View backtest report, decide on live trading    │
│    ↓ Deploy                                                  │
│  Deploying                                                   │
│    ↓ Ready                                                   │
│  Running — Normal signal execution                          │
│    ↓ Manual/Risk control                                     │
│  Paused — Strategy paused but state preserved               │
│    ↓ Stop                                                    │
│  Stopped — Strategy stopped, positions handled              │
│    ↓ Archive                                                 │
│  Archived — Historical strategy                             │
└─────────────────────────────────────────────────────────────┘
```

### Pre-Live Trading Checklist

```markdown
Live Trading Checklist:
  ☐ Backtest period ≥ 6 months, including different market conditions (bull/bear/sideways)
  ☐ Backtest returns positive, Sharpe ratio > 1.0
  ☐ Maximum drawdown within acceptable range (recommended < 20%)
  ☐ Strategy logic clear, no overfitting signs
  ☐ Risk control parameters configured (stop-loss/take-profit/position limits)
  ☐ Funds allocated to this strategy ≤ 20% of total funds
  ☐ Run on small testnet for 24-48 hours first
  ☐ Set alert notifications (strategy errors/risk triggers)
  ☐ Confirm exchange API permissions correct (trading permissions enabled)
```

---

## ⚡ Trade Execution

### Order Types

| Type | Description | Use Case |
|------|-------------|----------|
| `market` | Market order, immediate execution | Quick entry/exit |
| `limit` | Limit order, specified price | Grid trading, support level buying |
| `stop_market` | Stop market order | Stop-loss liquidation |
| `stop_limit` | Stop limit order | Precise stop-loss |
| `take_profit` | Take-profit limit order | Target price profit-taking |
| `trailing_stop` | Trailing stop-loss | Protect profits while letting winners run |

### Trade Execution Workflow

```
Xiao Fu:
  1. Monitor market data (via TradingAgents WebSocket)
  2. Strategy conditions met → Generate trading signal
  3. Signal checked by TradingAgents risk control engine
  4. Risk check passed → Submit order to exchange
  5. Order filled → Update position records
  6. Set stop-loss/take-profit orders
  7. Monitor position status

Xiao Fu → Main Hermes:
  Report: "BTCUSDT golden cross signal triggered, long position opened.
         Entry price: 85000 USDT, Position: 10%, Stop-loss: 83300 USDT"
```

### Batch Order Example

```python
# Batch create orders via TradingAgents API
def place_strategy_orders(orders: list, strategy_id: str):
    """Batch submit strategy orders"""
    # Each order checked by risk control engine
    results = []
    for order in orders:
        # Risk pre-check
        risk_check = api_call("POST", f"/risk/check-order", order)
        if risk_check["code"] != 0:
            results.append({
                "order": order,
                "status": "rejected",
                "reason": risk_check["message"]
            })
            continue

        # Submit order
        resp = api_call("POST", "/orders", {
            **order,
            "strategy_id": strategy_id
        })
        results.append(resp["data"])

    return results
```

---

## 🛡️ Risk Control System

### Risk Control Levels

```
Level 1: Strategy-level risk control
  ├── Max loss per trade (e.g. 2%)
  ├── Max position per strategy (e.g. 20%)
  ├── Max trades per day (e.g. 10)
  └── Strategy pause conditions (e.g. 3 consecutive losses)

Level 2: Agent-level risk control
  ├── Max total drawdown (e.g. 15%)
  ├── Max exposure per currency (e.g. 30%)
  ├── Leverage limit (e.g. ≤ 3x)
  └── Max daily loss amount (e.g. 1000 USDT)

Level 3: Account-level risk control
  ├── Global circuit breaker (stop all strategies when total drawdown > 20%)
  ├── Black swan protection (auto reduce positions during extreme volatility)
  ├── Connection error protection (how to handle exchange disconnection)
  └── Liquidation protection (negative balance auto injection or liquidation)
```

### Risk Control Rule Configuration

```yaml
# Risk control rule configuration example
risk_profiles:
  # Conservative
  conservative:
    max_drawdown: 0.10           # Max drawdown 10%
    max_leverage: 1.0            # No futures
    max_single_order_pct: 0.05   # Single order ≤ 5% of funds
    max_position_pct: 0.15       # Single strategy ≤ 15% of funds
    daily_loss_limit: 500        # Max daily loss 500 USDT
    stop_loss_default: 0.03      # Default stop-loss 3%
    circuit_breaker:
      enabled: true
      trigger: total_drawdown > 0.15  # Circuit breaker when total drawdown > 15%
      cooldown: 3600                  # Cooldown 1 hour

  # Balanced
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

  # Aggressive
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

### Risk Control Event Alerts

| Event | Alert Level | Action |
|-------|-------------|--------|
| Single trade loss exceeded | ⚠️ Warning | Reject order, notify Xiao Fu |
| Strategy consecutive losses | ⚠️ Warning | Pause strategy, Xiao Fu reassesses |
| Total drawdown near limit | 🔴 Critical | Notify main Hermes, consider reducing positions |
| Circuit breaker triggered | 🚨 Emergency | Stop all strategies, notify all |
| Exchange API error | ⚠️ Warning | Retry, pause related strategy if fails |
| Black swan detected | 🚨 Emergency | Execute emergency plan (reduce positions/hedge) |

> ⚠️ **Lesson learned**: Early on, no daily maximum loss limit was set, and an abnormal market movement caused a single-day loss of over 5000 USDT. Lesson: **Multiple layers of risk control must be set for live trading, especially daily loss limits and global circuit breakers**.

---

## 🔧 MCP Integration

### TradingAgents MCP Server

```yaml
# Configure in Xiao Fu (xiao-fu) profile
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

### MCP Exposed Operations

| Operation | Description | Parameters |
|-----------|-------------|------------|
| `list_strategies` | Query strategy list | `status` (optional filter) |
| `create_strategy` | Register new strategy | `name`, `type`, `parameters` |
| `deploy_strategy` | Deploy strategy to live trading | `strategy_id`, `exchange`, `capital` |
| `stop_strategy` | Stop strategy | `strategy_id` |
| `backtest_strategy` | Run backtest | `strategy_id`, `start`, `end` |
| `get_strategy_performance` | Query strategy performance | `strategy_id`, `period` |
| `list_positions` | View current positions | `strategy_id` (optional) |
| `place_order` | Manual order placement | `symbol`, `side`, `type`, `size` |
| `cancel_order` | Cancel order | `order_id` |
| `get_balance` | Query account balance | No parameters |
| `get_risk_events` | View risk control events | `severity`, `limit` |
| `trigger_circuit_breaker` | Manually trigger circuit breaker | `reason` |

### MCP Call Examples (Hermes Agent Perspective)

```
# User: Xiao Fu, try deploying that MA golden cross strategy I wrote
# Xiao Fu internal MCP call:
create_strategy(name="ma-cross-btc", type="custom", parameters={...})
backtest_strategy(strategy_id="strat_xxx", start="2026-01-01", end="2026-05-01")
# View backtest results...
deploy_strategy(strategy_id="strat_xxx", exchange="binance", capital=5000)

# User: How is the strategy performing today?
get_strategy_performance(strategy_id="strat_xxx", period="today")

# User: Any risk control issues?
get_risk_events(severity="warning", limit=10)
```

---

## 🔍 Troubleshooting

### 1. Inaccurate Backtest Results

```
Symptom: Backtest returns are high, but live performance is poor
Investigation:
  ✓ Check if backtest includes slippage and fees
  ✓ Confirm backtest data quality (missing/abnormal candles)
  ✓ Check for overfitting (validate on out-of-sample data)
  ✓ Check for future function (using future data)
  ✓ Confirm backtest period includes current market condition types
```

### 2. Strategy Not Executing After Deployment

```
Symptom: Strategy shows Running but produces no orders
Investigation:
  ✓ Check if strategy conditions are met (is market triggering signals)
  ✓ Check exchange connection status
  ✓ Check if risk control rules are rejecting all signals
  ✓ View strategy logs (logs/strategy_xxx.log)
  ✓ Confirm allocated funds are sufficient
```

### 3. Exchange API Connection Failure

```
Symptom: Returns 5001 exchange connection error
Investigation:
  ✓ Check if exchange API Key has expired
  ✓ Confirm exchange IP whitelist includes TradingAgents egress IP
  ✓ Check if exchange is under maintenance
  ✓ Confirm API permission settings are correct
  ✓ Try manually testing connection in TradingAgents backend
```

### 4. Frequent Risk Control Triggers

```
Symptom: Most orders rejected with 4003 risk control
Investigation:
  ✓ Check if current market volatility is abnormal
  ✓ Adjust risk control parameters (may be too strict)
  ✓ Check if strategy position calculation has bugs (e.g. abnormally large size)
  ✓ View risk control event logs for specific rejection reasons
  ✓ Consider temporarily relaxing risk control during increased market volatility
```

---

## 🕳️ Lessons Learned

### 1. Slippage Causing Backtest Profits but Live Trading Losses

**Phenomenon**: MA golden cross strategy backtested at 45% annualized, but only 12% after one month of live trading.

**Cause**: Backtest configuration did not include slippage and fees; slippage losses for high-frequency strategies in live trading far exceeded expectations.

**Solution**:
```yaml
# Add slippage and fees to backtest configuration
backtest_config:
  slippage: 0.001          # 0.1% slippage simulation
  maker_fee: 0.0002        # Maker fee 0.02%
  taker_fee: 0.0004        # Taker fee 0.04%
  # Recommendation: Use conservative parameters in backtest,
  # if still profitable under conservative parameters, then consider live trading
```

### 2. Strategy Overfitting—Beautiful History, Poor Future

**Phenomenon**: Strategy optimized with significant effort performed much worse in out-of-sample testing and live trading than in backtest.

**Cause**: Parameter over-optimization (overfitting), strategy learned to "memorize" noise in historical data rather than true patterns.

**Solution**:
```text
1. Backtest period must include at least bull, bear, and sideways markets
2. Reserve 20% of data for out-of-sample testing (not used during backtest)
3. Limit parameter ranges, avoid extreme values
4. Performance should be relatively stable across different parameter combinations
5. Prefer simple strategies (Occam's Razor)
```

### 3. Black Swan Event Liquidation Risk

**Phenomenon**: During an extreme market movement (BTC -30% in one day), a futures strategy failed to stop-loss in time, triggering liquidation.

**Cause**: Stop-loss orders failed to execute during extreme market conditions (slippage far exceeded stop-loss price), and risk control circuit breaker response was not timely.

**Solution**:
```yaml
# Black swan protection plan
black_swan_protection:
  # 1. Hard stop-loss (market order stop-loss, accept slippage)
  hard_stop: true

  # 2. Price volatility detection
  volatility_detector:
    enabled: true
    lookback: 60           # 60 candles
    threshold: 3.0         # 3 standard deviations

  # 3. Position reduction strategy
  when_volatility_high:
    action: reduce_position
    reduce_by: 0.5         # Halve position
    if_volatility_gt: 4.0  # When > 4 standard deviations

  # 4. Portfolio hedging
  hedging:
    enabled: true
    hedge_asset: "USDC"    # Move to stablecoin during extreme conditions
```

### 4. Capital Competition When Running Multiple Strategies

**Phenomenon**: Two strategies generated signals simultaneously, but account balance was insufficient to open both positions, causing order rejections.

**Cause**: No capital allocation and priority set between strategies, multiple strategies competing for the same funds.

**Solution**:
```yaml
# Capital allocation strategy
funds_allocation:
  mode: dedicated              # Dedicated mode: fixed funds per strategy
  # Or: mode: pooled (shared pool + priority)

  strategies:
    - id: strat_ma
      allocated_capital: 5000   # Fixed allocation 5000 USDT
      max_risk: 0.15            # Max loss 15% per strategy

    - id: strat_grid
      allocated_capital: 3000
      max_risk: 0.10

    - id: strat_arb
      allocated_capital: 2000
      max_risk: 0.05
```

### 5. WebSocket Disconnection Causing Signal Delay

**Phenomenon**: After market data WebSocket disconnected, it did not auto-reconnect, and the strategy produced no signals for several minutes, missing the best entry point.

**Cause**: WebSocket connection dropped after long runtime, client did not implement auto-reconnect and heartbeat keepalive.

**Solution**:
```python
# WebSocket auto-reconnect implementation
class TradingAgentsWS:
    def __init__(self, symbols, on_candle):
        self.symbols = symbols
        self.on_candle = on_candle
        self.ws = None
        self.reconnect_count = 0
        self.max_reconnect = 10

    def connect(self):
        """Connect and subscribe to market data"""
        url = "wss://ws.tradingagents.io/v1"
        params = {
            "api_key": TRADINGAGENTS_API_KEY,
            "symbols": self.symbols,
            "channels": ["candle"]
        }
        # ... connection logic ...
        # Start heartbeat
        self._start_heartbeat()

    def _start_heartbeat(self):
        """Send heartbeat every 30 seconds"""
        def ping():
            self.ws.send(json.dumps({"type": "ping"}))
        self.heartbeat_timer = set_interval(ping, 30000)

    def on_close(self):
        """Auto-reconnect after disconnection"""
        if self.reconnect_count < self.max_reconnect:
            delay = min(2 ** self.reconnect_count, 60)  # Exponential backoff
            time.sleep(delay)
            self.reconnect_count += 1
            self.connect()
        else:
            # Notify Xiao Fu to switch to backup data source
            self._notify_fallback()
```

---

## 📝 Summary

| Item | Recommendation |
|------|----------------|
| Integration preparation | Complete KYC, bind exchange API (trading permissions only) |
| Strategy development | Simplicity first, overfitting is more dangerous than insufficient parameters |
| Backtest validation | Include slippage/fees, reserve out-of-sample data |
| Live trading deployment | Start small, gradually increase position size |
| Risk control | Three-layer risk control (Strategy→Agent→Account), daily loss limit mandatory |
| Monitoring | WebSocket heartbeat keepalive, proper alert notifications |
| Collaboration | Xiao Fu generates signals → TradingAgents executes → Data back to Graphify for display |

> **TradingAgents is Xiao Fu's "hands"**—no matter how powerful strategy analysis is, it must be validated through execution. Risk control is the lifeline of trading; never run inadequately tested strategies under high risk.
