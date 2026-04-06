---
name: greenlight-dashboard
description: Deploy an LWC dashboard to display Greenlight test results. Use after running /greenlight tests. Automatically reads results, updates the dashboard component, and deploys to the org.
---

# Greenlight Dashboard

Deploys an LWC dashboard to visualize Agentforce test results from Greenlight. Run this after `/greenlight` completes.

---

## Automated Workflow (Follow This)

When the user invokes `/greenlight-dashboard`, execute these steps automatically:

### Step 1: Identify Target Org

Check for a recent Greenlight run to determine the target org:

```bash
# Look for the most recent test results
ls -la greenlight-output/
```

Ask the user which org to deploy to if multiple agents were tested, or confirm the detected org:

```
Use the AskQuestion tool:
{
  "title": "Deploy Dashboard",
  "questions": [{
    "id": "target_org",
    "prompt": "Deploy Greenlight Dashboard to which org?",
    "options": [
      {"id": "my-org", "label": "my-org (last used)"},
      {"id": "other", "label": "Let me specify a different org"}
    ]
  }]
}
```

### Step 2: Read Test Results

Read the raw results from the most recent Greenlight run:

```bash
# Find all result files
ls greenlight-output/*/raw-results/*.json

# Read the report for summary data
cat greenlight-output/{agent_name}/report.md
```

Parse the JSON results to extract:
- Agent name, version, org
- Test timestamp
- Pass/fail counts per job
- Topic and action accuracy
- Individual test case results
- Recommendations

### Step 3: Transform Results to Dashboard Format

Transform the raw Greenlight results into the `TEST_RESULTS` object format expected by the LWC. The structure should be:

```javascript
const TEST_RESULTS = {
    agentName: "...",
    agentLabel: "...",
    version: "...",
    org: "...",
    timestamp: "...",
    goLiveStatus: "READY" | "CONDITIONAL" | "NOT_READY",
    summary: {
        totalTests: N,
        passed: N,
        failed: N,
        passRate: N,
        topicAccuracy: N,
        actionAccuracy: N,
        avgCompleteness: N,
        avgCoherence: N,
        avgConciseness: N
    },
    targets: { topicAccuracy: 90, actionAccuracy: 85, responseQuality: 80 },
    jobs: [{ id, name, priority, topic, totalTests, passed, failed, passRate }],
    testCases: [{ id, jobId, utterance, expectedTopic, actualTopic, topicPass, ... }],
    recommendations: { immediate: [], shortTerm: [], longTerm: [] }
};
```

### Step 4: Update the LWC Component

Update `force-app/main/default/lwc/greenlightDashboard/greenlightDashboard.js` with the new `TEST_RESULTS` data.

Use the StrReplace tool to replace the existing `TEST_RESULTS` constant with the new data.

### Step 5: Deploy to Org

**IMPORTANT**: Components must be deployed in dependency order due to circular references.

**Step 5a**: Deploy LWC and FlexiPage together (FlexiPage depends on LWC):
```bash
sf project deploy start \
  --source-dir force-app/main/default/lwc/greenlightDashboard \
  --source-dir force-app/main/default/flexipages/Greenlight_Dashboard.flexipage-meta.xml \
  --target-org {TARGET_ORG} \
  --json
```

**Step 5b**: Deploy Tab and App together (Tab depends on FlexiPage, App depends on Tab):
```bash
sf project deploy start \
  --source-dir force-app/main/default/tabs/Greenlight_Dashboard.tab-meta.xml \
  --source-dir force-app/main/default/applications/Greenlight_Dashboard.app-meta.xml \
  --target-org {TARGET_ORG} \
  --json
```

**Step 5c**: Deploy Permission Set (depends on App):
```bash
sf project deploy start \
  --source-dir force-app/main/default/permissionsets/Greenlight_Dashboard.permissionset-meta.xml \
  --target-org {TARGET_ORG} \
  --json
```

### Step 6: Assign Permission Set

```bash
sf org assign permset --name Greenlight_Dashboard --target-org {TARGET_ORG} --json
```

### Step 7: Provide Access Instructions

After successful deployment, tell the user:

```
Dashboard deployed successfully!

To view the dashboard:
1. Open your Salesforce org: {instance_url}
2. Use the App Launcher (⊞) and search for "Greenlight Dashboard"
3. Click to open the dashboard

First time only: If the page is blank, activate it in Lightning App Builder:
1. Setup → Lightning App Builder → Find "Greenlight Dashboard" → Edit
2. Click "Activation" (top right) → App Default tab → Assign to "Greenlight Dashboard" app
3. Save
```

---

## Component Files Reference

| File | Purpose |
|------|---------|
| `greenlightDashboard.html` | Template — summary cards, results table, topic breakdown |
| `greenlightDashboard.js` | Logic — embedded test data, filter state, computed view models |
| `greenlightDashboard.css` | Custom CSS (no SLDS dependency) |
| `greenlightDashboard.js-meta.xml` | Exposed on AppPage/HomePage/RecordPage |

---

## Manual Local Dev (Optional)

For development/debugging, you can preview locally with hot-reload:

```bash
# Component must be deployed first
sf lightning dev component --name greenlightDashboard --target-org {TARGET_ORG}
```

The browser opens automatically. Edits to `.html`, `.js`, and `.css` reload instantly.

---

## Greenlight JSON Schema Reference

The raw results from Testing Center are at `greenlight-output/{agent_name}/raw-results/*.json`:

```json
{
  "status": "COMPLETED",
  "startTime": "2026-03-19T06:20:38Z",
  "endTime": "2026-03-19T06:20:59Z",
  "subjectName": "Agentforce_Service_Agent_Job1_Check_Order_Status",
  "testCases": [
    {
      "testNumber": 1,
      "status": "COMPLETED",
      "inputs": {
        "utterance": "I want to check the status of my order 284116644"
      },
      "generatedData": {
        "topic": "SAKS_Order_Management",
        "actionsSequence": "['Get_Order_Status']",
        "outcome": "December 8, 2025 | Order# 284116644..."
      },
      "testResults": [
        {
          "name": "topic_assertion",
          "result": "PASS",
          "score": 1,
          "expectedValue": "SAKS_Order_Management",
          "actualValue": "SAKS_Order_Management"
        },
        {
          "name": "actions_assertion",
          "result": "PASS",
          "score": 1,
          "expectedValue": "['Get_Order_Status']",
          "actualValue": "['Get_Order_Status']"
        },
        {
          "name": "output_validation",
          "result": "PASS",
          "score": 4,
          "metricExplainability": "The bot response provides..."
        },
        {
          "name": "completeness",
          "result": "PASS",
          "score": 5
        },
        {
          "name": "coherence",
          "result": "PASS",
          "score": 5
        },
        {
          "name": "conciseness",
          "result": "PASS",
          "score": 5
        }
      ]
    }
  ]
}
```

### Transformed schema for dashboard

Transform the raw results into this format for the LWC:

```js
const TEST_RESULTS = {
    agentName: "Agentforce_Service_Agent",
    agentLabel: "Sophie",
    version: "v3",
    org: "my-org",
    timestamp: "2026-03-19T06:22:10Z",
    summary: {
        totalTests: 10,
        passed: 9,
        failed: 1,
        passRate: 90,
        topicAccuracy: 100,
        actionAccuracy: 80,
        avgCompleteness: 4.3,
        avgCoherence: 4.9,
        avgConciseness: 5.0
    },
    jobs: [
        {
            id: "job1",
            name: "Check Order Status",
            priority: "P0",
            topic: "SAKS_Order_Management",
            totalTests: 4,
            passed: 4,
            failed: 0,
            passRate: 100
        },
        {
            id: "job2",
            name: "Initiate Return",
            priority: "P0",
            topic: "Customer_Returns",
            totalTests: 4,
            passed: 4,
            failed: 0,
            passRate: 100
        },
        {
            id: "job3",
            name: "Price Adjustment Status",
            priority: "P1",
            topic: "Price_Adjustments",
            totalTests: 2,
            passed: 0,
            failed: 2,
            passRate: 0
        }
    ],
    testCases: [
        {
            id: "tc1",
            jobId: "job1",
            utterance: "I want to check the status of my order 284116644",
            expectedTopic: "SAKS_Order_Management",
            actualTopic: "SAKS_Order_Management",
            topicPass: true,
            expectedActions: ["Get_Order_Status"],
            actualActions: ["Get_Order_Status"],
            actionPass: true,
            outputScore: 3,
            completenessScore: 5,
            coherenceScore: 5,
            concisenessScore: 5,
            outcome: "December 8, 2025 | Order# 284116644...",
            status: "PASS"
        }
        // ... more test cases
    ]
};
```

---

## Dashboard tabs

The dashboard has the following tabs:

### Overview Tab
- Agent name, version, org
- Test run timestamp
- Go-live recommendation (READY / CONDITIONAL / NOT READY)
- Summary cards: Total Tests, Pass Rate, Topic Accuracy, Action Accuracy

### Results by Job Tab
- Table of jobs with pass/fail counts
- Expandable rows to see individual test cases
- Priority indicators (P0, P1, P2)

### Detailed Results Tab
- Full table of all test cases
- Columns: Utterance, Topic (Pass/Fail), Action (Pass/Fail), Scores
- Expandable rows for agent response and explanations

### Recommendations Tab
- Key findings from the test run
- Immediate actions needed
- Long-term improvements

---

## Key files

| What | Where |
|------|-------|
| LWC component | `force-app/main/default/lwc/greenlightDashboard/` |
| Lightning App Page | `force-app/main/default/flexipages/Greenlight_Dashboard.flexipage-meta.xml` |
| Custom Tab | `force-app/main/default/tabs/Greenlight_Dashboard.tab-meta.xml` |
| Lightning App | `force-app/main/default/applications/Greenlight_Dashboard.app-meta.xml` |
| Permission Set | `force-app/main/default/permissionsets/Greenlight_Dashboard.permissionset-meta.xml` |
| Test Results | `greenlight-output/{agent_name}/raw-results/*.json` |

---

## Workflow: From Greenlight to Dashboard

1. Run `/greenlight` to execute tests and generate results
2. Results are saved to `greenlight-output/{agent_name}/raw-results/*.json`
3. Run `/greenlight-dashboard` to:
   - Read the raw results
   - Transform into dashboard format
   - Update the LWC component with the data
   - Deploy to the target org
4. Open the Greenlight Dashboard app in Salesforce to view results

---

## Creating the LWC component

When creating the dashboard for the first time, generate these files:

### greenlightDashboard.js-meta.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<LightningComponentBundle xmlns="http://soap.sforce.com/2006/04/metadata">
    <apiVersion>62.0</apiVersion>
    <isExposed>true</isExposed>
    <targets>
        <target>lightning__AppPage</target>
        <target>lightning__HomePage</target>
        <target>lightning__RecordPage</target>
    </targets>
</LightningComponentBundle>
```

### Greenlight_Dashboard.flexipage-meta.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<FlexiPage xmlns="http://soap.sforce.com/2006/04/metadata">
    <flexiPageRegions>
        <itemInstances>
            <componentInstance>
                <componentName>c:greenlightDashboard</componentName>
            </componentInstance>
        </itemInstances>
        <name>main</name>
        <type>Region</type>
    </flexiPageRegions>
    <masterLabel>Greenlight Dashboard</masterLabel>
    <template>
        <name>flexipage:defaultAppHomeTemplate</name>
    </template>
    <type>AppPage</type>
</FlexiPage>
```

### Greenlight_Dashboard.tab-meta.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomTab xmlns="http://soap.sforce.com/2006/04/metadata">
    <flexiPage>Greenlight_Dashboard</flexiPage>
    <label>Greenlight Dashboard</label>
    <motif>Custom73: Handsaw</motif>
</CustomTab>
```

### Greenlight_Dashboard.app-meta.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<CustomApplication xmlns="http://soap.sforce.com/2006/04/metadata">
    <defaultLandingTab>Greenlight_Dashboard</defaultLandingTab>
    <formFactors>
        <formFactor>Large</formFactor>
    </formFactors>
    <label>Greenlight Dashboard</label>
    <navType>Standard</navType>
    <tabs>Greenlight_Dashboard</tabs>
    <uiType>Lightning</uiType>
</CustomApplication>
```

### Greenlight_Dashboard.permissionset-meta.xml

```xml
<?xml version="1.0" encoding="UTF-8"?>
<PermissionSet xmlns="http://soap.sforce.com/2006/04/metadata">
    <applicationVisibilities>
        <application>Greenlight_Dashboard</application>
        <visible>true</visible>
    </applicationVisibilities>
    <label>Greenlight Dashboard</label>
    <tabSettings>
        <tab>Greenlight_Dashboard</tab>
        <visibility>Visible</visibility>
    </tabSettings>
</PermissionSet>
```
