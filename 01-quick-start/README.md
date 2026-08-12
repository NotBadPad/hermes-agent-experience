# 快速上手

## 安装 Hermes

```bash
# Linux / macOS / WSL2 / Android（Termux）
curl -fsSL https://raw.githubusercontent.com/NousResearch/hermes-agent/main/scripts/install.sh | bash

# 查看版本
hermes --version
```

Windows 与桌面端安装方式见 [Hermes 官方安装文档](https://hermes-agent.nousresearch.com/docs/getting-started/installation)。

## 初始化配置

```bash
# 运行初始化向导
hermes setup

# 或手动创建基础配置
mkdir -p ~/.hermes
```

## 设置模型提供商

### 交互式选择 Provider

```bash
# 选择 Provider、模型并保存配置
hermes model
```

也可以运行 `hermes setup model` 重新配置模型。API Key 放在 `~/.hermes/.env`，不要写进仓库。

### OpenAI 兼容接口

```yaml
# config.yaml
model:
  default: your-model
  provider: custom
  base_url: https://your-api-endpoint/v1
  api_key: ${YOUR_API_KEY_ENV}
```

## 创建第一个子代理

```bash
# 创建独立 Profile
hermes profile create my-agent

# 验证
hermes profile list

# 使用该 Profile 启动会话
hermes --profile my-agent
```

## 常用命令速查

```bash
hermes chat -q "你的消息"         # 单次提问
hermes --profile my-agent          # 使用指定 Profile
hermes setup                       # 配置向导
hermes gateway start              # 启动Gateway
hermes gateway status             # 查看Gateway状态
hermes update                     # 更新Hermes
hermes model                      # 切换模型
hermes profile list               # 列出所有子代理
```

## 环境变量管理

所有敏感信息通过 `.env` 文件或系统环境变量管理：

```bash
# ~/.hermes/.env
DEEPSEEK_API_KEY=sk-xxx
OPENAI_API_KEY=sk-xxx
XIAOMI_API_KEY=xxx
```

> **注意**: `.env` 文件应加入 `.gitignore`，切勿提交到仓库。
