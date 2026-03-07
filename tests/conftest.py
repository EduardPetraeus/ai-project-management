"""Shared fixtures for the ai-pm test suite."""

from pathlib import Path

import pytest
import yaml


@pytest.fixture()
def tmp_backlog(tmp_path):
    """Create a temporary backlog directory with sample tasks."""
    backlog = tmp_path / "backlog"
    backlog.mkdir()

    tasks = [
        {
            "id": "TASK-001",
            "title": "Set up database schema",
            "description": "Create initial database tables.",
            "status": "done",
            "priority": "high",
            "agent": "code",
            "review": "agent-review",
            "assignee": "session-001",
            "sprint": "S001",
            "depends_on": [],
            "blocks": ["TASK-002"],
            "definition_of_done": ["Tables created", "Migrations run"],
            "tags": ["backend", "database"],
            "estimate": "m",
            "actual_tokens": 30000,
            "actual_duration_minutes": 15,
            "completed": "2026-01-15",
            "created": "2026-01-10",
            "updated": "2026-01-15",
            "notes": "Completed successfully.",
        },
        {
            "id": "TASK-002",
            "title": "Implement API endpoints",
            "description": "Build REST API for the service.",
            "status": "ready",
            "priority": "high",
            "agent": "code",
            "review": "agent-review",
            "assignee": None,
            "sprint": "S001",
            "depends_on": ["TASK-001"],
            "blocks": ["TASK-003"],
            "definition_of_done": ["Endpoints return correct status codes", "Tests pass"],
            "tags": ["backend", "api"],
            "estimate": "l",
            "actual_tokens": None,
            "actual_duration_minutes": None,
            "completed": None,
            "created": "2026-01-10",
            "updated": "2026-01-10",
            "notes": "",
        },
        {
            "id": "TASK-003",
            "title": "Write integration tests",
            "description": "End-to-end tests for the API.",
            "status": "blocked",
            "priority": "medium",
            "agent": "test",
            "review": "auto-merge",
            "assignee": None,
            "sprint": "S001",
            "depends_on": ["TASK-002"],
            "blocks": [],
            "definition_of_done": ["90% coverage", "All endpoints tested"],
            "tags": ["testing"],
            "estimate": "m",
            "actual_tokens": None,
            "actual_duration_minutes": None,
            "completed": None,
            "created": "2026-01-10",
            "updated": "2026-01-10",
            "notes": "",
        },
    ]

    for task in tasks:
        path = backlog / f"{task['id']}.yaml"
        path.write_text(yaml.dump(task, default_flow_style=False, sort_keys=False))

    return tmp_path


@pytest.fixture()
def sample_tasks():
    """Return a list of sample task dicts for engine tests."""
    return [
        {
            "id": "TASK-001",
            "title": "First task",
            "status": "done",
            "priority": "high",
            "agent": "code",
            "depends_on": [],
            "blocks": ["TASK-002"],
            "tags": ["backend"],
            "assignee": "session-001",
        },
        {
            "id": "TASK-002",
            "title": "Second task",
            "status": "ready",
            "priority": "high",
            "agent": "code",
            "depends_on": ["TASK-001"],
            "blocks": ["TASK-003"],
            "tags": ["backend"],
            "assignee": None,
        },
        {
            "id": "TASK-003",
            "title": "Third task",
            "status": "blocked",
            "priority": "medium",
            "agent": "test",
            "depends_on": ["TASK-002"],
            "blocks": [],
            "tags": ["testing"],
            "assignee": None,
        },
    ]


@pytest.fixture()
def circular_tasks():
    """Return tasks with circular dependencies."""
    return [
        {"id": "TASK-001", "title": "A", "status": "backlog", "priority": "high", "depends_on": ["TASK-003"]},
        {"id": "TASK-002", "title": "B", "status": "backlog", "priority": "high", "depends_on": ["TASK-001"]},
        {"id": "TASK-003", "title": "C", "status": "backlog", "priority": "high", "depends_on": ["TASK-002"]},
    ]


@pytest.fixture()
def schemas_dir():
    """Return path to the actual schemas directory."""
    return Path(__file__).resolve().parent.parent / "src" / "ai_pm" / "schemas"


@pytest.fixture()
def examples_dir():
    """Return path to the examples directory."""
    return Path(__file__).resolve().parent.parent / "examples"


@pytest.fixture()
def templates_dir():
    """Return path to the templates directory."""
    return Path(__file__).resolve().parent.parent / "src" / "ai_pm" / "templates"
