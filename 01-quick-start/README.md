# 快速上手

## 安装 Hermes

```bash
# 方式一：pip 安装
pip install hermes-agent

# 方式二：源码安装
git clone https://github.com/NousResearch/hermes-agent.git
cd hermes-agent
pip install -e .

# 查看版本
hermes version
```

## 初始化配置

```bash
# 运行初始化向导
hermes init

# 或手动创建基础配置
mkdir -p ~/.hermes
```

## 设置模型提供商

### DeepSeek（推荐入门）

```bash
# 设置 API Key
export DEEPSEEK_API_KEY=sk-your-key-here

# 配置模型
hermes model set --provider deepseek --model deepseek-v4-flash
```

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
# 创建子代理目录
mkdir -p ~/.hermes/profiles/my-agent

# 编写配置
cat > ~/.hermes/profiles/my-agent/config.yaml << 'EOF'
model:
  default: deepseek-v4-flash
  provider: deepseek
  base_url: https://api.deepseek.com/v1
toolsets:
- hermes-cli
- terminal
- file
agent:
  max_turns: 90
display:
  personality: technical
EOF

# 验证
hermes profile list
```

## 常用命令速查

```bash
hermes -m "你的消息"              # 单次提问
hermes -p my-agent "任务"         # 使用子代理
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
