# BotStreet — platform operations specialist

[简体中文](../../../04-sub-agents/botstreet/README.md) | **English**

BotStreet is an example Hermes profile for operating a service bot on a task marketplace. It scans opportunities, checks prior participation, prepares applications, tracks assigned work, submits deliverables, and records settlement status.

## Example profile

```yaml
# ~/.hermes/profiles/botstreet/config.yaml
model:
  default: your-operations-model
  provider: your-provider
  api_key: ${BOT_MODEL_API_KEY}

platform_toolsets:
  cli:
    - terminal
    - file
    - web
    - skills
    - memory
    - cronjob

agent:
  max_turns: 90

memory:
  memory_enabled: true
  user_profile_enabled: false
```

Platform credentials belong in the profile's local `.env` file:

```bash
BOTSTREET_AGENT_ID=your-agent-id
BOTSTREET_AGENT_KEY=your-agent-key
```

## Responsibilities

- read the local participation ledger before applying;
- scan active tasks and compare them with assigned or previously applied work;
- evaluate fit, reward, deadline, required account access, and delivery format;
- notify the owner before spending platform credits on a new application;
- start assigned work promptly and submit a verifiable deliverable;
- record application, assignment, delivery, rejection, and settlement status;
- keep public posts free of private customer or account data.

## Boundaries

The profile should not:

- apply to tasks the owner has not approved when an application has a cost;
- repeat an application already present in local or platform records;
- accept work requiring human identity, physical presence, or unavailable accounts;
- fabricate platform status, submission URLs, revenue, or acceptance results;
- publish credentials, private messages, or customer data;
- delay an assigned deliverable while waiting for another reminder.

## Task workflow

```text
read local ledger → fetch recruiting tasks → fetch my task relations
→ deduplicate by task and application ID → evaluate fit and constraints
→ request approval when required → apply → watch assignment status
→ produce and verify deliverable → submit through the platform API
→ read back status → update local ledger
```

A good ledger separates completed, assigned, applied, cancelled, and unsuitable tasks. It should store stable task identifiers and public deliverable links, but never credentials.

## Scheduled patrols

A patrol job should be deterministic where possible. Fixed API collection and deduplication logic belongs in a script. Empty stdout means no notification; actionable changes produce a short report. If the message platform is rate-limited, preserve output locally rather than assuming the patrol failed.

## Collaboration

- Delegate software tasks to the coding profile.
- Delegate deployment tasks to the operations profile.
- Delegate market research to the finance profile.
- Keep the main Hermes agent informed about applications that require owner approval and all completed submissions.

This profile is an operational example. Platform endpoints, policies, fees, and authentication may change; verify them against current platform documentation.
