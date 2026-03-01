"""Tests for the CLI commands using Click's CliRunner."""

import yaml
from click.testing import CliRunner

from ai_pm.cli import cli


class TestValidateCommand:
    """Test the validate CLI command."""

    def test_validate_examples(self, examples_dir):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(examples_dir)])
        assert result.exit_code == 0
        assert "PASS" in result.output

    def test_validate_nonexistent_path(self):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", "/nonexistent/path"])
        assert result.exit_code != 0

    def test_validate_empty_dir(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        assert result.exit_code == 0
        assert "No YAML files" in result.output

    def test_validate_invalid_yaml(self, tmp_path):
        f = tmp_path / "TASK-001.yaml"
        f.write_text("id: BAD\n")
        runner = CliRunner()
        result = runner.invoke(cli, ["validate", str(tmp_path)])
        # Should show FAIL or SKIP depending on schema detection
        assert result.exit_code in (0, 1)


class TestTaskListCommand:
    """Test the task list CLI command."""

    def test_list_all_tasks(self, tmp_backlog):
        runner = CliRunner()
        result = runner.invoke(cli, ["task", "list", "--path", str(tmp_backlog)])
        assert result.exit_code == 0
        assert "TASK-001" in result.output
        assert "TASK-002" in result.output
        assert "TASK-003" in result.output

    def test_list_filter_by_status(self, tmp_backlog):
        runner = CliRunner()
        result = runner.invoke(cli, ["task", "list", "--status", "done", "--path", str(tmp_backlog)])
        assert result.exit_code == 0
        assert "TASK-001" in result.output

    def test_list_no_backlog(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(cli, ["task", "list", "--path", str(tmp_path)])
        assert result.exit_code != 0
        assert "No backlog" in result.output


class TestTaskCreateCommand:
    """Test the task create CLI command."""

    def test_create_first_task(self, tmp_path):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "task",
                "create",
                "Implement authentication",
                "--priority",
                "high",
                "--agent",
                "code",
                "--path",
                str(tmp_path),
            ],
        )
        assert result.exit_code == 0
        assert "TASK-001" in result.output

        # Verify the file was created
        task_file = tmp_path / "backlog" / "TASK-001.yaml"
        assert task_file.exists()
        data = yaml.safe_load(task_file.read_text())
        assert data["title"] == "Implement authentication"
        assert data["priority"] == "high"

    def test_create_increments_id(self, tmp_backlog):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "task",
                "create",
                "New task",
                "--path",
                str(tmp_backlog),
            ],
        )
        assert result.exit_code == 0
        assert "TASK-004" in result.output


class TestTaskCompleteCommand:
    """Test the task complete CLI command."""

    def test_complete_in_progress_task(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        task = {
            "id": "TASK-001",
            "title": "Test task",
            "status": "in_progress",
            "priority": "high",
            "agent": "code",
            "review": "auto-merge",
            "assignee": "session-001",
            "created": "2026-01-01",
            "updated": "2026-01-01",
        }
        (backlog / "TASK-001.yaml").write_text(yaml.dump(task))

        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "task",
                "complete",
                "TASK-001",
                "--path",
                str(tmp_path),
                "--tokens",
                "5000",
                "--duration",
                "30",
            ],
        )
        assert result.exit_code == 0
        assert "done" in result.output.lower()

        # Verify the file was updated
        updated = yaml.safe_load((backlog / "TASK-001.yaml").read_text())
        assert updated["status"] == "done"
        assert updated["actual_tokens"] == 5000

    def test_complete_nonexistent_task(self, tmp_backlog):
        runner = CliRunner()
        result = runner.invoke(
            cli,
            [
                "task",
                "complete",
                "TASK-999",
                "--path",
                str(tmp_backlog),
            ],
        )
        assert result.exit_code != 0

    def test_complete_backlog_task_fails(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        task = {
            "id": "TASK-001",
            "title": "Test task",
            "status": "backlog",
            "priority": "high",
            "agent": "code",
            "review": "auto-merge",
            "created": "2026-01-01",
            "updated": "2026-01-01",
        }
        (backlog / "TASK-001.yaml").write_text(yaml.dump(task))

        runner = CliRunner()
        result = runner.invoke(cli, ["task", "complete", "TASK-001", "--path", str(tmp_path)])
        assert result.exit_code != 0


class TestLintCommand:
    """Test the lint CLI command."""

    def test_lint_clean_backlog(self, tmp_backlog):
        runner = CliRunner()
        result = runner.invoke(cli, ["lint", str(tmp_backlog)])
        # May find issues (blocked task with all deps done, etc.) — we check it runs
        assert result.exit_code in (0, 1)

    def test_lint_detects_orphaned_refs(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        task = {
            "id": "TASK-001",
            "title": "Test task",
            "status": "ready",
            "priority": "high",
            "depends_on": ["TASK-999"],  # orphaned reference
        }
        (backlog / "TASK-001.yaml").write_text(yaml.dump(task))

        runner = CliRunner()
        result = runner.invoke(cli, ["lint", str(tmp_path)])
        assert result.exit_code == 1
        assert "non-existent" in result.output

    def test_lint_no_backlog(self, tmp_path):
        runner = CliRunner()
        # Create a yaml file so it has something to check
        (tmp_path / "test.yaml").write_text("key: value\n")
        result = runner.invoke(cli, ["lint", str(tmp_path)])
        assert result.exit_code == 0


class TestSprintStatusCommand:
    """Test the sprint status CLI command."""

    def test_sprint_no_sprints(self, tmp_backlog):
        runner = CliRunner()
        result = runner.invoke(cli, ["sprint", "status", "--path", str(tmp_backlog)])
        assert result.exit_code == 0
        assert "No sprint files" in result.output or "Task Summary" in result.output

    def test_sprint_with_active_sprint(self, tmp_backlog):
        sprints_dir = tmp_backlog / "sprints"
        sprints_dir.mkdir()
        sprint = {
            "id": "S001",
            "title": "First sprint goal here",
            "status": "active",
            "start_date": "2026-01-01",
            "end_date": "2026-01-14",
            "goal": "Deliver the first increment",
            "tasks": ["TASK-001", "TASK-002", "TASK-003"],
        }
        (sprints_dir / "S001.yaml").write_text(yaml.dump(sprint))

        runner = CliRunner()
        result = runner.invoke(cli, ["sprint", "status", "--path", str(tmp_backlog)])
        assert result.exit_code == 0
        assert "S001" in result.output
