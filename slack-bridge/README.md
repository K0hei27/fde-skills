# Greenlight Slack Bridge

Lightweight Heroku server that receives Greenlight test results and delivers them as Slack messages. Single responsibility — no Salesforce credentials, no session management.

## How It Works

```
FDE runs tests locally (sf CLI)
    → Greenlight skill generates report
        → skills/notify POSTs to /notify
            → Bridge looks up each email via Slack API
                → Sends DM or channel message
```

## Routes

| Method | Path | Description |
|--------|------|-------------|
| `POST` | `/notify` | Receive report + recipients → send Slack messages |
| `GET` | `/health` | Liveness check |

## POST /notify Payload

```json
{
  "emails":             ["dev@company.com"],
  "channel_id":         "C1234567890",
  "agent_name":         "MyAgent",
  "pass_count":         10,
  "fail_count":         2,
  "recommendation":     "NOT READY — fix CaseManagement flows before go-live.",
  "key_findings":       ["Finding 1", "Finding 2"],
  "immediate_actions":  ["Action 1", "Action 2"]
}
```

At least one of `emails` or `channel_id` required. The skill summarises the report before POSTing — raw markdown is never sent.

## Deploy to Heroku

```bash
git clone <this-repo>
cd slack-bridge
heroku create your-app-name
heroku config:set SLACK_BOT_TOKEN=xoxb-your-token
git push heroku main
```

## Required Slack Bot Scopes

| Scope | Purpose |
|-------|---------|
| `chat:write` | Send DMs and channel messages |
| `chat:write.public` | Post to public channels without joining |
| `users:read.email` | Resolve email → Slack user ID |

## Files

| File | Purpose |
|------|---------|
| `app.py` | Flask routes — `/notify` and `/health` |
| `config.py` | Reads `SLACK_BOT_TOKEN` and `PORT` from env |
| `notifier.py` | Slack API calls — email lookup + message delivery |
| `Procfile` | Heroku process config (`gunicorn app:app`) |
| `requirements.txt` | Flask, requests, gunicorn |
