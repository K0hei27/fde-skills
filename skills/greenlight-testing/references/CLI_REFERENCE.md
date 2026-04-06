# Salesforce CLI Reference for Agentforce Testing

Quick reference for Salesforce CLI commands used by Greenlight.

## Agent Commands

### List Agents
```bash
sf data query \
  --query "SELECT Id, DeveloperName, MasterLabel FROM BotDefinition" \
  --target-org <org> \
  --json
```

### List Agent Versions
```bash
sf data query \
  --query "SELECT Id, VersionNumber, Status FROM BotVersion WHERE BotDefinition.DeveloperName = '<agent>'" \
  --target-org <org> \
  --json
```

### Retrieve Agent Metadata
```bash
# Bot definition
sf project retrieve start --metadata Bot:<agent> --target-org <org>

# Topics and actions
sf project retrieve start --metadata GenAiPlannerBundle:<agent>_<version> --target-org <org>
```

## Test Commands

### Create Test
```bash
sf agent test create \
  --spec <spec.yaml> \
  --api-name <test_name> \
  --target-org <org> \
  --json
```

### Run Test
```bash
sf agent test run \
  --api-name <test_name> \
  --target-org <org> \
  --json

# Note: Use --api-name, NOT --test-id
```

### Get Results
```bash
sf agent test results \
  --job-id <job_id> \
  --target-org <org> \
  --json

# Note: Use --job-id, NOT --run-id
```

### List Tests
```bash
sf agent test list --target-org <org> --json
```

## Common Flags

| Flag | Description |
|------|-------------|
| `--target-org <org>` | Org alias or username |
| `--json` | Output in JSON format |
| `--wait <minutes>` | Wait for completion |

## Common Pitfalls

| Wrong | Correct |
|-------|---------|
| `--test-id` | `--api-name` (for run) |
| `--run-id` | `--job-id` (for results) |
| `--spec-file` | `--spec` (for create) |

## YAML Test Spec Format

```yaml
name: Test_Name
subjectType: AGENT
subjectName: Agent_Name
subjectVersion: v2
testCases:
  - utterance: "User question"
    contextVariables: []
    customEvaluations: []
    expectedTopic: Topic_Name        # Use localDeveloperName
    expectedActions:
      - Action_Name                  # Use localDeveloperName
    expectedOutcome: |
      Detailed expected behavior
    metrics:
      - completeness
      - coherence
      - conciseness
      - output_latency_milliseconds
```

## Documentation Links

- [Running Agent Tests](https://developer.salesforce.com/docs/ai/agentforce/guide/agent-dx-test-run.html)
- [CLI Command Reference](https://developer.salesforce.com/docs/atlas.en-us.sfdx_cli_reference.meta/sfdx_cli_reference/cli_reference_agent_commands_unified.htm)
