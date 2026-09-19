# Hermes Agent 经验分享

**简体中文** | [English](en/README.md)

> 将 Hermes Agent 的配置、技能、子代理、记忆与实战经验整理成结构化知识库，方便人类和 AI Agent 共同阅读和复用。

> 多语言维护规则见 [LOCALIZATION.md](LOCALIZATION.md)。当前维护简体中文与 English，英文目录与中文目录保持镜像结构。

## 📦 仓库结构

```
hermes-agent-experience/
├── README.md              ← 本文件，总览
├── AGENTS.md              ← AI Agent 入口（给AI读的版本）
├── CHANGELOG.md           ← 版本更新记录
├── LOCALIZATION.md        ← 多语言目录约定与维护规则
├── scripts/check_docs.py  ← Markdown、链接与翻译覆盖检查
├── en/                    ← English 文档镜像
│
├── 01-quick-start/        ← 快速上手
├── 02-configuration/      ← Hermes 配置详解
├── 03-skills/             ← 技能体系
├── 04-sub-agents/         ← 子代理配置（小开/小富/小运/botstreet）
├── 05-memory/             ← 记忆与经验教训
├── 06-integrations/       ← 平台集成（波街/虾345/graphify等）
└── 07-tips/               ← 技巧与最佳实践
```

## 🎯 适合谁看

- **Hermes Agent 新手** — 想快速上手并了解能做什么
- **AI Agent 开发者** — 了解如何配置子代理、编写技能、接入外部平台
- **波街/虾345 用户** — 了解 Bot 如何在实际平台接单赚钱
- **想复制这套配置的人** — 直接套用模块化结构和经验

## 🧩 核心内容速览

| 模块 | 内容 |
|------|------|
| ⚡ **快速开始** | 安装 Hermes、初始化配置、创建第一个子代理 |
| ⚙️ **配置** | 主配置、各子代理配置、环境变量模板（脱敏） |
| 🛠️ **技能** | 内置技能清单、自定义技能编写方法 |
| 🤖 **子代理** | 小开（代码）/ 小富（交易）/ 小运（运维）/ botstreet（波街） |
| 🧠 **记忆** | 服务器拓扑、项目经验、踩坑记录 |
| 🔗 **集成** | 波街/虾345/graphify/TradingAgents 接入经验 |
| 💡 **技巧** | prompt 技巧、MCP 集成、跨 agent 协作模式 |

## 🌐 多语言文档

| 语言 | 状态 | 入口 |
|------|------|------|
| 简体中文 | 源语言，持续维护 | [README.md](README.md) |
| English | 完整镜像，持续维护 | [en/README.md](en/README.md) |

中文内容更新时应同步修改 `en/` 下的对应文件。CI 会检查英文覆盖、本地链接和 Markdown 代码围栏。新增语言的方法见 [LOCALIZATION.md](LOCALIZATION.md)。

## 🆕 近期更新

- [2026-09-19 Hermes 运维经验：安全升级、配置迁移与网关排障](05-memory/recent-agent-ops-2026-09-19.md)：升级前备份、本地补丁语义移植、Doctor 配置迁移、Gateway 重启判定、网关分层诊断、磁盘满导致认证假限流及健康探针设计。
- [2026-08-11 Hermes 运维经验：Cron、Provider 与健康检查](05-memory/recent-agent-ops-2026-08-11.md)：区分任务执行与消息投递、确定性巡检脚本、自定义 Provider 可见性与凭据池、WAF 假故障、跨模型推理字段兼容及脱敏检查。
- [2026-07-08 AI 视频生成经验：参考角色 → 分镜图片 → Grok 图生视频](05-memory/ai-video-generation-2026-07-08.md)：原始视频抽帧提取角色、GPT 图片生成关键帧、Grok 分段图生视频、ffmpeg 拼接、抽帧验证和 BGM 混音经验。
- [2026-07-05 运维经验：服务器 IP 漂移与 NodeLite Agent 重绑](05-memory/recent-agent-ops-2026-07-05.md)：SSH 别名更新、公钥登录修复、NodeLite `Unauthorized` 离线节点排查与重绑验证。
- [2026-05-16 Agent 运行经验](05-memory/recent-agent-ops-2026-05-16.md)：Opendoor GPT 模型下线、辅助模型切 DeepSeek、Gateway 重启排查、Bot Street 交付与文档归档边界。

## 🔒 安全说明

本仓库已做脱敏处理：
- ✅ IP 地址 → 占位符（如 `SERVER_IP`）
- ✅ 域名 → 占位符（如 `example.com`）
- ✅ API Key / Token → 环境变量引用
- ✅ 个人邮箱 → 已移除
- ❌ GitHub 用户名保留（公共信息）

## 📜 使用许可

MIT — 随便用，欢迎 PR。
