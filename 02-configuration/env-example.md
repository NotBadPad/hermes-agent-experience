# 环境变量模板

> 将本文件复制为 `.env`，填入真实值。

## 必须配置

```bash
# DeepSeek API（建议使用v4系列模型）
DEEPSEEK_API_KEY=sk-your-deepseek-key-here

# OpenDoor API（访问GPT/Claude等模型）
OPENDOOR_API_KEY=your-opendoor-key-here
```

## 可选配置

```bash
# 小米 MiMo API（用于 mimo-v2.5-pro 模型）
XIAOMI_API_KEY=your-xiaomi-api-key-here

# Kimi API
KIMI_API_KEY=your-kimi-key-here

# Anthropic API（直接使用Claude）
ANTHROPIC_API_KEY=sk-ant-your-key-here

# GitHub Token（用于仓库操作）
# 格式: https://username:token@github.com

# Bot Street 波街凭证
BOTSTREET_AGENT_ID=your-agent-id
BOTSTREET_AGENT_KEY=your-agent-key
BOTSTREET_BOT_NAME=your-bot-name
BOTSTREET_API_BASE=https://botstreet.io/api/v1

# 虾345
XIA345_API_BASE=https://xia345.com

# Gemini API
GEMINI_API_KEY=your-gemini-key
GOOGLE_API_KEY=your-google-key
```

## .gitignore 推荐

```gitignore
# 环境变量
.env
*.env

# 密钥和认证
*.key
*.pem
auth.json
credentials.json

# 依赖
node_modules/
__pycache__/
*.pyc

# 构建产物
dist/
build/

# 数据库
*.db
*.sqlite

# 日志
*.log

# 系统文件
.DS_Store
Thumbs.db
```

## 安全建议

1. **永远不要**将 `.env` 文件提交到 git
2. 使用环境变量引用 `${VAR_NAME}` 而非硬编码值
3. 定期轮换 API Key
4. 不同环境（开发/生产）使用不同的 Key
5. GitHub Token 使用细粒度 PAT，只授予必要权限
