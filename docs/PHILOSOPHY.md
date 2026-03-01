# Philosophy

## Why YAML files instead of a database?

1. **Git-native.** Every task change has a commit, a timestamp, and an author. Full audit trail for free.
2. **No merge conflicts.** One file per task means Agent A edits TASK-042.yaml while Agent B edits TASK-043.yaml. They never touch the same file.
3. **Human-readable.** YAML is readable without tools. Open the file, read the task. No UI required.
4. **Machine-parseable.** Agents can read, filter, sort, and update YAML files deterministically. No natural language parsing needed.
5. **Portable.** Works with any CI/CD, any editor, any AI tool. No vendor lock-in.

## Why one file per task?

The alternative — a single backlog.yaml with all tasks — creates merge conflicts the moment two agents work in parallel. This is the #1 failure mode in multi-agent development.

With one file per task:
- Git history shows the lifecycle of each task independently
- Agents can claim and update tasks without coordination
- Sprints reference tasks by ID, not by position in a list
- Deleting a task is deleting a file — clean and atomic

## Design Principles

1. **Separate files over monolithic docs.** One YAML per task, one ADR per decision.
2. **Separation of concerns.** Governance (what may agents do) ≠ PM (what to do) ≠ Standards (how to do it).
3. **Templates are generic, instances are specific.** This repo provides templates. Projects instantiate them with real content.
4. **Machine-readable where possible.** YAML over freeform markdown for anything agents need to parse.
5. **Solo-first, team-ready.** Everything works for one person. Multi-team is additive, not a different architecture.
6. **Ship early, iterate.** First version doesn't need to be perfect.
