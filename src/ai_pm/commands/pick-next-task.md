# Pick Next Task

Find and claim the highest-priority task that is ready to work on.

## Instructions

1. Read all YAML files in the `backlog/` directory
2. Filter to tasks where:
   - `status` is `ready`
   - `assignee` is `null`
   - All tasks in `depends_on` have `status: done`
3. Sort by priority: critical > high > medium > low
4. Among equal priority, prefer the lowest task ID (oldest first)
5. If ROLES.yaml exists and specifies agent routing, filter to tasks matching your agent type
6. Claim the task:
   - Set `status: in_progress`
   - Set `assignee` to your session identifier
   - Set `updated` to today's date
7. Report the task you claimed:

```
## Task Claimed
- ID: [task id]
- Title: [title]
- Priority: [priority]
- Definition of Done: [list criteria]
- Dependencies: [resolved dependencies]
```

## If no tasks are available

Report: "No ready tasks found. All tasks are either blocked, in progress, or done."
Check if any blocked tasks can be unblocked.
