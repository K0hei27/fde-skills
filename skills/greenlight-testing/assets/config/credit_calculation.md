# Greenlight Credit Estimation Reference

This document provides credit estimation guidance for Greenlight test execution. Use this reference when generating `strategy.md` and `execution-plan.md` documents.

---

## Quick Reference

| User License | Credit Status | Cost |
|--------------|---------------|------|
| A4X / A1E (Agentforce for Sales, Service, or 1 Edition PUPM) | **Unmetered** | 0 FC |
| No A4X / A1E license | **Metered** | Standard rates |

> **First question to ask:** Does the user running tests have an A4X/A1E license?

---

## Credit Formula

```
Agent Execution = Test Cases × Actions per Test × $0.08 (sandbox)
LLM Judge for Eval = Test Cases × 4 LLM calls × $0.02
Total Cost = Agent Execution + LLM Judge for Eval
```

### Default Values

| Variable | Value | Notes |
|----------|-------|-------|
| Actions per test | 2 | Adjust for complex agents |
| Cost per action (sandbox) | $0.08 | $0.10 × 80% sandbox discount |
| LLM calls per test | 4 | For judge evaluation |
| Cost per LLM call | $0.02 | 1 LLM call = 4 FC |
| FC list price | $0.005/FC | $500 per 100,000 FC |

### Quick Estimates

| Test Cases | Actions | Agent Execution | LLM Judge for Eval | Total Cost |
|------------|---------|-----------------|---------------------|------------|
| 10 | 2 | $1.60 | $0.80 | ~$2.40 |
| 50 | 2 | $8.00 | $4.00 | ~$12.00 |
| 100 | 2 | $16.00 | $8.00 | ~$24.00 |
| 160 | 2 | $25.60 | $12.80 | ~$38.40 |
| 250 | 2 | $40.00 | $20.00 | ~$60.00 |
| 500 | 2 | $80.00 | $40.00 | ~$120.00 |

---

## What Consumes What

| Activity | Rate | Cost per Test |
|----------|------|---------------|
| Agent execution | 2 actions × $0.08/action (sandbox) | $0.16/test |
| LLM Judge for Eval | 4 LLM calls × $0.02/call | $0.08/test |
| Test case generation | Minimal | <$0.10 for 160 cases |

> **Note:** After 10/24/2025, all ERs have been migrated to Flex Credits. Sandbox orgs have 80% discount. 1 LLM call = 4 Flex Credits = $0.02.

---

## Strategy.md Credit Section

Include this section in every `strategy.md`:

```markdown
## 💳 Credit Estimate

### License Check

- [ ] User has A4X / A1E license → **Unmetered (0 FC)**
- [ ] User does NOT have A4X / A1E license → **Metered (see below)**

### Metered Estimate

| Job | User Story | Test Cases | Agent Execution | LLM Judge for Eval | Subtotal |
|-----|------------|------------|-----------------|---------------------|----------|
| 1 | {story_1} | {count} | ${exec} | ${judge} | ${total} |
| 2 | {story_2} | {count} | ${exec} | ${judge} | ${total} |
| ... | ... | ... | ... | ... | ... |
| **Total** | | **{total}** | **${total_exec}** | **${total_judge}** | **${total_cost}** |

> **Assumptions:** 2 actions per test ($0.16), 4 LLM judge calls per test ($0.08), sandbox rate (80% discount).
```

---

## Execution-Plan.md Credit Section

Include this section in every `execution-plan.md`:

```markdown
## Credit Calculation

| Item | Calculation | Cost |
|------|-------------|------|
| Agent Execution | {total_cases} tests × 2 actions × $0.08 | ${exec_cost} |
| LLM Judge for Eval | {total_cases} tests × 4 calls × $0.02 | ${judge_cost} |
| **Total Estimated Cost** | | **${total_cost}** |

> Actual costs may vary based on agent complexity and actions invoked per utterance.
```

---

## Adjusting Estimates

### When to increase actions per test

| Agent Complexity | Actions per Test | Rationale |
|------------------|------------------|-----------|
| Simple (FAQ, single lookup) | 1-2 | Single action per utterance |
| Standard (multi-step workflow) | 2-3 | Multiple actions triggered |
| Complex (orchestration, multi-topic) | 3-5 | Chain of actions |

### Complexity indicators

- **Simple:** Knowledge search, single record lookup
- **Standard:** Record creation, field updates, single flow
- **Complex:** Multi-record operations, external callouts, multi-turn flows

---

## Platform Limits

| Limit | Value |
|-------|-------|
| Test jobs per 10-hour window | 10 |
| Test cases per job | 1,000 |
| Concurrent test runs | Limited by org limits |

Greenlight automatically parallelizes jobs within these limits.

---

## Cost Avoidance Options

1. **Use A4X/A1E licensed user** → 0 FC consumed
2. **Manual test case creation** → 0 Einstein Requests for generation
3. **CSV upload** → External LLM generation, 0 platform ER consumed

---

## Reference Benchmarks

| Scenario | Consumption | Source |
|----------|-------------|--------|
| 10 tests, 2 actions, sandbox | $1.60 (exec) + $0.80 (judge) = $2.40 | Pricing SKU |
| Manual Agent Builder testing | ~$0.48/hour (6 actions × $0.08) | Field guidance |
| 1,000 test cases, 2 actions | $160 (exec) + $80 (judge) = ~$240 | Calculated |

---

## Caveats

- Credit estimates are **pre-execution approximations**
- Actual consumption varies based on:
  - Agent complexity
  - Actions triggered per utterance
  - Response length and processing
- Always confirm A4X/A1E license status before estimating
- Verify with pricing team for customer contracts (guidance may vary)
- Authoritative reference: **Agentforce Testing Center FAQ**
