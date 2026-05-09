# 🖥️ 服务器管理 — 经验与教训

> **目录**: `05-memory/` — 踩坑记录 & 最佳实践
> **相关子代理**: 小运（运维管理）
> **最后更新**: 2025-04

本文档记录了 Hermes Agent 团队在服务器管理和运维过程中遇到的典型问题和解决方案，供后续参考和新人快速上手。

---

## 📋 目录

1. [通用原则](#-通用原则)
2. [安全加固](#-安全加固)
3. [Docker 与容器化](#-docker-与容器化)
4. [Nginx 配置](#-nginx-配置)
5. [监控告警](#-监控告警)
6. [CI/CD 管道](#-cicd-管道)
7. [数据备份与恢复](#-数据备份与恢复)
8. [常见故障排查](#-常见故障排查)
9. [踩坑记录](#-踩坑记录)

---

## 🔒 通用原则

### 黄金法则

| # | 原则 | 说明 |
|---|------|------|
| 1 | **可回滚** | 任何变更必须有回滚方案，没有回滚方案 = 不允许变更 |
| 2 | **监控先行** | 服务上线前必须先配置好监控，否则等于盲跑 |
| 3 | **最小权限** | 任何进程/用户只授予完成任务所需的最小权限 |
| 4 | **基础设施即代码** | 服务器配置通过代码管理（Ansible/Docker Compose），不要手动 SSH 改配置 |
| 5 | **变更记录** | 每次变更记录原因、时间、操作人（或 Agent），方便回溯 |

### 服务器初始化清单

```bash
# ❗ 新服务器到手后必做事项
1. 更新系统包             # apt update && apt upgrade -y
2. 创建普通用户 + sudo    # adduser deploy && usermod -aG sudo deploy
3. SSH 密钥登录 + 禁用密码 # ssh-copy-id && PasswordAuthentication no
4. 禁用 root 直接登录     # PermitRootLogin no
5. 配置防火墙             # ufw allow 22,80,443 && ufw enable
6. 安装 Fail2ban          # apt install fail2ban
7. 配置自动安全更新       # apt install unattended-upgrades
8. 配置 NTP 时间同步      # timedatectl set-ntp true
9. 配置 swap（内存不足时） # fallocate -l 2G /swapfile
10. 安装 Docker（容器化） # 官方脚本安装
11. 部署监控 Agent        # Prometheus Node Exporter
```

---

## 🛡️ 安全加固

### SSH 安全配置

```bash
# /etc/ssh/sshd_config 关键配置
Port 2222                          # 更换默认端口（22→2222）
PermitRootLogin no                 # 禁止 root 直接登录
PasswordAuthentication no          # 禁用密码认证
PubkeyAuthentication yes           # 启用密钥认证
AllowUsers deploy                  # 限制可登录用户
MaxAuthTries 2                     # 最大认证尝试次数
ClientAliveInterval 300            # 客户端保活间隔
ClientAliveCountMax 2              # 保活失败最大次数
```

> ⚠️ **踩坑记录**：更换 SSH 端口后，务必先在当前会话中测试新端口能登录成功，再关闭旧端口。否则可能导致自己被锁在服务器外。

### 防火墙规则

```bash
# UFW 推荐规则
ufw default deny incoming
ufw default allow outgoing
ufw allow 2222/tcp                 # SSH（自定义端口）
ufw allow 80/tcp                   # HTTP
ufw allow 443/tcp                  # HTTPS
ufw allow 9090/tcp                 # Prometheus（限内网/IP白名单）
# 对特定服务限制来源IP
ufw allow from 192.168.1.0/24 to any port 3000  # 内网访问
```

### Fail2ban 配置

```ini
# /etc/fail2ban/jail.local
[sshd]
enabled = true
port = 2222           # 与 SSH 端口一致
maxretry = 3          # 3 次失败即封禁
bantime = 3600        # 封禁 1 小时
findtime = 600        # 10 分钟内计数

[nginx-botsearch]
enabled = true
filter = nginx-botsearch
logpath = /var/log/nginx/access.log
maxretry = 5
bantime = 86400       # 扫描机器人封禁 1 天
```

---

## 🐳 Docker 与容器化

### Docker 安装

```bash
# 官方推荐方式（不要在未确认的情况下直接执行，先看文档）
curl -fsSL https://get.docker.com -o get-docker.sh
# 检查脚本内容后再执行
# sudo sh get-docker.sh
sudo usermod -aG docker $USER   # 添加用户到 docker 组
```

> ⚠️ **踩坑记录**：Docker 官方安装脚本会添加 Docker 官方源并安装最新版。如果服务器在国内，安装可能很慢，建议配置国内镜像源后再执行。

### Docker Compose 最佳实践

```yaml
# docker-compose.yml 模板
version: '3.8'

services:
  app:
    image: registry.example.com/myapp:${TAG:-latest}
    restart: always
    ports:
      - "127.0.0.1:3000:3000"  # ❗ 只监听本地，用 Nginx 反向代理
    environment:
      - NODE_ENV=production
      - DB_URL=postgres://user:pass@db:5432/app
    volumes:
      - app_data:/app/data
    depends_on:
      - db
    logging:
      driver: "json-file"
      options:
        max-size: "10m"
        max-file: "3"
    deploy:
      resources:
        limits:
          cpus: '0.50'
          memory: 512M
        reservations:
          cpus: '0.25'
          memory: 256M
    healthcheck:
      test: ["CMD", "curl", "-f", "http://localhost:3000/health"]
      interval: 30s
      timeout: 10s
      retries: 3

  db:
    image: postgres:15-alpine
    restart: always
    volumes:
      - pg_data:/var/lib/postgresql/data
    environment:
      - POSTGRES_DB=app
      - POSTGRES_USER=app
      - POSTGRES_PASSWORD=${DB_PASSWORD}
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U app"]
      interval: 10s

volumes:
  app_data:
  pg_data:
```

### Docker 关键注意事项

| 问题 | 建议 |
|------|------|
| 容器资源限制 | 始终设置 `deploy.resources.limits`，避免单容器耗尽所有资源 |
| 日志管理 | 配置 `logging` 限制日志大小，否则磁盘会被撑爆 |
| 端口暴露 | 应用服务端口绑定到 `127.0.0.1`，通过 Nginx 反向代理对外暴露 |
| 健康检查 | 为每个服务配置 `healthcheck`，方便监控和自动恢复 |
| 数据卷 | 数据库等有状态服务必须使用数据卷（volume），不要用 bind mount |
| 镜像标签 | 生产环境使用具体版本标签（如 `v1.2.3`），不要用 `latest` |

> ⚠️ **踩坑记录**：曾经一个容器没有设置日志限制，运行一个月后日志文件撑满了 40GB 磁盘，导致所有服务崩溃。教训：**日志滚轮是必须配置的**。

### Docker 常用运维命令

```bash
# 查看容器资源占用
docker stats --no-stream

# 清理未使用的资源（谨慎使用）
docker system prune -af --volumes   # --volumes 会删除所有未使用的卷！

# 查看容器日志（限制行数）
docker logs --tail 100 -f <container>

# 进入容器排查
docker exec -it <container> /bin/sh

# 重启策略
docker update --restart=always <container>
```

---

## 🌐 Nginx 配置

### 反向代理模板

```nginx
# /etc/nginx/sites-available/app.conf
server {
    listen 80;
    server_name app.example.com;
    return 301 https://$server_name$request_uri;  # HTTP → HTTPS 重定向
}

server {
    listen 443 ssl http2;
    server_name app.example.com;

    ssl_certificate     /etc/letsencrypt/live/app.example.com/fullchain.pem;
    ssl_certificate_key /etc/letsencrypt/live/app.example.com/privkey.pem;
    ssl_protocols       TLSv1.2 TLSv1.3;

    # 安全头
    add_header Strict-Transport-Security "max-age=31536000; includeSubDomains" always;
    add_header X-Frame-Options "SAMEORIGIN" always;
    add_header X-Content-Type-Options "nosniff" always;

    # 代理到本地服务
    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;

        # WebSocket 支持
        proxy_http_version 1.1;
        proxy_set_header Upgrade $http_upgrade;
        proxy_set_header Connection "upgrade";

        # 超时设置
        proxy_connect_timeout 30s;
        proxy_read_timeout 60s;
        proxy_send_timeout 60s;
    }

    # 静态文件（直接由 Nginx 提供）
    location /static/ {
        alias /var/www/app/static/;
        expires 7d;
        add_header Cache-Control "public, immutable";
    }

    # 限制访问
    location /admin/ {
        proxy_pass http://127.0.0.1:3000;
        allow 192.168.1.0/24;    # 只允许内网访问
        allow 114.114.114.114;   # 或指定 IP
        deny all;
    }

    # 限制请求频率
    location /api/ {
        limit_req zone=api burst=20 nodelay;
        proxy_pass http://127.0.0.1:3000;
    }
}
```

### SSL 证书自动续期

```bash
# 使用 acme.sh 或 certbot 自动续期
# acme.sh 示例
acme.sh --issue -d app.example.com --nginx
acme.sh --install-cronjob

# 或 certbot
certbot --nginx -d app.example.com
# 续期会自动由 systemd timer 处理
systemctl status certbot.timer
```

> ⚠️ **踩坑记录**：SSL 证书过期是服务不可用的常见原因之一。务必配置自动续期，并设置监控告警（证书剩余天数低于 7 天发送通知）。

---

## 📡 监控告警

### Prometheus + Grafana 快速部署

```yaml
# docker-compose.monitoring.yml
version: '3.8'

services:
  prometheus:
    image: prom/prometheus:v2.45.0
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.retention.time=30d'
    restart: always

  grafana:
    image: grafana/grafana:10.0.0
    volumes:
      - grafana_data:/var/lib/grafana
    environment:
      - GF_SECURITY_ADMIN_PASSWORD=${GRAFANA_PASSWORD}
    restart: always

  node-exporter:
    image: prom/node-exporter:v1.6.0
    network_mode: host
    restart: always

  alertmanager:
    image: prom/alertmanager:v0.25.0
    volumes:
      - ./alertmanager.yml:/etc/alertmanager/alertmanager.yml
    restart: always

volumes:
  prometheus_data:
  grafana_data:
```

### 关键告警规则

```yaml
# prometheus 告警规则示例
groups:
  - name: server-alerts
    rules:
      - alert: HighCPUUsage
        expr: 100 - (avg by(instance) (rate(node_cpu_seconds_total{mode="idle"}[5m])) * 100) > 80
        for: 10m
        annotations:
          summary: "CPU 使用率超过 80%"

      - alert: HighMemoryUsage
        expr: (node_memory_MemTotal_bytes - node_memory_MemFree_bytes - node_memory_Cached_bytes) / node_memory_MemTotal_bytes * 100 > 85
        for: 5m
        annotations:
          summary: "内存使用率超过 85%"

      - alert: DiskSpaceLow
        expr: node_filesystem_avail_bytes{mountpoint="/"} / node_filesystem_size_bytes{mountpoint="/"} * 100 < 10
        for: 5m
        annotations:
          summary: "磁盘剩余空间不足 10%"

      - alert: ServiceDown
        expr: up{job="docker"} == 0
        for: 1m
        annotations:
          summary: "服务 {{ $labels.instance }} 不可达"

      - alert: SSLCertExpiring
        expr: probe_ssl_earliest_cert_expiry{instance="https://app.example.com"} - time() < 604800
        annotations:
          summary: "SSL 证书将在 7 天内过期"
```

### 监控指标速查

| 指标 | 查什么 | 正常范围 | 告警阈值 |
|------|--------|----------|----------|
| CPU 使用率 | `node_cpu_seconds_total` | 30-60% | > 80% 持续 10 分钟 |
| 内存使用率 | `node_memory_*` | 40-70% | > 85% |
| 磁盘使用率 | `node_filesystem_*` | < 80% | > 90% |
| 磁盘 IO | `node_disk_*` | 等待时间 < 100ms | > 500ms |
| 网络流量 | `node_network_*` | 按带宽比例 | > 80% 带宽 |
| 服务存活 | `up` | 1 | 0 |

---

## 🔄 CI/CD 管道

### GitHub Actions 模板

```yaml
# .github/workflows/deploy.yml
name: Deploy

on:
  push:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - name: Run tests
        run: |
          npm ci
          npm test

  build-and-deploy:
    needs: test
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Build Docker image
        run: |
          docker build -t registry.example.com/app:${GITHUB_SHA::7} .
          docker tag registry.example.com/app:${GITHUB_SHA::7} registry.example.com/app:latest

      - name: Push to registry
        run: |
          docker login -u ${{ secrets.REGISTRY_USER }} -p ${{ secrets.REGISTRY_PASS }}
          docker push registry.example.com/app:${GITHUB_SHA::7}
          docker push registry.example.com/app:latest

      - name: Deploy to server
        uses: appleboy/ssh-action@v0.1.5
        with:
          host: ${{ secrets.SERVER_HOST }}
          username: ${{ secrets.SERVER_USER }}
          key: ${{ secrets.SSH_PRIVATE_KEY }}
          script: |
            cd /opt/app
            docker compose pull
            docker compose up -d --force-recreate
            docker system prune -f
```

### CI/CD 注意事项

| 要点 | 说明 |
|------|------|
| **环境变量管理** | 敏感信息使用 GitHub Secrets / GitLab CI Variables，不要硬编码 |
| **构建缓存** | Docker 层缓存利用 `.dockerignore` 和依赖分离，减少构建时间 |
| **回滚策略** | 保留最近 3-5 个镜像版本，方便快速回滚 `docker compose up -d app:old-version` |
| **数据库迁移** | 在部署脚本中单独处理，不要和容器启动混在一起 |
| **健康检查** | 部署完成后自动执行健康检查，失败则自动回滚 |

> ⚠️ **踩坑记录**：有一次 CI 中 `docker system prune -f` 在部署完成后执行，但因为 `docker compose pull` 之前有正在运行的旧容器，`prune` 清理了旧镜像后，如果新容器启动失败，就没有可回滚的版本了。教训：**保留至少 2 个版本的回滚能力**。

---

## 💾 数据备份与恢复

### 备份策略

| 数据类型 | 备份方式 | 频率 | 保留期 | 存储位置 |
|----------|----------|------|--------|----------|
| 数据库（PostgreSQL） | `pg_dump` + 压缩 | 每日 | 30天 | 本地 + 对象存储 |
| 数据库（MySQL） | `mysqldump` | 每日 | 30天 | 本地 + 对象存储 |
| 应用数据卷 | `restic` / `borg` | 每日 | 90天 | 对象存储 |
| 配置文件 | Git 仓库 | 每次变更 | 永久 | Git |
| 系统快照 | 云服务商快照 | 每周 | 60天 | 云存储 |

### PostgreSQL 备份脚本

```bash
#!/bin/bash
# /opt/scripts/backup-postgres.sh
BACKUP_DIR="/var/backups/postgres"
DB_NAME="app"
RETENTION_DAYS=30
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
S3_BUCKET="s3://my-backups/postgres/"

# 创建备份
mkdir -p $BACKUP_DIR
docker exec -t app-db-1 pg_dump -U app $DB_NAME \
  | gzip > "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz"

# 上传到对象存储
aws s3 cp "$BACKUP_DIR/${DB_NAME}_${TIMESTAMP}.sql.gz" "$S3_BUCKET"

# 清理本地旧备份
find $BACKUP_DIR -name "${DB_NAME}_*.sql.gz" -mtime +$RETENTION_DAYS -delete

echo "Backup completed: ${DB_NAME}_${TIMESTAMP}.sql.gz"
```

### 恢复流程

```bash
# PostgreSQL 恢复
# 1. 停止应用服务（避免数据写入）
docker compose stop app

# 2. 恢复数据库
gunzip -c /var/backups/postgres/app_20250401_120000.sql.gz \
  | docker exec -i app-db-1 psql -U app -d app

# 3. 重启应用
docker compose start app

# 4. 验证数据完整性
# 检查关键数据表行数、最新记录时间戳
```

> ⚠️ **踩坑记录**：曾经只做了备份但从未测试恢复，等到真正需要恢复时才发现备份文件损坏。教训：**定期（每月）演练恢复流程**，确认备份文件可正常恢复。

---

## 🔧 常见故障排查

### CPU 过高

```bash
# 找出 CPU 消耗者
top -bn1 | head -20

# Docker 容器级别
docker stats --no-stream

# 查看具体进程
ps aux --sort=-%cpu | head -10

# Strace 追踪
strace -p <PID> -c -S time 2>&1 | head -20
```

**常见原因**：
- 代码死循环 / 无限递归
- 数据库慢查询（大量连接未释放）
- 缺乏资源限制的容器跑满 CPU
- 恶意攻击（DDoS / 挖矿程序）

---

### 内存不足 (OOM)

```bash
# 查看内存使用
free -h
# 或
cat /proc/meminfo

# 找出内存消耗者
ps aux --sort=-%mem | head -10

# 查看 OOM Killer 日志
dmesg | grep -i oom
journalctl -k | grep -i oom

# Docker 容器 OOM 统计
docker inspect <container> | jq '.[0].State.OOMKilled'
```

**常见原因**：
- 内存泄漏（Node.js/Python 长连接场景常见）
- 容器未设置内存限制
- Swap 空间不足

---

### 磁盘空间满

```bash
# 查看磁盘使用情况
df -h

# 找出大目录
du -sh /* 2>/dev/null | sort -rh | head -10

# 找出大文件
find / -type f -size +100M -exec ls -lh {} \; 2>/dev/null

# Docker 占用排查
docker system df
# 清理
docker system prune -f          # 清理未使用的容器和镜像
docker builder prune -f         # 清理构建缓存
```

**常见原因**：
- 容器日志未轮转（最常见！）
- Docker 镜像/构建缓存堆积
- 数据库 WAL 日志增长
- 备份文件累积

---

### 网络问题

```bash
# 端口监听检查
ss -tlnp

# 连接数统计
ss -tan | awk '{print $5}' | cut -d: -f1 | sort | uniq -c | sort -rn

# DNS 排查
dig +short example.com
nslookup example.com

# 路由追踪
traceroute -n example.com

# 带宽使用
iftop -i eth0
nload eth0
```

**常见原因**：
- DNS 解析失败
- 防火墙规则阻止
- 端口被占用
- 带宽跑满（被攻击或异常流量）

---

## 🕳️ 踩坑记录

### 1. Docker 日志撑爆磁盘

**现象**：服务运行一个月后，所有容器突然挂了，SSH 连不上。

**原因**：容器未配置日志限制，默认 `json-file` 驱动无限增长，单个容器日志达到 10GB+，40GB 磁盘被占满。

**解决方案**：
```yaml
# docker-compose.yml 添加日志配置
logging:
  driver: "json-file"
  options:
    max-size: "10m"      # 单个日志文件最大 10MB
    max-file: "3"        # 保留最近 3 个文件
```

**永久修复**（全局配置）：
```json
// /etc/docker/daemon.json
{
  "log-driver": "json-file",
  "log-opts": {
    "max-size": "10m",
    "max-file": "3"
  }
}
```

---

### 2. Swap 配置缺失导致内存不足

**现象**：服务器 2GB 内存，跑数据库时频繁 OOM。

**原因**：未配置 Swap 分区，物理内存用尽后直接触发 OOM Killer。

**解决方案**：
```bash
# 创建 2GB Swap 文件
fallocate -l 2G /swapfile
chmod 600 /swapfile
mkswap /swapfile
swapon /swapfile

# 永久生效（/etc/fstab）
echo '/swapfile none swap sw 0 0' >> /etc/fstab

# 调整 swappiness（控制使用 Swap 的倾向）
sysctl vm.swappiness=10
echo 'vm.swappiness=10' >> /etc/sysctl.conf
```

---

### 3. SSL 证书过期无人知

**现象**：用户反馈网站打不开，检查发现 HTTPS 证书已过期 3 天。

**原因**：使用 certbot 但未配置自动续期，或续期任务因 crontab 环境问题未执行。

**解决方案**：
```bash
# 监控证书过期时间
# Prometheus blackbox_exporter 配置 SSL 证书探测
# 或使用简单脚本
openssl s_client -connect app.example.com:443 -servername app.example.com </dev/null 2>/dev/null \
  | openssl x509 -noout -enddate
```

---

### 4. CI/CD 部署后镜像被 prune 导致无法回滚

**现象**：新版本部署后服务异常，尝试回滚发现镜像已被清理。

**原因**：CI 脚本中 `docker system prune -f` 清除了旧版本的镜像。

**解决方案**：
```bash
# 保留最近 N 个版本
docker system prune -f --filter "until=24h"
# 或不要自动 prune，由运维手动清理
```

---

### 5. UFW 重启后 SSH 端口规则丢失

**现象**：重启服务器后 SSH 连接超时（使用了自定义端口 2222）。

**原因**：UFW 规则虽然 `ufw allow 2222`，但重启后规则被重置或默认策略拒绝了所有入站。

**解决方案**：
```bash
# 确认规则已保存
ufw status verbose

# 如果使用云服务商，同时在安全组/防火墙开放端口
# 双重保险：服务器防火墙 + 云服务商安全组
```

---

### 6. Docker Compose 容器依赖顺序问题

**现象**：应用容器启动时连接数据库失败，但数据库容器已经在运行。

**原因**：`depends_on` 只保证容器启动顺序，不保证数据库服务已就绪（PostgreSQL 需要初始化时间）。

**解决方案**：
```yaml
services:
  app:
    depends_on:
      db:
        condition: service_healthy  # 等待健康检查通过
    # 或应用层增加重试机制
    environment:
      - DB_RETRY_INTERVAL=5
      - DB_MAX_RETRIES=12
```

---

### 7. 备份文件无人测试恢复

**现象**：数据库迁移前做了备份，迁移失败后恢复发现备份文件为空（0 bytes）。

**原因**：备份脚本执行时数据库连接失败，但没有错误检查和告警，生成的是空文件。

**解决方案**：
```bash
# 备份脚本增加完整性检查
if [ ! -s "$BACKUP_FILE" ]; then
    echo "ERROR: Backup file is empty!"
    curl -X POST -H "Content-Type: application/json" \
      -d '{"text":"❌ 备份失败: 备份文件为空"}' \
      $NOTIFICATION_WEBHOOK
    exit 1
fi

# 每月执行恢复演练（恢复到一个测试环境验证）
```

---

## 📝 总结

| 领域 | 最重要的三件事 |
|------|----------------|
| 安全 | SSH 密钥登录 + Fail2ban + 最小权限 |
| Docker | 日志限制 + 资源限制 + 健康检查 |
| 监控 | CPU/内存/磁盘告警 + SSL 证书到期告警 + 服务存活监控 |
| 备份 | 自动备份 + 异地存储 + 定期恢复演练 |
| CI/CD | Secrets 管理 + 可回滚 + 部署后健康检查 |
| 故障响应 | 告警通知 + 标准排查流程 + 事后复盘 |

> **最后提醒**：运维没有银弹。最好的运维策略是 **"自动化一切 + 监控一切 + 定期演练"**。每次故障都是一次学习机会，记得把解决方案整理回这个文档。
