# AGENTS.md — Hermes Agent 经验分享（AI 入口）

[简体中文](AGENTS.md) | [English](en/AGENTS.md)

> 本文档面向 AI Agent。阅读后你将了解这个仓库的结构和核心内容。

## 多语言维护

- 简体中文是源语言，英文文档放在 `en/` 下并镜像原目录结构。
- 修改中文文档时，同一个提交内同步更新英文版本。
- 命令、路径、环境变量、API 字段和模型 ID 不做翻译。
- 提交前运行 `python3 scripts/check_docs.py`。
- 详细规则见 `LOCALIZATION.md`。

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

- 主模型: 可按任务切换；近期默认走自建网关模型，辅助任务统一使用 DeepSeek Flash
- 子代理模型: 小开(自建网关模型) / 小富(mimo-v2.5-pro) / 小运(deepseek-v4-pro) / botstreet(mimo-v2.5-pro)
- Opendoor: 已移除 GPT 系模型，只保留 Claude / Gemini 系模型路由
- 接入平台: Bot Street(波街) / xia345(虾345) / TradingAgents / Graphify
- 环境变量: 统一使用 .env 文件管理，所有 API Key 通过环境变量引用
- 外部技能: 从 addyosmani/agent-skills 引入 22 个生产级工程技能

## 协作模式

- 代码任务 → 小开（代码专家）
- 交易/理财 → 小富（金融分析）
- 服务器/运维 → 小运（运维管理）
- Bot接单/赚钱 → botstreet（波街运营）
- 通用任务 → 主 Hermes（当前 Agent）

## 波街运营状态（2026-05-16）

- 任务扫描先核对本地清单，避免重复申请
- 新任务先汇报给主人确认，不自动扣火花申请
- 已指派任务可由 Agent 完成交付并提交 API
- 定时巡检在消息平台限流时可改为本地输出

## 近期重点文档

- `05-memory/recent-agent-ops-2026-08-11.md` — Cron 执行/输出/投递分层诊断、确定性巡检、自定义 Provider 与凭据池、健康探针假故障、跨模型协议兼容和公开脱敏经验
- `05-memory/ai-video-generation-2026-07-08.md` — 参考角色提取、分镜图生成、Grok 分段图生视频、ffmpeg 拼接、抽帧验证与 BGM 混音经验
- `05-memory/recent-agent-ops-2026-07-05.md` — 服务器 IP 漂移、SSH key 修复、NodeLite Agent token mismatch 重绑经验
- `05-memory/recent-agent-ops-2026-05-16.md` — 模型路由、辅助模型、Gateway、Bot Street、文档归档经验
