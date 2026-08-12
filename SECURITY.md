# 安全脱敏提醒

[简体中文](SECURITY.md) | [English](en/SECURITY.md)

> 本仓库所有配置为脱敏后的通用模板，**不要**将真实凭证直接套用。

## 使用前必须替换

| 占位符 | 说明 |
|--------|------|
| `YOUR_API_KEY` | 替换为你的真实 API Key |
| `SERVER_IP` | 替换为你的服务器 IP |
| `example.com` | 替换为你的域名 |
| `your-agent-id` | 替换为平台分配的真实 ID |

## 禁止提交

- `.env` 文件
- 包含真实 API Key / Token 的配置文件
- SSH 密钥 / 证书
- 私人 JSON 认证文件

## 安全 checklist

- [ ] 所有 API Key 使用 `${ENV_VAR}` 引用而非硬编码
- [ ] IP 地址已替换为占位符
- [ ] 域名已替换为占位符
- [ ] 私人邮箱已移除
- [ ] `.env` 文件在 `.gitignore` 中
