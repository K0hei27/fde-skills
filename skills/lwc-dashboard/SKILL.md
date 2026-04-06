---
name: lwc-dashboard
description: Build, preview, and deploy LWC dashboards for Agentforce test results. Use when creating result visualizations, previewing LWC locally, or deploying dashboard components to a Salesforce org.
---

# LWC Dashboard Skill

Build and deploy Lightning Web Components for visualizing Agentforce test results in your Salesforce org.

## When to Use This Skill

Use this skill when the user:
- Wants to visualize test results in Salesforce
- Needs to create an LWC dashboard
- Asks to deploy result visualization to an org
- Wants to preview LWC components locally

---

## Component Overview

| File | Purpose |
|------|---------|
| `*Dashboard.html` | Template — tabs, summary cards, results table |
| `*Dashboard.js` | Logic — embedded data, filter state, computed view models |
| `*Dashboard.css` | Custom CSS styling |
| `*Dashboard.js-meta.xml` | Exposed on AppPage/HomePage/RecordPage |

---

## Workflow

### 1. Create the LWC Component

Generate an LWC dashboard component with:
- Summary cards (pass rate, total tests, etc.)
- Results table with filtering
- Collapsible detail rows

### 2. Deploy to Org

```bash
sf project deploy start \
  --source-dir force-app/main/default/lwc/greenlightDashboard \
  --target-org {target_org}
```

### 3. Create App Scaffolding (One-Time)

| File | Purpose |
|------|---------|
| `flexipages/*.flexipage-meta.xml` | Lightning App Page containing the LWC |
| `tabs/*.tab-meta.xml` | Custom tab pointing to the FlexiPage |
| `applications/*.app-meta.xml` | Lightning App with the tab |
| `permissionsets/*.permissionset-meta.xml` | Permission set for access |

### 4. Local Development

```bash
# First time: deploy component, then start local dev
sf project deploy start --source-dir force-app/main/default/lwc/greenlightDashboard --target-org {org}

# Start local dev server (HMR enabled)
sf lightning dev component --name greenlightDashboard --target-org {org}
```

---

## LWC Best Practices

### No expressions in HTML attributes
```html
<!-- INVALID -->
<tr key={row.key + '-detail'}>

<!-- VALID — compute in getter -->
<tr key={row.detailRowKey}>
```

### Dynamic styles via JS getter
```javascript
get passRateStyle() {
    return `width: ${this.passRate}%`;
}
```

```html
<div class="bar-fill" style={passRateStyle}></div>
```

### Reactive state updates
Use object spread to trigger reactivity:
```javascript
this.expandedRows = { ...this.expandedRows, [key]: !this.expandedRows[key] };
```

---

## Embedding Test Data

For simple dashboards, embed data directly in the JS file:

```javascript
const TEST_DATA = {
  summary: { total: 50, passed: 45, failed: 5, passRate: 90 },
  results: [
    { id: 1, utterance: "Check my order", topic: "Orders", status: "PASS" },
    // ... more results
  ]
};
```

For dynamic data, create an Apex controller:

```apex
public with sharing class DashboardController {
    @AuraEnabled(cacheable=true)
    public static List<TestResult> getResults(String agentName) {
        // Query and return results
    }
}
```

---

## Deploy Checklist

1. Create LWC component files
2. Deploy component to org
3. Create FlexiPage, Tab, App, PermSet
4. Deploy scaffolding
5. Activate FlexiPage in Lightning App Builder
6. Assign permission set to users

```bash
# Full deployment
sf project deploy start \
  --source-dir force-app/main/default/lwc/greenlightDashboard \
  --source-dir force-app/main/default/flexipages/Greenlight_Dashboard.flexipage-meta.xml \
  --source-dir force-app/main/default/tabs/Greenlight_Dashboard.tab-meta.xml \
  --source-dir force-app/main/default/applications/Greenlight.app-meta.xml \
  --source-dir force-app/main/default/permissionsets/Greenlight_Dashboard.permissionset-meta.xml \
  --target-org {target_org}

# Assign access
sf org assign permset --name Greenlight_Dashboard --on-behalf-of {username} --target-org {target_org}
```
