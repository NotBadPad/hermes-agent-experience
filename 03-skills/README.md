# 🛠️ Hermes 技能体系

> 技能（Skill）是 Hermes Agent 的能力单元。每个技能定义了一组工具、提示词和行为模式，让 Agent 能胜任特定领域的任务。本目录记录了 Hermes 内置技能清单以及自定义技能的编写方法。

---

## 目录

- [技能体系概览](#技能体系概览)
- [内置技能清单](#内置技能清单)
- [外部引入技能（addyosmani/agent-skills）](#外部引入技能)
- [技能结构说明](#技能结构说明)
- [自定义技能编写](#自定义技能编写)
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
└── 外部引入技能（2026-05-11 从 addyosmani/agent-skills 引入）
    ├── 小开: 17 个开发技能（API设计/代码审查/TDD/调试...）
    ├── 小运: 2 个运维技能（CI/CD/发布上线）
    └── 主 agent: 3 个通用技能（上下文工程/技能使用/想法打磨）
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

---

### 2. `file` — 文件操作

| 属性 | 值 |
|------|-----|
| 类型 | 通用技能 |
| 默认启用 | ✅ 是 |
| 用途 | 读写文件、搜索内容、目录操作 |

---

### 3. `web` — 网络请求

| 属性 | 值 |
|------|-----|
| 类型 | 通用技能 |
| 默认启用 | ✅ 是 |
| 用途 | HTTP 请求、网页抓取、API 调用 |

---

### 4. `memory` — 持久记忆

| 属性 | 值 |
|------|-----|
| 类型 | 通用技能 |
| 默认启用 | ✅ 是（可关闭） |
| 用途 | 跨会话保存和检索信息 |

---

### 5. `hermes-cli` — CLI 交互

| 属性 | 值 |
|------|-----|
| 类型 | 平台技能 |
| 默认启用 | ✅ 是（CLI 模式） |
| 用途 | 命令行输入输出、管道处理 |

---

### 6. `hermes-telegram` / `hermes-discord` / `hermes-wechat`

| 平台 | 技能名 | 说明 |
|------|--------|------|
| Telegram | `hermes-telegram` | 消息收发、Bot 指令、群组管理 |
| Discord | `hermes-discord` | 频道消息、Slash 命令、音视频 |
| 微信 | `hermes-wechat` | 微信消息处理、公众号管理 |

---

## 外部引入技能

### 来源：[addyosmani/agent-skills](https://github.com/addyosmani/agent-skills)

2026-05-11 从该仓库引入 22 个生产级工程技能，按 agent 角色分配。

### 🐉 小开（代码专家）— 17 个技能

| 技能 | 说明 | 字数 |
|:-----|:-----|:---:|
| `api-and-interface-design` | API 和接口设计指南 | 10K |
| `browser-testing-with-devtools` | DevTools 浏览器测试 | 12K |
| `code-review-and-quality` | 多维度代码审查 | 14K |
| `code-simplification` | 代码简化重构 | 13K |
| `debugging-and-error-recovery` | 系统化根因调试 | 10K |
| `deprecation-and-migration` | 废弃与迁移管理 | 9K |
| `doubt-driven-development` | 怀疑驱动开发（高价值） | **16K** |
| `frontend-ui-engineering` | 生产级前端 UI | 11K |
| `git-workflow-and-versioning` | Git 工作流最佳实践 | 10K |
| `incremental-implementation` | 增量实现策略 | 9K |
| `performance-optimization` | 性能优化方法论 | 11K |
| `planning-and-task-breakdown` | 任务分解与规划 | 7K |
| `security-and-hardening` | 安全加固实践 | 11K |
| `source-driven-development` | 源码驱动开发 | 8K |
| `spec-driven-development` | 规范驱动开发 | 8K |
| `documentation-and-adrs` | 文档与架构决策记录 | 9K |
| `test-driven-development` | 测试驱动开发（合并版） | — |

### 🛠️ 小运（运维）— 2 个技能

| 技能 | 说明 | 字数 |
|:-----|:-----|:---:|
| `ci-cd-and-automation` | CI/CD 自动化流水线 | 11K |
| `shipping-and-launch` | 生产环境发布与上线 | 10K |

### 🧠 Main Hermes — 3 个技能

| 技能 | 说明 | 字数 |
|:-----|:-----|:---:|
| `context-engineering` | 上下文工程优化 | 11K |
| `using-agent-skills` | 技能发现与调用 | 9K |
| `idea-refine` | 结构化想法打磨 | 8K |

### 亮点技能

- 🔥 **`doubt-driven-development`** — 对每个非平凡决定做对抗性审查，减少幻觉
- 🔥 **`code-review-and-quality`** — 比现有更系统的多维度代码审查流程
- 🔥 **`context-engineering`** — 上下文管理优化，减少 Agent 幻觉

---

## 技能结构说明

### 技能目录规范

每个技能是一个独立目录，位于 `skills/` 下：

```
skills/
└── <skill-name>/
    └── SKILL.md             ← 技能定义（含 YAML frontmatter）
```

### SKILL.md 格式

```yaml
---
name: my-skill
description: "技能描述"
version: 1.0.0
---

# 技能名称

## Overview
概述

## When to Use
触发条件

## Steps
操作步骤
```

---

## 自定义技能编写

### 快速创建

```bash
# 使用 skill_manage 工具
skill_manage(action='create', name='my-skill', content='...', category='devops')

# 或手动创建
mkdir -p ~/.hermes/skills/category/my-skill/
```

### 编写要点

1. **YAML frontmatter** — 必须包含 `name` 和 `description`
2. **触发条件** — 在 `## When to Use` 中明确
3. **操作步骤** — 具体、可执行、带命令示例
4. **踩坑记录** — `## Pitfalls` 记录常见问题
5. **验证步骤** — 如何确认技能执行成功

---

## 最佳实践

### 1. 技能粒度控制

- 一个技能只做一件事 — 保持职责单一
- 不要在一次技能中混入不相关的工具

### 2. 子代理技能隔离

- 每个子代理只加载与其角色相关的技能
- 代码子代理不应加载金融分析技能
- 通过 profile 配置精确控制

### 3. 技能维护

- 使用技能后如发现问题，立即用 `skill_manage(action='patch')` 修复
- 过时的技能是负债，不是资产
- 定期审查技能内容是否仍然准确

---

## 本仓库技能目录结构

```
03-skills/
└── README.md                ← 本文档
```

> 具体的技能文件位于实际 Hermes 配置目录 `~/.hermes/skills/` 下。本文档只记录技能体系和编写方法，不包含运行时文件。
