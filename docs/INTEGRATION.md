# Integration Guide

## How this connects to the Agentic Engineering OS

```
┌─────────────────────────────────────────────────────┐
│          agentic-engineering (umbrella)               │
├─────────────┬─────────────────┬──────────────────────┤
│ governance  │ project-mgmt    │ engineering-standards │
│ "what may   │ "what to do"    │ "how to do it"       │
│  agent do?" │  ← THIS REPO   │                      │
├─────────────┴─────────────────┴──────────────────────┤
│          ai-project-templates (scaffolder)            │
└─────────────────────────────────────────────────────┘
```

## Setting up in a project repo

### 1. Copy templates

```bash
cp -r ai-project-management/templates/backlog/ your-project/backlog/
cp ai-project-management/templates/ROADMAP.yaml your-project/
cp ai-project-management/templates/ROLES.yaml your-project/
cp ai-project-management/templates/METRICS.yaml your-project/
```

### 2. Install commands

Copy commands to your project's Claude Code commands directory:

```bash
mkdir -p your-project/.claude/commands
cp ai-project-management/commands/*.md your-project/.claude/commands/
```

### 3. Add to CLAUDE.md

Add this section to your project's CLAUDE.md:

```markdown
## Task Management

Tasks live in `backlog/` as individual YAML files (one per task).
Use `/pick-next-task` to find work, `/complete-task` when done, `/create-task` to add new tasks.
Task format defined in ai-project-management/schemas/task-schema.json.
```

### 4. Create your first tasks

```bash
# Copy the template and customize
cp backlog/TASK-TEMPLATE.yaml backlog/TASK-001.yaml
# Edit TASK-001.yaml with your first real task
```

## Governance integration

- `TRUST_PROFILE.yaml` maps to governance framework trust levels
- `ROLES.yaml` agent types align with governance agent tiers
- Review levels (`auto-merge`, `agent-review`, `human-review`) enforce governance blast radius control

## Metrics and observability

- `METRICS.yaml` tracks tokens, duration, and velocity per sprint
- `complete-task` command populates actual metrics on task files
- Use this data to optimize agent performance over time
