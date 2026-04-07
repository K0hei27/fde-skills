"""
Greenlight Slack Bridge — Notification Logic

Handles two delivery paths:
  1. Email list  → users.lookupByEmail per address → chat.postMessage DM
  2. Channel ID  → chat.postMessage to that channel directly

Required Slack bot scopes:
    chat:write        — send messages
    users:read.email  — resolve email → user ID (email path only)
"""

import requests
from config import SLACK_BOT_TOKEN

SLACK_API = "https://slack.com/api"


def _slack_post(method, payload):
    """POST to any Slack Web API method. Returns the parsed JSON response."""
    resp = requests.post(
        f"{SLACK_API}/{method}",
        headers={
            "Authorization": f"Bearer {SLACK_BOT_TOKEN}",
            "Content-Type": "application/json",
        },
        json=payload,
        timeout=10,
    )
    resp.raise_for_status()
    return resp.json()


def _lookup_user_by_email(email):
    """
    Resolve a work email to a Slack user ID via users.lookupByEmail.
    Returns user_id string or None on failure.
    Requires users:read.email scope.
    """
    result = _slack_post("users.lookupByEmail", {"email": email})
    if result.get("ok"):
        return result["user"]["id"]
    print(f"  lookup failed for {email}: {result.get('error')}")
    return None


def _build_blocks(report):
    """
    Build Slack Block Kit blocks from the structured report summary.
    Raw markdown is never sent — the skill summarises before POSTing.
    Each field is capped well within Slack's 3000-char block limit.
    """
    agent       = report["agent_name"]
    passed      = report["pass_count"]
    failed      = report["fail_count"]
    total       = passed + failed
    rate        = round(passed / total * 100) if total else 0
    status      = "PASS" if failed == 0 else ("CONDITIONAL" if rate >= 80 else "FAIL")
    emoji       = {"PASS": "✅", "CONDITIONAL": "⚠️", "FAIL": "❌"}[status]
    rec         = report.get("recommendation", "")
    findings    = report.get("key_findings", [])
    actions     = report.get("immediate_actions", [])

    blocks = [
        {
            "type": "header",
            "text": {"type": "plain_text", "text": f"{emoji} Greenlight Report — {agent}"},
        },
        {
            "type": "section",
            "fields": [
                {"type": "mrkdwn", "text": f"*Status:*\n{emoji} {status}"},
                {"type": "mrkdwn", "text": f"*Pass Rate:*\n{rate}% ({passed}/{total})"},
            ],
        },
    ]

    if rec:
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Go-Live Recommendation*\n{rec}"},
        })

    if findings:
        findings_text = "\n".join(f"• {f}" for f in findings[:5])
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Key Findings*\n{findings_text}"},
        })

    if actions:
        actions_text = "\n".join(f"{i+1}. {a}" for i, a in enumerate(actions[:5]))
        blocks.append({
            "type": "section",
            "text": {"type": "mrkdwn", "text": f"*Immediate Actions*\n{actions_text}"},
        })

    blocks.append({
        "type": "context",
        "elements": [{"type": "mrkdwn", "text": "Full report available in your project at `greenlight-output/`"}],
    })
    blocks.append({"type": "divider"})
    return blocks


def _send_message(channel, report):
    """
    Send the formatted report to any Slack channel or DM channel (user ID).
    Returns True on success.
    """
    blocks = _build_blocks(report)
    fallback = (
        f"Greenlight Report — {report['agent_name']}: "
        f"{report['pass_count']} passed / {report['fail_count']} failed"
    )
    result = _slack_post("chat.postMessage", {
        "channel": channel,
        "blocks":  blocks,
        "text":    fallback,
    })
    if result.get("ok"):
        print(f"  ✅ sent to {channel}")
        return True
    print(f"  ❌ failed to send to {channel}: {result.get('error')}")
    return False


def notify_recipients(emails, channel_id, report):
    """
    Deliver the report to all specified recipients.

    Args:
        emails:     list of work email strings (resolved to Slack user IDs)
        channel_id: Slack channel ID string, or None
        report:     dict with agent_name, pass_count, fail_count, report_markdown

    Returns:
        list of dicts: [{ "target": ..., "sent": bool, "error": str|None }]
    """
    results = []

    for email in (emails or []):
        entry = {"target": email, "sent": False, "error": None}
        try:
            user_id = _lookup_user_by_email(email)
            if user_id:
                entry["sent"] = _send_message(user_id, report)
            else:
                entry["error"] = "user not found in Slack workspace"
        except Exception as e:
            entry["error"] = str(e)
        results.append(entry)

    if channel_id:
        entry = {"target": channel_id, "sent": False, "error": None}
        try:
            entry["sent"] = _send_message(channel_id, report)
        except Exception as e:
            entry["error"] = str(e)
        results.append(entry)

    return results
