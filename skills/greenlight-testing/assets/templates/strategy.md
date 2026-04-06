# Test Strategy: {agent_name}

*Generated: {timestamp}*
*Org: {org_alias}*
*Agent Version: {version}*

---

## Executive Summary

| | |
|---|---|
| **Goal** | {goal_description} |
| **Agent** | {agent_name} ({agent_label}) |
| **Test Cases** | {total_test_cases} |
| **Est. Credits** | ~{estimated_credits} |
| **Est. Duration** | {estimated_duration} minutes |
| **Go-Live Date** | {timeline} |

---

## Coverage Matrix

| User Story | Priority | Topic | Expected Actions | Weight | Test Cases |
|------------|----------|-------|------------------|--------|------------|
{coverage_rows}
| **Total** | | | | | **{total_test_cases}** |

---

## Accuracy Targets

| Priority | Topic Accuracy | Action Accuracy | Response Quality |
|----------|----------------|-----------------|------------------|
| P0 (Critical) | ≥{p0_topic}% | ≥{p0_action}% | ≥{p0_response}% |
| P1 (Important) | ≥{p1_topic}% | ≥{p1_action}% | ≥{p1_response}% |
| P2 (Nice to have) | ≥{p2_topic}% | ≥{p2_action}% | ≥{p2_response}% |

---

## User Story Details

{user_story_details}

---

## Job Plan

| Job # | User Story | Topic | Priority | Test Cases |
|-------|------------|-------|----------|------------|
{job_rows}

---

## Credit Estimate

| Item | Calculation | Value |
|------|-------------|-------|
| Test Cases | {total_test_cases} | |
| Credits per Test | × 0.5 | |
| **Subtotal** | | {subtotal_credits} |
| Overhead (10%) | | +{overhead_credits} |
| **Estimated Total** | | **~{total_credits}** |

> See `config/credit_calculation.md` for detailed credit information.

---

## Readiness Criteria

| Status | Criteria |
|--------|----------|
| ✅ **Ready** | All P0 topics at target accuracy, action accuracy ≥90%, no critical failures |
| ⚠️ **Conditional** | P0 at threshold (not target), gaps documented with remediation plan |
| 🚫 **Not Ready** | Any P0 metric below threshold, or blocking action failures |

---

## Topics & Actions Reference

### Detected Topics

| Topic Name | Description |
|------------|-------------|
{topics_table}

### Detected Actions

| Action Name | Type |
|-------------|------|
{actions_table}

---

## Next Steps

After reviewing this strategy:

1. **Approve** - Proceed to generate execution plan with test cases
2. **Edit** - Request changes to coverage, priorities, or targets
3. **Cancel** - Start over with different parameters

---

## User Story Detail Template

### {story_name} ({priority})

**Topic:** {topic_name}
**Actions:** {action_names}
**Test Cases:** {test_case_count}

**Scenario:**
{scenario_description}

**Expected Agent Behavior:**
1. {behavior_step_1}
2. {behavior_step_2}
3. {behavior_step_3}

**Success Criteria:**
- {criteria_1}
- {criteria_2}
- {criteria_3}

**Edge Cases:**
| Condition | Expected Response |
|-----------|-------------------|
| {condition_1} | {response_1} |
| {condition_2} | {response_2} |

---
