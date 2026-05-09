# 🛠️ Hermes 技能体系

> 技能（Skill）是 Hermes Agent 的能力单元。每个技能定义了一组工具、提示词和行为模式，让 Agent 能胜任特定领域的任务。本目录记录了 Hermes 内置技能清单以及自定义技能的编写方法。

---

## 目录

- [技能体系概览](#技能体系概览)
- [内置技能清单](#内置技能清单)
- [技能结构说明](#技能结构说明)
- [自定义技能编写](#自定义技能编写)
- [技能加载与调试](#技能加载与调试)
- [最佳实践](#最佳实践)

---

## 技能体系概览

Hermes 的技能体系采用分层设计：

```
技能
├── 通用技能（全局生效，所有会话自动加载）
│   ├── terminal           — 终端执行 & 文件操作
│   ├── file               — 文件读写 & 搜索
│   ├── web                — 网页请求 & 抓取
│   └── memory             — 持久记忆读写
│
├── 平台技能（按接入平台启用）
│   ├── hermes-cli         — CLI 交互
│   ├── hermes-telegram    — Telegram 平台
│   ├── hermes-discord     — Discord 平台
│   └── hermes-wechat      — 微信平台
│
├── 子代理专属技能（按角色启用）
│   ├── code-engineer      — 代码开发（小开）
│   ├── financial-analysis — 金融分析（小富）
│   ├── server-ops         — 运维管理（小运）
│   └── bot-street         — Bot 运营（botstreet）
│
└── 自定义技能（用户编写）
    └── my-custom-skill/   — 按模板编写
```

### 技能加载优先级

```
自定义技能 > 子代理专属技能 > 平台技能 > 通用技能
```

同名技能会覆盖，优先级高的生效。

---

## 内置技能清单

### 1. `terminal` — 终端执行

| 属性 | 值 |
|------|-----|
| 类型 | 通用技能 |
| 默认启用 | ✅ 是 |
| 用途 | 执行 shell 命令、脚本运行、安装依赖 |

**提供工具**：
- `run_command` — 执行任意 shell 命令，支持 stdout/stderr 捕获
- `run_script` — 执行脚本文件
- `check_output` — 检查命令输出，用于条件判断

**示例**：
```bash
# 运行命令
run_command("ls -la /home")

# 安装依赖
run_command("pip install requests")
```

> ⚠️ 安全提示：`terminal` 技能具有完整 shell 权限，请确保子代理沙箱隔离或信任限制。

---

### 2. `file` — 文件操作

| 属性 | 值 |
|------|-----|
| 类型 | 通用技能 |
| 默认启用 | ✅ 是 |
| 用途 | 读写文件、搜索内容、目录操作 |

**提供工具**：
- `read_file` — 读取文件内容（支持分页）
- `write_file` — 写入/覆盖文件
- `patch` — 精确替换编辑
- `search_files` — 全文搜索 / 文件名搜索
- `list_directory` — 列出目录内容

**使用建议**：
- 大文件使用 `offset` / `limit` 分页读取
- 修改文件优先使用 `patch`（精确的 find-and-replace），避免全量重写
- `search_files` 支持 content 搜索（rg）和 files 搜索（glob）

---

### 3. `web` — 网络请求

| 属性 | 值 |
|------|-----|
| 类型 | 通用技能 |
| 默认启用 | ✅ 是 |
| 用途 | HTTP 请求、网页抓取、API 调用 |

**提供工具**：
- `http_get` — GET 请求
- `http_post` — POST 请求
- `fetch_webpage` — 获取并解析网页内容

**常用场景**：
- 调用 REST API
- 抓取文档 / 公告
- 与外部服务交互

---

### 4. `memory` — 持久记忆

| 属性 | 值 |
|------|-----|
| 类型 | 通用技能 |
| 默认启用 | ✅ 是（可关闭） |
| 用途 | 跨会话保存和检索信息 |

**提供工具**：
- `remember` — 写入一条记忆
- `recall` — 检索相关记忆

**配置项**（`config.yaml`）：
```yaml
memory:
  memory_enabled: true          # 启用记忆
  user_profile_enabled: true   # 启用用户画像
  memory_char_limit: 2200      # 每条记忆最大字符
  user_char_limit: 1375        # 画像最大字符
```

---

### 5. `hermes-cli` — CLI 交互

| 属性 | 值 |
|------|-----|
| 类型 | 平台技能 |
| 默认启用 | ✅ 是（CLI 模式） |
| 用途 | 命令行输入输出、管道处理 |

提供标准的 CLI 输入输出处理能力，包括 ANSI 转义、进度条、彩色输出等。

---

### 6. `hermes-telegram` / `hermes-discord` / `hermes-wechat`

| 平台 | 技能名 | 说明 |
|------|--------|------|
| Telegram | `hermes-telegram` | 消息收发、Bot 指令、群组管理 |
| Discord | `hermes-discord` | 频道消息、Slash 命令、音视频 |
| 微信 | `hermes-wechat` | 微信消息处理、公众号管理 |

> 注意：微信平台（WeChat/Weixin）集成需要额外的兼容层支持。

---

## 技能结构说明

### 技能目录规范

每个技能是一个独立的目录，位于 `skills/` 或子代理配置的 `skills/` 下：

```
skills/
└── <skill-name>/
    ├── config.yaml          ← 技能配置（必选）
    ├── prompt.md            ← 技能提示词（可选）
    └── tools/               ← 自定义工具（可选）
        ├── tool_a.py
        └── tool_b.py
```

### `config.yaml` 模板

```yaml
# skills/<name>/config.yaml
name: my-skill                # 技能名称（唯一）
description: "技能描述"        # 简要说明
version: 1.0.0                # 版本号
enabled: true                 # 是否默认启用

# 触发条件（可选）
triggers:
  - keyword: "部署"
  - regex: "^(deploy|rollout|发布)"
  - intent: "deployment"

# 依赖的工具集
toolsets:
  - terminal
  - file

# 环境变量引用（可选）
env:
  MY_SKILL_KEY: ${MY_SKILL_ENV_VAR}

# 加载模式
load_mode: lazy                # eager | lazy（按需加载）
```

### `prompt.md` 模板

```markdown
# Skill: <name>

## 角色定义
你是 [技能领域] 专家。

## 能力范围
- 能力 1
- 能力 2
- 能力 3

## 约束条件
- 约束 1
- 约束 2

## 输出规范
- 格式要求
- 示例
```

---

## 自定义技能编写

### 快速创建

```bash
# 方式一：使用 Hermes CLI
hermes skill create my-custom-skill

# 方式二：手动创建
mkdir -p ~/.hermes/skills/my-custom-skill/{tools}
```

### 编写步骤

1. **创建技能目录** — 按上述规范创建
2. **编写 `config.yaml`** — 定义名称、触发条件、依赖工具
3. **编写 `prompt.md`** — 定义技能的行为提示词
4. **添加自定义工具**（可选）— 在 `tools/` 下编写 Python 工具函数
5. **启用技能** — 在 `config.yaml` 中设置 `enabled: true`

### 自定义工具示例

```python
# skills/my-custom-skill/tools/my_tool.py
from hermes.tool import tool

@tool(name="my_tool", description="我的自定义工具")
def my_tool(param1: str, param2: int = 10) -> str:
    """
    工具逻辑实现。

    Args:
        param1: 参数说明
        param2: 参数说明，默认 10

    Returns:
        处理结果
    """
    # 实现逻辑
    result = f"处理 {param1} × {param2}"
    return result
```

### 注册技能

在 `config.yaml` 中引用自定义技能：

```yaml
# ~/.hermes/config.yaml 或 profiles/<name>/config.yaml
skills:
  - my-custom-skill          # 引用自定义技能
```

---

## 技能加载与调试

### 查看已加载技能

```bash
hermes skill list            # 列出所有可用技能
hermes skill list --active   # 列出当前活跃技能
hermes skill info <name>     # 查看技能详情
```

### 技能调试

```bash
# 测试技能加载
hermes skill test my-custom-skill

# 查看技能日志
tail -f ~/.hermes/logs/skills.log

# 检查技能冲突
hermes skill check-conflicts
```

### 常见问题

| 问题 | 原因 | 解决 |
|------|------|------|
| 技能未生效 | 未在 config 中引用 | 添加 `skills: [skill-name]` |
| 工具冲突 | 多个技能提供同名工具 | 检查优先级设置 |
| 技能加载失败 | config.yaml 格式错误 | 用 `hermes skill test` 验证 |
| 环境变量缺失 | `$` 引用但未设置 | 检查 `.env` 文件 |

---

## 最佳实践

### 1. 技能粒度控制

- **一个技能只做一件事**——保持职责单一，便于复用和测试
- **不要在一次技能中混入不相关的工具**——例如终端操作和网络请求应分为不同技能

### 2. 提示词设计

- 在 `prompt.md` 中明确技能的**角色**、**能力边界**和**输出规范**
- 使用具体示例指导 Agent 的行为
- 设定明确的约束条件防止误操作

### 3. 安全考量

- 敏感操作（删除、修改配置）应在工具层面做二次确认
- 终端技能注意命令注入防护
- 网络技能注意 API Key 等凭据保护

### 4. 子代理技能隔离

- 每个子代理应只加载与其角色相关的技能
- 代码子代理（小开）不应加载金融分析技能
- 通过 `config.yaml` 中的 `skills` 字段精确控制

### 5. 版本管理

```
skills/
├── deploy-tool/
│   ├── v1/                  ← 保留旧版本
│   └── config.yaml          ← 当前版本指向 v2
```

---

## 本仓库技能目录结构

```
03-skills/
└── README.md                ← 本文档
```

> 具体的技能文件位于实际 Hermes 配置目录 `~/.hermes/skills/` 下。本文档只记录技能体系和编写方法，不包含运行时文件。
