"""
Greenlight Slack Bridge — Configuration

Notification-only server. All Salesforce execution happens on the FDE's
local machine. This server only needs Slack credentials.
"""

import os

SLACK_BOT_TOKEN = os.environ.get('SLACK_BOT_TOKEN')
PORT = int(os.environ.get('PORT', 5001))
