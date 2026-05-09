# 📊 Graphify 平台集成

> **目录**: `06-integrations/` — 平台接入经验
> **相关子代理**: 小开（数据可视化开发）、小运（服务部署）
> **最后更新**: 2026-05

本文档记录了 Hermes Agent 接入 Graphify 平台的经验，包括平台介绍、API 对接、数据源配置、图表生成、看板管理及踩坑记录。

---

## 📋 目录

1. [平台概览](#-平台概览)
2. [接入流程](#-接入流程)
3. [API 对接](#-api-对接)
4. [数据源配置](#-数据源配置)
5. [图表生成与看板](#-图表生成与看板)
6. [自动报表工作流](#-自动报表工作流)
7. [MCP 集成](#-mcp-集成)
8. [常见问题排查](#-常见问题排查)
9. [踩坑记录](#-踩坑记录)

---

## 🏪 平台概览

### Graphify 是什么

Graphify 是一个 AI 驱动的数据可视化平台，支持连接多种数据源（数据库、API、CSV 等），通过自然语言生成图表和仪表盘。与虾345 和 Bot Street 不同，Graphify 是**数据消费和分析展示**平台——小富的分析结果通过 Graphify 生成可视化看板，供团队或客户查看。

### 平台定位

| 维度 | 说明 |
|------|------|
| 核心功能 | 自然语言 → 图表 / 自动看板 / 定时报表 |
| 数据源支持 | MySQL, PostgreSQL, MongoDB, BigQuery, CSV, REST API |
| 图表类型 | 折线图、柱状图、饼图、散点图、热力图、地图、表格等 30+ 种 |
| 输出格式 | PNG, SVG, PDF, HTML, 嵌入式 iframe |
| 分享方式 | 公开链接 / 密码分享 / 嵌入 / 邮件订阅 |
| AI 能力 | 自然语言查询、自动图表推荐、异常检测标注 |
| 定价模式 | 按看板数 + 数据量 + AI 查询次数 |

### 环境变量

| 变量 | 说明 | 示例 |
|------|------|------|
| `GRAPHIFY_API_BASE` | API 基础地址 | `https://api.graphify.io/v1` |
| `GRAPHIFY_API_KEY` | API Key | `gfk_xxxxxxxxxxxx` |
| `GRAPHIFY_WORKSPACE_ID` | 工作空间 ID | `ws_xxxxxxxx` |
| `GRAPHIFY_SECRET_KEY` | Webhook 签名密钥 | `***` |

---

## 🚀 接入流程

### 完整接入步骤

```
步骤 1: 注册 Graphify 账号
  → 访问 https://graphify.io → 注册 → 创建工作空间

步骤 2: 连接数据源
  → 工作台 → 数据源管理 → 添加数据源（数据库/API/文件）

步骤 3: 获取 API 凭证
  → 设置 → API 管理 → 生成 API Key

步骤 4: 环境配置
  → 在 .env 文件中配置 GRAPHIFY_* 环境变量

步骤 5: 测试连通性
  → 调用 /v1/workspaces/{ws_id} 验证

步骤 6: 配置子代理
  → 在小富或 botstreet 的 profile 中添加 Graphify MCP

步骤 7: 创建第一个看板
  → 用自然语言指令生成图表 → 调整配置 → 发布看板

步骤 8: 设置自动报表
  → 配置定时刷新 → 设置邮件/Webhook 订阅
```

### 前置条件

- ✅ 已注册 Graphify 账号并创建工作空间
- ✅ 已连接至少一个数据源
- ✅ 已获取 API Key
- ✅ （可选）公网可访问的 Webhook 端点（用于事件通知）

---

## 🔌 API 对接

### API 基本信息

| 项目 | 内容 |
|------|------|
| 基础 URL | `https://api.graphify.io/v1` |
| 认证方式 | Bearer Token（`Authorization: Bearer <api_key>`） |
| 请求格式 | `application/json` |
| 响应格式 | `application/json` |
| 速率限制 | 60 req/min（标准）/ 300 req/min（专业版） |

### 核心 API 端点

#### 数据源管理

```
GET    /datasources                     # 获取数据源列表
POST   /datasources                     # 添加数据源
GET    /datasources/:id                 # 获取数据源详情
PATCH  /datasources/:id                 # 更新数据源配置
DELETE /datasources/:id                 # 删除数据源
POST   /datasources/:id/test            # 测试数据源连接
```

#### 图表管理

```
GET    /charts                          # 获取图表列表
POST   /charts                          # 创建图表
GET    /charts/:id                      # 获取图表详情
PATCH  /charts/:id                      # 更新图表配置
DELETE /charts/:id                      # 删除图表
POST   /charts/:id/render               # 渲染图表（获取图片/数据）
POST   /charts/from-query               # 通过自然语言查询生成图表
```

#### 看板管理

```
GET    /dashboards                      # 获取看板列表
POST   /dashboards                      # 创建看板
GET    /dashboards/:id                  # 获取看板详情
PATCH  /dashboards/:id                  # 更新看板
DELETE /dashboards/:id                  # 删除看板
POST   /dashboards/:id/publish          # 发布看板
POST   /dashboards/:id/share            # 生成分享链接
```

#### 报表与订阅

```
GET    /reports                         # 获取报表列表
POST   /reports                         # 创建定时报表
GET    /reports/:id                     # 获取报表详情
PATCH  /reports/:id                     # 更新报表配置
POST   /reports/:id/run                 # 手动执行报表
POST   /reports/:id/subscribe           # 订阅报表
DELETE /reports/:id/subscribe           # 取消订阅
```

### API 调用示例

```bash
# 1. 查询数据源列表
curl -s -H "Authorization: Bearer $GRAPHIFY_API_KEY" \
  "$GRAPHIFY_API_BASE/datasources" | jq .

# 2. 通过自然语言创建图表
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

# 3. 创建看板
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

### API 响应格式

```json
// 成功响应
{
  "status": "ok",
  "data": {
    // 具体业务数据
  },
  "meta": {
    "request_id": "req_xxxxxxxx",
    "timestamp": "2026-05-09T10:00:00Z"
  }
}

// 错误响应
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

### 错误码表

| 错误码 | 说明 | 处理方式 |
|--------|------|----------|
| `invalid_api_key` | API Key 无效 | 检查环境变量和 Key 有效期 |
| `datasource_unreachable` | 数据源不可达 | 检查数据源网络和凭证 |
| `query_execution_error` | 查询执行失败 | 检查 SQL/查询语句语法 |
| `chart_render_error` | 图表渲染失败 | 检查图表配置参数 |
| `rate_limit_exceeded` | 请求频率超限 | 等待 `retry_after` 秒后重试 |
| `workspace_full` | 看板数量已达上限 | 升级套餐或清理无用看板 |

---

## 🔌 数据源配置

### 支持的数据源类型

| 类型 | 配置要点 | 适用场景 |
|------|----------|----------|
| **PostgreSQL** | 连接串、SSL 模式、只读用户推荐 | 交易数据、用户数据 |
| **MySQL** | 主机、端口、数据库名、凭据 | Web 应用数据 |
| **MongoDB** | 连接 URI、数据库名、集合名 | 日志、时序数据 |
| **BigQuery** | 服务账号 JSON Key、项目 ID | 大规模数据分析 |
| **CSV/Excel** | 文件上传、分隔符、编码 | 一次性/临时数据 |
| **REST API** | URL、认证方式、JSON Path 映射 | 外部 API 数据接入 |

### 推荐的安全配置

```yaml
# 数据源连接最佳实践
datasource_security:
  - 使用只读账号（数据库数据源）
  - 限制 IP 白名单（仅允许 Graphify 出口 IP）
  - 定期轮换密码/密钥（每 90 天）
  - 敏感数据列标记脱敏规则
  - 设置查询超时（默认 60s）
```

### 数据源连接示例（PostgreSQL）

```bash
# 通过 API 添加 PostgreSQL 数据源
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

> ⚠️ **踩坑记录**：最初使用了主库的高权限账号，Graphify 的一次错误查询（全表扫描无 LIMIT）导致数据库 CPU 飙升到 100%。教训：**数据源连接务必使用只读账号 + 设置查询超时 + 添加查询 LIMIT 约束**。

---

## 📈 图表生成与看板

### 自然语言查询最佳实践

```markdown
✅ 好的查询:
  "最近7天各币种交易量占比（饼图）"
  "BTC 和 ETH 的 30 日价格走势对比（折线图）"
  "按小时统计过去 24 小时的交易笔数热力图"
  "展示前 10 大用户持仓占比（水平柱状图）"
  "每日净利润趋势，标注超过 2σ 的异常点"

❌ 不好的查询:
  "显示数据"（太模糊）
  "做个图"（没有指定数据和图表类型）
  "帮我分析"（没有明确的可视化需求）
```

### 常用图表类型速查

| 图表类型 | 适用场景 | 参数要点 |
|----------|----------|----------|
| `line` | 时间序列趋势 | x 轴时间字段、y 轴数值字段、分组字段 |
| `bar` | 分类对比 | x 轴分类字段、y 轴数值字段、水平/垂直 |
| `pie` | 占比分布 | 分类字段、数值字段、是否显示百分比 |
| `scatter` | 相关性分析 | x 轴字段、y 轴字段、点大小/颜色字段 |
| `heatmap` | 密度/矩阵 | x/y 轴分类、颜色映射字段 |
| `area` | 累积趋势 | 同折线图，支持堆叠 |
| `table` | 数据明细 | 列选择、排序、分页、条件格式 |

### 看板布局方案

```yaml
# 交易监控看板布局参考
dashboard_layout:
  header: "📊 交易监控中心"
  refresh_interval: 300  # 5 分钟自动刷新
  
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

### 图表创建示例（Python SDK）

```python
import requests

GRAPHIFY_API_BASE = "https://api.graphify.io/v1"
HEADERS = {"Authorization": f"Bearer {GRAPHIFY_API_KEY}"}

def create_chart_from_query(datasource_id: str, query: str, chart_type: str = "line"):
    """通过自然语言查询创建图表"""
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
    """渲染图表为图片"""
    resp = requests.post(
        f"{GRAPHIFY_API_BASE}/charts/{chart_id}/render",
        headers=HEADERS,
        json={"format": format, "width": 1200, "height": 600}
    )
    return resp.json()

# 使用示例
result = create_chart_from_query(
    datasource_id="ds_xxxxxxxx",
    query="最近30天每日交易量趋势",
    chart_type="line"
)
chart_id = result["data"]["chart_id"]

# 渲染为图片链接
image_data = render_chart(chart_id, "png")
print(f"图表链接: {image_data['data']['url']}")
```

---

## 🔄 自动报表工作流

### 定时报表配置

```yaml
# 日报配置示例
daily_report:
  name: "每日交易总结"
  schedule: "0 9 * * *"           # 每天早上 9 点（Cron 表达式）
  timezone: "Asia/Shanghai"
  
  charts:
    - chart_id: "ch_daily_pnl"     # 每日盈亏
    - chart_id: "ch_asset_curve"   # 资产曲线
    - chart_id: "ch_position"      # 持仓分布
    - chart_id: "ch_trade_count"   # 交易频率
  
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

### 报表与子代理协作流程

```
主 Hermes:
  "小富，生成一份本周交易分析报告"

小富（金融分析）:
  1. 分析本周交易数据
  2. 整理关键指标（盈利率、最大回撤、胜率）
  3. 总结市场判断和策略建议
  4. → 输出结构化分析结果

主 Hermes → Graphify MCP:
  1. 根据分析结果生成看板/图表
  2. 设置定时刷新（日报）
  3. 配置订阅推送（邮件+Slack）

最终交付:
  → 人类用户收到:
    📧 邮件: 本周交易报告（含 Graphify 看板链接）
    💬 Slack: 看板预览 + 关键指标摘要
```

### Webhook 事件通知

| 事件 | 触发条件 | 用途 |
|------|----------|------|
| `chart.rendered` | 图表渲染完成 | 获取渲染结果通知 |
| `dashboard.published` | 看板发布 | 通知团队查看 |
| `report.completed` | 定时报表执行完成 | 触发后续处理流程 |
| `datasource.error` | 数据源连接异常 | 告警通知 |
| `anomaly.detected` | 数据异常自动检测 | 异常告警 |

---

## 🔧 MCP 集成

### Graphify MCP 服务器

```yaml
# 在子代理 profile 中配置（建议配置给小富或 botstreet）
mcp_servers:
  graphify-api:
    command: /usr/local/bin/graphify-mcp
    args: []
    env:
      GRAPHIFY_API_KEY: ${GRAPHIFY_API_KEY}
      GRAPHIFY_API_BASE: ${GRAPHIFY_API_BASE}
      GRAPHIFY_WORKSPACE_ID: ${GRAPHIFY_WORKSPACE_ID}
```

### MCP 暴露的操作

| 操作 | 说明 | 参数 |
|------|------|------|
| `list_dashboards` | 查看看板列表 | `workspace_id` |
| `get_dashboard` | 获取看板详情 | `dashboard_id` |
| `create_chart` | 创建图表 | `datasource_id`, `query`, `chart_type` |
| `create_dashboard` | 创建看板 | `name`, `charts`, `layout` |
| `render_chart` | 渲染图表图片 | `chart_id`, `format` |
| `publish_dashboard` | 发布看板 | `dashboard_id` |
| `share_dashboard` | 生成分享链接 | `dashboard_id`, `password` |
| `run_report` | 执行报表 | `report_id` |
| `list_datasources` | 查看数据源 | 无参数 |
| `test_datasource` | 测试数据源连接 | `datasource_id` |

### MCP 调用示例（Hermes Agent 视角）

```
# 用户：小富，把本周的分析结果做成看板
# 小富内部调用 MCP:
create_chart(datasource_id="ds_trading", query="本周每日盈亏趋势", chart_type="line")
create_chart(datasource_id="ds_trading", query="各币种持仓占比", chart_type="pie")
create_dashboard(name="本周交易报告", charts=[...], layout={...})
publish_dashboard(dashboard_id="db_xxx")

# 用户：把这个看板分享给团队
share_dashboard(dashboard_id="db_xxx", password="team2026")
```

---

## 🔍 常见问题排查

### 1. 数据源连接失败

```
症状: 添加数据源时返回 `datasource_unreachable`
排查:
  ✓ 检查数据源主机名/IP 是否正确
  ✓ 确认 Graphify 出口 IP 已加入数据库白名单
  ✓ 检查认证凭据是否正确
  ✓ 测试数据库端口连通性（telnet <host> <port>）
  ✓ 查看数据源错误详情中的 last_success 时间
```

### 2. 图表查询返回空

```
症状: 自然语言查询成功但图表显示无数据
排查:
  ✓ 确认数据源中确实有数据（直接跑 SQL 验证）
  ✓ 检查查询条件的时间范围是否合理
  ✓ 确认表中字段名与查询用语匹配
  ✓ 尝试更简单的查询逐步排错
```

### 3. 图表渲染慢或超时

```
症状: 渲染图表耗时超过 30 秒或返回超时
排查:
  ✓ 查询是否涉及大表全表扫描（加 LIMIT/时间过滤）
  ✓ 图表数据点是否过多（降低粒度/聚合）
  ✓ 数据源本身的查询性能
  ✓ 尝试使用缓存（设置 cache_ttl）
```

### 4. 看板分享链接失效

```
症状: 分享给用户的看板链接无法访问
排查:
  ✓ 看板是否已发布（publish）
  ✓ 分享链接是否过期（检查 expiry 设置）
  ✓ 密码是否正确（如设置了密码访问）
  ✓ 分享权限设置是否包含目标用户
```

---

## 🕳️ 踩坑记录

### 1. 数据源查询导致数据库负载过高

**现象**：小富调用 Graphify 生成复杂图表时，数据库 CPU 飙升至 90%+，影响正常交易业务。

**原因**：自然语言查询生成的 SQL 未做 LIMIT 限制，且关联了多张大表，产生了高成本的 JOIN 查询。

**解决方案**：
```yaml
# 1. 数据源配置中设置查询超时和 LIMIT
datasource_config:
  query_timeout: 30          # 查询超时 30 秒
  default_limit: 10000       # 默认最大返回行数
  
# 2. 使用只读副本而非主库
datasource:
  host: "trading-replica.example.com"  # 只读副本
```

### 2. 图表数量过多导致看板加载缓慢

**现象**：交易监控看板包含 20+ 图表，首次加载耗时超过 15 秒。

**原因**：所有图表同时渲染，浏览器和 API 并发压力大。

**解决方案**：
```yaml
# 看板优化策略
dashboard_optimization:
  - 控制单个看板图表数量（建议 ≤ 12 个）
  - 启用图表懒加载（仅加载视口内的图表）
  - 设置合适的数据缓存（cache_ttl: 300s）
  - 分拆为多个主题看板（如：概览 / 持仓 / 风控）
```

### 3. 定时报表时区问题

**现象**：配置的每日报表在 UTC+8 9:00 发送，但实际发送时间是 UTC 时间 9:00（即 UTC+8 17:00）。

**原因**：报表调度时未设置 `timezone` 参数，默认使用 UTC。

**解决方案**：
```json
{
  "schedule": "0 9 * * *",
  "timezone": "Asia/Shanghai"  // 显式指定时区
}
```

### 4. 图表数据脱敏遗漏

**现象**：分享给客户的看板中，意外显示了内部风控指标和交易员姓名。

**原因**：数据源的查询未添加脱敏规则，风控相关的敏感字段直接暴露。

**解决方案**：
```yaml
# 数据源字段脱敏配置
datasource_masking:
  enabled: true
  rules:
    - column: "trader_name"
      mask: "***"
    - column: "risk_score"
      mask: "round(value, 0)"
    - column: "internal_notes"
      action: exclude  # 完全排除此列
```

---

## 📝 总结

| 项目 | 建议 |
|------|------|
| 数据源 | 只读 + 超时 + LIMIT，优先使用只读副本 |
| 图表 | 控制数量 ≤ 12/看板，启用缓存和懒加载 |
| 看板 | 按主题分拆（概览/持仓/风控），设置发布审核 |
| 报表 | 显式指定时区，配置异常告警 |
| 安全 | 敏感字段脱敏，分享链接设置密码和时效 |
| 协作 | 小富分析 → Graphify 出图 → 自动推送 |

> **Graphify 让数据会说话**——配合小富的分析能力和自动报表，原本需要手动整理的数据变成了实时、可交互的决策看板。
