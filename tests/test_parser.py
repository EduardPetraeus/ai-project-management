"""Tests for YAML parsing and file discovery."""

import pytest
import yaml

from ai_pm.parser import (
    ParseError,
    discover_yaml_files,
    find_backlog_dir,
    load_all_tasks,
    load_yaml_file,
)


class TestLoadYamlFile:
    """Test YAML file loading."""

    def test_load_valid_yaml(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("id: TASK-001\ntitle: Test\n")
        data = load_yaml_file(f)
        assert data["id"] == "TASK-001"
        assert data["title"] == "Test"

    def test_load_nonexistent_file(self, tmp_path):
        with pytest.raises(ParseError, match="does not exist"):
            load_yaml_file(tmp_path / "missing.yaml")

    def test_load_empty_file(self, tmp_path):
        f = tmp_path / "empty.yaml"
        f.write_text("")
        with pytest.raises(ParseError, match="empty"):
            load_yaml_file(f)

    def test_load_whitespace_only(self, tmp_path):
        f = tmp_path / "blank.yaml"
        f.write_text("   \n  \n")
        with pytest.raises(ParseError, match="empty"):
            load_yaml_file(f)

    def test_load_malformed_yaml(self, tmp_path):
        f = tmp_path / "bad.yaml"
        f.write_text("key: [invalid\n  yaml: broken")
        with pytest.raises(ParseError, match="Invalid YAML"):
            load_yaml_file(f)

    def test_load_non_dict_yaml(self, tmp_path):
        f = tmp_path / "list.yaml"
        f.write_text("- item1\n- item2\n")
        with pytest.raises(ParseError, match="Expected a YAML mapping"):
            load_yaml_file(f)

    def test_load_directory_raises(self, tmp_path):
        with pytest.raises(ParseError, match="not a file"):
            load_yaml_file(tmp_path)

    def test_load_complex_yaml(self, tmp_path):
        f = tmp_path / "complex.yaml"
        f.write_text(
            yaml.dump(
                {
                    "id": "TASK-001",
                    "depends_on": ["TASK-002", "TASK-003"],
                    "tags": ["a", "b"],
                    "nested": {"key": "value"},
                }
            )
        )
        data = load_yaml_file(f)
        assert len(data["depends_on"]) == 2
        assert data["nested"]["key"] == "value"


class TestDiscoverYamlFiles:
    """Test YAML file discovery."""

    def test_discover_in_directory(self, tmp_path):
        (tmp_path / "a.yaml").write_text("x: 1")
        (tmp_path / "b.yaml").write_text("x: 2")
        (tmp_path / "c.txt").write_text("not yaml")
        files = discover_yaml_files(tmp_path)
        assert len(files) == 2

    def test_discover_recursive(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "a.yaml").write_text("x: 1")
        (sub / "b.yaml").write_text("x: 2")
        files = discover_yaml_files(tmp_path, recursive=True)
        assert len(files) == 2

    def test_discover_non_recursive(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "a.yaml").write_text("x: 1")
        (sub / "b.yaml").write_text("x: 2")
        files = discover_yaml_files(tmp_path, recursive=False)
        assert len(files) == 1

    def test_discover_empty_directory(self, tmp_path):
        files = discover_yaml_files(tmp_path)
        assert files == []

    def test_discover_nonexistent_directory(self, tmp_path):
        files = discover_yaml_files(tmp_path / "nope")
        assert files == []

    def test_discover_single_file(self, tmp_path):
        f = tmp_path / "test.yaml"
        f.write_text("x: 1")
        files = discover_yaml_files(f)
        assert files == [f]

    def test_discover_yml_extension(self, tmp_path):
        (tmp_path / "a.yml").write_text("x: 1")
        files = discover_yaml_files(tmp_path)
        assert len(files) == 1

    def test_discover_sorted(self, tmp_path):
        (tmp_path / "c.yaml").write_text("x: 1")
        (tmp_path / "a.yaml").write_text("x: 2")
        (tmp_path / "b.yaml").write_text("x: 3")
        files = discover_yaml_files(tmp_path)
        stems = [f.stem for f in files]
        assert stems == sorted(stems)


class TestLoadAllTasks:
    """Test loading all tasks from a backlog directory."""

    def test_load_tasks(self, tmp_backlog):
        backlog = tmp_backlog / "backlog"
        tasks = load_all_tasks(backlog)
        assert len(tasks) == 3
        assert tasks[0]["id"] == "TASK-001"

    def test_load_empty_backlog(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        tasks = load_all_tasks(backlog)
        assert tasks == []

    def test_ignores_non_task_files(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "TASK-001.yaml").write_text(
            "id: TASK-001\ntitle: Test\nstatus: ready\npriority: high\nagent: code\n"
            "review: auto-merge\ncreated: '2026-01-01'\n"
        )
        (backlog / "README.yaml").write_text("readme: true")
        tasks = load_all_tasks(backlog)
        assert len(tasks) == 1

    def test_sorted_by_id(self, tmp_path):
        backlog = tmp_path / "backlog"
        backlog.mkdir()
        (backlog / "TASK-003.yaml").write_text("id: TASK-003\ntitle: Third\n")
        (backlog / "TASK-001.yaml").write_text("id: TASK-001\ntitle: First\n")
        tasks = load_all_tasks(backlog)
        assert tasks[0]["id"] == "TASK-001"
        assert tasks[1]["id"] == "TASK-003"


class TestFindBacklogDir:
    """Test backlog directory discovery."""

    def test_find_in_current(self, tmp_backlog):
        result = find_backlog_dir(tmp_backlog)
        assert result is not None
        assert result.name == "backlog"

    def test_find_when_pointing_at_backlog(self, tmp_backlog):
        result = find_backlog_dir(tmp_backlog / "backlog")
        assert result is not None

    def test_not_found(self, tmp_path):
        result = find_backlog_dir(tmp_path)
        assert result is None
