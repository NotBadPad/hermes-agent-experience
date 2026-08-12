# 📊 Graphify Platform Integration

> **Directory**: `06-integrations/` — Platform integration experience
> **Related Sub-agents**: Xiaokai (data visualization development), Xiaoyun (service deployment)
> **Last Updated**: 2026-05

This document records Hermes Agent's experience integrating with the Graphify platform, including platform introduction, API integration, data source configuration, chart generation, dashboard management, and lessons learned.

---

## 📋 Table of Contents

1. [Platform Overview](#-platform-overview)
2. [Integration Process](#-integration-process)
3. [API Integration](#-api-integration)
4. [Data Source Configuration](#-data-source-configuration)
5. [Chart Generation and Dashboards](#-chart-generation-and-dashboards)
6. [Automated Reporting Workflow](#-automated-reporting-workflow)
7. [MCP Integration](#-mcp-integration)
8. [Common Issues Troubleshooting](#-common-issues-troubleshooting)
9. [Lessons Learned](#-lessons-learned)

---

## 🏪 Platform Overview

### What is Graphify

Graphify is an AI-driven data visualization platform that supports connecting to multiple data sources (databases, APIs, CSV, etc.) and generates charts and dashboards through natural language. Unlike Xia345 and Bot Street, Graphify is a **data consumption and analysis display** platform—Xiaofu's analysis results are visualized through Graphify dashboards for team or client viewing.

### Platform Positioning

| Dimension | Description |
|-----------|-------------|
| Core Features | Natural language → Charts / Auto dashboards / Scheduled reports |
| Data Source Support | MySQL, PostgreSQL, MongoDB, BigQuery, CSV, REST API |
| Chart Types | Line, bar, pie, scatter, heatmap, map, table, and 30+ more |
| Output Formats | PNG, SVG, PDF, HTML, embedded iframe |
| Sharing Methods | Public link / Password sharing / Embed / Email subscription |
| AI Capabilities | Natural language queries, auto chart recommendations, anomaly detection |
| Pricing Model | Per dashboard count + data volume + AI query count |

### Environment Variables

| Variable | Description | Example |
|----------|-------------|---------|
| `GRAPHIFY_API_BASE` | API base URL | `https://api.graphify.io/v1` |
| `GRAPHIFY_API_KEY` | API Key | `gfk_xxxxxxxxxxxx` |
| `GRAPHIFY_WORKSPACE_ID` | Workspace ID | `ws_xxxxxxxx` |
| `GRAPHIFY_SECRET_KEY` | Webhook signing key | `***` |

---

## 🚀 Integration Process

### Complete Integration Steps

```
Step 1: Register Graphify account
  → Visit https://graphify.io → Register → Create workspace

Step 2: Connect data source
  → Workspace → Data source management → Add data source (database/API/file)

Step 3: Obtain API credentials
  → Settings → API Management → Generate API Key

Step 4: Environment configuration
  → Configure GRAPHIFY_* environment variables in .env file

Step 5: Test connectivity
  → Call /v1/workspaces/{ws_id} to verify

Step 6: Configure sub-agent
  → Add Graphify MCP to Xiaofu or botstreet's profile

Step 7: Create first dashboard
  → Generate charts via natural language commands → Adjust configuration → Publish dashboard

Step 8: Set up automated reporting
  → Configure scheduled refresh → Set up email/Webhook subscription
```

### Prerequisites

- ✅ Registered Graphify account and created workspace
- ✅ Connected at least one data source
- ✅ Obtained API Key
- ✅ (Optional) Publicly accessible Webhook endpoint (for event notifications)

---

## 🔌 API Integration

### API Basic Information

| Item | Content |
|------|---------|
| Base URL | `https://api.graphify.io/v1` |
| Authentication | Bearer Token (`Authorization: Bearer <api_key>`) |
| Request Format | `application/json` |
| Response Format | `application/json` |
| Rate Limit | 60 req/min (Standard) / 300 req/min (Pro) |

### Core API Endpoints

#### Data Source Management

```
GET    /datasources                     # Get data source list
POST   /datasources                     # Add data source
GET    /datasources/:id                 # Get data source details
PATCH  /datasources/:id                 # Update data source configuration
DELETE /datasources/:id                 # Delete data source
POST   /datasources/:id/test            # Test data source connection
```

#### Chart Management

```
GET    /charts                          # Get chart list
POST   /charts                          # Create chart
GET    /charts/:id                      # Get chart details
PATCH  /charts/:id                      # Update chart configuration
DELETE /charts/:id                      # Delete chart
POST   /charts/:id/render               # Render chart (get image/data)
POST   /charts/from-query               # Generate chart via natural language query
```

#### Dashboard Management

```
GET    /dashboards                      # Get dashboard list
POST   /dashboards                      # Create dashboard
GET    /dashboards/:id                  # Get dashboard details
PATCH  /dashboards/:id                  # Update dashboard
DELETE /dashboards/:id                  # Delete dashboard
POST   /dashboards/:id/publish          # Publish dashboard
POST   /dashboards/:id/share            # Generate sharing link
```

#### Reports and Subscriptions

```
GET    /reports                         # Get report list
POST   /reports                         # Create scheduled report
GET    /reports/:id                     # Get report details
PATCH  /reports/:id                     # Update report configuration
POST   /reports/:id/run                 # Manually execute report
POST   /reports/:id/subscribe           # Subscribe to report
DELETE /reports/:id/subscribe           # Unsubscribe
```

### API Call Examples

```bash
# 1. Query data source list
curl -s -H "Authorization: Bearer $GRAPHIFY_API_KEY" \
  "$GRAPHIFY_API_BASE/datasources" | jq .

# 2. Create chart via natural language
curl -s -X POST "$GRAPHIFY_API_BASE/charts/from-query" \
  -H "Authorization: Bearer $GRAPHIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "datasource_id": "ds_xxxxxxxx",
    "query": "最近30天每日交易量趋势，按币种分色",
    "chart_type": "line",
    "options": {
      "title": "30日交易量趋势",
      "show_legend": true,
      "timezone": "UTC+8"
    }
  }' | jq .

# 3. Create dashboard
curl -s -X POST "$GRAPHIFY_API_BASE/dashboards" \
  -H "Authorization: Bearer $GRAPHIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "交易监控看板",
    "description": "实时交易数据监控与异常告警",
    "layout": "grid",
    "charts": [
      {"chart_id": "ch_xxx1", "position": {"x": 0, "y": 0, "w": 6, "h": 4}},
      {"chart_id": "ch_xxx2", "position": {"x": 6, "y": 0, "w": 6, "h": 4}}
    ],
    "refresh_interval": 300
  }' | jq .
```

### API Response Format

```json
// Success response
{
  "status": "ok",
  "data": {
    // Specific business data
  },
  "meta": {
    "request_id": "req_xxxxxxxx",
    "timestamp": "2026-05-09T10:00:00Z"
  }
}

// Error response
{
  "status": "error",
  "error": {
    "code": "datasource_unreachable",
    "message": "无法连接到数据源，请检查网络和凭证",
    "details": {
      "datasource_id": "ds_xxxxxxxx",
      "last_success": "2026-05-09T09:30:00Z"
    }
  },
  "meta": {
    "request_id": "req_xxxxxxxx"
  }
}
```

### Error Code Reference

| Error Code | Description | Resolution |
|------------|-------------|------------|
| `invalid_api_key` | Invalid API Key | Check environment variables and key validity |
| `datasource_unreachable` | Data source unreachable | Check data source network and credentials |
| `query_execution_error` | Query execution failed | Check SQL/query syntax |
| `chart_render_error` | Chart rendering failed | Check chart configuration parameters |
| `rate_limit_exceeded` | Rate limit exceeded | Wait `retry_after` seconds before retrying |
| `workspace_full` | Dashboard count limit reached | Upgrade plan or clean up unused dashboards |

---

## 🔌 Data Source Configuration

### Supported Data Source Types

| Type | Configuration Points | Use Case |
|------|---------------------|----------|
| **PostgreSQL** | Connection string, SSL mode, read-only user recommended | Transaction data, user data |
| **MySQL** | Host, port, database name, credentials | Web application data |
| **MongoDB** | Connection URI, database name, collection name | Logs, time-series data |
| **BigQuery** | Service account JSON Key, project ID | Large-scale data analysis |
| **CSV/Excel** | File upload, delimiter, encoding | One-time/temporary data |
| **REST API** | URL, authentication method, JSON Path mapping | External API data ingestion |

### Recommended Security Configuration

```yaml
# Data source connection best practices
datasource_security:
  - Use read-only account (database data sources)
  - Limit IP whitelist (only allow Graphify egress IPs)
  - Regular password/key rotation (every 90 days)
  - Mark sensitive data columns with masking rules
  - Set query timeout (default 60s)
```

### Data Source Connection Example (PostgreSQL)

```bash
# Add PostgreSQL data source via API
curl -s -X POST "$GRAPHIFY_API_BASE/datasources" \
  -H "Authorization: Bearer $GRAPHIFY_API_KEY" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "prod-trading-db",
    "type": "postgresql",
    "config": {
      "host": "DB_HOST",
      "port": 5432,
      "database": "trading",
      "username": "graphify_reader",
      "password": "***",
      "ssl_mode": "require",
      "max_connections": 5,
      "query_timeout": 60
    },
    "tables": [
      {"schema": "public", "table": "trades"},
      {"schema": "public", "table": "orders"},
      {"schema": "public", "table": "balances"}
    ]
  }' | jq .
```

> ⚠️ **Lesson Learned**: Initially used a high-privilege account on the primary database. A faulty query from Graphify (full table scan without LIMIT) caused database CPU to spike to 100%. Lesson: **Data source connections must use read-only accounts + set query timeouts + add query LIMIT constraints**.

---

## 📈 Chart Generation and Dashboards

### Natural Language Query Best Practices

```markdown
✅ Good queries:
  "最近7天各币种交易量占比（饼图）"
  "BTC 和 ETH 的 30 日价格走势对比（折线图）"
  "按小时统计过去 24 小时的交易笔数热力图"
  "展示前 10 大用户持仓占比（水平柱状图）"
  "每日净利润趋势，标注超过 2σ 的异常点"

❌ Bad queries:
  "显示数据" (too vague)
  "做个图" (no data or chart type specified)
  "帮我分析" (no clear visualization requirement)
```

### Common Chart Types Quick Reference

| Chart Type | Use Case | Parameter Points |
|------------|----------|------------------|
| `line` | Time series trends | X-axis time field, Y-axis value field, grouping field |
| `bar` | Categorical comparison | X-axis category field, Y-axis value field, horizontal/vertical |
| `pie` | Proportion distribution | Category field, value field, show percentage or not |
| `scatter` | Correlation analysis | X-axis field, Y-axis field, point size/color field |
| `heatmap` | Density/matrix | X/Y axis categories, color mapping field |
| `area` | Cumulative trends | Same as line chart, supports stacking |
| `table` | Data details | Column selection, sorting, pagination, conditional formatting |

### Dashboard Layout Reference

```yaml
# Trading monitoring dashboard layout reference
dashboard_layout:
  header: "📊 交易监控中心"
  refresh_interval: 300  # 5 minute auto-refresh

  rows:
    - title: "概览指标"
      charts:
        - 总资产（大数字卡片）
        - 今日盈亏（大数字卡片 + 涨跌色）
        - 交易次数（大数字卡片）
        - 胜率（大数字卡片 + 百分比）

    - title: "趋势分析"
      charts:
        - 资产净值曲线（折线图，6 个月）
        - 每日盈亏柱状图（柱状图，30 天）
        - BTC/ETH 价格叠加（双轴折线图）
        - 波动率热力图（热力图，24h×7d）

    - title: "持仓分析"
      charts:
        - 持仓占比（饼图）
        - 各币种盈亏（水平柱状图）
        - 风险敞口（散点图，按风险等级着色）
        - 交易对相关性矩阵（热力图）
```

### Chart Creation Example (Python SDK)

```python
import requests

GRAPHIFY_API_BASE = "https://api.graphify.io/v1"
HEADERS = {"Authorization": f"Bearer {GRAPHIFY_API_KEY}"}

def create_chart_from_query(datasource_id: str, query: str, chart_type: str = "line"):
    """Create chart via natural language query"""
    resp = requests.post(
        f"{GRAPHIFY_API_BASE}/charts/from-query",
        headers=HEADERS,
        json={
            "datasource_id": datasource_id,
            "query": query,
            "chart_type": chart_type,
            "options": {
                "title": query[:30],
                "show_legend": True,
                "theme": "dark"
            }
        }
    )
    return resp.json()

def render_chart(chart_id: str, format: str = "png"):
    """Render chart as image"""
    resp = requests.post(
        f"{GRAPHIFY_API_BASE}/charts/{chart_id}/render",
        headers=HEADERS,
        json={"format": format, "width": 1200, "height": 600}
    )
    return resp.json()

# Usage example
result = create_chart_from_query(
    datasource_id="ds_xxxxxxxx",
    query="最近30天每日交易量趋势",
    chart_type="line"
)
chart_id = result["data"]["chart_id"]

# Render as image link
image_data = render_chart(chart_id, "png")
print(f"图表链接: {image_data['data']['url']}")
```

---

## 🔄 Automated Reporting Workflow

### Scheduled Report Configuration

```yaml
# Daily report configuration example
daily_report:
  name: "每日交易总结"
  schedule: "0 9 * * *"           # Every morning at 9 AM (Cron expression)
  timezone: "Asia/Shanghai"

  charts:
    - chart_id: "ch_daily_pnl"     # Daily P&L
    - chart_id: "ch_asset_curve"   # Asset curve
    - chart_id: "ch_position"      # Position distribution
    - chart_id: "ch_trade_count"   # Trade frequency

  delivery:
    - type: email
      recipients: ["team@example.com"]
      subject: "📊 每日交易总结 - {{date}}"
    - type: webhook
      url: "https://example.com/webhook/graphify-report"
    - type: slack
      webhook_url: "https://hooks.slack.com/services/xxx"
      channel: "#trading-reports"
```

### Report and Sub-agent Collaboration Workflow

```
Main Hermes:
  "Xiaofu, generate a weekly trading analysis report"

Xiaofu (Financial Analysis):
  1. Analyze this week's trading data
  2. Organize key metrics (profit rate, max drawdown, win rate)
  3. Summarize market judgments and strategy recommendations
  4. → Output structured analysis results

Main Hermes → Graphify MCP:
  1. Generate dashboards/charts based on analysis results
  2. Set up scheduled refresh (daily report)
  3. Configure subscription push (email + Slack)

Final delivery:
  → Human user receives:
    📧 Email: Weekly trading report (with Graphify dashboard link)
    💬 Slack: Dashboard preview + key metrics summary
```

### Webhook Event Notifications

| Event | Trigger Condition | Purpose |
|-------|-------------------|---------|
| `chart.rendered` | Chart rendering complete | Get render result notification |
| `dashboard.published` | Dashboard published | Notify team to view |
| `report.completed` | Scheduled report execution complete | Trigger subsequent processing |
| `datasource.error` | Data source connection exception | Alert notification |
| `anomaly.detected` | Data anomaly auto-detected | Anomaly alert |

---

## 🔧 MCP Integration

### Graphify MCP Server

```yaml
# Configure in sub-agent profile (recommended for Xiaofu or botstreet)
mcp_servers:
  graphify-api:
    command: /usr/local/bin/graphify-mcp
    args: []
    env:
      GRAPHIFY_API_KEY: ${GRAPHIFY_API_KEY}
      GRAPHIFY_API_BASE: ${GRAPHIFY_API_BASE}
      GRAPHIFY_WORKSPACE_ID: ${GRAPHIFY_WORKSPACE_ID}
```

### MCP Exposed Operations

| Operation | Description | Parameters |
|-----------|-------------|------------|
| `list_dashboards` | View dashboard list | `workspace_id` |
| `get_dashboard` | Get dashboard details | `dashboard_id` |
| `create_chart` | Create chart | `datasource_id`, `query`, `chart_type` |
| `create_dashboard` | Create dashboard | `name`, `charts`, `layout` |
| `render_chart` | Render chart image | `chart_id`, `format` |
| `publish_dashboard` | Publish dashboard | `dashboard_id` |
| `share_dashboard` | Generate sharing link | `dashboard_id`, `password` |
| `run_report` | Execute report | `report_id` |
| `list_datasources` | View data sources | No parameters |
| `test_datasource` | Test data source connection | `datasource_id` |

### MCP Call Example (Hermes Agent Perspective)

```
# User: Xiaofu, turn this week's analysis results into a dashboard
# Xiaofu internal MCP call:
create_chart(datasource_id="ds_trading", query="本周每日盈亏趋势", chart_type="line")
create_chart(datasource_id="ds_trading", query="各币种持仓占比", chart_type="pie")
create_dashboard(name="本周交易报告", charts=[...], layout={...})
publish_dashboard(dashboard_id="db_xxx")

# User: Share this dashboard with the team
share_dashboard(dashboard_id="db_xxx", password="<SHARE_PASSWORD>")
```

---

## 🔍 Common Issues Troubleshooting

### 1. Data Source Connection Failed

```
Symptom: Adding data source returns `datasource_unreachable`
Troubleshooting:
  ✓ Check if data source hostname/IP is correct
  ✓ Confirm Graphify egress IP is added to database whitelist
  ✓ Check if authentication credentials are correct
  ✓ Test database port connectivity (telnet <host> <port>)
  ✓ View last_success time in data source error details
```

### 2. Chart Query Returns Empty

```
Symptom: Natural language query succeeds but chart shows no data
Troubleshooting:
  ✓ Confirm data source actually has data (run SQL directly to verify)
  ✓ Check if query time range is reasonable
  ✓ Confirm table field names match query terminology
  ✓ Try simpler queries to troubleshoot step by step
```

### 3. Chart Rendering Slow or Timeout

```
Symptom: Rendering chart takes over 30 seconds or returns timeout
Troubleshooting:
  ✓ Does query involve large table full scan (add LIMIT/time filter)
  ✓ Are there too many chart data points (reduce granularity/aggregate)
  ✓ Data source's own query performance
  ✓ Try using cache (set cache_ttl)
```

### 4. Dashboard Sharing Link Invalid

```
Symptom: Shared dashboard link inaccessible to users
Troubleshooting:
  ✓ Is dashboard published
  ✓ Is sharing link expired (check expiry setting)
  ✓ Is password correct (if password access is set)
  ✓ Does sharing permission include target users
```

---

## 🕳️ Lessons Learned

### 1. Data Source Queries Causing High Database Load

**Symptom**: When Xiaofu calls Graphify to generate complex charts, database CPU spikes to 90%+, affecting normal trading operations.

**Cause**: Natural language queries generated SQL without LIMIT constraints, and joined multiple large tables, producing high-cost JOIN queries.

**Solution**:
```yaml
# 1. Set query timeout and LIMIT in data source configuration
datasource_config:
  query_timeout: 30          # Query timeout 30 seconds
  default_limit: 10000       # Default max return rows

# 2. Use read replica instead of primary
datasource:
  host: "trading-replica.example.com"  # Read replica
```

### 2. Too Many Charts Causing Slow Dashboard Loading

**Symptom**: Trading monitoring dashboard with 20+ charts takes over 15 seconds to load initially.

**Cause**: All charts render simultaneously, putting pressure on browser and API concurrency.

**Solution**:
```yaml
# Dashboard optimization strategy
dashboard_optimization:
  - Control single dashboard chart count (recommend ≤ 12)
  - Enable chart lazy loading (only load charts in viewport)
  - Set appropriate data cache (cache_ttl: 300s)
  - Split into multiple themed dashboards (e.g., Overview / Positions / Risk)
```

### 3. Scheduled Report Timezone Issue

**Symptom**: Configured daily report to send at UTC+8 9:00, but actual send time is UTC 9:00 (i.e., UTC+8 17:00).

**Cause**: Report scheduling didn't set `timezone` parameter, defaulting to UTC.

**Solution**:
```json
{
  "schedule": "0 9 * * *",
  "timezone": "Asia/Shanghai"  // Explicitly specify timezone
}
```

### 4. Chart Data Masking Omission

**Symptom**: Dashboard shared with clients accidentally displayed internal risk metrics and trader names.

**Cause**: Data source queries didn't add masking rules, directly exposing risk-related sensitive fields.

**Solution**:
```yaml
# Data source field masking configuration
datasource_masking:
  enabled: true
  rules:
    - column: "trader_name"
      mask: "***"
    - column: "risk_score"
      mask: "round(value, 0)"
    - column: "internal_notes"
      action: exclude  # Completely exclude this column
```

---

## 📝 Summary

| Item | Recommendation |
|------|----------------|
| Data Source | Read-only + timeout + LIMIT, prefer read replicas |
| Charts | Control count ≤ 12/dashboard, enable cache and lazy loading |
| Dashboards | Split by theme (Overview/Positions/Risk), set publish review |
| Reports | Explicitly specify timezone, configure anomaly alerts |
| Security | Sensitive field masking, sharing links with password and expiry |
| Collaboration | Xiaofu analysis → Graphify visualization → Auto push |

> **Graphify makes data speak**—combined with Xiaofu's analysis capabilities and automated reporting, data that previously required manual organization becomes real-time, interactive decision dashboards.
