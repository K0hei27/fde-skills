# Execution Plan: {agent_name}

*Generated: {timestamp}*
*Based on strategy approved: {strategy_timestamp}*
*Org: {org_alias}*
*Agent Version: {version}*

---

## Pre-Execution Summary

| Metric | Value |
|--------|-------|
| **Total Test Cases** | {total_test_cases} |
| **Total Jobs** | {total_jobs} |
| **Estimated Credits** | ~{estimated_credits} |
| **Estimated Duration** | ~{estimated_duration} minutes |

---

## Jobs Overview

| Job # | Name | User Story | Topic | Actions | Test Cases | Credits |
|-------|------|------------|-------|---------|------------|---------|
{job_overview_rows}
| **Total** | | | | | **{total_test_cases}** | **~{total_credits}** |

---

## Credit Calculation

| Item | Calculation | Value |
|------|-------------|-------|
| Test Cases | {total_test_cases} | |
| Credits per Test | × 0.5 | |
| **Subtotal** | | {subtotal_credits} |
| Overhead (10%) | | +{overhead_credits} |
| **Estimated Total** | | **~{total_credits}** |

> **Note:** Actual credits may vary based on response complexity and retries.

---

{job_details}

---

## Generated YAML Files

| Job | File Path | Status |
|-----|-----------|--------|
{yaml_files_table}

---

## Pre-Execution Checklist

Before approving this execution plan, please verify:

- [ ] **Utterances are realistic** - Do they match how real users would interact?
- [ ] **Expected topics are correct** - Do they match your agent's topic configuration?
- [ ] **Expected actions are accurate** - Are these the actions that should be invoked?
- [ ] **Expected outcomes are specific** - Do they describe exactly what the agent should do?
- [ ] **Test data exists** - If using real data, is it present in the org?
- [ ] **Credit estimate is acceptable** - Are you comfortable with the estimated cost?

---

## How to Proceed

After reviewing this plan:

1. **Approve** - If everything looks correct, approve to run the tests
2. **Edit** - If changes are needed, ask to modify specific test cases or jobs
3. **Cancel** - If major changes are needed, cancel and restart the strategy phase

---

## Job Details Template

### Job {job_number}: {job_name}

**User Story:** {user_story}
**Priority:** {priority}
**Topic:** {topic_name}
**Expected Actions:** {action_names}
**Test Cases:** {test_case_count}

#### Test Cases Summary

| # | Utterance | Expected Topic | Expected Actions |
|---|-----------|----------------|------------------|
{test_case_summary_rows}

#### Detailed Expected Outcomes

{detailed_outcomes}

---
