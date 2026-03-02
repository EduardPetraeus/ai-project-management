# STATUS — ai-project-management v2 (Workstream 1)

## What Was Done

### New CLI Commands
- **`ai-pm critical-path <path>`** — Shows the longest dependency chain of non-done tasks through the task DAG. Identifies the bottleneck sequence that determines project completion time.
- **`ai-pm pick-next <path>`** — Selects the highest-priority unblocked ready task. Supports `--agent <type>` filter. Only returns tasks with all dependencies resolved and no assignee.

### Cross-File Reference Validation
- **`validate_cross_references(task_dir)`** in `validator.py` — Scans all TASK-*.yaml files and validates that every task ID in `depends_on` and `blocks` fields actually exists in the directory. Reports each broken reference as a human-readable error.
- Integrated into the `ai-pm validate` command: cross-reference errors now appear alongside schema validation results.

### Tests
- 14 new tests added (120 total, all passing):
  - `TestCriticalPathCommand` (4 tests): chain display, all-done case, no-backlog error, DAG longest-path selection
  - `TestPickNextCommand` (4 tests): ready task selection, no-backlog error, no-ready fallback, agent type filtering
  - `TestCrossReferenceValidation` (6 tests): valid refs, nonexistent depends_on (TASK-999), nonexistent blocks, multiple broken refs, empty directory, null depends_on

### README
- Added full CLI section documenting all commands with examples.
- Detailed usage for `critical-path` and `pick-next`.

## What Works
- `ai-pm critical-path .tasks/` outputs the critical path
- `ai-pm pick-next .tasks/` outputs highest-priority unblocked task
- Cross-file ref validation catches TASK-999 references (test proves it)
- All 120 tests pass
- Ruff lint + format clean

## Known Issues
- System Python is 3.9.6; `pyproject.toml` declares `requires-python = ">=3.11"`. All code uses `from __future__ import annotations` so it runs on 3.9, but `pyproject.toml` should be aligned if 3.9 support is intended.
- Package not installed via pip (uses PYTHONPATH for tests). Consider adding a Makefile target or CI step for `pip install -e .`.

## Files Changed
- `src/ai_pm/cli.py` — Added `critical-path` and `pick-next` commands, integrated cross-ref validation into `validate`
- `src/ai_pm/validator.py` — Added `validate_cross_references()` function
- `tests/test_cli.py` — Added `TestCriticalPathCommand` and `TestPickNextCommand`
- `tests/test_validator.py` — Added `TestCrossReferenceValidation`
- `README.md` — Added CLI documentation section
