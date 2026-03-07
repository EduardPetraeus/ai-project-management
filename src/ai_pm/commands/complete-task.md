# Complete Task

Mark the current task as done and update metrics.

## Instructions

1. Verify all `definition_of_done` criteria are met
2. Update the task YAML file:
   - Set `status: done` (or `review` if review is required)
   - Set `completed` to today's date
   - Set `updated` to today's date
   - Set `actual_tokens` if available
   - Set `actual_duration_minutes` if available
   - Add any relevant notes
3. Check if completing this task unblocks other tasks:
   - Find all tasks that have this task ID in their `depends_on`
   - For each: if ALL dependencies are now `done`, change status from `blocked` to `ready`
4. Update METRICS.yaml if it exists (increment counters)
5. Report:

```
## Task Complete
- ID: [task id]
- Title: [title]
- Status: done
- Definition of Done: [all criteria met ✅]
- Unblocked: [list of task IDs now ready, or "none"]
- Tokens used: [if available]
- Next: [suggested next task or "run pick-next-task"]
```
