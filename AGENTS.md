# AGENTS.md — Hermes Agent 经验分享（AI 入口）

> 本文档面向 AI Agent。阅读后你将了解这个仓库的结构和核心内容。

## 仓库定位

本仓库记录了一个 Hermes Agent 的真实配置、技能体系、子代理分工、平台集成经验和踩坑记录。你可以直接作为参考来配置自己的 Hermes。

## 快速导航

- **先看结构** → 仓库根 `README.md`
- **快速搭建** → `01-quick-start/`
- **核心配置** → `02-configuration/`
- **技能清单** → `03-skills/`
- **子代理配置** → `04-sub-agents/`
- **经验教训** → `05-memory/`
- **平台接入** → `06-integrations/`
- **使用技巧** → `07-tips/`

## 关键事实

- 主模型: deepseek-v4-flash
- 子代理模型: 小开(gpt-5.4) / 小富(mimo-v2.5-pro) / 小运(deepseek-v4-pro) / botstreet(mimo-v2.5-pro)
- 接入平台: Bot Street(波街) / xia345(虾345) / TradingAgents / Graphify
- 环境变量: 统一使用 .env 文件管理，所有 API Key 通过环境变量引用

## 协作模式

- 代码任务 → 小开（代码专家）
- 交易/理财 → 小富（金融分析）
- 服务器/运维 → 小运（运维管理）
- Bot接单/赚钱 → botstreet（波街运营）
- 通用任务 → 主 Hermes（当前 Agent）
