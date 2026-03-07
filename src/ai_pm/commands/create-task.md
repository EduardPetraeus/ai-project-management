# Create Task

Scaffold a new task from the template.

## Arguments

Provide: title, priority, agent type, and definition of done.
Example: `/create-task "Implement user authentication" high code "JWT tokens working" "Login endpoint returns 200" "Tests pass"`

## Instructions

1. Determine the next task ID:
   - Read all existing files in `backlog/`
   - Find the highest TASK-XXX number
   - Increment by 1 (e.g., TASK-042 → TASK-043)
2. Copy `templates/backlog/TASK-TEMPLATE.yaml` to `backlog/TASK-[next-id].yaml`
3. Fill in the provided values:
   - `id`: the new task ID
   - `title`: from argument
   - `priority`: from argument (default: medium)
   - `agent`: from argument (default: code)
   - `definition_of_done`: from arguments
   - `status`: `backlog` (default) or `ready` if no dependencies
   - `created` and `updated`: today's date
4. Report:

```
## Task Created
- ID: [task id]
- Title: [title]
- Priority: [priority]
- Agent: [agent type]
- Status: [status]
- File: backlog/[filename]
```
