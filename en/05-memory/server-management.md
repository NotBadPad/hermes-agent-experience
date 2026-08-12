# Server operations: practical defaults

[简体中文](../../05-memory/server-management.md) | **English**

This runbook collects conservative defaults for servers managed through Hermes Agent. Adapt commands to the operating system and verify official installation instructions before executing third-party scripts.

## Before changing anything

1. Confirm the target host and environment.
2. Inspect OS, CPU, memory, disk, time, open ports, DNS, and service managers.
3. Read the project documentation and current configuration.
4. Check backups and define rollback.
5. Record the intended change and expected verification signal.

## SSH and access

- Prefer key authentication.
- Use a non-root administrative account where practical.
- Restrict password login and root login only after key access is verified in a second session.
- Keep private keys outside repositories and chat transcripts.
- Limit management ports by source network when possible.

Example firewall intent:

```bash
ufw default deny incoming
ufw default allow outgoing
ufw allow OpenSSH
ufw allow 80/tcp
ufw allow 443/tcp
ufw enable
```

Review the generated rules before enabling the firewall on a remote host.

## Application isolation

Run services under dedicated users or containers. Mount only required paths, use read-only filesystems where feasible, and apply CPU and memory limits. Do not expose databases or application ports directly to the public network when a local bind and reverse proxy are sufficient.

```yaml
services:
  app:
    image: example/app:stable
    restart: unless-stopped
    ports:
      - "127.0.0.1:3000:3000"
    env_file:
      - .env
```

## Nginx reverse proxy

```nginx
server {
    listen 80;
    server_name app.example.com;

    location / {
        proxy_pass http://127.0.0.1:3000;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

Check configuration before reload:

```bash
nginx -t
systemctl reload nginx
```

A reload is usually preferable to a restart. Verify the certificate, SNI match, status code, and page content from outside the server.

## TLS

Use an automated renewal method such as ACME. Monitor expiry instead of assuming renewal works. After issuance, verify subject names and dates:

```bash
openssl x509 -in /path/to/fullchain.pem -noout -subject -dates -ext subjectAltName
```

## Monitoring

At minimum, monitor:

- host reachability;
- CPU, memory, swap, disk, inode, and network use;
- process or container state;
- application health endpoint;
- HTTP status and latency;
- certificate expiry;
- backup completion;
- error-log rate.

Keep routine logs out of notification stdout. Alerts should explain the host, metric, threshold, observed value, and next diagnostic step.

## Backups

A backup is only credible after a restore test. Define retention, encryption, off-host storage, and recovery time. Back up data and the configuration required to recreate the service, but do not copy secrets into public archives.

## Incident response

```text
confirm symptom → inspect recent changes → check reachability
→ service state → ports → logs → resources → dependencies
→ apply reversible fix → verify local and public behavior
→ document cause, impact, fix, and prevention
```

Avoid restart loops. A restart may hide the original evidence and can make a database or queue problem worse.

## Deployment completion criteria

A deployment is complete only when:

- the process manager reports healthy;
- the local health endpoint works;
- the reverse proxy routes to the expected service;
- DNS and TLS are correct;
- the public endpoint returns the expected content;
- logs show no new critical errors;
- rollback and maintenance instructions are recorded.
