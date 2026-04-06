---
name: agent-preview
description: Quick Agentforce testing via sf agent preview CLI. Use for fast iterative testing, single utterance tests, or when you don't need full Testing Center orchestration.
---

# Agent Preview Skill

Fast, interactive Agentforce testing using `sf agent preview` CLI command.

## When to Use This Skill

Use this skill when the user:
- Wants to quickly test an agent utterance
- Needs fast iterative testing during development
- Asks for "quick test" or "preview agent"
- Doesn't need full go-live readiness testing

For comprehensive go-live testing, use `greenlight-testing` instead.

---

## Prerequisites

- Salesforce CLI (`sf`) v2.x installed
- Authenticated to target org: `sf org login web --alias {org}`
- Agent deployed and activated in the org

---

## Quick Start

### Single Utterance Test

```bash
sf agent preview \
  --name {AgentName} \
  --target-org {org_alias}
```

This opens an interactive session. Type utterances and see agent responses.

### Test with Specific Input

```bash
echo "What is my order status?" | sf agent preview \
  --name {AgentName} \
  --target-org {org_alias}
```

---

## Workflow

### Step 1: Identify the Agent

```bash
sf data query \
  --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition" \
  --target-org {org_alias} \
  --json
```

### Step 2: Start Preview Session

```bash
sf agent preview --name {AgentDeveloperName} --target-org {org_alias}
```

### Step 3: Test Utterances

Enter test utterances interactively:
```
You: What is my order status?
Agent: I can help you check your order status. Could you please provide your order number?

You: Order 12345
Agent: I found order #12345. It was placed on March 15 and is currently in transit...
```

### Step 4: Analyze Results

Look for:
- Correct topic routing
- Expected action invocations
- Appropriate responses
- Proper error handling

---

## Common Test Scenarios

### Topic Routing
Test that utterances route to the correct topic:
```
"Check my order status"     → Orders topic
"I want to return something" → Returns topic
"What are your hours?"      → FAQ/Knowledge topic
```

### Action Invocation
Verify actions are called:
```
"Look up order 12345"       → Get_Order_Status action
"Start a return"            → Initiate_Return action
```

### Edge Cases
Test boundary conditions:
```
"asdfghjkl"                 → Fallback/clarification
""                          → Prompt for input
"<script>alert(1)</script>" → Safe handling
```

---

## Batch Testing (Script)

For multiple utterances, create a test script:

```bash
#!/bin/bash
# test-agent.sh

ORG="my-org"
AGENT="Customer_Service"

utterances=(
    "What is my order status?"
    "I want to return my purchase"
    "What are your business hours?"
)

for utterance in "${utterances[@]}"; do
    echo "Testing: $utterance"
    echo "$utterance" | sf agent preview --name $AGENT --target-org $ORG
    echo "---"
done
```

---

## Comparison: agent-preview vs Testing Center

| Aspect | agent-preview | Testing Center |
|--------|---------------|----------------|
| Speed | Fast, immediate | Slower, queued |
| Setup | None | Test spec YAML |
| Metrics | Manual review | Automated scoring |
| Scale | Single utterances | Batch execution |
| Best for | Development | Go-live readiness |

---

## Tips

1. **Use for iteration** - Quick feedback during agent development
2. **Test edge cases** - Unusual inputs, empty strings, special characters
3. **Check action params** - Verify correct data extraction
4. **Note failures** - Document issues for greenlight-testing later
