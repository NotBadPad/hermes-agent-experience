# Hermes 配置详解

## 配置文件位置

```
~/.hermes/
├── config.yaml        ← 主配置文件
├── .env               ← 环境变量（API Key 等敏感信息）
├── auth.json          ← 认证信息
├── skills/            ← 全局技能目录
├── profiles/          ← 子代理配置目录
│   ├── <name>/
│   │   ├── config.yaml
│   │   ├── .env
│   │   └── skills/
│   └── ...
├── cron/              ← 定时任务
├── logs/              ← 日志
├── sessions/          ← 会话记录
└── memories/          ← 持久化记忆
```

## 主配置 config.yaml 核心字段

### 模型配置

```yaml
model:
  default: deepseek-v4-flash          # 默认模型
  provider: deepseek                   # 提供商（deepseek/custom/openai等）
  base_url: https://api.deepseek.com/v1
providers: {}                          # 额外提供商配置
fallback_providers: []                 # 降级提供商
```

### Agent 行为

```yaml
agent:
  max_turns: 90                        # 单次会话最大轮次
  gateway_timeout: 1800                # Gateway超时（秒）
  verbose: false                       # 是否输出详细日志
  reasoning_effort: medium             # 推理强度（low/medium/high）
  tool_use_enforcement: auto           # 工具使用策略
```

### 工具集

```yaml
toolsets:
- hermes-cli                           # CLI工具
# 子代理可以扩展
platform_toolsets:
  cli:
  - hermes-cli
  telegram:
  - hermes-telegram
  discord:
  - hermes-discord
```

### 终端配置

```yaml
terminal:
  backend: local                        # 终端后端（local/docker/ssh）
  cwd: .                                # 默认工作目录
  timeout: 180                          # 命令超时（秒）
  auto_source_bashrc: true              # 自动加载bashrc
```

### 记忆系统

```yaml
memory:
  memory_enabled: true                  # 启用持久记忆
  user_profile_enabled: true            # 启用用户画像
  memory_char_limit: 2200               # 记忆字符上限
  user_char_limit: 1375                 # 用户画像字符上限
```

### 子代理配置

子代理放在 `~/.hermes/profiles/<name>/config.yaml`，与主配置结构相同，但只包含差异部分：

```yaml
model:
  default: gpt-5.4                      # 子代理使用的模型
  provider: custom
  base_url: https://ai.opendoor.cn/v1
  api_key: ${OPENDOOR_API_KEY}
toolsets:
- hermes-cli
- terminal
- file
agent:
  max_turns: 90
display:
  personality: technical
memory:
  memory_enabled: true
  user_profile_enabled: false
```

### 自定义模型提供商

```yaml
custom_providers:
- name: mimo-v2.5-pro
  base_url: https://token-plan-sgp.xiaomimimo.com/v1
  api_key: ${XIAOMI_API_KEY}
  api_mode: chat_completions
  model: mimo-v2.5-pro
- name: opendoor
  base_url: https://ai.opendoor.cn/v1
  api_key: ${OPENDOOR_API_KEY}
  api_mode: chat_completions
```

### MCP 服务器配置

```yaml
mcp_servers:
  vibe-trading:
    command: vibe-trading-mcp
```

### 关键配置项速查

| 配置项 | 说明 | 默认值 |
|--------|------|--------|
| `model.default` | 默认模型名 | — |
| `model.provider` | 模型提供商 | — |
| `agent.max_turns` | 最大对话轮次 | 90 |
| `agent.reasoning_effort` | 推理强度 | medium |
| `terminal.backend` | 终端后端 | local |
| `terminal.cwd` | 工作目录 | . |
| `memory.memory_enabled` | 启用记忆 | true |
| `memory.memory_char_limit` | 记忆上限 | 2200 |
| `display.personality` | 回复风格 | — |
