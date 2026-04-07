---
name: greenlight-notify
description: Deliver a Greenlight test report via Slack DM or channel post. Run this after greenlight-testing or any skill that produces a report. Reads the report, asks who should receive it, and POSTs to the Greenlight Slack bridge.
---

# Greenlight Notify

Sends a Greenlight test report to one or more recipients via Slack. Run this after `/greenlight` (or any skill that produces a report) completes.

---

## Automated Workflow (Follow This)

When the user invokes `/greenlight-notify`, execute these steps automatically:

### Step 1: Find the Report

Look for the most recent Greenlight report:

```bash
ls -t greenlight-output/*/report.md | head -5
```

If multiple reports exist, ask the user which one to send:

```
Use the AskQuestion tool:
{
  "title": "Which report to send?",
  "questions": [{
    "id": "report_path",
    "prompt": "Multiple reports found. Which one should be sent?",
    "options": [
      { "id": "<path1>", "label": "<agent_name> — <date>" },
      { "id": "<path2>", "label": "<agent_name> — <date>" }
    ]
  }]
}
```

Read the selected report:

```bash
cat greenlight-output/{agent_name}/report.md
```

Parse and summarise from the report — do NOT send raw markdown to the bridge:
- `agent_name` — from the report header
- `pass_count` and `fail_count` — from the summary table
- `recommendation` — the one-sentence go-live verdict (e.g. "NOT READY — critical CaseManagement flow failures must be resolved before go-live")
- `key_findings` — up to 5 bullet points, one sentence each, from the Key Findings section
- `immediate_actions` — up to 5 items from the Immediate Actions section, condensed to one line each

The Slack message must fit within Slack's block limits. The full report stays in the project — Slack gets the executive summary only.

### Step 2: Check for Saved Recipients

Check if the user has a `.greenlight` config file with saved defaults:

```bash
cat .greenlight 2>/dev/null || echo "no config"
```

Expected format (if present):

```
notify_emails=dev@company.com,pm@company.com
notify_channel=C1234567890
```

If defaults exist, confirm with the user before using them:

```
Use the AskQuestion tool:
{
  "title": "Send to saved recipients?",
  "questions": [{
    "id": "use_defaults",
    "prompt": "Use saved recipients? (emails: dev@company.com — or enter new ones)",
    "options": [
      { "id": "yes",   "label": "Yes, use saved recipients" },
      { "id": "no",    "label": "No, I'll enter different recipients" },
      { "id": "skip",  "label": "Skip notification" }
    ]
  }]
}
```

### Step 3: Collect Recipients

If no saved defaults, or the user chose to enter new ones, ask:

```
"Who should receive this report?

Enter one or more of:
  • Email addresses (comma-separated): dev@company.com, pm@company.com
  • A Slack channel ID (e.g. C1234567890) for channel broadcast
  • Both emails and a channel ID

Or press Enter to skip."
```

Parse the input:
- Strings containing `@` → treat as email addresses
- Strings starting with `C` and 10 characters → treat as Slack channel ID

If the user provides neither and doesn't skip, remind them:
```
"No recipients provided. Enter at least one email address or Slack channel ID, or press Enter to skip."
```

### Step 4: POST to Slack Bridge

Construct the payload and POST to the Greenlight Heroku bridge:

```bash
curl -s -X POST "https://greenlight-fde-75bc8eacff05.herokuapp.com/notify" \
  -H "Content-Type: application/json" \
  -d '{
    "emails":             ["dev@company.com"],
    "channel_id":         "C1234567890",
    "agent_name":         "{agent_name}",
    "pass_count":         {pass_count},
    "fail_count":         {fail_count},
    "recommendation":     "{one_sentence_verdict}",
    "key_findings":       ["{finding_1}", "{finding_2}", "{finding_3}"],
    "immediate_actions":  ["{action_1}", "{action_2}", "{action_3}"]
  }'
```

Notes:
- Omit `emails` if none were provided, omit `channel_id` if none was provided
- `recommendation`, `key_findings`, `immediate_actions` are summaries — not raw markdown
- Keep each finding/action to one sentence — Slack blocks have a 3000-char limit per element
- The full report stays in `greenlight-output/` — Slack gets the executive summary only
- The bridge URL is shared across all FDEs — no per-user configuration needed

### Step 5: Report Delivery Status

Parse the response and tell the user what happened:

**Success (all delivered):**
```
Report sent successfully!

Recipients notified:
  ✅ dev@company.com
  ✅ pm@company.com
  ✅ #agentforce-results (C1234567890)
```

**Partial failure (HTTP 207):**
```
Report sent with some errors:

  ✅ dev@company.com — delivered
  ❌ unknown@company.com — user not found in Slack workspace
```

**Full failure:**
```
Failed to send report.
Error: {error from response}

Check that:
  • GREENLIGHT_HEROKU_URL is set correctly
  • The Slack bridge server is running
  • SLACK_BOT_TOKEN is configured on the server
```

### Step 6 (Optional): Save Recipients for Next Time

If the user entered new recipients, offer to save them:

```
"Save these recipients as defaults for future runs? (yes / no)"
```

If yes, write or update `.greenlight` in the project root:

```bash
# Append or replace notify lines
grep -v "^notify_" .greenlight 2>/dev/null > .greenlight.tmp || true
echo "notify_emails=dev@company.com,pm@company.com" >> .greenlight.tmp
echo "notify_channel=C1234567890" >> .greenlight.tmp
mv .greenlight.tmp .greenlight
```

Note: `.greenlight` belongs in the **client's Salesforce project repo** (e.g. `force-app/../.greenlight`), not in the greenlight skills repo. The FDE commits it there alongside their test specs and org config. It should be gitignored in the greenlight skills repo itself.

---

## Bridge URL

The Heroku bridge is a shared team instance — no per-FDE configuration needed:

```
https://greenlight-fde-75bc8eacff05.herokuapp.com
```

All FDEs POST to the same URL. The bridge is stateless — each request is independent.

---

## Slack Bridge Requirements

The Slack bridge (`slack-bridge/`) must be deployed to Heroku with:

| Env Var          | Value                   |
|------------------|-------------------------|
| `SLACK_BOT_TOKEN`| Your Slack bot token     |
| `PORT`           | Set automatically by Heroku |

**Required Slack bot scopes:**
- `chat:write` — send DMs and channel messages
- `users:read.email` — resolve email addresses to Slack user IDs (only needed for email delivery)

For channel posting to public channels without the bot being a member, also add:
- `chat:write.public`

---

## Workflow: From Greenlight to Notify

```
1. Run /greenlight          → greenlight-output/{agent}/report.md
2. (Optional) Run /greenlight-dashboard  → LWC deployed to org
3. Run /greenlight-notify   → report DM'd to recipients via Slack
```

---

## Key Files

| What                  | Where                                       |
|-----------------------|---------------------------------------------|
| Slack bridge server   | `slack-bridge/app.py`                       |
| Notification logic    | `slack-bridge/notifier.py`                  |
| Bridge config         | `slack-bridge/config.py`                    |
| Saved recipients      | `.greenlight` (gitignored, local only)      |
| Test reports          | `greenlight-output/{agent_name}/report.md`  |
