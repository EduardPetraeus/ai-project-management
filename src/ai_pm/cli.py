"""CLI for the AI Project Management task engine."""

from __future__ import annotations

import sys
from datetime import date
from pathlib import Path

import click
import yaml
from rich.console import Console
from rich.panel import Panel
from rich.table import Table

from ai_pm.engine import TaskEngine, TaskStatus
from ai_pm.parser import ParseError, discover_yaml_files, find_backlog_dir, load_all_tasks, load_yaml_file
from ai_pm.validator import SCHEMAS_DIR, find_schema_for_file, validate_cross_references, validate_file

console = Console()


@click.group()
def cli():
    """AI Project Management — YAML-based task engine."""


@cli.command()
@click.argument("path", type=click.Path(exists=True))
@click.option("--schemas-dir", type=click.Path(exists=True), default=None, help="Custom schemas directory")
def validate(path: str, schemas_dir: str | None):
    """Validate all YAML files against their schemas."""
    target = Path(path)
    schema_dir = Path(schemas_dir) if schemas_dir else SCHEMAS_DIR

    yaml_files = discover_yaml_files(target)

    if not yaml_files:
        console.print(f"[yellow]No YAML files found in {target}[/yellow]")
        sys.exit(0)

    console.print(f"\nValidating {len(yaml_files)} YAML file(s) against schemas in {schema_dir}\n")

    total = 0
    passed = 0
    failed = 0
    skipped = 0

    for yaml_path in yaml_files:
        total += 1
        try:
            data = load_yaml_file(yaml_path)
        except ParseError as e:
            console.print(f"  [red]ERROR[/red] {yaml_path}: {e.reason}")
            failed += 1
            continue

        schema_path = find_schema_for_file(data, yaml_path, schema_dir)
        if schema_path is None:
            console.print(f"  [yellow]SKIP[/yellow] {yaml_path} (no matching schema)")
            skipped += 1
            continue

        is_valid, errors = validate_file(yaml_path, schema_dir, quiet=True)
        if is_valid:
            console.print(f"  [green]PASS[/green] {yaml_path} ({schema_path.stem})")
            passed += 1
        else:
            error_text = "\n".join(f"    - {e}" for e in errors)
            console.print(f"  [red]FAIL[/red] {yaml_path} ({schema_path.stem})\n{error_text}")
            failed += 1

    # Cross-file reference validation
    xref_errors = validate_cross_references(target)
    if xref_errors:
        console.print("\n[bold red]Cross-reference errors:[/bold red]")
        for err in xref_errors:
            console.print(f"  [red]-[/red] {err}")
        failed += len(xref_errors)

    console.print(f"\n[bold]Results:[/bold] {passed} passed, {failed} failed, {skipped} skipped ({total} total)")

    if failed > 0:
        sys.exit(1)


@cli.group()
def task():
    """Task management commands."""


@task.command("list")
@click.option("--status", default=None, help="Filter by status")
@click.option("--priority", default=None, help="Filter by priority")
@click.option("--path", "search_path", type=click.Path(exists=True), default=".", help="Project root or backlog dir")
def task_list(status: str | None, priority: str | None, search_path: str):
    """List tasks from backlog directory."""
    backlog = find_backlog_dir(Path(search_path))
    if backlog is None:
        console.print("[red]No backlog/ directory found with TASK-*.yaml files[/red]")
        sys.exit(1)

    tasks = load_all_tasks(backlog)
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    engine = TaskEngine(tasks)
    filtered = engine.filter_tasks(status=status, priority=priority)

    if not filtered:
        console.print("[yellow]No tasks match the given filters[/yellow]")
        return

    table = Table(title=f"Tasks ({len(filtered)})")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Status", style="bold")
    table.add_column("Priority", style="bold")
    table.add_column("Agent", style="dim")
    table.add_column("Assignee", style="dim")

    priority_colors = {"critical": "red", "high": "yellow", "medium": "white", "low": "dim"}
    status_colors = {
        "backlog": "dim",
        "ready": "cyan",
        "in_progress": "yellow",
        "review": "magenta",
        "done": "green",
        "blocked": "red",
    }

    for t in filtered:
        p = t.get("priority", "medium")
        s = t.get("status", "backlog")
        table.add_row(
            t.get("id", "?"),
            t.get("title", "Untitled"),
            f"[{status_colors.get(s, 'white')}]{s}[/{status_colors.get(s, 'white')}]",
            f"[{priority_colors.get(p, 'white')}]{p}[/{priority_colors.get(p, 'white')}]",
            t.get("agent", "-"),
            t.get("assignee") or "-",
        )

    console.print(table)


@task.command("create")
@click.argument("title")
@click.option("--priority", default="medium", type=click.Choice(["critical", "high", "medium", "low"]))
@click.option("--agent", default="code", type=click.Choice(["code", "test", "docs", "security", "review", "human"]))
@click.option("--path", "search_path", type=click.Path(exists=True), default=".", help="Project root")
def task_create(title: str, priority: str, agent: str, search_path: str):
    """Create a new task YAML from template."""
    project_root = Path(search_path)
    backlog = project_root / "backlog"
    backlog.mkdir(exist_ok=True)

    # Determine next task ID
    existing = sorted(backlog.glob("TASK-*.yaml"))
    if existing:
        last_num = max(int(p.stem.split("-")[1]) for p in existing)
        next_num = last_num + 1
    else:
        next_num = 1

    task_id = f"TASK-{next_num:03d}"
    today = date.today().isoformat()

    task_data = {
        "id": task_id,
        "title": title,
        "description": "TODO: Add detailed description\n",
        "status": "backlog",
        "priority": priority,
        "agent": agent,
        "review": "agent-review",
        "assignee": None,
        "sprint": None,
        "depends_on": [],
        "blocks": [],
        "definition_of_done": ["TODO: Add measurable criteria"],
        "tags": [],
        "estimate": "m",
        "actual_tokens": None,
        "actual_duration_minutes": None,
        "completed": None,
        "created": today,
        "updated": today,
        "notes": "",
    }

    output_path = backlog / f"{task_id}.yaml"
    output_path.write_text(yaml.dump(task_data, default_flow_style=False, sort_keys=False, allow_unicode=True))

    console.print(
        Panel(
            f"[green]Task Created[/green]\n"
            f"  ID: {task_id}\n"
            f"  Title: {title}\n"
            f"  Priority: {priority}\n"
            f"  Agent: {agent}\n"
            f"  Status: backlog\n"
            f"  File: {output_path}",
            title="New Task",
        )
    )


@task.command("complete")
@click.argument("task_id")
@click.option("--path", "search_path", type=click.Path(exists=True), default=".", help="Project root or backlog dir")
@click.option("--tokens", type=int, default=None, help="Tokens consumed")
@click.option("--duration", type=int, default=None, help="Duration in minutes")
def task_complete(task_id: str, search_path: str, tokens: int | None, duration: int | None):
    """Mark a task as done."""
    backlog = find_backlog_dir(Path(search_path))
    if backlog is None:
        console.print("[red]No backlog/ directory found[/red]")
        sys.exit(1)

    # Find the task file
    task_file = backlog / f"{task_id}.yaml"
    if not task_file.exists():
        console.print(f"[red]Task file not found: {task_file}[/red]")
        sys.exit(1)

    try:
        data = load_yaml_file(task_file)
    except ParseError as e:
        console.print(f"[red]Cannot parse task: {e}[/red]")
        sys.exit(1)

    today = date.today().isoformat()

    # Validate transition
    engine = TaskEngine([data])
    try:
        current = TaskStatus(data["status"])
        if current in (TaskStatus.IN_PROGRESS, TaskStatus.REVIEW):
            if current == TaskStatus.IN_PROGRESS:
                engine.transition(task_id, TaskStatus.REVIEW)
                engine.transition(task_id, TaskStatus.DONE)
            else:
                engine.transition(task_id, TaskStatus.DONE)
        else:
            msg = f"Cannot complete: status '{data['status']}' is not in_progress or review."
            console.print(f"[red]{msg}[/red]")
            sys.exit(1)
    except Exception as e:
        console.print(f"[red]Transition error: {e}[/red]")
        sys.exit(1)

    # Update task data
    data["status"] = "done"
    data["completed"] = today
    data["updated"] = today
    if tokens is not None:
        data["actual_tokens"] = tokens
    if duration is not None:
        data["actual_duration_minutes"] = duration

    # Write back
    task_file.write_text(yaml.dump(data, default_flow_style=False, sort_keys=False, allow_unicode=True))

    # Check for unblocked tasks
    all_tasks = load_all_tasks(backlog)
    unblocked = []
    for other in all_tasks:
        if other.get("id") == task_id:
            continue
        deps = other.get("depends_on", []) or []
        if task_id in deps and other.get("status") == "blocked":
            all_deps_done = all(any(t.get("id") == d and t.get("status") == "done" for t in all_tasks) for d in deps)
            if all_deps_done:
                # Update blocked task to ready
                other_file = backlog / f"{other['id']}.yaml"
                if other_file.exists():
                    other["status"] = "ready"
                    other["updated"] = today
                    other_file.write_text(
                        yaml.dump(other, default_flow_style=False, sort_keys=False, allow_unicode=True)
                    )
                    unblocked.append(other["id"])

    console.print(
        Panel(
            f"[green]Task Complete[/green]\n"
            f"  ID: {task_id}\n"
            f"  Title: {data.get('title', '?')}\n"
            f"  Status: done\n"
            f"  Completed: {today}\n"
            f"  Unblocked: {', '.join(unblocked) if unblocked else 'none'}",
            title="Done",
        )
    )


@cli.command("critical-path")
@click.argument("path", type=click.Path(exists=True))
def critical_path_cmd(path: str):
    """Show the critical path (longest dependency chain) through the task DAG."""
    target = Path(path)
    backlog = find_backlog_dir(target)

    if backlog is None:
        console.print("[red]No backlog/ directory found with TASK-*.yaml files[/red]")
        sys.exit(1)

    tasks = load_all_tasks(backlog)
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    engine = TaskEngine(tasks)
    cp = engine.critical_path()

    if not cp:
        console.print("[green]All tasks are done — no critical path.[/green]")
        return

    console.print(f"\n[bold]Critical Path ({len(cp)} tasks):[/bold]\n")
    for i, task_id in enumerate(cp, 1):
        task = engine.get_task(task_id)
        title = task.get("title", "Untitled") if task else "?"
        status = task.get("status", "?") if task else "?"
        console.print(f"  {i}. [cyan]{task_id}[/cyan] — {title} [{status}]")
        if i < len(cp):
            console.print("     |")

    console.print()


@cli.command("pick-next")
@click.argument("path", type=click.Path(exists=True))
@click.option("--agent", default=None, help="Filter by agent type")
def pick_next_cmd(path: str, agent: str | None):
    """Pick the highest-priority unblocked task ready for work."""
    target = Path(path)
    backlog = find_backlog_dir(target)

    if backlog is None:
        console.print("[red]No backlog/ directory found with TASK-*.yaml files[/red]")
        sys.exit(1)

    tasks = load_all_tasks(backlog)
    if not tasks:
        console.print("[yellow]No tasks found[/yellow]")
        return

    engine = TaskEngine(tasks)
    picked = engine.pick_next(agent_type=agent)

    if picked is None:
        console.print("[yellow]No unblocked ready tasks available.[/yellow]")
        return

    console.print(
        Panel(
            f"[green]Next Task[/green]\n"
            f"  ID:       {picked.get('id', '?')}\n"
            f"  Title:    {picked.get('title', 'Untitled')}\n"
            f"  Priority: {picked.get('priority', '?')}\n"
            f"  Agent:    {picked.get('agent', '?')}\n"
            f"  Status:   {picked.get('status', '?')}\n"
            f"  Deps:     {', '.join(picked.get('depends_on', []) or []) or 'none'}",
            title="Pick Next",
        )
    )


@cli.command()
@click.argument("path", type=click.Path(exists=True))
def lint(path: str):
    """Check for orphaned refs, circular deps, missing fields."""
    target = Path(path)
    backlog = find_backlog_dir(target)

    if backlog is None:
        console.print("[yellow]No backlog/ directory found. Checking YAML validity only.[/yellow]")
        yaml_files = discover_yaml_files(target)
        issues = 0
        for yf in yaml_files:
            try:
                load_yaml_file(yf)
                console.print(f"  [green]OK[/green] {yf}")
            except ParseError as e:
                console.print(f"  [red]ERROR[/red] {yf}: {e.reason}")
                issues += 1
        if issues:
            sys.exit(1)
        return

    tasks = load_all_tasks(backlog)
    if not tasks:
        console.print("[yellow]No tasks found in backlog[/yellow]")
        return

    engine = TaskEngine(tasks)
    task_ids = set(engine.tasks.keys())
    issues: list[str] = []

    # Check for orphaned dependency references
    for tid, task in engine.tasks.items():
        for dep in task.get("depends_on", []) or []:
            if dep not in task_ids:
                issues.append(f"{tid}: depends_on references non-existent task '{dep}'")

        for blocked in task.get("blocks", []) or []:
            if blocked not in task_ids:
                issues.append(f"{tid}: blocks references non-existent task '{blocked}'")

    # Check for circular dependencies
    cycles = engine.detect_circular_dependencies()
    for cycle in cycles:
        issues.append(f"Circular dependency: {' -> '.join(cycle)}")

    # Check for missing required fields
    required_fields = ["id", "title", "status", "priority"]
    for tid, task in engine.tasks.items():
        for field in required_fields:
            if field not in task or task[field] is None:
                issues.append(f"{tid}: missing required field '{field}'")

    # Check for tasks stuck in_progress without assignee
    for tid, task in engine.tasks.items():
        if task.get("status") == "in_progress" and not task.get("assignee"):
            issues.append(f"{tid}: status is 'in_progress' but no assignee set")

    # Check for blocked tasks with all dependencies done
    for tid, task in engine.tasks.items():
        if task.get("status") == "blocked":
            deps = task.get("depends_on", []) or []
            all_done = all(engine.tasks.get(d, {}).get("status") == "done" for d in deps if d in task_ids)
            if all_done and deps:
                issues.append(f"{tid}: status is 'blocked' but all dependencies are done (should be 'ready')")

    if issues:
        console.print(
            Panel(
                "\n".join(f"  [red]-[/red] {i}" for i in issues),
                title=f"[red]Lint Issues ({len(issues)})[/red]",
            )
        )
        sys.exit(1)
    else:
        console.print(f"[green]No issues found across {len(tasks)} tasks[/green]")


@cli.group()
def sprint():
    """Sprint management commands."""


@sprint.command("status")
@click.option("--path", "search_path", type=click.Path(exists=True), default=".", help="Project root")
def sprint_status(search_path: str):
    """Show current sprint summary."""
    project_root = Path(search_path)

    # Look for sprint files
    sprint_dirs = [
        project_root / "sprints",
        project_root / "templates" / "sprints",
    ]

    sprint_files: list[Path] = []
    for sprint_dir in sprint_dirs:
        if sprint_dir.exists():
            sprint_files.extend(f for f in sprint_dir.glob("*.yaml") if not f.stem.endswith("TEMPLATE"))

    if not sprint_files:
        console.print("[yellow]No sprint files found. Showing task summary instead.[/yellow]\n")
        _show_task_summary(project_root)
        return

    # Find active sprint
    active_sprint = None
    for sf in sprint_files:
        try:
            data = load_yaml_file(sf)
            if data.get("status") == "active":
                active_sprint = data
                break
        except ParseError:
            continue

    if active_sprint is None:
        console.print("[yellow]No active sprint. Showing task summary.[/yellow]\n")
        _show_task_summary(project_root)
        return

    # Load tasks for this sprint
    backlog = find_backlog_dir(project_root)
    all_tasks = load_all_tasks(backlog) if backlog else []
    sprint_task_ids = set(active_sprint.get("tasks", []))
    sprint_tasks = [t for t in all_tasks if t.get("id") in sprint_task_ids]

    # Build status counts
    status_counts: dict[str, int] = {}
    for t in sprint_tasks:
        s = t.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    total = len(sprint_tasks)
    done = status_counts.get("done", 0)
    progress = f"{done}/{total}" if total > 0 else "0/0"

    table = Table(title=f"Sprint {active_sprint.get('id', '?')}: {active_sprint.get('title', '?')}")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")

    for s in ["done", "review", "in_progress", "ready", "blocked", "backlog"]:
        if s in status_counts:
            table.add_row(s, str(status_counts[s]))

    console.print(table)
    console.print(f"\n[bold]Progress:[/bold] {progress} tasks completed")
    if active_sprint.get("goal"):
        console.print(f"[bold]Goal:[/bold] {active_sprint['goal'].strip()}")


def _show_task_summary(project_root: Path) -> None:
    """Show a summary of all tasks when no sprint is active."""
    backlog = find_backlog_dir(project_root)
    if backlog is None:
        console.print("[dim]No backlog/ directory found[/dim]")
        return

    tasks = load_all_tasks(backlog)
    if not tasks:
        console.print("[dim]No tasks found[/dim]")
        return

    status_counts: dict[str, int] = {}
    for t in tasks:
        s = t.get("status", "unknown")
        status_counts[s] = status_counts.get(s, 0) + 1

    table = Table(title=f"Task Summary ({len(tasks)} total)")
    table.add_column("Status", style="bold")
    table.add_column("Count", justify="right")

    for s in ["done", "review", "in_progress", "ready", "blocked", "backlog"]:
        if s in status_counts:
            table.add_row(s, str(status_counts[s]))

    console.print(table)


if __name__ == "__main__":
    cli()
