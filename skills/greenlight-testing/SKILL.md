---
name: greenlight
description: >-
  Automate Agentforce testing orchestration to answer "Are we ready for go-live?"
  Use when the user wants to test an Agentforce agent, needs a test strategy,
  asks about go-live readiness, wants to generate test cases, or needs help with
  Agentforce Testing Center. Guides through org selection, agent selection,
  requirements gathering, test strategy generation, execution plan review,
  test execution, and comprehensive reporting.
license: MIT
metadata:
  version: "2.1.0"
  author: Salesforce FDE Team
  compatibility: "Requires: Salesforce CLI, Python 3.7+, PyYAML"
allowed-tools: "Bash Read Write Glob Grep AskUserQuestion"
user-invocable: true
---

# Greenlight v2.1

Automate Agentforce testing orchestration to answer: **"Are we ready for go-live?"**

---

## Recommended Model

**This skill is optimized for Claude 4.5 Opus High (claude-4.5-opus-high)**

For best results with structured outputs, accurate test case generation, and following the multi-step approval workflow, configure Cursor to use this model.

Why this model works best:
- Better at following complex multi-step workflows with approval gates
- More accurate structured output (YAML, JSON, Markdown)
- Deeper reasoning for realistic test scenario generation
- Consistent adherence to "DO NOT proceed until approved" constraints

---

## When to Use This Skill

Use this skill when the user:
- Wants to test an Agentforce agent
- Needs a test strategy or test plan
- Asks "are we ready for go-live?"
- Wants to generate test cases
- Needs help with Agentforce Testing Center
- Runs `/greenlight`

---

## Critical Workflow Rules

**IMPORTANT: This skill follows a strict 4-step approval workflow. You MUST:**

1. **NEVER** proceed to the next phase without explicit user approval
2. **NEVER** run tests without the user reviewing execution-plan.md first
3. **NEVER** use terminal input() prompts - use AskQuestion tool for all user interaction
4. **NEVER** hardcode org aliases, agent names, topic names, or action names
5. **ALWAYS** save strategy and plans to markdown files for user review
6. **ALWAYS** gather detailed requirements for realistic expectedOutcome values

---

## Workflow Overview

```
Prerequisites Check (ALWAYS run first)
    ↓
Phase 0: First-Time Setup (if needed)
    ├─ Create config.json
    └─ Initialize SFDX project context (auto-creates if needed)
    ↓
Phase 1: Connect & Select (Org → Agent → Version)
    ↓
Phase 2a: Basic Strategy (goals, priorities, timeline)
    ↓
Phase 2b: Deep Requirements Gathering
    ├─ Per user story details
    ├─ Context variables (ContactId, AccountId, etc.)
    └─ Sample conversations & test data
    ↓
Phase 3: Generate & Review Strategy → strategy.md → [USER APPROVAL REQUIRED]
    ↓
Phase 4: Generate & Review Execution Plan → execution-plan.md → [USER APPROVAL REQUIRED]
    ↓
Phase 5: Execute Tests
    ↓
Phase 6: Generate Report → report.md
```

---

## Prerequisites Check (ALWAYS Run First)

**Before starting any workflow, check all prerequisites and help user set up if needed.**

### Step P.1: Check Salesforce CLI

```bash
sf --version
```

**If command fails or sf not found:**

Tell the user:
```
Salesforce CLI (sf) is required but not installed.

To install:
1. Visit: https://developer.salesforce.com/tools/salesforcecli
2. Or run: npm install -g @salesforce/cli

After installing, try again.
```

**STOP here if sf CLI is not installed.** Do not proceed.

### Step P.2: Check Python and PyYAML

```bash
python3 -c "import yaml; print('PyYAML installed')"
```

**If PyYAML is not installed, ask user permission to install:**

```
Use the AskQuestion tool with:
{
  "title": "Install Required Dependency",
  "questions": [
    {
      "id": "install_pyyaml",
      "prompt": "PyYAML is required for generating test specifications but is not installed. May I install it?",
      "options": [
        {"id": "yes", "label": "Yes, install PyYAML (pip install pyyaml)"},
        {"id": "no", "label": "No, I'll install it manually"}
      ]
    }
  ]
}
```

If user selects "yes":
```bash
pip3 install pyyaml
```

If user selects "no", tell them:
```
Please run: pip3 install pyyaml

Then try again.
```

**STOP here if user declines and PyYAML is not installed.**

### Step P.3: Check for Authenticated Orgs

```bash
sf org list --json
```

**If no authenticated orgs found:**

Tell the user:
```
No authenticated Salesforce orgs found.

You need to authenticate to a Salesforce org that has your Agentforce agent.

To authenticate:
1. Run: sf org login web --alias my-org
2. A browser will open for Salesforce login
3. After login, return here and try again

Would you like me to run the authentication command now?
```

```
Use the AskQuestion tool with:
{
  "title": "Salesforce Authentication",
  "questions": [
    {
      "id": "auth_now",
      "prompt": "No authenticated Salesforce orgs found. Would you like to authenticate now?",
      "options": [
        {"id": "yes", "label": "Yes, authenticate now (opens browser)"},
        {"id": "no", "label": "No, I'll do it manually later"}
      ]
    }
  ]
}
```

If user selects "yes", ask for alias:
```
What alias would you like to use for this org? (e.g., 'my-org', 'dev-sandbox')
```

Then run:
```bash
sf org login web --alias {user_provided_alias}
```

Wait for authentication to complete, then verify:
```bash
sf org list --json
```

**If user declines or auth fails, STOP here.** Tell user to authenticate and try again.

### Step P.4: All Prerequisites Met

Once all checks pass, display:
```
Prerequisites check complete:
- Salesforce CLI: Installed
- PyYAML: Installed  
- Authenticated orgs: Found {count} org(s)

Ready to proceed with Agentforce testing.
```

Then continue to Phase 0.

---

## Phase 0: First-Time Setup

**When:** Config file `greenlight-output/config.json` does not exist.

### Step 0.1: Check for Existing Config

```bash
# Check if config exists
ls greenlight-output/config.json
```

### Step 0.2: If No Config, Run Setup Wizard

Use AskQuestion to gather preferences:

```
Use the AskQuestion tool with:
{
  "title": "Greenlight First-Time Setup",
  "questions": [
    {
      "id": "output_dir",
      "prompt": "Where should Greenlight save output files?",
      "options": [
        {"id": "default", "label": "greenlight-output/ (recommended)"},
        {"id": "custom", "label": "Let me specify a custom path"}
      ]
    }
  ]
}
```

### Step 0.3: Save Config

Create `greenlight-output/config.json`:

```json
{
  "output_directory": "greenlight-output",
  "setup_complete": true,
  "created_at": "{timestamp}"
}
```

### Step 0.4: Initialize SFDX Project Context (CRITICAL)

**Problem:** The skill uses `sf project retrieve start` which requires an SFDX project directory. Cursor users are typically in their project already, but Claude Code users may not be.

**Solution:** Auto-detect and create a temporary SFDX project if needed.

#### Check if in SFDX Project

```bash
# Check for sfdx-project.json
test -f sfdx-project.json && echo "SFDX_PROJECT_EXISTS=true" || echo "SFDX_PROJECT_EXISTS=false"
```

#### If NOT in SFDX Project, Create Temporary One

```bash
# Create temporary SFDX project in greenlight-output/
mkdir -p greenlight-output/.sfdx-temp
cd greenlight-output/.sfdx-temp

# Initialize SFDX project
sf project generate --name greenlight-temp

# Store the project path for later use
echo "Created temporary SFDX project at: $(pwd)"
```

#### Store Project Context

Save the working directory context:

```bash
# If existing project
export GREENLIGHT_SFDX_DIR="$(pwd)"
export GREENLIGHT_USING_TEMP_PROJECT="false"

# If created temp project
export GREENLIGHT_SFDX_DIR="$(pwd)/greenlight-output/.sfdx-temp/greenlight-temp"
export GREENLIGHT_USING_TEMP_PROJECT="true"
```

**IMPORTANT:** All `sf project retrieve start` commands MUST be run from `$GREENLIGHT_SFDX_DIR`.

**Tell the user:**
```
Setting up workspace...
✅ SFDX project context initialized
```

---

## Phase 1: Connect & Select

### Step 1.1: Detect Authenticated Orgs

```bash
sf org list --json
```

Parse the JSON response to extract:
- `result.nonScratchOrgs[]` - Production/Sandbox orgs
- `result.scratchOrgs[]` - Scratch orgs

For each org, extract: `alias`, `username`, `instanceUrl`, `isDefaultUsername`

### Step 1.2: Present Org Selection

**DO NOT use terminal input(). Use AskQuestion tool:**

```
Use the AskQuestion tool with:
{
  "title": "Select Salesforce Org",
  "questions": [
    {
      "id": "org_selection",
      "prompt": "Which Salesforce org do you want to test?",
      "options": [
        // Dynamically build from sf org list results
        {"id": "org1_alias", "label": "org1_alias (user@example.com) [DEFAULT]"},
        {"id": "org2_alias", "label": "org2_alias (user@example.sandbox)"},
        // ... more orgs
      ]
    }
  ]
}
```

**If no orgs found:**
```
No authenticated Salesforce orgs found.

To authenticate, run:
  sf org login web --alias my-org

Then try /greenlight again.
```

### Step 1.3: Query Available Agents

Using the selected org:

```bash
sf data query \
  --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition" \
  --target-org {selected_org} \
  --json
```

### Step 1.4: Present Agent Selection

```
Use the AskQuestion tool with:
{
  "title": "Select Agentforce Agent",
  "questions": [
    {
      "id": "agent_selection",
      "prompt": "Which agent do you want to test?",
      "options": [
        // Dynamically build from query results
        {"id": "Customer_Service", "label": "Customer Service (Customer_Service)"},
        {"id": "Sales_Assistant", "label": "Sales Assistant (Sales_Assistant)"},
        // ... more agents
      ]
    }
  ]
}
```

### Step 1.5: Query Agent Versions

```bash
sf data query \
  --query "SELECT Id, DeveloperName, VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = '{selected_agent}'" \
  --target-org {selected_org} \
  --json
```

### Step 1.6: Present Version Selection

Default to the version with `Status = 'Active'`:

```
Use the AskQuestion tool with:
{
  "title": "Select Agent Version",
  "questions": [
    {
      "id": "version_selection",
      "prompt": "Which version do you want to test? (Active version is recommended)",
      "options": [
        {"id": "v3", "label": "v3 - ACTIVE (recommended)"},
        {"id": "v2", "label": "v2 - Draft"},
        {"id": "v1", "label": "v1 - Inactive"}
      ]
    }
  ]
}
```

### Step 1.7: Retrieve Agent Metadata

**IMPORTANT:** Run these commands from the SFDX project directory (`$GREENLIGHT_SFDX_DIR` set in Step 0.4).

```bash
# Change to SFDX project directory
cd "$GREENLIGHT_SFDX_DIR"

# Retrieve bot definition
sf project retrieve start \
  --metadata Bot:{selected_agent} \
  --target-org {selected_org}

# Retrieve topics and actions (use the version suffix)
sf project retrieve start \
  --metadata GenAiPlannerBundle:{selected_agent}_{version} \
  --target-org {selected_org}

# Return to original directory if needed
cd -
```

**Tell the user:**
```
Retrieving agent metadata from Salesforce...
✅ Bot definition retrieved
✅ Topics and actions retrieved
```

### Step 1.8: Parse Metadata

Parse the XML files at:
- `$GREENLIGHT_SFDX_DIR/force-app/main/default/bots/{agent}/*.bot-meta.xml`
- `$GREENLIGHT_SFDX_DIR/force-app/main/default/genAiPlannerBundles/{agent}_{version}/*.genAiPlannerBundle`

Extract:
- **Topics**: From `<localTopics><localDeveloperName>` - use this exact name for expectedTopic
- **Actions**: From `<localActionLinks><genAiFunctionName>` - use for expectedActions
- **Topic Descriptions**: From `<localTopics><description>`

**IMPORTANT**: Store the `localDeveloperName` values exactly as they appear - these are the values needed for test specs.

### Step 1.9: Confirm Topics with User

Present detected topics for confirmation:

```
Use the AskQuestion tool with:
{
  "title": "Confirm Detected Topics",
  "questions": [
    {
      "id": "topics_confirmed",
      "prompt": "I found these topics in your agent. Are they correct?\\n\\n- Claims: Handles claim inquiries\\n- Knowledge_Search: Answers FAQs\\n- Benefits: Benefit information\\n\\nIf any are missing or incorrect, select 'Edit'",
      "options": [
        {"id": "confirm", "label": "Yes, these are correct"},
        {"id": "edit", "label": "No, let me provide the correct topic names"}
      ]
    }
  ]
}
```

If user selects "Edit", ask for the correct topic names.

---

## Phase 2a: Basic Strategy

### Step 2a.1: Accuracy Goals

```
Use the AskQuestion tool with:
{
  "title": "Define Accuracy Goals",
  "questions": [
    {
      "id": "accuracy_goal",
      "prompt": "What are your accuracy targets for go-live?",
      "options": [
        {"id": "high", "label": "High (95% topic, 90% action, 85% response) - Production ready"},
        {"id": "medium", "label": "Medium (90% topic, 85% action, 80% response) - Pilot ready"},
        {"id": "low", "label": "Low (85% topic, 80% action, 75% response) - Beta/Testing"},
        {"id": "custom", "label": "Custom - Let me specify my own targets"}
      ]
    }
  ]
}
```

### Step 2a.2: User Stories with Priorities

Ask user to provide their user stories:

```
Please provide your user stories with priorities.

Format each story as: P0/P1/P2: Description

Example:
- P0: Check claim status
- P0: Submit new claim
- P1: Find nearby providers
- P1: Answer benefit questions
- P2: Update contact information

P0 = Critical for go-live (must pass)
P1 = Important (should pass)
P2 = Nice to have (can accept some failures)

Enter your user stories:
```

### Step 2a.3: Focus Areas

```
Use the AskQuestion tool with:
{
  "title": "Focus Areas",
  "questions": [
    {
      "id": "focus_areas",
      "prompt": "Any specific topics or scenarios you want to focus on? (e.g., areas that had issues in UAT)",
      "options": [
        {"id": "none", "label": "No specific focus - test all evenly"},
        {"id": "specify", "label": "Yes - let me specify focus areas"}
      ]
    }
  ]
}
```

### Step 2a.4: Timeline

```
Use the AskQuestion tool with:
{
  "title": "Go-Live Timeline",
  "questions": [
    {
      "id": "timeline",
      "prompt": "When do you need to go live?",
      "options": [
        {"id": "1week", "label": "Within 1 week"},
        {"id": "2weeks", "label": "Within 2 weeks"},
        {"id": "1month", "label": "Within 1 month"},
        {"id": "flexible", "label": "Flexible / No specific date"}
      ]
    }
  ]
}
```

---

## Phase 2b: Deep Requirements Gathering

**CRITICAL: This phase ensures realistic expectedOutcome values instead of generic ones.**

### Why This Matters

**BAD expectedOutcome (generic - DO NOT DO THIS):**
```yaml
expectedOutcome: "Agent should correctly handle the claims scenario"
```

**GOOD expectedOutcome (specific - DO THIS):**
```yaml
expectedOutcome: |
  Agent should:
  1. Retrieve claim #12345 details (status, date filed, amount)
  2. Show current status: "In Review" or "Approved" or "Denied"
  3. If approved: Show payment date and amount ($XXX.XX)
  4. If denied: Explain denial reason and appeal process
  5. Offer to connect to claims specialist if user has questions
```

### Step 2b.1: For Each P0/P1 User Story, Gather Details

For each user story, ask:

```
Let's define specific requirements for: "{user_story}"

1. SCENARIO: What is the user trying to accomplish?
   - What data/context does the user provide? (e.g., claim number, member ID)
   
2. EXPECTED BEHAVIOR: What should the agent do?
   - What data should it retrieve?
   - What actions should it invoke?
   - What should it tell the user?

3. SUCCESS CRITERIA: How do you know it worked?
   - What specific information must be in the response?
   - What format should the data be in?

4. EDGE CASES: What if something goes wrong?
   - What if the data doesn't exist?
   - What if the user provides incomplete info?
   - What error messages are appropriate?

Please provide these details:
```

### Step 2b.2: Map User Stories to Topics

Present the detected topics and ask user to map:

```
Use the AskQuestion tool with:
{
  "title": "Map User Stories to Topics",
  "questions": [
    {
      "id": "story1_topic",
      "prompt": "Which topic handles: 'Check claim status'?",
      "options": [
        {"id": "Claims", "label": "Claims"},
        {"id": "Knowledge_Search", "label": "Knowledge_Search"},
        {"id": "Benefits", "label": "Benefits"}
      ]
    },
    {
      "id": "story1_actions",
      "prompt": "Which action(s) should be invoked for 'Check claim status'?",
      "options": [
        {"id": "Get_Claim_Status", "label": "Get_Claim_Status"},
        {"id": "Get_Claim_Details", "label": "Get_Claim_Details"},
        {"id": "both", "label": "Both actions"}
      ],
      "allow_multiple": true
    }
  ]
}
```

### Step 2b.3: Identify Required Context Variables (CRITICAL)

**Why This Matters:**
Without proper context variables, agents will correctly ask users to identify themselves (secure behavior), but tests will fail expecting immediate action invocation, resulting in 0% action accuracy.

**Common examples:**
- `ContactId` - For customer portals (agent verifies user identity before retrieving personal data)
- `AccountId` - For account-specific actions
- `UserId` - For internal agent actions

**Ask the user:**

```
Use the AskQuestion tool with:
{
  "title": "Context Variables",
  "questions": [
    {
      "id": "needs_context_vars",
      "prompt": "Does your agent need context variables (like ContactId, AccountId) to invoke actions? These are values the agent needs to verify user identity or retrieve user-specific data.",
      "options": [
        {"id": "yes", "label": "Yes - provide context variables"},
        {"id": "no", "label": "No - agent doesn't require context"}
      ]
    }
  ]
}
```

**If user selects "yes", ask:**

```
Please list the context variables your agent needs in this format:

ContactId: 003Hp00000ABC123
AccountId: 001Hp00000XYZ789

These will be included in all test cases.
```

**Store the context variables** for use in test spec generation (Step 4.1).

**If user selects "no":**

```
⚠️ Note: Tests will be generated without context variables. If your agent asks users
to identify themselves before invoking actions, this is correct secure behavior,
but tests expecting immediate action invocation will fail.
```

### Step 2b.4: Collect Sample Conversations (Optional but Recommended)

```
Would you like to provide example conversations showing ideal agent behavior?

This helps generate more realistic test cases.

Example format:
---
User: "What's the status of my claim 12345?"
Agent: "I found claim #12345. It was filed on January 15, 2026 for $500.00. 
        Current status: In Review. Expected decision date: January 25, 2026.
        Would you like me to explain the review process or connect you with 
        a claims specialist?"
---

Enter your example conversation (or type 'skip' to continue):
```

### Step 2b.5: Query Test Data from Org

**Try to find real test data automatically:**

```bash
# Example: Find members with claims
sf data query \
  --query "SELECT Id, Name, MemberId__c FROM Account WHERE RecordType.Name = 'Member' LIMIT 5" \
  --target-org {selected_org} \
  --json

# Example: Find sample claims
sf data query \
  --query "SELECT Id, ClaimNumber__c, Status__c FROM Claim__c LIMIT 5" \
  --target-org {selected_org} \
  --json
```

If data found, use it in test cases. If not, show warning:

```
Use the AskQuestion tool with:
{
  "title": "Test Data",
  "questions": [
    {
      "id": "test_data",
      "prompt": "I couldn't find test data in your org. Test cases with placeholder data may fail. How would you like to proceed?",
      "options": [
        {"id": "provide", "label": "Let me provide test data (member IDs, claim numbers, etc.)"},
        {"id": "placeholders", "label": "Use placeholders - I'll update them later"},
        {"id": "skip", "label": "Skip data-dependent test cases"}
      ]
    }
  ]
}
```

---

## Phase 3: Generate & Review Strategy

### Step 3.1: Generate Strategy Document

Create the strategy document at `greenlight-output/{agent_name}/strategy.md`:

```markdown
# Test Strategy: {agent_name}

*Generated: {timestamp}*
*Org: {org_alias}*
*Agent Version: {version}*

---

## Executive Summary

| | |
|---|---|
| **Goal** | {goal_description} |
| **Test Cases** | {total_test_cases} |
| **Est. Credits** | {credits_calculation} |
| **Est. Duration** | {estimated_minutes} minutes |
| **Go-Live Date** | {timeline} |

---

## Coverage Matrix

| User Story | Priority | Topic | Actions | Test Cases |
|------------|----------|-------|---------|------------|
| {story_1} | P0 | {topic_1} | {actions_1} | {count_1} |
| {story_2} | P0 | {topic_2} | {actions_2} | {count_2} |
| ... | ... | ... | ... | ... |

---

## Accuracy Targets

| Priority | Topic % | Action % | Response % |
|----------|---------|----------|------------|
| P0 | ≥{p0_topic}% | ≥{p0_action}% | ≥{p0_response}% |
| P1 | ≥{p1_topic}% | ≥{p1_action}% | ≥{p1_response}% |
| P2 | ≥{p2_topic}% | ≥{p2_action}% | ≥{p2_response}% |

---

## User Story Details

### {user_story_1} (P0)

**Scenario:** {scenario_description}

**Expected Agent Behavior:**
1. {behavior_step_1}
2. {behavior_step_2}
3. {behavior_step_3}

**Success Criteria:**
- {criteria_1}
- {criteria_2}

**Edge Cases:**
- If {condition}: {expected_response}
- If {condition}: {expected_response}

---

## Job Plan

| Job | User Story | Topic | Test Cases |
|-----|------------|-------|------------|
| 1 | {story_1} | {topic_1} | {count_1} |
| 2 | {story_2} | {topic_2} | {count_2} |
| ... | ... | ... | ... |

---

## Credit Estimate

| Item | Count | Credits |
|------|-------|---------|
| Test Cases | {total_cases} | |
| Credits per Test | x 0.5 | |
| **Subtotal** | | {subtotal} |
| Overhead (10%) | | {overhead} |
| **Total** | | **~{total_credits}** |

---

## Readiness Criteria

| Status | Criteria |
|--------|----------|
| ✅ **Ready** | All P0 topics at target, action accuracy ≥90% |
| ⚠️ **Conditional** | P0 at threshold, gaps documented |
| 🚫 **Not Ready** | Any P0 below threshold |
```

### Step 3.2: Present Summary and Ask for Approval

**Display summary in conversation:**

```
## Test Strategy Summary

I've created a test strategy for {agent_name}:

- **Total Test Cases:** {total}
- **Estimated Credits:** ~{credits}
- **Coverage:** {num_stories} user stories across {num_topics} topics

**User Stories:**
- P0: {p0_count} stories ({p0_tests} test cases)
- P1: {p1_count} stories ({p1_tests} test cases)
- P2: {p2_count} stories ({p2_tests} test cases)

Full strategy saved to: `greenlight-output/{agent_name}/strategy.md`

Please review the file, then let me know if you'd like to proceed.
```

**Use AskQuestion for approval:**

```
Use the AskQuestion tool with:
{
  "title": "Strategy Review",
  "questions": [
    {
      "id": "strategy_approval",
      "prompt": "Do you approve this test strategy?",
      "options": [
        {"id": "approve", "label": "Yes, proceed to execution plan"},
        {"id": "edit", "label": "No, I want to make changes"},
        {"id": "cancel", "label": "Cancel and start over"}
      ]
    }
  ]
}
```

**CRITICAL: DO NOT proceed to Phase 4 unless user selects "approve".**

---

## Phase 4: Generate & Review Execution Plan

### Step 4.0: Verify Topic and Action API Names (REQUIRED)

**CRITICAL: Before generating test specs, verify the actual topic and action API names from metadata.**

This step ensures `expectedTopic` and `expectedActions` values match the actual agent configuration.

#### Extract Names from Retrieved Metadata

Use the metadata already retrieved in Step 1.7. Parse the `GenAiPlannerBundle` XML files at:
- `$GREENLIGHT_SFDX_DIR/force-app/main/default/genAiPlannerBundles/{agent}_{version}/*.genAiPlannerBundle`

Extract:
- **Topics:** `<localTopics><localDeveloperName>` → Use as `expectedTopic`
- **Actions:** `<localActionLinks><genAiFunctionName>` → Use as `expectedActions`

**Note:** GenAiTopic and GenAiFunction objects are NOT queryable via SOQL. Always use metadata parsing.

#### Present Verified Names to User

**Display the verified API names before proceeding:**

```
## Verified Topic & Action API Names

### Topics (use these exact values for expectedTopic)

| Topic Label | API Name (use this) |
|-------------|---------------------|
| Claims | `Claims` |
| Benefits | `Benefits` |
| Knowledge Search | `Knowledge_Search` |

### Actions (use these exact values for expectedActions)

| Action Label | API Name (use this) | Topic |
|--------------|---------------------|-------|
| Get Claim Status | `Get_Claim_Status` | Claims |
| Submit Claim | `Submit_Claim` | Claims |
| Search Knowledge | `Search_Knowledge` | Knowledge_Search |

⚠️ **Please confirm these names match your agent configuration before proceeding.**
```

**Use AskQuestion for confirmation:**

```
Use the AskQuestion tool with:
{
  "title": "Verify API Names",
  "questions": [
    {
      "id": "api_names_confirmed",
      "prompt": "I found the above topic and action API names in your org. Do they look correct?",
      "options": [
        {"id": "confirm", "label": "Yes, proceed with these names"},
        {"id": "edit", "label": "No, let me provide corrections"}
      ]
    }
  ]
}
```

**Why This Matters:**
- Test specs with incorrect topic/action names will **fail silently** or produce misleading results
- The `localDeveloperName` from metadata must match exactly (case-sensitive)
- Common mistakes to avoid:
  - ❌ Using display labels: `"Get Claim Status"` 
  - ❌ Using full IDs: `"Claims_16jd5c475874c40"`
  - ✅ Using API names: `"Get_Claim_Status"`

**CRITICAL: DO NOT proceed to Step 4.1 unless user confirms the API names.**

---

### Step 4.1: Generate Test Spec YAML Files

For each job/user story, create YAML test spec:

```yaml
name: {agent_name}_Job{n}_{story_slug}
subjectType: AGENT
subjectName: {agent_name}
subjectVersion: {version}
testCases:
  - utterance: "{realistic_user_utterance_1}"
    contextVariables:  # Use context variables from Step 2b.3
      - name: ContactId
        value: "{contact_id_value}"
      # Add more as needed, or leave empty [] if none provided
    customEvaluations: []
    expectedTopic: {topic_localDeveloperName}
    expectedActions:
      - {action_1_localDeveloperName}
      - {action_2_localDeveloperName}
    expectedOutcome: |
      {detailed_expected_outcome_from_phase_2b}
    metrics:
      - completeness
      - coherence
      - conciseness
      - output_latency_milliseconds
  
  - utterance: "{realistic_user_utterance_2}"
    # ... more test cases
```

**IMPORTANT - expectedOutcome Guidelines:**

```
CONSTRAINTS for expectedOutcome:
- NEVER use generic phrases like "should handle correctly" or "should process the request"
- ALWAYS include specific data fields that should appear in the response
- ALWAYS describe the sequence of steps the agent should take
- INCLUDE what happens in success AND failure scenarios
- USE the details gathered in Phase 2b

Example transformations:

BAD: "Agent should handle the order correctly"
GOOD: "Agent retrieves order #ORD-12345 showing: item name (Blue Widget), 
       purchase date (Jan 15, 2026), price ($49.99), shipping status (In Transit, 
       expected Jan 20). Asks if user wants to track shipment or modify order."

BAD: "Agent should process the return"
GOOD: "Agent checks return eligibility for order #ORD-12345:
       1. Verifies order is within 30-day return window (YES - 15 days remaining)
       2. Confirms item is in returnable category (YES - Electronics)
       3. Generates return label (URL: returns.example.com/ABC123)
       4. Confirms refund amount ($49.99) to original payment method (Visa ***1234)
       5. Provides estimated refund timeline (3-5 business days)"
```

### Step 4.2: Generate Execution Plan Document

Create `greenlight-output/{agent_name}/execution-plan.md`:

```markdown
# Execution Plan: {agent_name}

*Generated: {timestamp}*
*Based on strategy approved: {strategy_timestamp}*

---

## Jobs to Execute

| Job # | Name | Test Cases | Est. Credits | Est. Duration |
|-------|------|------------|--------------|---------------|
| 1 | {job_1_name} | {count_1} | {credits_1} | {duration_1} |
| 2 | {job_2_name} | {count_2} | {credits_2} | {duration_2} |
| ... | ... | ... | ... | ... |
| **Total** | | **{total_cases}** | **{total_credits}** | **{total_duration}** |

---

## Job 1: {job_1_name}

**User Story:** {user_story}
**Topic:** {topic_name}
**Actions:** {action_names}

### Test Cases

| # | Utterance | Expected Topic | Expected Actions | Expected Outcome |
|---|-----------|----------------|------------------|------------------|
| 1 | "{utterance_1}" | {topic} | {actions} | {outcome_summary} |
| 2 | "{utterance_2}" | {topic} | {actions} | {outcome_summary} |
| ... | ... | ... | ... | ... |

### Detailed Expected Outcomes

**Test Case 1:** "{utterance_1}"
```
{full_expected_outcome_1}
```

**Test Case 2:** "{utterance_2}"
```
{full_expected_outcome_2}
```

---

## Job 2: {job_2_name}

[Repeat structure for each job]

---

## Credit Calculation

| Item | Calculation | Total |
|------|-------------|-------|
| Test Cases | {total_cases} | |
| Credits per Test | × 0.5 | |
| Subtotal | | {subtotal} |
| Overhead (10%) | | +{overhead} |
| **Total Credits** | | **~{total}** |

**Note:** Actual credits may vary based on response complexity and retries.

---

## YAML Files Generated

| Job | File Path |
|-----|-----------|
| 1 | `greenlight-output/{agent}/test-specs/job1_{slug}.yaml` |
| 2 | `greenlight-output/{agent}/test-specs/job2_{slug}.yaml` |
| ... | ... |

---

## Pre-Execution Checklist

- [ ] Review test utterances for accuracy
- [ ] Verify expected topics match your agent configuration
- [ ] Confirm expected actions are correct
- [ ] Check that expected outcomes match your requirements
- [ ] Ensure test data exists in org (if using real data)
```

### Step 4.3: Present Summary and Ask for Approval

**Display in conversation with verified API names:**

```
## Execution Plan Ready

I've generated the execution plan with {total_cases} test cases across {num_jobs} jobs.

### Verified API Names Used

| Type | API Name | Mapped User Stories |
|------|----------|---------------------|
| Topic | `{topic_1}` | {story_1}, {story_2} |
| Topic | `{topic_2}` | {story_3} |
| Action | `{action_1}` | {story_1} |
| Action | `{action_2}` | {story_2} |

### Jobs Overview

| Job | Topic | Action | Test Cases | Cost |
|-----|-------|--------|------------|------|
| 1 | `{topic_1}` | `{action_1}` | {count_1} | ${cost_1} |
| 2 | `{topic_1}` | `{action_2}` | {count_2} | ${cost_2} |
| 3 | `{topic_2}` | `{action_3}` | {count_3} | ${cost_3} |
| **Total** | | | **{total_cases}** | **${total_cost}** |

**Estimated Cost:** ~${total_cost} (Agent Execution + LLM Judge for Eval)
**Estimated Duration:** ~{total_duration} minutes

**Files Generated:**
- Execution plan: `greenlight-output/{agent_name}/execution-plan.md`
- Test specs: `greenlight-output/{agent_name}/test-specs/*.yaml`

### Context Variables Review

{if context variables provided}
✅ **Context variables included:**
- ContactId: {value}
- AccountId: {value}

{if NO context variables provided}
⚠️ **WARNING: No context variables provided**

If your agent requires user identity (ContactId, AccountId, etc.) to invoke actions:
- Agent will correctly ask users to identify themselves (secure behavior)
- But tests will expect immediate action invocation
- Result: Tests may fail with 0% action accuracy

This is a common cause of test failures. If you're unsure, review your agent's
action requirements before proceeding.

⚠️ **Please verify the topic and action API names above match your agent before approving.**

The execution-plan.md shows all utterances and expected outcomes.
Make sure they look realistic and match your requirements.
```

**Use AskQuestion for approval:**

```
Use the AskQuestion tool with:
{
  "title": "Execution Plan Review",
  "questions": [
    {
      "id": "execution_approval",
      "prompt": "Do you approve this execution plan? Tests will consume approximately {total_credits} credits.",
      "options": [
        {"id": "approve", "label": "Yes, run the tests"},
        {"id": "edit", "label": "No, I need to make changes"},
        {"id": "cancel", "label": "Cancel"}
      ]
    }
  ]
}
```

**CRITICAL: DO NOT proceed to Phase 5 unless user selects "approve".**

---

## Phase 5: Execute Tests

### Step 5.1: Create Tests in Salesforce

For each YAML spec file:

```bash
sf agent test create \
  --spec greenlight-output/{agent}/test-specs/{job_file}.yaml \
  --api-name {agent}_{job_name} \
  --target-org {org_alias} \
  --json
```

**Show progress in conversation (NOT terminal):**

```
Creating test jobs...

✅ Job 1: {job_1_name} - Created
✅ Job 2: {job_2_name} - Created
✅ Job 3: {job_3_name} - Created

All {num_jobs} test jobs created successfully.
```

### Step 5.2: Run Tests in Parallel

```bash
# Run each test (use --api-name, NOT --test-id)
sf agent test run \
  --api-name {agent}_{job_name} \
  --target-org {org_alias} \
  --json
```

**Show progress:**

```
Running tests in parallel...

▶️ Starting Job 1: {job_1_name}
▶️ Starting Job 2: {job_2_name}
▶️ Starting Job 3: {job_3_name}

Started {num_jobs} test runs.
```

### Step 5.3: Monitor Test Execution

```bash
# Check status (use --job-id, NOT --run-id)
sf agent test results \
  --job-id {run_id} \
  --target-org {org_alias} \
  --json
```

Poll until all jobs complete:

```
Monitoring test execution...

⏳ {num_running} jobs still running...
✅ Job 1 COMPLETED
✅ Job 2 COMPLETED
⏳ {num_running} jobs still running...
✅ Job 3 COMPLETED

All jobs completed!
```

### Step 5.4: Save Results

Save raw JSON results to `greenlight-output/{agent_name}/raw-results/`:

```
Saving results...

✅ raw-results/job1_{name}_results.json
✅ raw-results/job2_{name}_results.json
✅ raw-results/job3_{name}_results.json
```

---

## Phase 6: Generate Report

### Step 6.1: Analyze Results

Parse all result JSON files and calculate:
- Overall pass rate
- Pass rate by topic
- Pass rate by priority (P0/P1/P2)
- Common failure patterns
- Action accuracy
- Response quality metrics

### Step 6.2: Generate Report

Create `greenlight-output/{agent_name}/report.md`:

```markdown
# Greenlight Report: {agent_name}

*Generated: {timestamp}*
*Org: {org_alias}*
*Agent Version: {version}*

---

## Executive Summary

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| Overall Pass Rate | {pass_rate}% | ≥{target}% | {status_emoji} |
| Topic Accuracy | {topic_acc}% | ≥{topic_target}% | {status_emoji} |
| Action Accuracy | {action_acc}% | ≥{action_target}% | {status_emoji} |
| Response Quality | {response_qual}% | ≥{response_target}% | {status_emoji} |

### Go-Live Recommendation

{recommendation_emoji} **{READY / CONDITIONAL / NOT READY}**

{recommendation_explanation}

### Key Findings

1. {finding_1}
2. {finding_2}
3. {finding_3}

---

## Performance by Priority

| Priority | Test Cases | Passed | Failed | Pass Rate | Status |
|----------|------------|--------|--------|-----------|--------|
| P0 | {p0_total} | {p0_pass} | {p0_fail} | {p0_rate}% | {p0_status} |
| P1 | {p1_total} | {p1_pass} | {p1_fail} | {p1_rate}% | {p1_status} |
| P2 | {p2_total} | {p2_pass} | {p2_fail} | {p2_rate}% | {p2_status} |

---

## Topic Analysis

### {topic_1}

| Metric | Result |
|--------|--------|
| Test Cases | {count} |
| Pass Rate | {rate}% |
| Topic Accuracy | {topic_acc}% |
| Action Accuracy | {action_acc}% |

**Strengths:**
- {strength_1}
- {strength_2}

**Issues:**
- {issue_1}
- {issue_2}

---

## Failure Analysis

### Top Failure Patterns

1. **{pattern_1}** ({count_1} occurrences)
   - Root cause: {cause_1}
   - Example: "{example_utterance_1}"
   - Recommendation: {fix_1}

2. **{pattern_2}** ({count_2} occurrences)
   - Root cause: {cause_2}
   - Example: "{example_utterance_2}"
   - Recommendation: {fix_2}

---

## Recommendations

### Immediate Actions (Before Go-Live)

1. **{action_1}**
   - Impact: {impact}
   - Effort: {effort}

2. **{action_2}**
   - Impact: {impact}
   - Effort: {effort}

### Short-Term Improvements

1. {improvement_1}
2. {improvement_2}

### Long-Term Strategy

1. {strategy_1}
2. {strategy_2}

---

## Resource Usage

| Metric | Value |
|--------|-------|
| Total Test Cases | {total_cases} |
| Credits Used | {credits_used} |
| Total Duration | {duration} |
| Avg. Response Time | {avg_latency}ms |

---

## Next Steps

1. {next_step_1}
2. {next_step_2}
3. {next_step_3}

---

## Appendix: Detailed Results

[Full test case results table...]
```

### Step 6.3: Present Summary

**Display in conversation:**

```
## Greenlight Report Complete

### Go-Live Recommendation: {READY/CONDITIONAL/NOT READY} {emoji}

**Overall Results:**
- Pass Rate: {pass_rate}%
- Topic Accuracy: {topic_acc}%
- Action Accuracy: {action_acc}%

**By Priority:**
- P0: {p0_rate}% ({p0_pass}/{p0_total} passed)
- P1: {p1_rate}% ({p1_pass}/{p1_total} passed)
- P2: {p2_rate}% ({p2_pass}/{p2_total} passed)

**Top Issues:**
1. {issue_1}
2. {issue_2}
3. {issue_3}

**Full report saved to:** `greenlight-output/{agent_name}/report.md`

**All output files:**
- Strategy: `greenlight-output/{agent_name}/strategy.md`
- Execution Plan: `greenlight-output/{agent_name}/execution-plan.md`
- Report: `greenlight-output/{agent_name}/report.md`
- Test Specs: `greenlight-output/{agent_name}/test-specs/`
- Raw Results: `greenlight-output/{agent_name}/raw-results/`
```

---

## Output File Structure

```
greenlight-output/
├── config.json                     # User preferences (created on first run)
├── .sfdx-temp/                     # Temporary SFDX project (auto-created if needed)
│   └── greenlight-temp/            # Contains force-app/ and sfdx-project.json
│       └── force-app/              # Retrieved metadata stored here
└── {agent_name}/
    ├── strategy.md                 # Test strategy document
    ├── execution-plan.md           # Pre-execution review with all test cases
    ├── report.md                   # Final analysis report
    ├── test-specs/                 # Generated YAML test specs
    │   ├── job1_{story_slug}.yaml
    │   ├── job2_{story_slug}.yaml
    │   └── ...
    └── raw-results/                # Raw JSON results from Salesforce
        ├── job1_{name}_results.json
        ├── job2_{name}_results.json
        └── ...
```

**Note:** The `.sfdx-temp/` directory is only created when running the skill outside an existing SFDX project (e.g., from your home directory). If you're already in an SFDX project, the skill uses your existing project structure.

---

## Salesforce CLI Command Reference

### List Orgs
```bash
sf org list --json
```

### Query Agents
```bash
sf data query \
  --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition" \
  --target-org {org} \
  --json
```

### Query Agent Versions
```bash
sf data query \
  --query "SELECT Id, VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = '{agent}'" \
  --target-org {org} \
  --json
```

### Retrieve Metadata
```bash
sf project retrieve start --metadata Bot:{agent} --target-org {org}
sf project retrieve start --metadata GenAiPlannerBundle:{agent}_{version} --target-org {org}
```

### Create Test
```bash
sf agent test create \
  --spec {spec_file}.yaml \
  --api-name {test_api_name} \
  --target-org {org} \
  --json
```

### Run Test
```bash
sf agent test run \
  --api-name {test_api_name} \
  --target-org {org} \
  --json
# Note: Use --api-name, NOT --test-id
```

### Get Results
```bash
sf agent test results \
  --job-id {job_id} \
  --target-org {org} \
  --json
# Note: Use --job-id, NOT --run-id
```

---

## Common Pitfalls to Avoid

### 1. Wrong CLI Flags
- ❌ `--test-id` → ✅ `--api-name` (for sf agent test run)
- ❌ `--run-id` → ✅ `--job-id` (for sf agent test results)
- ❌ `--spec-file` → ✅ `--spec` (for sf agent test create)

### 2. Wrong YAML Field Names
- ❌ `expectedTopics` → ✅ `expectedTopic` (singular)
- ❌ `expectedOutcomes` → ✅ `expectedOutcome` (singular)

### 3. Wrong Topic/Action Names
- ❌ Full names with IDs: `Claims_16jd5c475874c40`
- ✅ Use `localDeveloperName` only: `Claims`

### 4. Generic Expected Outcomes
- ❌ "Agent should handle correctly"
- ✅ Specific steps, data fields, and conditions

### 5. Missing Context Variables (CRITICAL)
- ❌ Leaving `contextVariables: []` when agent needs ContactId/AccountId
- ✅ Provide context variables for agents that verify user identity
- **Impact:** 0% action accuracy - agent asks for identity (correct) but tests expect actions
- **Fix:** Gather context variables in Phase 2b.3

### 6. Trying to Query GenAiTopic/GenAiFunction via SOQL
- ❌ `sf data query --query "SELECT ... FROM GenAiTopic..."`
- ✅ Parse metadata from GenAiPlannerBundle XML files
- **Reason:** These objects are not queryable via SOQL

### 7. Skipping User Approval
- ❌ Proceeding without strategy.md review
- ❌ Running tests without execution-plan.md review
- ✅ Always wait for explicit user approval at each checkpoint
