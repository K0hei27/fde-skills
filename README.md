# fde-skills

**FDE Agent Skills** — Claude Code / Cursor skills for Agentforce testing and development.

## What is this?

`fde-skills` provides skills for the FDE team to test and develop Agentforce agents:

| Skill | Description |
|-------|-------------|
| `greenlight-testing` | Full go-live readiness testing via Testing Center |
| `agent-preview` | Quick agent testing via sf agent preview CLI |
| `lwc-dashboard` | Deploy LWC dashboard to visualize test results |

## Installation

### One-command install (recommended)

```bash
# Auto-detect (installs to Cursor and/or Claude Code)
curl -sSL https://raw.githubusercontent.com/K0hei27/fde-skills/main/install.sh | bash

# Cursor only
curl -sSL https://raw.githubusercontent.com/K0hei27/fde-skills/main/install.sh | bash -s -- --target cursor

# Claude Code only
curl -sSL https://raw.githubusercontent.com/K0hei27/fde-skills/main/install.sh | bash -s -- --target claude

# Both
curl -sSL https://raw.githubusercontent.com/K0hei27/fde-skills/main/install.sh | bash -s -- --target both
```

### From local clone

```bash
git clone https://github.com/K0hei27/fde-skills.git
cd fde-skills
./install.sh --target both
```

### Post-install

```bash
# Update to latest
cd ~/.cursor/skills/fde-skills && git pull

# Or reinstall
curl -sSL https://raw.githubusercontent.com/K0hei27/fde-skills/main/install.sh | bash
```

After install, restart your IDE. Skills are available in any project.

### What installs where

| Component | Claude Code | Cursor |
|-----------|-------------|--------|
| Skills | `~/.claude/skills/fde-skills/` | `~/.cursor/skills/fde-skills/` |

## Prerequisites

- **Salesforce CLI** (`sf`) v2.x — [install guide](https://developer.salesforce.com/tools/salesforcecli)
- **Python 3.7+** with PyYAML (`pip install pyyaml`)
- **Claude Code** or **Cursor** IDE
- **Salesforce org** with Agentforce enabled

## Quick Start

### Test an agent for go-live

In Cursor or Claude Code, just ask:

```
I want to test my Agentforce agent for go-live readiness
```

Or use the slash command (Claude Code):

```
/greenlight
```

### Quick preview test

```
Quick test my agent with "What is my order status?"
```

### Create a results dashboard

```
Create an LWC dashboard to visualize my test results
```

## Skills Reference

| Skill | Triggers | Description |
|-------|----------|-------------|
| `greenlight-testing` | "test agent", "go-live ready", "/greenlight" | Full Testing Center orchestration with strategy, execution plan, and comprehensive report |
| `agent-preview` | "preview agent", "quick test" | Fast iterative testing via sf agent preview CLI |
| `lwc-dashboard` | "dashboard", "visualize results" | Deploy LWC component to show test results in-org |

## Workflow (greenlight-testing)

```
Prerequisites Check
    ↓
Phase 1: Connect & Select (Org → Agent → Version)
    ↓
Phase 2: Requirements Gathering
    ↓
Phase 3: Generate Strategy → strategy.md → [APPROVAL]
    ↓
Phase 4: Generate Execution Plan → execution-plan.md → [APPROVAL]
    ↓
Phase 5: Execute Tests
    ↓
Phase 6: Generate Report → report.md
```

## Project Structure

```
fde-skills/
├── install.sh                    # Curl installer
├── skills/
│   ├── greenlight-testing/
│   │   ├── SKILL.md             # Testing Center orchestration
│   │   ├── scripts/             # Python helper scripts
│   │   └── assets/              # Templates, configs
│   ├── agent-preview/
│   │   └── SKILL.md             # sf agent preview testing
│   └── lwc-dashboard/
│       └── SKILL.md             # LWC dashboard generation
├── README.md
└── LICENSE
```

## Adding New Skills

1. Create `skills/{skill-name}/SKILL.md`
2. Push to repo
3. Users get it on next `git pull`

## Related Projects

- **[agentforce-adlc](https://github.com/almandsky/agentforce-adlc)** — Agent Development Life Cycle skills (author, deploy, test, optimize)
- **[sf-skills](https://github.com/Jaganpro/sf-skills)** — General Salesforce Claude Code skills

## License

MIT
