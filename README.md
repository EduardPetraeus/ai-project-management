# ai-pm

[![PyPI version](https://img.shields.io/pypi/v/ai-pm.svg)](https://pypi.org/project/ai-pm/)
[![Python](https://img.shields.io/pypi/pyversions/ai-pm.svg)](https://pypi.org/project/ai-pm/)
[![CI](https://github.com/EduardPetraeus/ai-project-management/actions/workflows/ci.yml/badge.svg)](https://github.com/EduardPetraeus/ai-project-management/actions)
[![License: MIT](https://img.shields.io/badge/License-MIT-blue.svg)](https://opensource.org/licenses/MIT)

**YAML-based task engine for agentic software development.** One file per task, zero merge conflicts. Designed for AI agents, not humans.

## Why ai-pm?

AI agents working in parallel break traditional project management:

| Problem | Traditional tools | ai-pm |
|---------|------------------|-------|
| Two agents edit the same task board | Merge conflict | Each task is a separate YAML file -- no conflicts |
| Agent needs to parse task status | Scrape UI or freeform text | Machine-readable YAML with JSON Schema validation |
| Track what changed | Lost in database | Every status change is a git commit |
| Scale from 1 agent to 10 | Different tool needed | Same format, additive complexity |

**ai-pm is project management built for the agentic era.** If you're building with Claude Code, Cursor, Aider, or any AI coding agent, this is how you coordinate their work.

## Install

```bash
pip install ai-pm
```

## Quick Start

```bash
# Initialize a project with templates and commands
ai-pm init

# Create your first task
ai-pm task create "Implement user authentication" --priority high --agent code

# List tasks
ai-pm task list

# Validate all YAML files against schemas
ai-pm validate backlog/

# Pick the highest-priority unblocked task
ai-pm pick-next backlog/

# Complete a task with metrics
ai-pm task complete TASK-001 --tokens 5000 --duration 30

# Show the critical path through the task DAG
ai-pm critical-path backlog/

# Lint for orphaned refs, circular deps, missing fields
ai-pm lint backlog/

# Sprint status
ai-pm sprint status
```

## Task Lifecycle

```
backlog --> ready --> in_progress --> review --> done
                                       ^
                                    blocked (auto-unblocked when dependencies resolve)
```

## Project Structure (after `ai-pm init`)

```
your-project/
  backlog/
    TASK-TEMPLATE.yaml      # one file per task
    TASK-001.yaml
    TASK-002.yaml
  sprints/
    SPRINT-TEMPLATE.yaml    # sprint goal + task refs
  ROADMAP.yaml              # milestones
  ROLES.yaml                # agent routing
  METRICS.yaml              # performance tracking
  TRUST_PROFILE.yaml        # trust levels
  .claude/commands/
    pick-next-task.md        # Claude Code slash commands
    complete-task.md
    create-task.md
```

## Task Format

Each task is a standalone YAML file:

```yaml
id: TASK-001
title: "Implement user authentication"
description: |
  Build JWT-based auth with refresh token rotation.
  Store sessions in Redis. Follow OWASP guidelines.

status: ready             # backlog | ready | in_progress | review | done | blocked
priority: high            # critical | high | medium | low
agent: code               # code | test | docs | security | review | human
review: agent-review      # auto-merge | agent-review | human-review
assignee: null            # agent-session-id or person
sprint: S001

depends_on: []            # tasks that must complete first
blocks: [TASK-005]        # tasks waiting on this one

definition_of_done:
  - "JWT generation and validation working"
  - "Refresh token rotation implemented"
  - "Unit tests pass"

tags: [backend, auth]
estimate: l               # xs | s | m | l | xl
```

## Schema Validation

All YAML files are validated against bundled JSON Schemas:

```bash
ai-pm validate .          # validates tasks, sprints, roadmaps, roles, metrics
ai-pm validate backlog/   # validate only tasks
```

Schemas auto-detect the file type based on content structure -- no configuration needed.

## Integration with Claude Code

After running `ai-pm init`, your project gets Claude Code slash commands:

- `/pick-next-task` -- find and claim the next task
- `/complete-task` -- mark a task as done with metrics
- `/create-task` -- scaffold a new task YAML

These commands work out of the box with Claude Code's `/` command system.

## Examples

See the [`examples/`](examples/) directory for complete setups:

- **[solo-developer](examples/solo-developer/)** -- one person, one agent
- **[multi-team](examples/multi-team/)** -- multiple agents with role routing and parallel work

## Contributing

See [CONTRIBUTING.md](CONTRIBUTING.md) for guidelines.

## License

MIT
