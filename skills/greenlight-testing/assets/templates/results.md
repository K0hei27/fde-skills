# Greenlight Report: {agent_name}

*Generated: {timestamp}*
*Org: {org_alias}*
*Agent Version: {version}*
*Strategy Approved: {strategy_timestamp}*

---

## Executive Summary

### Go-Live Recommendation

{recommendation_emoji} **{recommendation_status}**

{recommendation_explanation}

### Key Metrics

| Metric | Result | Target | Status |
|--------|--------|--------|--------|
| **Overall Pass Rate** | {overall_pass_rate}% | ≥{overall_target}% | {overall_status} |
| **Topic Accuracy** | {topic_accuracy}% | ≥{topic_target}% | {topic_status} |
| **Action Accuracy** | {action_accuracy}% | ≥{action_target}% | {action_status} |
| **Response Quality** | {response_quality}% | ≥{response_target}% | {response_status} |

### Key Findings

1. {finding_1}
2. {finding_2}
3. {finding_3}

---

## Performance by Priority

| Priority | Test Cases | Passed | Failed | Pass Rate | Target | Status |
|----------|------------|--------|--------|-----------|--------|--------|
| P0 (Critical) | {p0_total} | {p0_passed} | {p0_failed} | {p0_rate}% | ≥{p0_target}% | {p0_status} |
| P1 (Important) | {p1_total} | {p1_passed} | {p1_failed} | {p1_rate}% | ≥{p1_target}% | {p1_status} |
| P2 (Nice to have) | {p2_total} | {p2_passed} | {p2_failed} | {p2_rate}% | ≥{p2_target}% | {p2_status} |
| **Total** | **{total_cases}** | **{total_passed}** | **{total_failed}** | **{total_rate}%** | | |

---

## Topic Analysis

{topic_analysis_sections}

---

## Failure Analysis

### Failure Distribution

| Failure Type | Count | Percentage | Impact |
|--------------|-------|------------|--------|
{failure_distribution}

### Top Failure Patterns

{failure_patterns}

---

## Recommendations

### Immediate Actions (Before Go-Live)

{immediate_actions}

### Short-Term Improvements (Within 2 Weeks)

{short_term_improvements}

### Long-Term Strategy (Ongoing)

{long_term_strategy}

---

## Resource Usage

| Metric | Value |
|--------|-------|
| Total Test Cases | {total_test_cases} |
| Tests Passed | {tests_passed} |
| Tests Failed | {tests_failed} |
| Credits Used | ~{credits_used} |
| Total Duration | {total_duration} |
| Avg. Response Time | {avg_latency}ms |

---

## Job Results Summary

| Job # | Name | Test Cases | Passed | Failed | Pass Rate | Status |
|-------|------|------------|--------|--------|-----------|--------|
{job_results_table}

---

## Next Steps

{next_steps}

---

## Appendix A: Detailed Test Results

{detailed_results_table}

---

## Appendix B: Test Configuration

| Setting | Value |
|---------|-------|
| Agent | {agent_name} |
| Version | {version} |
| Org | {org_alias} |
| Total Jobs | {total_jobs} |
| Strategy Date | {strategy_timestamp} |
| Execution Date | {execution_timestamp} |

---

## Topic Analysis Template

### {topic_name}

**User Story:** {user_story}
**Priority:** {priority}

| Metric | Result | Target |
|--------|--------|--------|
| Test Cases | {test_count} | |
| Pass Rate | {pass_rate}% | ≥{target}% |
| Topic Accuracy | {topic_acc}% | ≥{topic_target}% |
| Action Accuracy | {action_acc}% | ≥{action_target}% |
| Avg. Latency | {latency}ms | <{latency_target}ms |

**Strengths:**
- {strength_1}
- {strength_2}

**Issues:**
- {issue_1}: {issue_detail_1}
- {issue_2}: {issue_detail_2}

**Recommendations:**
- {recommendation_1}
- {recommendation_2}

---

## Failure Pattern Template

### Pattern {n}: {pattern_name}

**Occurrences:** {count} ({percentage}% of failures)
**Severity:** {severity}
**Priority Impact:** {affected_priorities}

**Root Cause:**
{root_cause_description}

**Example Failures:**

| Utterance | Expected | Actual |
|-----------|----------|--------|
| "{utterance_1}" | {expected_1} | {actual_1} |
| "{utterance_2}" | {expected_2} | {actual_2} |

**Recommended Fix:**
{fix_recommendation}

**Estimated Effort:** {effort_estimate}

---
