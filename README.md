# Hermes Agent 经验分享

> 将 Hermes Agent 的配置、技能、子代理、记忆与实战经验整理成结构化知识库，方便人类和 AI Agent 共同阅读和复用。

## 📦 仓库结构

```
hermes-agent-experience/
├── README.md              ← 本文件，总览
├── AGENTS.md              ← AI Agent 入口（给AI读的版本）
├── CHANGELOG.md           ← 版本更新记录
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

## 🆕 近期更新

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
