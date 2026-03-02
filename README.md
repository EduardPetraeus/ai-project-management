# ai-project-management

YAML-based project management framework for agentic engineering. One file per task, zero merge conflicts. Works solo or multi-team.

## Quick Start

```bash
# 1. Copy templates into your project
cp -r templates/backlog/ your-project/backlog/
cp templates/ROADMAP.yaml your-project/
cp templates/ROLES.yaml your-project/

# 2. Install Claude Code commands
cp commands/*.md your-project/.claude/commands/

# 3. Create your first task
cp your-project/backlog/TASK-TEMPLATE.yaml your-project/backlog/TASK-001.yaml
# Edit TASK-001.yaml with real content

# 4. Start working
# Use /pick-next-task to claim work
# Use /complete-task when done
# Use /create-task to add new tasks
```

## Why?

AI agents working in parallel need a task system that:
- **Never creates merge conflicts** — one YAML file per task
- **Is machine-readable** — agents parse YAML, not freeform text
- **Has git history** — every status change is a commit
- **Scales from solo to team** — same format, additive complexity

## Structure

```
templates/
├── backlog/TASK-TEMPLATE.yaml    # one file per task
├── sprints/SPRINT-TEMPLATE.yaml  # sprint goal + task refs
├── ROADMAP.yaml                  # milestones, not tasks
├── ROLES.yaml                    # agent routing
├── TRUST_PROFILE.yaml            # trust levels (governance integration)
└── METRICS.yaml                  # performance tracking

schemas/
└── task-schema.json              # JSON Schema for task validation

commands/
├── pick-next-task.md             # find and claim next task
├── complete-task.md              # mark task done + update metrics
└── create-task.md                # scaffold new task

examples/
├── solo-developer/               # one person, one agent
└── multi-team/                   # multiple agents, role routing

docs/
├── PHILOSOPHY.md                 # design decisions
└── INTEGRATION.md                # connecting to governance + standards
```

## CLI

Install: `pip install -e .` (or add `src/` to `PYTHONPATH`).

```bash
# Validate all YAML files against schemas (+ cross-reference check)
ai-pm validate .tasks/

# Lint tasks for orphaned refs, circular deps, missing fields
ai-pm lint .tasks/

# List tasks (with optional filters)
ai-pm task list --path .
ai-pm task list --status ready --path .

# Create a new task
ai-pm task create "Implement feature X" --priority high --agent code

# Complete a task
ai-pm task complete TASK-001 --tokens 5000 --duration 30

# Show the critical path through the task DAG
ai-pm critical-path .tasks/

# Pick the highest-priority unblocked task ready for work
ai-pm pick-next .tasks/
ai-pm pick-next .tasks/ --agent code

# Sprint status
ai-pm sprint status --path .
```

### `critical-path`

Shows the longest dependency chain of non-done tasks. Useful for identifying the bottleneck sequence that determines project completion time.

```
$ ai-pm critical-path backlog/

Critical Path (3 tasks):

  1. TASK-001 — Set up database schema [ready]
     |
  2. TASK-002 — Implement API endpoints [blocked]
     |
  3. TASK-003 — Write integration tests [blocked]
```

### `pick-next`

Selects the highest-priority task that is in `ready` status, has all dependencies resolved (done), and is unassigned. Optionally filter by agent type.

```
$ ai-pm pick-next backlog/

╭─ Pick Next ──────────────────────╮
│ Next Task                        │
│   ID:       TASK-002             │
│   Title:    Implement API        │
│   Priority: high                 │
│   Agent:    code                 │
│   Status:   ready                │
│   Deps:     TASK-001             │
╰──────────────────────────────────╯
```

## Task Lifecycle

```
backlog → ready → in_progress → review → done
                                  ↑
                               blocked (unblocked when dependencies resolve)
```

## Part of the Agentic Engineering OS

| Repo | Role |
|------|------|
| [ai-governance-framework](https://github.com/EduardPetraeus/ai-governance-framework) | What may agents do |
| **ai-project-management** (this repo) | **What to do** |
| [ai-engineering-standards](https://github.com/EduardPetraeus/ai-engineering-standards) | How to do it |
| [ai-project-templates](https://github.com/EduardPetraeus/ai-project-templates) | Scaffolder |
| [agentic-engineering](https://github.com/EduardPetraeus/agentic-engineering) | Umbrella docs |

## License

MIT
