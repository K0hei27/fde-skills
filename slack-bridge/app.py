"""
Greenlight Slack Bridge — Notification Server

Single-purpose server: receives test results from the Greenlight skill
and delivers them as Slack DMs or channel posts. No Salesforce credentials
live here — all test execution happens on the FDE's local machine.

Routes:
    POST /notify  — receive report + recipient list → send Slack messages
    GET  /health  — liveness check

Required Slack bot scopes:
    chat:write        — send DMs and channel messages
    users:read.email  — resolve email addresses to Slack user IDs
"""

from flask import Flask, request, jsonify
from config import SLACK_BOT_TOKEN, PORT
from notifier import notify_recipients

app = Flask(__name__)


@app.route('/notify', methods=['POST'])
def notify():
    """
    Receive a Greenlight report and deliver it to the specified recipients.

    Expected JSON payload:
    {
        "emails":          ["dev@company.com", "pm@company.com"],  // optional
        "channel_id":      "C1234567890",                          // optional
        "agent_name":      "MyAgent",
        "pass_count":      10,
        "fail_count":      2,
        "report_markdown": "# Report\\n..."
    }

    At least one of `emails` or `channel_id` must be provided.
    Returns per-recipient delivery status.
    """
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Request body must be JSON"}), 400

    emails = data.get('emails') or []
    channel_id = data.get('channel_id')

    if not emails and not channel_id:
        return jsonify({"error": "Provide at least one of: emails, channel_id"}), 400

    if not SLACK_BOT_TOKEN:
        return jsonify({"error": "SLACK_BOT_TOKEN not configured on server"}), 500

    report = {
        "agent_name":         data.get('agent_name', 'Unknown Agent'),
        "pass_count":         data.get('pass_count', 0),
        "fail_count":         data.get('fail_count', 0),
        "recommendation":     data.get('recommendation', ''),
        "key_findings":       data.get('key_findings', []),
        "immediate_actions":  data.get('immediate_actions', []),
    }

    results = notify_recipients(emails=emails, channel_id=channel_id, report=report)
    all_sent = all(r['sent'] for r in results)

    return jsonify({
        "ok":       all_sent,
        "notified": results,
    }), 200 if all_sent else 207


@app.route('/health', methods=['GET'])
def health():
    return jsonify({
        "status":             "ok",
        "token_configured":   bool(SLACK_BOT_TOKEN),
    }), 200


if __name__ == '__main__':
    app.run(host='0.0.0.0', port=PORT)
