# Integration Guide

## Setting up in a project

### Option 1: Using `ai-pm init` (recommended)

```bash
pip install ai-pm
cd your-project
ai-pm init
```

This creates:
- `backlog/` with task template
- `sprints/` with sprint template
- `ROADMAP.yaml`, `ROLES.yaml`, `METRICS.yaml`, `TRUST_PROFILE.yaml`
- `.claude/commands/` with Claude Code slash commands

### Option 2: Manual setup

```bash
# Copy templates from the repo
cp -r templates/backlog/ your-project/backlog/
cp templates/ROADMAP.yaml your-project/
cp templates/ROLES.yaml your-project/
cp templates/METRICS.yaml your-project/

# Install Claude Code commands
mkdir -p your-project/.claude/commands
cp commands/*.md your-project/.claude/commands/
```

### Add to CLAUDE.md

Add this section to your project's CLAUDE.md:

```markdown
## Task Management

Tasks live in `backlog/` as individual YAML files (one per task).
Use `/pick-next-task` to find work, `/complete-task` when done, `/create-task` to add new tasks.
Validate with: `ai-pm validate backlog/`
```

### Create your first tasks

```bash
# Use the CLI
ai-pm task create "Implement feature X" --priority high --agent code

# Or copy the template manually
cp backlog/TASK-TEMPLATE.yaml backlog/TASK-001.yaml
```

## Governance integration

- `TRUST_PROFILE.yaml` defines trust levels for different agent types
- `ROLES.yaml` agent types control which agents can claim which tasks
- Review levels (`auto-merge`, `agent-review`, `human-review`) enforce blast radius control

## Metrics and observability

- `METRICS.yaml` tracks tokens, duration, and velocity per sprint
- `ai-pm task complete` populates actual metrics on task files
- Use this data to optimize agent performance over time
